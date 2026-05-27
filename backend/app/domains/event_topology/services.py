"""
Event Topology Services - Centralized event governance and topology management.

Provides:
- Event contract registry management
- Topology governance engine
- Schema versioning and validation
- Event lineage tracking
- Distributed propagation policies
"""
import asyncio
import logging
import hashlib
import json
from typing import Dict, List, Optional, Any, Callable, Set
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, or_, func

from .models import (
    EventContract,
    EventContractVersion,
    TopologyNode,
    TopologyEdge,
    PropagationPolicy,
    EventLineage,
    EventCorrelation,
    TopologyValidationRule,
    EventContractAudit,
    ContractStatus,
    ContractType,
    SchemaStatus,
    PropagationMode,
    LineageEventType,
)

logger = logging.getLogger(__name__)


class ContractRegistry:
    """Centralized event contract registry with versioning and governance"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._contracts: Dict[str, EventContract] = {}
        self._schemas: Dict[str, Dict[str, Any]] = {}
        self._propagation_cache: Dict[str, List[PropagationPolicy]] = {}
        self._running = False
    
    async def initialize(self) -> None:
        """Initialize contract registry"""
        await self._load_contracts()
        self._running = True
        logger.info("ContractRegistry initialized with %d contracts", len(self._contracts))
    
    async def shutdown(self) -> None:
        """Shutdown contract registry"""
        self._running = False
        logger.info("ContractRegistry shutdown")
    
    async def _load_contracts(self) -> None:
        """Load contracts from database"""
        result = await self.db.execute(select(EventContract))
        for contract in result.scalars().all():
            self._contracts[contract.name] = contract
    
    # ==================== Contract Management ====================
    
    async def register_contract(
        self,
        name: str,
        contract_type: str,
        schema: Dict[str, Any],
        category: Optional[str] = None,
        description: Optional[str] = None,
        owner_team: Optional[str] = None,
        owner_id: Optional[UUID] = None,
    ) -> EventContract:
        """Register a new event contract"""
        # Generate version
        version = "1.0.0"
        
        # Calculate schema digest
        schema_str = json.dumps(schema, sort_keys=True)
        schema_digest = hashlib.sha256(schema_str.encode()).hexdigest()
        
        # Create contract
        contract = EventContract(
            name=name,
            version=version,
            contract_type=contract_type,
            category=category,
            description=description,
            schema=schema,
            schema_version="1.0",
            status=ContractStatus.DRAFT.value,
            owner_team=owner_team,
            owner_id=owner_id,
        )
        
        self.db.add(contract)
        await self.db.flush()
        
        # Create initial version
        version_record = EventContractVersion(
            contract_id=contract.id,
            version=version,
            version_number=1,
            schema=schema,
            schema_digest=schema_digest,
            status=SchemaStatus.DRAFT.value,
        )
        
        self.db.add(version_record)
        
        # Create audit entry
        audit = EventContractAudit(
            audit_id=str(uuid4()),
            contract_id=contract.id,
            action="created",
            new_state={"name": name, "type": contract_type, "version": version},
            actor_id=owner_id,
        )
        
        self.db.add(audit)
        await self.db.commit()
        await self.db.refresh(contract)
        
        self._contracts[name] = contract
        return contract
    
    async def activate_contract(self, contract_name: str) -> Optional[EventContract]:
        """Activate a contract for production use"""
        contract = self._contracts.get(contract_name)
        if not contract:
            return None
        
        contract.status = ContractStatus.ACTIVE.value
        contract.version = "1.0.0"
        
        # Update version status
        result = await self.db.execute(
            select(EventContractVersion).where(
                EventContractVersion.contract_id == contract.id
            )
        )
        for ver in result.scalars().all():
            ver.status = SchemaStatus.ACTIVE.value
        
        # Audit
        audit = EventContractAudit(
            audit_id=str(uuid4()),
            contract_id=contract.id,
            action="activated",
            previous_state={"status": ContractStatus.DRAFT.value},
            new_state={"status": ContractStatus.ACTIVE.value},
        )
        self.db.add(audit)
        
        await self.db.commit()
        await self.db.refresh(contract)
        
        return contract
    
    async def deprecate_contract(self, contract_name: str) -> Optional[EventContract]:
        """Mark contract as deprecated"""
        contract = self._contracts.get(contract_name)
        if not contract:
            return None
        
        contract.status = ContractStatus.DEPRECATED.value
        contract.deprecated_at = datetime.utcnow()
        
        # Audit
        audit = EventContractAudit(
            audit_id=str(uuid4()),
            contract_id=contract.id,
            action="deprecated",
            new_state={"status": ContractStatus.DEPRECATED.value},
        )
        self.db.add(audit)
        
        await self.db.commit()
        return contract
    
    async def evolve_contract(
        self,
        contract_name: str,
        new_schema: Dict[str, Any],
        changelog: str,
        breaking: bool = False,
    ) -> Optional[EventContractVersion]:
        """Evolve contract to new version"""
        contract = self._contracts.get(contract_name)
        if not contract:
            return None
        
        # Calculate new version
        current_version = contract.version
        parts = current_version.split(".")
        major = int(parts[0])
        minor = int(parts[1]) + 1
        
        if breaking:
            major += 1
            minor = 0
        
        new_version = f"{major}.{minor}.0"
        schema_digest = hashlib.sha256(json.dumps(new_schema, sort_keys=True).encode()).hexdigest()
        
        # Get current version number
        result = await self.db.execute(
            select(func.max(EventContractVersion.version_number)).where(
                EventContractVersion.contract_id == contract.id
            )
        )
        max_version = result.scalar() or 0
        
        # Create new version
        version_record = EventContractVersion(
            contract_id=contract.id,
            version=new_version,
            version_number=max_version + 1,
            schema=new_schema,
            schema_digest=schema_digest,
            changelog=changelog,
            breaking_changes=breaking,
            status=SchemaStatus.DRAFT.value,
        )
        
        self.db.add(version_record)
        
        # Update contract
        contract.version = new_version
        contract.schema = new_schema
        contract.schema_version = new_version
        
        # Audit
        audit = EventContractAudit(
            audit_id=str(uuid4()),
            contract_id=contract.id,
            action="evolved",
            previous_state={"version": current_version},
            new_state={"version": new_version, "breaking": breaking},
        )
        self.db.add(audit)
        
        await self.db.commit()
        await self.db.refresh(version_record)
        
        return version_record
    
    async def get_contract(self, contract_name: str) -> Optional[EventContract]:
        """Get contract by name"""
        return self._contracts.get(contract_name)
    
    async def get_active_contracts(self) -> List[EventContract]:
        """Get all active contracts"""
        return [c for c in self._contracts.values() if c.status == ContractStatus.ACTIVE.value]
    
    async def validate_event(self, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Validate event against contract schema"""
        contract = self._contracts.get(event_type)
        if not contract:
            return {"valid": False, "errors": [f"Contract not found: {event_type}"]}
        
        if contract.status != ContractStatus.ACTIVE.value:
            return {"valid": False, "errors": ["Contract not active"]}
        
        errors = []
        
        # Validate against schema
        schema = contract.schema
        required_fields = schema.get("required", [])
        
        for field in required_fields:
            if field not in payload:
                errors.append(f"Missing required field: {field}")
        
        # Check field types
        properties = schema.get("properties", {})
        for field, value in payload.items():
            if field in properties:
                expected_type = properties[field].get("type")
                if expected_type and not self._validate_type(value, expected_type):
                    errors.append(f"Invalid type for field {field}: expected {expected_type}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "contract_version": contract.version,
        }
    
    def _validate_type(self, value: Any, expected_type: str) -> bool:
        """Validate value against expected type"""
        type_map = {
            "string": str,
            "number": (int, float),
            "integer": int,
            "boolean": bool,
            "array": list,
            "object": dict,
        }
        
        if expected_type not in type_map:
            return True
        
        expected = type_map[expected_type]
        return isinstance(value, expected)


class TopologyGovernanceEngine:
    """Engine for managing topology governance and validation"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._nodes: Dict[str, TopologyNode] = {}
        self._edges: Dict[str, TopologyEdge] = {}
        self._validation_rules: Dict[str, TopologyValidationRule] = {}
        self._running = False
    
    async def initialize(self) -> None:
        """Initialize topology governance"""
        await self._load_topology()
        await self._load_validation_rules()
        self._running = True
        logger.info("TopologyGovernanceEngine initialized")
    
    async def shutdown(self) -> None:
        """Shutdown topology governance"""
        self._running = False
        logger.info("TopologyGovernanceEngine shutdown")
    
    async def _load_topology(self) -> None:
        """Load topology from database"""
        result = await self.db.execute(select(TopologyNode))
        for node in result.scalars().all():
            self._nodes[str(node.id)] = node
        
        result = await self.db.execute(select(TopologyEdge))
        for edge in result.scalars().all():
            self._edges[str(edge.id)] = edge
    
    async def _load_validation_rules(self) -> None:
        """Load validation rules from database"""
        result = await self.db.execute(
            select(TopologyValidationRule).where(TopologyValidationRule.is_active == True)
        )
        for rule in result.scalars().all():
            self._validation_rules[rule.name] = rule
    
    # ==================== Node Management ====================
    
    async def register_node(
        self,
        name: str,
        node_type: str,
        classification: Optional[str] = None,
        endpoint: Optional[str] = None,
        protocol: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
        region: Optional[str] = None,
    ) -> TopologyNode:
        """Register a new topology node"""
        node = TopologyNode(
            name=name,
            node_type=node_type,
            classification=classification,
            endpoint=endpoint,
            protocol=protocol,
            capabilities=capabilities or [],
            status="active",
            health_score=1.0,
            region=region,
            last_heartbeat=datetime.utcnow(),
        )
        
        self.db.add(node)
        await self.db.commit()
        await self.db.refresh(node)
        
        self._nodes[str(node.id)] = node
        return node
    
    async def update_node_health(
        self,
        node_id: UUID,
        health_score: float,
        error_rate: float,
        latency_p99: float,
    ) -> Optional[TopologyNode]:
        """Update node health metrics"""
        node = self._nodes.get(str(node_id))
        if not node:
            return None
        
        node.health_score = health_score
        node.error_rate = error_rate
        node.latency_p99 = latency_p99
        node.last_heartbeat = datetime.utcnow()
        
        await self.db.commit()
        return node
    
    async def get_node(self, node_id: UUID) -> Optional[TopologyNode]:
        """Get node by ID"""
        return self._nodes.get(str(node_id))
    
    async def get_nodes_by_type(self, node_type: str) -> List[TopologyNode]:
        """Get all nodes of a specific type"""
        return [n for n in self._nodes.values() if n.node_type == node_type]
    
    # ==================== Edge Management ====================
    
    async def create_edge(
        self,
        name: str,
        source_node_id: UUID,
        target_node_id: UUID,
        edge_type: str,
        protocol: Optional[str] = None,
    ) -> TopologyEdge:
        """Create topology edge between nodes"""
        edge = TopologyEdge(
            name=name,
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            edge_type=edge_type,
            protocol=protocol,
            status="active",
            is_active=True,
        )
        
        self.db.add(edge)
        await self.db.commit()
        await self.db.refresh(edge)
        
        self._edges[str(edge.id)] = edge
        return edge
    
    async def get_topology_graph(self) -> Dict[str, Any]:
        """Get complete topology graph"""
        nodes = []
        for node in self._nodes.values():
            nodes.append({
                "id": str(node.id),
                "name": node.name,
                "type": node.node_type,
                "status": node.status,
                "health_score": node.health_score,
            })
        
        edges = []
        for edge in self._edges.values():
            edges.append({
                "id": str(edge.id),
                "source": str(edge.source_node_id),
                "target": str(edge.target_node_id),
                "type": edge.edge_type,
                "status": edge.status,
            })
        
        return {"nodes": nodes, "edges": edges}
    
    # ==================== Validation ====================
    
    async def validate_topology(self) -> Dict[str, Any]:
        """Run all validation rules against topology"""
        violations = []
        
        for rule in self._validation_rules.values():
            rule_result = await self._evaluate_rule(rule)
            if not rule_result["passed"]:
                violations.extend(rule_result["violations"])
        
        return {
            "valid": len(violations) == 0,
            "violations": violations,
            "rule_count": len(self._validation_rules),
        }
    
    async def _evaluate_rule(self, rule: TopologyValidationRule) -> Dict[str, Any]:
        """Evaluate single validation rule"""
        violations = []
        rule_def = rule.rule_definition
        
        rule_type = rule.rule_type
        
        if rule_type == "connectivity":
            # Check connectivity requirements
            min_connections = rule_def.get("min_connections", 1)
            node_types = rule.applies_to_node_types or []
            
            for node in self._nodes.values():
                if not node_types or node.node_type in node_types:
                    connected = await self._count_node_connections(node.id)
                    if connected < min_connections:
                        violations.append({
                            "node": node.name,
                            "type": node.node_type,
                            "rule": rule.name,
                            "message": f"Node has {connected} connections, minimum required: {min_connections}",
                            "severity": rule.severity,
                        })
        
        elif rule_type == "latency":
            # Check latency requirements
            max_latency = rule_def.get("max_latency_ms", 1000)
            
            for edge in self._edges.values():
                if edge.avg_latency_ms > max_latency:
                    violations.append({
                        "edge": edge.name,
                        "latency": edge.avg_latency_ms,
                        "rule": rule.name,
                        "message": f"Edge latency {edge.avg_latency_ms}ms exceeds maximum {max_latency}ms",
                        "severity": rule.severity,
                    })
        
        return {
            "passed": len(violations) == 0,
            "violations": violations,
        }
    
    async def _count_node_connections(self, node_id: UUID) -> int:
        """Count connections for a node"""
        count = 0
        for edge in self._edges.values():
            if edge.source_node_id == node_id or edge.target_node_id == node_id:
                count += 1
        return count


class EventLineageTracker:
    """Tracks event lineage through the distributed system"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._lineages: Dict[str, EventLineage] = {}
    
    async def initialize(self) -> None:
        """Initialize lineage tracker"""
        await self._load_lineages()
        logger.info("EventLineageTracker initialized")
    
    async def _load_lineages(self) -> None:
        """Load recent lineages"""
        cutoff = datetime.utcnow() - timedelta(hours=24)
        result = await self.db.execute(
            select(EventLineage).where(EventLineage.created_at >= cutoff)
        )
        for lineage in result.scalars().all():
            self._lineages[lineage.event_id] = lineage
    
    async def record_event(
        self,
        event_id: str,
        event_type: str,
        source_node_id: Optional[UUID] = None,
        source_service: Optional[str] = None,
        trace_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        causation_id: Optional[str] = None,
    ) -> EventLineage:
        """Record event in lineage"""
        lineage = EventLineage(
            event_id=event_id,
            event_type=event_type,
            source_node_id=source_node_id,
            source_service=source_service,
            trace_id=trace_id,
            correlation_id=correlation_id,
            causation_id=causation_id,
            lineage_type=LineageEventType.CREATED.value,
            created_at=datetime.utcnow(),
        )
        
        self.db.add(lineage)
        await self.db.commit()
        await self.db.refresh(lineage)
        
        self._lineages[event_id] = lineage
        return lineage
    
    async def record_event_visit(
        self,
        event_id: str,
        node_id: UUID,
        node_name: str,
        transformation: Optional[Dict[str, Any]] = None,
    ) -> Optional[EventLineage]:
        """Record event visit to a node"""
        lineage = self._lineages.get(event_id)
        if not lineage:
            return None
        
        visits = lineage.node_visits or []
        visits.append({
            "node_id": str(node_id),
            "node_name": node_name,
            "timestamp": datetime.utcnow().isoformat(),
            "transformation": transformation,
        })
        lineage.node_visits = visits
        
        await self.db.commit()
        return lineage
    
    async def get_event_lineage(self, event_id: str) -> Optional[EventLineage]:
        """Get lineage for an event"""
        return self._lineages.get(event_id)
    
    async def get_correlated_events(
        self,
        correlation_id: str,
        limit: int = 100,
    ) -> List[EventLineage]:
        """Get all events with a correlation ID"""
        result = await self.db.execute(
            select(EventLineage)
            .where(EventLineage.correlation_id == correlation_id)
            .order_by(EventLineage.created_at)
            .limit(limit)
        )
        return list(result.scalars().all())


class PropagationEngine:
    """Manages event propagation policies"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._policies: Dict[str, PropagationPolicy] = {}
    
    async def initialize(self) -> None:
        """Initialize propagation engine"""
        await self._load_policies()
        logger.info("PropagationEngine initialized with %d policies", len(self._policies))
    
    async def _load_policies(self) -> None:
        """Load propagation policies"""
        result = await self.db.execute(
            select(PropagationPolicy).where(PropagationPolicy.is_active == True)
        )
        for policy in result.scalars().all():
            self._policies[str(policy.id)] = policy
    
    async def create_policy(
        self,
        name: str,
        propagation_mode: str = PropagationMode.SYNC.value,
        event_type: Optional[str] = None,
        source_node_id: Optional[UUID] = None,
        target_node_id: Optional[UUID] = None,
        routing_rules: Optional[Dict[str, Any]] = None,
        priority: int = 5,
        qos_level: str = "best_effort",
    ) -> PropagationPolicy:
        """Create a new propagation policy"""
        policy = PropagationPolicy(
            name=name,
            event_type=event_type,
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            propagation_mode=propagation_mode,
            routing_rules=routing_rules,
            priority=priority,
            qos_level=qos_level,
        )
        
        self.db.add(policy)
        await self.db.commit()
        await self.db.refresh(policy)
        
        self._policies[str(policy.id)] = policy
        return policy
    
    async def get_matching_policies(
        self,
        event_type: str,
        source_node_id: Optional[UUID] = None,
    ) -> List[PropagationPolicy]:
        """Get policies matching event and source"""
        matches = []
        
        for policy in self._policies.values():
            if policy.event_type and policy.event_type != event_type:
                continue
            
            if policy.source_node_id and policy.source_node_id != source_node_id:
                continue
            
            matches.append(policy)
        
        return sorted(matches, key=lambda p: p.priority, reverse=True)
    
    async def apply_policy(
        self,
        policy_id: UUID,
        event_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Apply propagation policy to event"""
        policy = self._policies.get(str(policy_id))
        if not policy:
            return {"success": False, "error": "Policy not found"}
        
        # Apply routing rules
        routing_result = self._apply_routing(policy.routing_rules, event_data)
        
        # Apply filters
        if policy.filters:
            filtered = self._apply_filters(policy.filters, routing_result)
            if not filtered["passed"]:
                return {"success": False, "reason": "Filtered out", "result": filtered}
        
        # Apply transformations
        if policy.transformations:
            transformed = self._apply_transformations(policy.transformations, filtered["data"])
            routing_result = transformed
        
        # Update metrics
        policy.execution_count += 1
        policy.success_count += 1
        
        await self.db.commit()
        
        return {
            "success": True,
            "mode": policy.propagation_mode,
            "result": routing_result,
        }
    
    def _apply_routing(
        self,
        routing_rules: Optional[Dict[str, Any]],
        event_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Apply routing rules to event"""
        if not routing_rules:
            return event_data
        
        result = event_data.copy()
        
        # Apply header modifications
        headers = routing_rules.get("headers", {})
        for key, value in headers.items():
            if callable(value):
                result[key] = value(event_data)
            else:
                result[key] = value
        
        return result
    
    def _apply_filters(
        self,
        filters: Dict[str, Any],
        event_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Apply filters to event"""
        for field, condition in filters.items():
            value = event_data.get(field)
            
            if "equals" in condition and value != condition["equals"]:
                return {"passed": False, "reason": f"{field} does not match"}
            
            if "contains" in condition and condition["contains"] not in str(value):
                return {"passed": False, "reason": f"{field} does not contain {condition['contains']}"}
        
        return {"passed": True, "data": event_data}
    
    def _apply_transformations(
        self,
        transformations: Dict[str, Any],
        event_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Apply transformations to event"""
        result = event_data.copy()
        
        for transform in transformations:
            transform_type = transform.get("type")
            
            if transform_type == "rename_field":
                old_name = transform.get("from")
                new_name = transform.get("to")
                if old_name in result:
                    result[new_name] = result.pop(old_name)
            
            elif transform_type == "add_field":
                field_name = transform.get("field")
                field_value = transform.get("value")
                if callable(field_value):
                    result[field_name] = field_value(event_data)
                else:
                    result[field_name] = field_value
            
            elif transform_type == "remove_field":
                field_name = transform.get("field")
                result.pop(field_name, None)
        
        return result


class EventTopologyService:
    """Main service for event topology governance and management"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.contract_registry = ContractRegistry(db)
        self.topology_engine = TopologyGovernanceEngine(db)
        self.lineage_tracker = EventLineageTracker(db)
        self.propagation_engine = PropagationEngine(db)
    
    async def initialize(self) -> None:
        """Initialize all sub-services"""
        await self.contract_registry.initialize()
        await self.topology_engine.initialize()
        await self.lineage_tracker.initialize()
        await self.propagation_engine.initialize()
        logger.info("EventTopologyService fully initialized")
    
    async def shutdown(self) -> None:
        """Shutdown all sub-services"""
        await self.contract_registry.shutdown()
        await self.topology_engine.shutdown()
        logger.info("EventTopologyService shutdown")
    
    async def get_topology_summary(self) -> Dict[str, Any]:
        """Get summary of event topology"""
        topology_graph = await self.topology_engine.get_topology_graph()
        active_contracts = await self.contract_registry.get_active_contracts()
        
        return {
            "nodes": len(topology_graph["nodes"]),
            "edges": len(topology_graph["edges"]),
            "active_contracts": len(active_contracts),
            "propagation_policies": len(self.propagation_engine._policies),
            "graph": topology_graph,
        }