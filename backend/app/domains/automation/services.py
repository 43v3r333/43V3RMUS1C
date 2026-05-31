"""
Automation Engine Services - Rule-based automation execution
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .models import TriggerType, RuleStatus, AutomationTrigger, AutomationRule
from ..events import DomainEvent, EventType

logger = logging.getLogger(__name__)


class AutomationEngine:
    """
    Automation engine for rule-based automation.
    Manages automation rules, triggers, and action execution.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._active_rules: Dict[str, AutomationRule] = {}
        self._action_handlers: Dict[str, Callable] = {}
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """Register default action handlers"""
        self._action_handlers["notify"] = self._handle_notify
        self._action_handlers["webhook"] = self._handle_webhook
        self._action_handlers["create_task"] = self._handle_create_task
        self._action_handlers["update_status"] = self._handle_update_status
        self._action_handlers["transcode"] = self._handle_transcode
    
    def register_action_handler(self, action_type: str, handler: Callable):
        """Register a custom action handler"""
        self._action_handlers[action_type] = handler
    
    # ==================== Rule Operations ====================
    
    async def create_rule(
        self,
        name: str,
        actions: List[Dict],
        description: Optional[str] = None,
        trigger_id: Optional[UUID] = None,
        owner_id: Optional[UUID] = None,
    ) -> AutomationRule:
        """Create a new automation rule"""
        rule = AutomationRule(
            name=name,
            description=description,
            trigger_id=trigger_id,
            actions=actions,
            owner_id=owner_id,
            status=RuleStatus.ACTIVE.value,
        )
        
        self.db.add(rule)
        await self.db.commit()
        await self.db.refresh(rule)
        
        return rule
    
    async def get_rule(self, rule_id: UUID) -> Optional[AutomationRule]:
        """Get rule by ID"""
        result = await self.db.execute(
            select(AutomationRule).where(AutomationRule.id == rule_id)
        )
        return result.scalar_one_or_none()
    
    async def get_active_rules(
        self,
        owner_id: Optional[UUID] = None,
    ) -> List[AutomationRule]:
        """Get all active rules"""
        query = select(AutomationRule).where(
            AutomationRule.is_enabled == True,
            AutomationRule.status == RuleStatus.ACTIVE.value,
        )
        
        if owner_id:
            query = query.where(AutomationRule.owner_id == owner_id)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def update_rule(
        self,
        rule: AutomationRule,
        **kwargs,
    ) -> AutomationRule:
        """Update rule properties"""
        for key, value in kwargs.items():
            if hasattr(rule, key):
                setattr(rule, key, value)
        
        self.db.add(rule)
        await self.db.commit()
        await self.db.refresh(rule)
        
        return rule
    
    async def enable_rule(self, rule: AutomationRule) -> AutomationRule:
        """Enable a rule"""
        rule.is_enabled = True
        rule.status = RuleStatus.ACTIVE.value
        return await self.update_rule(rule)
    
    async def disable_rule(self, rule: AutomationRule) -> AutomationRule:
        """Disable a rule"""
        rule.is_enabled = False
        rule.status = RuleStatus.DISABLED.value
        return await self.update_rule(rule)
    
    # ==================== Trigger Operations ====================
    
    async def create_trigger(
        self,
        name: str,
        trigger_type: TriggerType,
        config: Optional[Dict] = None,
        event_filters: Optional[Dict] = None,
        conditions: Optional[List[Dict]] = None,
    ) -> AutomationTrigger:
        """Create a new trigger"""
        trigger = AutomationTrigger(
            name=name,
            trigger_type=trigger_type.value,
            config=config or {},
            event_filters=event_filters,
            conditions=conditions,
        )
        
        self.db.add(trigger)
        await self.db.commit()
        await self.db.refresh(trigger)
        
        return trigger
    
    async def evaluate_conditions(
        self,
        conditions: List[Dict],
        context: Dict[str, Any],
    ) -> bool:
        """Evaluate rule conditions against context"""
        if not conditions:
            return True
        
        for condition in conditions:
            field = condition.get("field")
            operator = condition.get("operator")
            value = condition.get("value")
            
            context_value = context.get(field)
            
            if operator == "equals":
                if context_value != value:
                    return False
            elif operator == "contains":
                if value not in str(context_value):
                    return False
            elif operator == "greater_than":
                if not (context_value and context_value > value):
                    return False
            elif operator == "less_than":
                if not (context_value and context_value < value):
                    return False
            elif operator == "in":
                if context_value not in value:
                    return False
        
        return True
    
    # ==================== Rule Execution ====================
    
    async def evaluate_event(
        self,
        event: DomainEvent,
    ) -> List[AutomationRule]:
        """Evaluate rules for an event"""
        rules = await self.get_active_rules()
        matching_rules = []
        
        for rule in rules:
            # Check if rule applies to this event type
            trigger = None
            if rule.trigger_id:
                result = await self.db.execute(
                    select(AutomationTrigger).where(
                        AutomationTrigger.id == rule.trigger_id
                    )
                )
                trigger = result.scalar_one_or_none()
            
            if trigger:
                # Check event filters
                filters = trigger.event_filters or {}
                event_type_filter = filters.get("event_type")
                
                if event_type_filter and event.event_type.value != event_type_filter:
                    continue
                
                # Check conditions
                conditions = trigger.conditions or []
                if not await self.evaluate_conditions(conditions, event.metadata or {}):
                    continue
            
            matching_rules.append(rule)
        
        return matching_rules
    
    async def execute_rule(
        self,
        rule: AutomationRule,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute automation rule actions"""
        context = context or {}
        results = []
        errors = []
        
        # Check max executions
        if rule.max_executions and rule.execution_count >= rule.max_executions:
            return {
                "rule_id": str(rule.id),
                "status": "skipped",
                "reason": "max_execution_count_reached",
            }
        
        rule.last_triggered_at = datetime.utcnow()
        rule.execution_count += 1
        
        for action in (rule.actions or []):
            action_type = action.get("type")
            action_config = action.get("config", {})
            
            handler = self._action_handlers.get(action_type)
            
            if not handler:
                errors.append(f"No handler for action type: {action_type}")
                continue
            
            try:
                result = await handler(action_config, context)
                results.append({
                    "action": action_type,
                    "status": "success",
                    "result": result,
                })
            except Exception as e:
                logger.error(f"Action {action_type} failed: {e}")
                errors.append(str(e))
                
                if not rule.retry_on_failure:
                    break
        
        # Update rule
        if errors:
            rule.last_error = "; ".join(errors)
            await self.update_rule(rule, last_error=rule.last_error)
        else:
            await self.update_rule(rule)
        
        return {
            "rule_id": str(rule.id),
            "status": "failed" if errors else "success",
            "actions": results,
            "errors": errors,
        }
    
    # ==================== Action Handlers ====================
    
    async def _handle_notify(
        self,
        config: Dict,
        context: Dict,
    ) -> Dict[str, Any]:
        """Handle notification action"""
        message = config.get("message", "")
        channel = config.get("channel", "default")
        
        # Placeholder - actual implementation would send notification
        return {
            "notified": True,
            "channel": channel,
            "message": message,
        }
    
    async def _handle_webhook(
        self,
        config: Dict,
        context: Dict,
    ) -> Dict[str, Any]:
        """Handle webhook action"""
        url = config.get("url")
        method = config.get("method", "POST")
        
        # Placeholder - actual implementation would call webhook
        return {
            "webhook_called": True,
            "url": url,
            "method": method,
        }
    
    async def _handle_create_task(
        self,
        config: Dict,
        context: Dict,
    ) -> Dict[str, Any]:
        """Handle create task action"""
        task_name = config.get("task_name")
        task_type = config.get("task_type")
        
        # Placeholder - actual implementation would create task
        return {
            "task_created": True,
            "name": task_name,
            "type": task_type,
        }
    
    async def _handle_update_status(
        self,
        config: Dict,
        context: Dict,
    ) -> Dict[str, Any]:
        """Handle update status action"""
        status = config.get("status")
        entity_type = config.get("entity_type")
        entity_id = config.get("entity_id")
        
        # Placeholder - actual implementation would update status
        return {
            "status_updated": True,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "new_status": status,
        }
    
    async def _handle_transcode(
        self,
        config: Dict,
        context: Dict,
    ) -> Dict[str, Any]:
        """Handle transcode action"""
        asset_id = config.get("asset_id")
        output_format = config.get("output_format")
        
        # Placeholder - actual implementation would queue transcode task
        return {
            "transcode_queued": True,
            "asset_id": asset_id,
            "format": output_format,
        }