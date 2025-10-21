"""
Ollama client for interacting with local AI models
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List
import httpx
from pathlib import Path
import base64

from ..config import settings

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for interacting with Ollama API"""
    
    def __init__(self, host: Optional[str] = None):
        self.host = host or settings.ollama_host
        self.vision_model = settings.ollama_vision_model
        self.coder_model = settings.ollama_coder_model
        self.timeout = settings.ollama_timeout
        
    async def _make_request(
        self, 
        endpoint: str, 
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Make async request to Ollama API"""
        url = f"{self.host}/api/{endpoint}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                
                # Handle streaming response
                if payload.get("stream", False):
                    full_response = ""
                    async for line in response.aiter_lines():
                        if line:
                            import json
                            data = json.loads(line)
                            if "response" in data:
                                full_response += data["response"]
                            if data.get("done", False):
                                return {"response": full_response}
                    return {"response": full_response}
                else:
                    return response.json()
                    
        except httpx.TimeoutException:
            logger.error(f"Request to {url} timed out after {self.timeout}s")
            raise TimeoutError(f"Ollama request timed out")
        except httpx.HTTPError as e:
            logger.error(f"HTTP error during Ollama request: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during Ollama request: {e}")
            raise
    
    async def analyze_image(
        self, 
        image_path: Path, 
        prompt: str,
        model: Optional[str] = None
    ) -> str:
        """
        Analyze an image using vision model
        
        Args:
            image_path: Path to the image file
            prompt: Text prompt for the analysis
            model: Optional model override
            
        Returns:
            Analysis result as text
        """
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        # Read and encode image
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")
        
        payload = {
            "model": model or self.vision_model,
            "prompt": prompt,
            "images": [image_data],
            "stream": False
        }
        
        logger.info(f"Analyzing image {image_path.name} with {payload['model']}")
        result = await self._make_request("generate", payload)
        return result.get("response", "")
    
    async def generate_text(
        self, 
        prompt: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Generate text using coder model
        
        Args:
            prompt: User prompt
            model: Optional model override
            system_prompt: Optional system prompt
            
        Returns:
            Generated text
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": model or self.coder_model,
            "messages": messages,
            "stream": False
        }
        
        logger.info(f"Generating text with {payload['model']}")
        result = await self._make_request("chat", payload)
        
        if "message" in result:
            return result["message"].get("content", "")
        return result.get("response", "")
    
    async def analyze_osm_data(
        self,
        osm_data: Dict[str, Any],
        terrain_info: Dict[str, Any],
        prompt: str
    ) -> str:
        """
        Analyze OSM data combined with terrain information
        
        Args:
            osm_data: OpenStreetMap data
            terrain_info: Terrain analysis information
            prompt: Specific question or analysis request
            
        Returns:
            Analysis result
        """
        system_prompt = """You are an expert in urban planning, geography, and game level design.
Your task is to analyze OpenStreetMap data and terrain information to provide insights
for generating realistic game environments for BeamNG.drive racing simulator."""
        
        user_prompt = f"""
Analyze the following data and {prompt}

OSM Data Summary:
- Roads: {len(osm_data.get('roads', []))} segments
- Buildings: {len(osm_data.get('buildings', []))} structures
- Traffic features: {len(osm_data.get('traffic_lights', []))} traffic lights

Terrain Information:
{terrain_info}

Provide specific recommendations for object placement, density, and infrastructure.
"""
        
        return await self.generate_text(user_prompt, system_prompt=system_prompt)
    
    async def check_health(self) -> bool:
        """Check if Ollama server is accessible"""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.host}/api/tags")
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return False
    
    async def list_models(self) -> List[str]:
        """List available models"""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{self.host}/api/tags")
                response.raise_for_status()
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []
    
    async def pull_model(self, model_name: str) -> bool:
        """
        Pull a model from Ollama library
        
        Args:
            model_name: Name of the model to pull
            
        Returns:
            True if successful
        """
        logger.info(f"Pulling model {model_name}...")
        
        try:
            payload = {"name": model_name, "stream": False}
            await self._make_request("pull", payload)
            logger.info(f"Successfully pulled model {model_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to pull model {model_name}: {e}")
            return False
