"""
Semantic Execution Contracts Services.

Provides:
- Semantic contract management
- Execution interpretation
- Context inheritance systems
- Semantic propagation engine
- Meaning synchronization
- Distributed cognition coordination
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable, Set, Tuple
from uuid import UUID, uuid4
from datetime import datetime
from dataclasses import dataclass, field
from collections import defaultdict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, or_

from .models import (
    ContractType,
    ContractStatus,
    PropagationStrategy,
    InterpretationMethod,
    ContractDefinition,
    ContractBinding,
    SemanticInterpretation,
    PropagatedSemantics,
    ContextInheritance,
    MeaningSynchronization,
    ContractVersion,
    ExecutionSemantics,
)

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Contract validation result"""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    applied_rules: List[str] = field(default_factory=list)


@dataclass
class PropagationReport:
    """Semantic propagation report"""
    total: int
    successful: int
    failed: int
    nodes_with_semantics: Set[str] = field(default_factory=set)
    failed_nodes: List[str] = field(default_factory=list)


@dataclass
class InterpretationContext:
    """Interpretation context for derivation"""
    execution_id: str
    execution_type: str
    available_meanings: Dict[str, Any]
    derivation_stack: List[str] = field(default_factory=list)


class SemanticContractManager:
    """
    Semantic contract management and governance.
    Handles contract registry, validation, and enforcement.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._contracts: Dict[str, ContractDefinition] = {}
        self._bindings: Dict[str, List[ContractBinding]] = defaultdict(list)
        self._running = False
    
    async def initialize(self) -> None:
        """Initialize the contract manager"""
        await self._load_contracts()
        await self._load_bindings()
        self._running = True
        logger.info("SemanticContractManager initialized with %d contracts", len(self._contracts))
    
    async def shutdown(self) -> None:
        """Shutdown the contract manager"""
        self._running = False
        logger.info("SemanticContractManager shutdown")
    
    async def _load_contracts(self) -> None:
        """Load active contracts from database"""
        result = await self.db.execute(
            select(ContractDefinition).where(
                ContractDefinition.status == ContractStatus.ACTIVE.value
            )
        )
        for contract in result.scalars().all():
            self._contracts[contract.contract_id] = contract
    
    async def _load_bindings(self) -> None:
        """Load contract bindings from database"""
        result = await self.db.execute(
            select(ContractBinding).where(ContractBinding.is_active == True)
        )
        for binding in result.scalars().all():
            self._bindings[binding.target_entity_id].append(binding)
    
    # ==================== Contract Management ====================
    
    async def create_contract(
        self,
        contract_key: str,
        contract_type: ContractType,
        domain: str,
        name: str,
        specification: Dict[str, Any],
        version: str = "1.0.0",
        description: Optional[str] = None,
        interpretation_rules: Optional[List[Dict[str, Any]]] = None,
        validation_rules: Optional[List[Dict[str, Any]]] = None,
        applicability: Optional[List[str]] = None,
        created_by: Optional[UUID] = None,
    ) -> ContractDefinition:
        """Create a new semantic contract"""
        contract = ContractDefinition(
            contract_id=str(uuid4()),
            contract_key=contract_key,
            version=version,
            contract_type=contract_type.value,
            domain=domain,
            name=name,
            description=description,
            specification=specification,
            interpretation_rules=interpretation_rules,
            validation_rules=validation_rules,
            applicability=applicability,
            created_by=created_by,
            status=ContractStatus.DRAFT.value,
        )
        
        self.db.add(contract)
        await self.db.commit()
        await self.db.refresh(contract)
        
        self._contracts[contract.contract_id] = contract
        logger.info("Created contract: %s v%s", contract_key, version)
        return contract
    
    async def activate_contract(self, contract_id: str) -> Optional[ContractDefinition]:
        """Activate a contract"""
        contract = self._contracts.get(contract_id)
        if not contract:
            result = await self.db.execute(
                select(ContractDefinition).where(
                    ContractDefinition.contract_id == contract_id
                )
            )
            contract = result.scalar_one_or_none()
        
        if contract:
            contract.status = ContractStatus.ACTIVE.value
            contract.activated_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(contract)
            self._contracts[contract_id] = contract
            logger.info("Activated contract: %s", contract.contract_key)
        
        return contract
    
    async def get_contract_for_entity(
        self,
        entity_type: str,
        entity_id: str,
    ) -> List[Tuple[ContractDefinition, ContractBinding]]:
        """Get all applicable contracts for an entity"""
        bindings = self._bindings.get(entity_id, [])
        applicable = []
        
        for binding in bindings:
            if binding.is_active and binding.target_entity_type == entity_type:
                contract = self._contracts.get(binding.contract_id)
                if contract:
                    applicable.append((contract, binding))
        
        # Sort by priority
        applicable.sort(key=lambda x: x[1].priority, reverse=True)
        return applicable
    
    async def validate_against_contracts(
        self,
        entity_type: str,
        entity_id: str,
        entity_data: Dict[str, Any],
    ) -> ValidationResult:
        """Validate an entity against all applicable contracts"""
        result = ValidationResult(is_valid=True)
        
        contracts = await self.get_contract_for_entity(entity_type, entity_id)
        
        for contract, binding in contracts:
            # Skip if rule has been disabled
            if binding.disabled_rules and "validation" in binding.disabled_rules:
                continue
            
            # Apply overrides if present
            data = {**entity_data}
            if binding.value_overrides:
                data.update(binding.value_overrides)
            
            # Validate using contract's validation rules
            if contract.validation_rules:
                for rule in contract.validation_rules:
                    rule_result = await self._apply_validation_rule(rule, data)
                    if not rule_result["is_valid"]:
                        result.errors.extend(rule_result["errors"])
                        result.is_valid = False
                    result.applied_rules.append(f"{contract.contract_key}:{rule.get('type')}")
        
        return result
    
    async def _apply_validation_rule(
        self,
        rule: Dict[str, Any],
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Apply a single validation rule"""
        rule_type = rule.get("type")
        params = rule.get("params", {})
        
        result = {"is_valid": True, "errors": []}
        
        if rule_type == "required_field":
            field_name = params.get("field")
            if not field_name or field_name not in data:
                result["is_valid"] = False
                result["errors"].append(f"Required field '{field_name}' missing")
        
        elif rule_type == "type_check":
            field_name = params.get("field")
            expected_type = params.get("expected_type")
            if field_name in data and not isinstance(data[field_name], eval(expected_type)):
                result["is_valid"] = False
                result["errors"].append(f"Field '{field_name}' type mismatch")
        
        elif rule_type == "value_range":
            field_name = params.get("field")
            min_val = params.get("min")
            max_val = params.get("max")
            if field_name in data:
                val = data[field_name]
                if min_val is not None and val < min_val:
                    result["is_valid"] = False
                    result["errors"].append(f"Field '{field_name}' below minimum")
                if max_val is not None and val > max_val:
                    result["is_valid"] = False
                    result["errors"].append(f"Field '{field_name}' above maximum")
        
        elif rule_type == "pattern_match":
            import re
            field_name = params.get("field")
            pattern = params.get("pattern")
            if field_name in data and not re.match(pattern, str(data[field_name])):
                result["is_valid"] = False
                result["errors"].append(f"Field '{field_name}' pattern mismatch")
        
        return result
    
    # ==================== Execution Interpretation ====================
    
    async def interpret_execution(
        self,
        execution_id: str,
        execution_type: str,
        meaning_key: str,
        interpreted_value: Any,
        interpretation_method: InterpretationMethod,
        interpretation_rules: Optional[List[Dict[str, Any]]] = None,
        workflow_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        confidence: float = 1.0,
    ) -> SemanticInterpretation:
        """Create an interpretation for an execution"""
        # Apply interpretation rules if available
        final_value = interpreted_value
        if interpretation_rules:
            for rule in interpretation_rules:
                if rule.get("type") == "transform":
                    final_value = rule.get("transform_fn", lambda x: x)(final_value)
        
        interpretation = SemanticInterpretation(
            interpretation_id=str(uuid4()),
            execution_id=execution_id,
            execution_type=execution_type,
            workflow_id=workflow_id,
            meaning_key=meaning_key,
            interpretation_method=interpretation_method.value,
            interpreted_value=final_value,
            confidence=confidence,
            context=context,
        )
        
        self.db.add(interpretation)
        
        # Update execution semantics
        await self._update_execution_semantics(
            execution_id=execution_id,
            workflow_id=workflow_id,
            meaning_key=meaning_key,
            interpretation_data={"method": interpretation_method.value, "value": final_value},
        )
        
        await self.db.commit()
        await self.db.refresh(interpretation)
        
        logger.info("Interpreted execution %s with meaning %s", execution_id, meaning_key)
        return interpretation
    
    async def derive_interpretation(
        self,
        source_interpretation: SemanticInterpretation,
        target_execution_id: str,
        target_execution_type: str,
    ) -> Optional[SemanticInterpretation]:
        """Derive a new interpretation from an existing one"""
        if source_interpretation.derivation_chain is None:
            derivation_chain = []
        else:
            derivation_chain = list(source_interpretation.derivation_chain)
        derivation_chain.append(source_interpretation.interpretation_id)
        
        derived = SemanticInterpretation(
            interpretation_id=str(uuid4()),
            execution_id=target_execution_id,
            execution_type=target_execution_type,
            meaning_key=source_interpretation.meaning_key,
            meaning_version=source_interpretation.meaning_version,
            interpretation_method=InterpretationMethod.DERIVED.value,
            interpreted_value=source_interpretation.interpreted_value,
            confidence=source_interpretation.confidence * 0.9,  # Reduce confidence for derived
            derivation_chain=derivation_chain,
        )
        
        self.db.add(derived)
        await self.db.commit()
        await self.db.refresh(derived)
        
        return derived
    
    async def _update_execution_semantics(
        self,
        execution_id: str,
        workflow_id: Optional[str],
        meaning_key: str,
        interpretation_data: Dict[str, Any],
    ) -> None:
        """Update or create execution semantics record"""
        result = await self.db.execute(
            select(ExecutionSemantics).where(
                ExecutionSemantics.execution_id == execution_id
            )
        )
        semantics = result.scalar_one_or_none()
        
        if semantics:
            # Update existing
            semantics.semantic_state[meaning_key] = interpretation_data
            semantics.updated_at = datetime.utcnow()
        else:
            # Create new
            semantics = ExecutionSemantics(
                execution_id=execution_id,
                workflow_id=workflow_id,
                semantic_state={meaning_key: interpretation_data},
                interpretations=[{"meaning_key": meaning_key, **interpretation_data}],
            )
            self.db.add(semantics)
    
    # ==================== Semantic Propagation ====================
    
    async def propagate_semantics(
        self,
        source_type: str,
        source_id: str,
        source_meaning_key: str,
        target_nodes: List[str],
        strategy: PropagationStrategy = PropagationStrategy.IMMEDIATE,
        depth: int = 1,
    ) -> PropagationReport:
        """Propagate semantics from source to target nodes"""
        report = PropagationReport(total=len(target_nodes), successful=0, failed=0)
        
        for target_id in target_nodes:
            try:
                propagation = PropagatedSemantics(
                    propagation_id=str(uuid4()),
                    source_type=source_type,
                    source_id=source_id,
                    source_meaning_key=source_meaning_key,
                    target_type="node",
                    target_id=target_id,
                    target_meaning_key=source_meaning_key,
                    propagation_strategy=strategy.value,
                    propagation_depth=depth,
                )
                
                self.db.add(propagation)
                report.successful += 1
                report.nodes_with_semantics.add(target_id)
                
            except Exception as e:
                report.failed += 1
                report.failed_nodes.append(target_id)
                logger.error("Failed to propagate semantics to %s: %s", target_id, str(e))
        
        await self.db.commit()
        logger.info("Propagated semantics to %d nodes (%d failed)", report.successful, report.failed)
        return report
    
    # ==================== Context Inheritance ====================
    
    async def inherit_context(
        self,
        source_entity_type: str,
        source_entity_id: str,
        source_context_key: str,
        target_entity_type: str,
        target_entity_id: str,
        inheritance_type: str = "full",
        transformation_rule: Optional[Dict[str, Any]] = None,
    ) -> ContextInheritance:
        """Create a context inheritance relationship"""
        inheritance = ContextInheritance(
            inheritance_id=str(uuid4()),
            source_entity_type=source_entity_type,
            source_entity_id=source_entity_id,
            source_context_key=source_context_key,
            target_entity_type=target_entity_type,
            target_entity_id=target_entity_id,
            target_context_key=source_context_key,
            inheritance_type=inheritance_type,
            transformation_rule=transformation_rule,
        )
        
        self.db.add(inheritance)
        await self.db.commit()
        await self.db.refresh(inheritance)
        
        return inheritance
    
    async def get_inherited_trajectory(
        self,
        entity_type: str,
        entity_id: str,
        context_key: str,
        max_depth: int = 10,
    ) -> List[ContextInheritance]:
        """Get the inheritance trajectory for a context"""
        trajectory = []
        visited = set()
        
        current_type = entity_type
        current_id = entity_id
        current_key = context_key
        depth = 0
        
        while depth < max_depth:
            result = await self.db.execute(
                select(ContextInheritance).where(
                    ContextInheritance.source_entity_type == current_type,
                    ContextInheritance.source_entity_id == current_id,
                    ContextInheritance.source_context_key == current_key,
                    ContextInheritance.is_active == True,
                )
            )
            
            inheritance = result.scalar_one_or_none()
            if not inheritance:
                break
            
            if inheritance.inheritance_id in visited:
                break
            
            trajectory.append(inheritance)
            visited.add(inheritance.inheritance_id)
            
            current_type = inheritance.target_entity_type
            current_id = inheritance.target_entity_id
            current_key = inheritance.target_context_key
            depth += 1
        
        return trajectory
    
    # ==================== Meaning Synchronization ====================
    
    async def sync_meaning(
        self,
        meaning_key: str,
        node_values: Dict[str, Any],
        strategy: str = "last_write_wins",
    ) -> MeaningSynchronization:
        """Synchronize meaning across distributed nodes"""
        most_recent_node = max(node_values.keys(), key=lambda k: node_values[k].get("timestamp", 0))
        most_recent_value = node_values[most_recent_node].get("value")
        
        sync = MeaningSynchronization(
            sync_id=str(uuid4()),
            meaning_key=meaning_key,
            node_id="all",
            current_value=most_recent_value,
            sync_strategy=strategy,
            last_synced_at=datetime.utcnow(),
        )
        
        self.db.add(sync)
        await self.db.commit()
        await self.db.refresh(sync)
        
        return sync


class DistributedInterpretationEngine:
    """
    Distributed semantic interpretation engine.
    Coordinates interpretation across distributed execution nodes.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._interpretation_cache: Dict[str, SemanticInterpretation] = {}
        self._pending_propagations: Dict[str, List[str]] = defaultdict(list)
    
    async def initialize(self) -> None:
        """Initialize the distributed engine"""
        await self._load_cached_interpretations()
        logger.info("DistributedInterpretationEngine initialized")
    
    async def _load_cached_interpretations(self) -> None:
        """Load recent interpretations into cache"""
        result = await self.db.execute(
            select(SemanticInterpretation)
            .order_by(SemanticInterpretation.created_at.desc())
            .limit(1000)
        )
        for interpretation in result.scalars().all():
            cache_key = f"{interpretation.execution_id}:{interpretation.meaning_key}"
            self._interpretation_cache[cache_key] = interpretation
    
    async def interpret_orchestration(
        self,
        execution_id: str,
        execution_type: str,
        orchestration_context: Dict[str, Any],
    ) -> Dict[str, SemanticInterpretation]:
        """Interpret an orchestration execution with context"""
        interpretations = {}
        
        # Determine relevant meanings based on execution type
        if execution_type == "workflow":
            meanings_to_apply = [
                ("workflow.start", {"type": "derived", "value": orchestration_context.get("start_node")}),
                ("workflow.nodes", {"type": "direct", "value": orchestration_context.get("nodes", [])}),
                ("workflow.complexity", {"type": "computed", "value": len(orchestration_context.get("nodes", []))}),
            ]
        elif execution_type == "agent":
            meanings_to_apply = [
                ("agent.action", {"type": "direct", "value": orchestration_context.get("action")}),
                ("agent.context", {"type": "inherited", "value": orchestration_context.get("context")}),
            ]
        else:
            meanings_to_apply = [
                ("execution.state", {"type": "direct", "value": orchestration_context.get("state")}),
            ]
        
        for meaning_key, value_data in meanings_to_apply:
            method = InterpretationMethod(value_data.get("type", "direct"))
            interpretation = await self._create_interpretation(
                execution_id=execution_id,
                execution_type=execution_type,
                meaning_key=meaning_key,
                value=value_data.get("value"),
                method=method,
            )
            if interpretation:
                interpretations[meaning_key] = interpretation
        
        return interpretations
    
    async def _create_interpretation(
        self,
        execution_id: str,
        execution_type: str,
        meaning_key: str,
        value: Any,
        method: InterpretationMethod,
    ) -> Optional[SemanticInterpretation]:
        """Create an interpretation and cache it"""
        cache_key = f"{execution_id}:{meaning_key}"
        
        # Check cache first
        if cache_key in self._interpretation_cache:
            return self._interpretation_cache[cache_key]
        
        interpretation = SemanticInterpretation(
            interpretation_id=str(uuid4()),
            execution_id=execution_id,
            execution_type=execution_type,
            meaning_key=meaning_key,
            interpretation_method=method.value,
            interpreted_value=value,
            confidence=0.95 if method == InterpretationMethod.DIRECT else 0.8,
        )
        
        self.db.add(interpretation)
        await self.db.commit()
        await self.db.refresh(interpretation)
        
        self._interpretation_cache[cache_key] = interpretation
        return interpretation
    
    async def queue_propagation(
        self,
        source_execution_id: str,
        target_node_ids: List[str],
    ) -> None:
        """Queue semantics for propagation to target nodes"""
        self._pending_propagations[source_execution_id] = target_node_ids
    
    async def flush_propagations(self) -> List[PropagationReport]:
        """Flush all pending queued propagations"""
        reports = []
        manager = SemanticContractManager(self.db)
        await manager.initialize()
        
        for execution_id, target_nodes in self._pending_propagations.items():
            result = await self.db.execute(
                select(SemanticInterpretation).where(
                    SemanticInterpretation.execution_id == execution_id
                )
            )
            interpretations = list(result.scalars().all())
            
            for interpretation in interpretations:
                report = await manager.propagate_semantics(
                    source_type="execution",
                    source_id=execution_id,
                    source_meaning_key=interpretation.meaning_key,
                    target_nodes=target_nodes,
                )
                reports.append(report)
        
        self._pending_propagations.clear()
        return reports
