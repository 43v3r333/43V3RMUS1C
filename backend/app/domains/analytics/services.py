"""
Analytics Engine Services - Analytics tracking and reporting
"""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, text

from .models import AnalyticsEvent, Report

logger = logging.getLogger(__name__)


class AnalyticsEngine:
    """
    Analytics engine for event tracking and reporting.
    Provides analytics collection, aggregation, and report generation.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ==================== Event Tracking ====================
    
    async def track_event(
        self,
        event_type: str,
        event_category: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        object_type: Optional[str] = None,
        object_id: Optional[str] = None,
        properties: Optional[Dict] = None,
        value: Optional[float] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        referrer: Optional[str] = None,
    ) -> AnalyticsEvent:
        """Track an analytics event"""
        event = AnalyticsEvent(
            event_type=event_type,
            event_category=event_category,
            user_id=user_id,
            session_id=session_id,
            object_type=object_type,
            object_id=object_id,
            properties=properties,
            value=value,
            ip_address=ip_address,
            user_agent=user_agent,
            referrer=referrer,
        )
        
        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(event)
        
        return event
    
    async def track_page_view(
        self,
        path: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        referrer: Optional[str] = None,
    ) -> AnalyticsEvent:
        """Track a page view"""
        return await self.track_event(
            event_type="page_view",
            event_category="engagement",
            user_id=user_id,
            session_id=session_id,
            properties={"path": path},
            referrer=referrer,
        )
    
    async def track_render(
        self,
        asset_id: str,
        render_type: str,
        duration: float,
        user_id: Optional[str] = None,
    ) -> AnalyticsEvent:
        """Track a render event"""
        return await self.track_event(
            event_type="render",
            event_category="workflow",
            user_id=user_id,
            object_type="render_job",
            object_id=asset_id,
            properties={"render_type": render_type},
            value=duration,
        )
    
    async def track_media_upload(
        self,
        media_id: str,
        file_size: int,
        media_type: str,
        user_id: Optional[str] = None,
    ) -> AnalyticsEvent:
        """Track a media upload"""
        return await self.track_event(
            event_type="media_upload",
            event_category="media",
            user_id=user_id,
            object_type="media_asset",
            object_id=media_id,
            properties={"media_type": media_type},
            value=float(file_size),
        )
    
    # ==================== Querying ====================
    
    async def get_events(
        self,
        since: datetime,
        until: Optional[datetime] = None,
        event_type: Optional[str] = None,
        user_id: Optional[str] = None,
        limit: int = 1000,
    ) -> List[AnalyticsEvent]:
        """Get analytics events"""
        query = select(AnalyticsEvent).where(
            AnalyticsEvent.created_at >= since
        )
        
        if until:
            query = query.where(AnalyticsEvent.created_at <= until)
        if event_type:
            query = query.where(AnalyticsEvent.event_type == event_type)
        if user_id:
            query = query.where(AnalyticsEvent.user_id == user_id)
        
        query = query.order_by(AnalyticsEvent.created_at.desc()).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def count_events(
        self,
        event_type: str,
        since: datetime,
        until: Optional[datetime] = None,
        user_id: Optional[str] = None,
    ) -> int:
        """Count events by type"""
        query = select(func.count(AnalyticsEvent.id)).where(
            AnalyticsEvent.event_type == event_type,
            AnalyticsEvent.created_at >= since,
        )
        
        if until:
            query = query.where(AnalyticsEvent.created_at <= until)
        if user_id:
            query = query.where(AnalyticsEvent.user_id == user_id)
        
        result = await self.db.execute(query)
        return result.scalar() or 0
    
    # ==================== Aggregation ====================
    
    async def aggregate_by_day(
        self,
        event_type: str,
        since: datetime,
        until: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """Aggregate events by day"""
        query = text("""
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as count
            FROM analytics_events
            WHERE event_type = :event_type
                AND created_at >= :since
            GROUP BY DATE(created_at)
            ORDER BY date
        """)
        
        result = await self.db.execute(query, {
            "event_type": event_type,
            "since": since,
            "until": until or datetime.utcnow(),
        })
        
        return [{"date": row[0], "count": row[1]} for row in result.fetchall()]
    
    async def aggregate_by_hour(
        self,
        event_type: str,
        since: datetime,
    ) -> List[Dict[str, Any]]:
        """Aggregate events by hour"""
        query = text("""
            SELECT 
                DATE_TRUNC('hour', created_at) as hour,
                COUNT(*) as count
            FROM analytics_events
            WHERE event_type = :event_type
                AND created_at >= :since
            GROUP BY DATE_TRUNC('hour', created_at)
            ORDER BY hour
        """)
        
        result = await self.db.execute(query, {
            "event_type": event_type,
            "since": since,
        })
        
        return [{"hour": row[0], "count": row[1]} for row in result.fetchall()]
    
    async def get_top_users(
        self,
        event_type: str,
        since: datetime,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get top users by event count"""
        query = text("""
            SELECT 
                user_id,
                COUNT(*) as count
            FROM analytics_events
            WHERE event_type = :event_type
                AND user_id IS NOT NULL
                AND created_at >= :since
            GROUP BY user_id
            ORDER BY count DESC
            LIMIT :limit
        """)
        
        result = await self.db.execute(query, {
            "event_type": event_type,
            "since": since,
            "limit": limit,
        })
        
        return [{"user_id": row[0], "count": row[1]} for row in result.fetchall()]
    
    # ==================== Reports ====================
    
    async def create_report(
        self,
        name: str,
        report_type: str,
        filters: Optional[Dict] = None,
        metrics: Optional[List[str]] = None,
        dimensions: Optional[List[str]] = None,
        owner_id: Optional[UUID] = None,
    ) -> Report:
        """Create a new report"""
        report = Report(
            name=name,
            report_type=report_type,
            filters=filters,
            metrics=metrics,
            dimensions=dimensions,
            owner_id=owner_id,
        )
        
        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)
        
        return report
    
    async def generate_report(self, report: Report) -> Dict[str, Any]:
        """Generate report data"""
        # Parse filters
        since = report.filters.get("since", datetime.utcnow() - timedelta(days=7))
        until = report.filters.get("until")
        event_type = report.filters.get("event_type")
        
        # Build data based on report type
        if report.report_type == "daily":
            data = await self.aggregate_by_day(event_type, since, until)
        elif report.report_type == "hourly":
            data = await self.aggregate_by_hour(event_type, since)
        elif report.report_type == "top_users":
            data = await self.get_top_users(event_type, since)
        else:
            data = []
        
        report.data = data
        report.last_run_at = datetime.utcnow()
        
        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)
        
        return data
    
    # ==================== Dashboard Metrics ====================
    
    async def get_dashboard_metrics(
        self,
        since: datetime = None,
    ) -> Dict[str, Any]:
        """Get dashboard summary metrics"""
        since = since or (datetime.utcnow() - timedelta(days=7))
        
        # Count different event types
        page_views = await self.count_events("page_view", since)
        uploads = await self.count_events("media_upload", since)
        renders = await self.count_events("render", since)
        
        # Get daily trends
        trends = await self.aggregate_by_day("page_view", since)
        
        return {
            "period": {
                "since": since.isoformat(),
                "until": datetime.utcnow().isoformat(),
            },
            "metrics": {
                "page_views": page_views,
                "media_uploads": uploads,
                "renders": renders,
            },
            "trends": trends,
        }