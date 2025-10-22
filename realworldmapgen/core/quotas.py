"""
Resource Quota Management System
Manages generation limits, storage quotas, and API rate limits
"""

from datetime import datetime, timedelta
from typing import Optional, Dict
from enum import Enum
from pydantic import BaseModel


class QuotaType(str, Enum):
    TERRAIN_GENERATION = "terrain_generation"
    EXPORTS = "exports"
    STORAGE = "storage"
    API_CALLS = "api_calls"
    WEBHOOK_CALLS = "webhook_calls"


class QuotaPlan(str, Enum):
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class QuotaLimits(BaseModel):
    plan: QuotaPlan
    terrain_generation_per_month: int
    exports_per_month: int
    storage_gb: int
    api_calls_per_day: int
    webhook_calls_per_month: int
    max_terrain_size: int  # square km
    concurrent_generations: int


# Quota plans definition
QUOTA_PLANS = {
    QuotaPlan.FREE: QuotaLimits(
        plan=QuotaPlan.FREE,
        terrain_generation_per_month=50,
        exports_per_month=20,
        storage_gb=1,
        api_calls_per_day=1000,
        webhook_calls_per_month=100,
        max_terrain_size=100,
        concurrent_generations=1
    ),
    QuotaPlan.STARTER: QuotaLimits(
        plan=QuotaPlan.STARTER,
        terrain_generation_per_month=500,
        exports_per_month=200,
        storage_gb=10,
        api_calls_per_day=10000,
        webhook_calls_per_month=1000,
        max_terrain_size=500,
        concurrent_generations=3
    ),
    QuotaPlan.PRO: QuotaLimits(
        plan=QuotaPlan.PRO,
        terrain_generation_per_month=5000,
        exports_per_month=2000,
        storage_gb=100,
        api_calls_per_day=100000,
        webhook_calls_per_month=10000,
        max_terrain_size=2000,
        concurrent_generations=10
    ),
    QuotaPlan.ENTERPRISE: QuotaLimits(
        plan=QuotaPlan.ENTERPRISE,
        terrain_generation_per_month=-1,  # Unlimited
        exports_per_month=-1,
        storage_gb=-1,
        api_calls_per_day=-1,
        webhook_calls_per_month=-1,
        max_terrain_size=-1,
        concurrent_generations=-1
    )
}


class QuotaUsage(BaseModel):
    user_id: str
    quota_type: QuotaType
    count: int
    period_start: datetime
    period_end: datetime
    last_reset: datetime


class QuotaManager:
    """Manages resource quotas and usage tracking"""
    
    def __init__(self):
        self.user_plans: Dict[str, QuotaPlan] = {}
        self.usage: Dict[str, Dict[QuotaType, QuotaUsage]] = {}
    
    def set_user_plan(self, user_id: str, plan: QuotaPlan):
        """Set quota plan for user"""
        self.user_plans[user_id] = plan
    
    def get_user_plan(self, user_id: str) -> QuotaPlan:
        """Get user's quota plan"""
        return self.user_plans.get(user_id, QuotaPlan.FREE)
    
    def get_user_limits(self, user_id: str) -> QuotaLimits:
        """Get quota limits for user"""
        plan = self.get_user_plan(user_id)
        return QUOTA_PLANS[plan]
    
    def check_quota(
        self,
        user_id: str,
        quota_type: QuotaType,
        amount: int = 1
    ) -> bool:
        """Check if user has quota available"""
        limits = self.get_user_limits(user_id)
        usage = self.get_usage(user_id, quota_type)
        
        # Get limit based on quota type
        if quota_type == QuotaType.TERRAIN_GENERATION:
            limit = limits.terrain_generation_per_month
        elif quota_type == QuotaType.EXPORTS:
            limit = limits.exports_per_month
        elif quota_type == QuotaType.API_CALLS:
            limit = limits.api_calls_per_day
        elif quota_type == QuotaType.WEBHOOK_CALLS:
            limit = limits.webhook_calls_per_month
        else:
            return True
        
        # Unlimited for enterprise
        if limit == -1:
            return True
        
        return usage.count + amount <= limit
    
    def consume_quota(
        self,
        user_id: str,
        quota_type: QuotaType,
        amount: int = 1
    ) -> bool:
        """Consume quota if available"""
        if not self.check_quota(user_id, quota_type, amount):
            return False
        
        usage = self.get_usage(user_id, quota_type)
        usage.count += amount
        
        return True
    
    def get_usage(
        self,
        user_id: str,
        quota_type: QuotaType
    ) -> QuotaUsage:
        """Get current usage for quota type"""
        if user_id not in self.usage:
            self.usage[user_id] = {}
        
        if quota_type not in self.usage[user_id]:
            # Create new usage entry
            now = datetime.now()
            period_start, period_end = self._get_period(quota_type, now)
            
            self.usage[user_id][quota_type] = QuotaUsage(
                user_id=user_id,
                quota_type=quota_type,
                count=0,
                period_start=period_start,
                period_end=period_end,
                last_reset=now
            )
        
        usage = self.usage[user_id][quota_type]
        
        # Check if period expired
        if datetime.now() >= usage.period_end:
            self._reset_usage(user_id, quota_type)
        
        return self.usage[user_id][quota_type]
    
    def _reset_usage(self, user_id: str, quota_type: QuotaType):
        """Reset usage for new period"""
        now = datetime.now()
        period_start, period_end = self._get_period(quota_type, now)
        
        self.usage[user_id][quota_type] = QuotaUsage(
            user_id=user_id,
            quota_type=quota_type,
            count=0,
            period_start=period_start,
            period_end=period_end,
            last_reset=now
        )
    
    def _get_period(
        self,
        quota_type: QuotaType,
        current_time: datetime
    ) -> tuple[datetime, datetime]:
        """Get period start and end for quota type"""
        if quota_type == QuotaType.API_CALLS:
            # Daily reset
            start = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
        else:
            # Monthly reset
            start = current_time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if current_time.month == 12:
                end = start.replace(year=start.year + 1, month=1)
            else:
                end = start.replace(month=start.month + 1)
        
        return start, end
    
    def get_usage_percentage(
        self,
        user_id: str,
        quota_type: QuotaType
    ) -> float:
        """Get usage as percentage of limit"""
        limits = self.get_user_limits(user_id)
        usage = self.get_usage(user_id, quota_type)
        
        if quota_type == QuotaType.TERRAIN_GENERATION:
            limit = limits.terrain_generation_per_month
        elif quota_type == QuotaType.EXPORTS:
            limit = limits.exports_per_month
        elif quota_type == QuotaType.API_CALLS:
            limit = limits.api_calls_per_day
        elif quota_type == QuotaType.WEBHOOK_CALLS:
            limit = limits.webhook_calls_per_month
        else:
            return 0.0
        
        if limit == -1:
            return 0.0
        
        return (usage.count / limit) * 100
    
    def get_all_usage(self, user_id: str) -> Dict[QuotaType, QuotaUsage]:
        """Get all usage stats for user"""
        result = {}
        for quota_type in QuotaType:
            result[quota_type] = self.get_usage(user_id, quota_type)
        return result


# Global quota manager
quota_manager = QuotaManager()


def require_quota(quota_type: QuotaType, amount: int = 1):
    """Decorator to require quota for operation"""
    def decorator(func):
        async def wrapper(*args, user_id: str = None, **kwargs):
            if not user_id:
                raise ValueError("User ID required for quota check")
            
            if not quota_manager.check_quota(user_id, quota_type, amount):
                limits = quota_manager.get_user_limits(user_id)
                raise PermissionError(
                    f"Quota exceeded for {quota_type}. "
                    f"Upgrade your plan for more resources."
                )
            
            result = await func(*args, user_id=user_id, **kwargs)
            quota_manager.consume_quota(user_id, quota_type, amount)
            
            return result
        return wrapper
    return decorator
