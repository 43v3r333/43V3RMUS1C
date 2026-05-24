"""
Event Persistence Service - Database persistence for events
"""
import logging
from typing import Dict, List, Optional, Any
from uuid import UUID
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from .models import DomainEventRecord
from . import DomainEvent, EventType

logger = logging.getLogger(__name__)


class EventPersistence:
    """
    Event persistence for database storage and replay.
    Provides event sourcing capabilities and audit trails.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def persist_event(self, event: DomainEvent) -> DomainEventRecord:
        """Persist a domain event to the database"""
        record = DomainEventRecord(
            event_type=event.event_type.value,
            event_id=str(event.event_id),
            aggregate_id=str(event.aggregate_id),
            correlation_id=str(event.correlation_id) if event.correlation_id else None,
            causation_id=str(event.causation_id) if event.causation_id else None,
            user_id=str(event.user_id) if event.user_id else None,
            session_id=str(event.session_id) if event.session_id else None,
            metadata=event.metadata,
            timestamp=event.timestamp,
        )
        
        self.db.add(record)
        await self.db.commit()
        await self.db.refresh(record)
        
        return record
    
    async def persist_events(self, events: List[DomainEvent]) -> List[DomainEventRecord]:
        """Persist multiple domain events"""
        records = []
        
        for event in events:
            record = DomainEventRecord(
                event_type=event.event_type.value,
                event_id=str(event.event_id),
                aggregate_id=str(event.aggregate_id),
                correlation_id=str(event.correlation_id) if event.correlation_id else None,
                causation_id=str(event.causation_id) if event.causation_id else None,
                user_id=str(event.user_id) if event.user_id else None,
                session_id=str(event.session_id) if event.session_id else None,
                metadata=event.metadata,
                timestamp=event.timestamp,
            )
            records.append(record)
        
        self.db.add_all(records)
        await self.db.commit()
        
        for record in records:
            await self.db.refresh(record)
        
        return records
    
    async def get_event_by_id(self, event_id: str) -> Optional[DomainEventRecord]:
        """Get event by ID"""
        result = await self.db.execute(
            select(DomainEventRecord).where(DomainEventRecord.event_id == event_id)
        )
        return result.scalar_one_or_none()
    
    async def get_events_by_aggregate(
        self,
        aggregate_id: UUID,
        limit: int = 100,
    ) -> List[DomainEventRecord]:
        """Get all events for an aggregate"""
        result = await self.db.execute(
            select(DomainEventRecord)
            .where(DomainEventRecord.aggregate_id == str(aggregate_id))
            .order_by(DomainEventRecord.timestamp)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_events_by_type(
        self,
        event_type: EventType,
        since: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[DomainEventRecord]:
        """Get events by type"""
        query = select(DomainEventRecord).where(
            DomainEventRecord.event_type == event_type.value
        )
        
        if since:
            query = query.where(DomainEventRecord.timestamp >= since)
        
        query = query.order_by(DomainEventRecord.timestamp.desc()).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_events_by_correlation(
        self,
        correlation_id: UUID,
    ) -> List[DomainEventRecord]:
        """Get all events with same correlation ID"""
        result = await self.db.execute(
            select(DomainEventRecord)
            .where(DomainEventRecord.correlation_id == str(correlation_id))
            .order_by(DomainEventRecord.timestamp)
        )
        return list(result.scalars().all())
    
    async def mark_processed(
        self,
        event_id: str,
        processor: Optional[str] = None,
    ) -> Optional[DomainEventRecord]:
        """Mark event as processed"""
        result = await self.db.execute(
            select(DomainEventRecord).where(DomainEventRecord.event_id == event_id)
        )
        record = result.scalar_one_or_none()
        
        if record:
            record.processed = True
            record.processed_at = datetime.utcnow()
            record.processor = processor
            self.db.add(record)
            await self.db.commit()
            await self.db.refresh(record)
        
        return record
    
    async def mark_failed(
        self,
        event_id: str,
        error_message: str,
    ) -> Optional[DomainEventRecord]:
        """Mark event as failed"""
        result = await self.db.execute(
            select(DomainEventRecord).where(DomainEventRecord.event_id == event_id)
        )
        record = result.scalar_one_or_none()
        
        if record:
            record.failed = True
            record.error_message = error_message
            record.retry_count += 1
            self.db.add(record)
            await self.db.commit()
            await self.db.refresh(record)
        
        return record
    
    async def get_unprocessed_events(
        self,
        limit: int = 100,
    ) -> List[DomainEventRecord]:
        """Get unprocessed events for retry"""
        result = await self.db.execute(
            select(DomainEventRecord)
            .where(
                and_(
                    DomainEventRecord.processed == False,
                    DomainEventRecord.failed == False,
                )
            )
            .order_by(DomainEventRecord.timestamp)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_failed_events(
        self,
        max_retries: int = 3,
        limit: int = 100,
    ) -> List[DomainEventRecord]:
        """Get failed events that can be retried"""
        result = await self.db.execute(
            select(DomainEventRecord)
            .where(
                and_(
                    DomainEventRecord.failed == True,
                    DomainEventRecord.retry_count < max_retries,
                )
            )
            .order_by(DomainEventRecord.timestamp)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def delete_events_before(
        self,
        before: datetime,
    ) -> int:
        """Delete old processed events"""
        result = await self.db.execute(
            select(DomainEventRecord)
            .where(
                and_(
                    DomainEventRecord.processed == True,
                    DomainEventRecord.timestamp < before,
                )
            )
        )
        records = result.scalars().all()
        
        count = len(records)
        for record in records:
            await self.db.delete(record)
        
        await self.db.commit()
        
        return count