"""
Webhook API Routes
Support for webhook notifications on generation/export events
"""

from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
import hmac
import hashlib
import httpx
from datetime import datetime

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

# In-memory storage (should be database in production)
webhooks_db = {}


class WebhookCreate(BaseModel):
    url: HttpUrl
    events: List[str]
    secret: Optional[str] = None


class Webhook(BaseModel):
    id: str
    url: str
    events: List[str]
    secret: Optional[str] = None
    created_at: datetime
    is_active: bool = True


class WebhookEvent(BaseModel):
    event: str
    data: dict
    timestamp: datetime


@router.post("", response_model=Webhook)
async def create_webhook(webhook: WebhookCreate):
    """
    Create a new webhook subscription
    
    Events:
    - generation.started
    - generation.completed
    - generation.failed
    - export.started
    - export.completed
    - export.failed
    """
    webhook_id = f"wh_{datetime.now().timestamp()}"
    
    new_webhook = Webhook(
        id=webhook_id,
        url=str(webhook.url),
        events=webhook.events,
        secret=webhook.secret,
        created_at=datetime.now()
    )
    
    webhooks_db[webhook_id] = new_webhook
    return new_webhook


@router.get("", response_model=List[Webhook])
async def list_webhooks():
    """List all webhooks"""
    return list(webhooks_db.values())


@router.get("/{webhook_id}", response_model=Webhook)
async def get_webhook(webhook_id: str):
    """Get webhook by ID"""
    if webhook_id not in webhooks_db:
        raise HTTPException(status_code=404, detail="Webhook not found")
    return webhooks_db[webhook_id]


@router.delete("/{webhook_id}")
async def delete_webhook(webhook_id: str):
    """Delete a webhook"""
    if webhook_id not in webhooks_db:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    del webhooks_db[webhook_id]
    return {"success": True, "id": webhook_id}


@router.patch("/{webhook_id}")
async def update_webhook(webhook_id: str, update: WebhookCreate):
    """Update webhook configuration"""
    if webhook_id not in webhooks_db:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    webhook = webhooks_db[webhook_id]
    webhook.url = str(update.url)
    webhook.events = update.events
    if update.secret:
        webhook.secret = update.secret
    
    return webhook


async def trigger_webhook(event: WebhookEvent, background_tasks: BackgroundTasks):
    """
    Trigger webhooks for a specific event
    Called internally when events occur
    """
    for webhook in webhooks_db.values():
        if not webhook.is_active:
            continue
            
        if event.event not in webhook.events:
            continue
        
        # Send webhook in background
        background_tasks.add_task(
            send_webhook,
            webhook.url,
            event.dict(),
            webhook.secret
        )


async def send_webhook(url: str, payload: dict, secret: Optional[str] = None):
    """Send HTTP POST to webhook URL"""
    headers = {"Content-Type": "application/json"}
    
    # Add signature if secret provided
    if secret:
        payload_str = str(payload)
        signature = hmac.new(
            secret.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
        headers["X-TerraForge-Signature"] = f"sha256={signature}"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=payload,
                headers=headers,
                timeout=10.0
            )
            response.raise_for_status()
    except Exception as e:
        # Log webhook delivery failure
        print(f"Webhook delivery failed to {url}: {e}")


# Example usage in generation routes:
"""
from .webhook_routes import trigger_webhook, WebhookEvent

# When generation completes:
await trigger_webhook(
    WebhookEvent(
        event="generation.completed",
        data={
            "id": generation_id,
            "status": "completed",
            "result": {...}
        },
        timestamp=datetime.now()
    ),
    background_tasks
)
"""
