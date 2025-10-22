"""
Data Retention Policy Management
Automated data cleanup and compliance management
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum
from pydantic import BaseModel


class RetentionPeriod(str, Enum):
    DAYS_7 = "7d"
    DAYS_30 = "30d"
    DAYS_90 = "90d"
    DAYS_180 = "180d"
    DAYS_365 = "365d"
    YEARS_2 = "2y"
    YEARS_5 = "5y"
    PERMANENT = "permanent"


class DataCategory(str, Enum):
    TERRAIN_DATA = "terrain_data"
    EXPORT_FILES = "export_files"
    USER_SESSIONS = "user_sessions"
    AUDIT_LOGS = "audit_logs"
    ANALYTICS_DATA = "analytics_data"
    TEMPORARY_FILES = "temporary_files"
    WEBHOOK_LOGS = "webhook_logs"
    ERROR_LOGS = "error_logs"


class RetentionPolicy(BaseModel):
    category: DataCategory
    retention_period: RetentionPeriod
    auto_delete: bool = True
    archive_before_delete: bool = False
    compliance_required: bool = False
    description: str


class DataRecord(BaseModel):
    id: str
    category: DataCategory
    created_at: datetime
    last_accessed: datetime
    size_bytes: int
    metadata: Dict


# Default retention policies
DEFAULT_POLICIES = {
    DataCategory.TERRAIN_DATA: RetentionPolicy(
        category=DataCategory.TERRAIN_DATA,
        retention_period=RetentionPeriod.DAYS_90,
        auto_delete=True,
        archive_before_delete=True,
        description="Generated terrain heightmaps and textures"
    ),
    DataCategory.EXPORT_FILES: RetentionPolicy(
        category=DataCategory.EXPORT_FILES,
        retention_period=RetentionPeriod.DAYS_30,
        auto_delete=True,
        archive_before_delete=False,
        description="Exported terrain files for game engines"
    ),
    DataCategory.USER_SESSIONS: RetentionPolicy(
        category=DataCategory.USER_SESSIONS,
        retention_period=RetentionPeriod.DAYS_7,
        auto_delete=True,
        archive_before_delete=False,
        description="User session data and tokens"
    ),
    DataCategory.AUDIT_LOGS: RetentionPolicy(
        category=DataCategory.AUDIT_LOGS,
        retention_period=RetentionPeriod.YEARS_2,
        auto_delete=False,
        archive_before_delete=True,
        compliance_required=True,
        description="Security and compliance audit logs"
    ),
    DataCategory.ANALYTICS_DATA: RetentionPolicy(
        category=DataCategory.ANALYTICS_DATA,
        retention_period=RetentionPeriod.DAYS_365,
        auto_delete=True,
        archive_before_delete=True,
        description="Usage analytics and metrics"
    ),
    DataCategory.TEMPORARY_FILES: RetentionPolicy(
        category=DataCategory.TEMPORARY_FILES,
        retention_period=RetentionPeriod.DAYS_7,
        auto_delete=True,
        archive_before_delete=False,
        description="Temporary processing files"
    ),
    DataCategory.WEBHOOK_LOGS: RetentionPolicy(
        category=DataCategory.WEBHOOK_LOGS,
        retention_period=RetentionPeriod.DAYS_30,
        auto_delete=True,
        archive_before_delete=False,
        description="Webhook delivery logs"
    ),
    DataCategory.ERROR_LOGS: RetentionPolicy(
        category=DataCategory.ERROR_LOGS,
        retention_period=RetentionPeriod.DAYS_90,
        auto_delete=True,
        archive_before_delete=True,
        description="Application error logs"
    ),
}


class DataRetentionManager:
    """Manages data retention policies and cleanup"""
    
    def __init__(self):
        self.policies: Dict[DataCategory, RetentionPolicy] = DEFAULT_POLICIES.copy()
        self.records: Dict[str, DataRecord] = {}
        self.archived_count = 0
        self.deleted_count = 0
    
    def set_policy(self, policy: RetentionPolicy):
        """Set retention policy for category"""
        self.policies[policy.category] = policy
    
    def get_policy(self, category: DataCategory) -> RetentionPolicy:
        """Get retention policy for category"""
        return self.policies.get(category, DEFAULT_POLICIES[category])
    
    def register_data(self, record: DataRecord):
        """Register data record for tracking"""
        self.records[record.id] = record
    
    def should_retain(self, record: DataRecord) -> bool:
        """Check if record should be retained"""
        policy = self.get_policy(record.category)
        
        if policy.retention_period == RetentionPeriod.PERMANENT:
            return True
        
        # Calculate expiry date
        expiry_date = self._calculate_expiry(record.created_at, policy.retention_period)
        
        return datetime.now() < expiry_date
    
    def _calculate_expiry(
        self,
        created_at: datetime,
        retention_period: RetentionPeriod
    ) -> datetime:
        """Calculate expiry date based on retention period"""
        if retention_period == RetentionPeriod.DAYS_7:
            return created_at + timedelta(days=7)
        elif retention_period == RetentionPeriod.DAYS_30:
            return created_at + timedelta(days=30)
        elif retention_period == RetentionPeriod.DAYS_90:
            return created_at + timedelta(days=90)
        elif retention_period == RetentionPeriod.DAYS_180:
            return created_at + timedelta(days=180)
        elif retention_period == RetentionPeriod.DAYS_365:
            return created_at + timedelta(days=365)
        elif retention_period == RetentionPeriod.YEARS_2:
            return created_at + timedelta(days=730)
        elif retention_period == RetentionPeriod.YEARS_5:
            return created_at + timedelta(days=1825)
        else:
            return created_at + timedelta(days=365)
    
    def cleanup_expired_data(self) -> Dict[str, int]:
        """Clean up expired data according to policies"""
        results = {
            "archived": 0,
            "deleted": 0,
            "retained": 0,
            "errors": 0
        }
        
        for record_id, record in list(self.records.items()):
            try:
                if self.should_retain(record):
                    results["retained"] += 1
                    continue
                
                policy = self.get_policy(record.category)
                
                if not policy.auto_delete:
                    results["retained"] += 1
                    continue
                
                # Archive if required
                if policy.archive_before_delete:
                    self._archive_record(record)
                    results["archived"] += 1
                
                # Delete record
                self._delete_record(record)
                del self.records[record_id]
                results["deleted"] += 1
                
            except Exception as e:
                print(f"Error processing record {record_id}: {e}")
                results["errors"] += 1
        
        self.archived_count += results["archived"]
        self.deleted_count += results["deleted"]
        
        return results
    
    def _archive_record(self, record: DataRecord):
        """Archive record before deletion"""
        # Implementation would store to cold storage
        print(f"Archiving {record.category} record {record.id}")
    
    def _delete_record(self, record: DataRecord):
        """Delete record permanently"""
        # Implementation would delete from storage
        print(f"Deleting {record.category} record {record.id}")
    
    def get_stats(self) -> Dict:
        """Get retention statistics"""
        stats = {
            "total_records": len(self.records),
            "by_category": {},
            "total_size_bytes": 0,
            "archived_total": self.archived_count,
            "deleted_total": self.deleted_count
        }
        
        for record in self.records.values():
            if record.category not in stats["by_category"]:
                stats["by_category"][record.category] = {
                    "count": 0,
                    "size_bytes": 0
                }
            
            stats["by_category"][record.category]["count"] += 1
            stats["by_category"][record.category]["size_bytes"] += record.size_bytes
            stats["total_size_bytes"] += record.size_bytes
        
        return stats


# Global retention manager
retention_manager = DataRetentionManager()
