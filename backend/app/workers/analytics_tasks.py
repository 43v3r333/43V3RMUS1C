"""
Analytics tasks
"""
import logging
from datetime import datetime, timedelta

from ..celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="aggregate_analytics")
def aggregate_analytics(self):
    """Aggregate analytics data"""
    from ..core.database import SessionLocal
    from ..models.analytics import AnalyticsEvent, PlatformMetric
    
    db = SessionLocal()
    try:
        # Aggregate today's events
        today = datetime.utcnow().date()
        
        # Count events by type
        events = db.query(AnalyticsEvent).filter(
            AnalyticsEvent.timestamp >= today
        ).all()
        
        # Create platform metric
        metric = PlatformMetric(
            metric_name="analytics_events_total",
            metric_type="counter",
            value=len(events),
            unit="events",
            timestamp=datetime.utcnow(),
            tags={"date": str(today)}
        )
        
        db.add(metric)
        db.commit()
        
        return {"aggregated": len(events)}
    
    finally:
        db.close()


@celery_app.task(bind=True, name="cleanup_old_logs")
def cleanup_old_logs(self, retention_days: int = 90):
    """Cleanup old system logs"""
    from ..core.database import SessionLocal
    from ..models.analytics import SystemLog
    
    db = SessionLocal()
    try:
        cutoff = datetime.utcnow() - timedelta(days=retention_days)
        
        # Soft delete old logs
        old_logs = db.query(SystemLog).filter(
            SystemLog.timestamp < cutoff
        ).all()
        
        count = 0
        for log in old_logs:
            log.soft_delete()
            count += 1
        
        db.commit()
        
        logger.info(f"Cleaned up {count} old system logs")
        return {"cleaned": count}
    
    finally:
        db.close()


@celery_app.task(bind=True, name="fetch_trend_data")
def fetch_trend_data(self, source: str = "spotify"):
    """Fetch trend data from external sources"""
    from ..core.database import SessionLocal
    from ..models.analytics import TrendData
    
    db = SessionLocal()
    try:
        # TODO: Implement actual trend data fetching from APIs
        # For now, create placeholder data
        logger.info(f"Fetching trends from {source}")
        
        trends = [
            TrendData(
                source=source,
                trend_type="track",
                name="Sample Track",
                rank=1,
                change="up",
                metrics={"streams": 1000000},
                date=datetime.utcnow()
            )
        ]
        
        for trend in trends:
            db.add(trend)
        
        db.commit()
        
        return {"fetched": len(trends), "source": source}
    
    finally:
        db.close()