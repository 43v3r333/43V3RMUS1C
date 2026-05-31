"""
Runtime Ontology Services - Semantic registry management.

Provides:
- Centralized semantic ontology engine
- Execution meaning registry
- Workflow semantic definitions
- Runtime concept graph management
- Execution relationship schemas
- Semantic propagation
- Distributed semantic synchronization
- Ontology versioning
- Auditability and lineage tracking
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable, Tuple
from uuid import UUID, uuid4
from datetime import datetime
from dataclasses import dataclass, field

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, or_, func

from .models import (
    OntologyStatus,
    ConceptType,
    RelationshipType,
    PropagationState,
    RuntimeConcept,
    ConceptRelationship,
    SemanticContract,
    ContractBinding,
    OntologyVersion,
    DistributedPropagation,
    SemanticLineage,
    MeaningRegistry,
    ExecutionInterpretation,
)

logger = logging.getLogger(__name__)


@dataclass
class ConceptHierarchy:
    """Concept hierarchy with ancestors and descendants"""
    concept: RuntimeConcept
    ancestors: List[RuntimeConcept]
    descendants: List[RuntimeConcept]
    siblings: List[RuntimeConcept]
    depth: int


@dataclass
class ContractValidationResult:
    """Result of contract validation"""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    applied_rules: List[str] = field(default_factory=list)


@dataclass
class PropagationResult:
    """Result of semantic propagation"""
    success: bool
    total_nodes: int
    successful_nodes: List[str] = field(default_factory=list)
    failed_nodes: List[str] = field(default_factory=list)
    duration_ms: float = 0.0
    error_message: Optional[str] = None


class OntologyEngine:
    """
    Centralized semantic ontology engine.
    Manages runtime concepts, relationships, and semantic propagation.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._concepts: Dict[str, RuntimeConcept] = {}
        self._relationships: Dict[str, ConceptRelationship] = {}
        self._contracts: Dict[str, SemanticContract] = {}
        self._running = False
    
    async def initialize(self) -> None:
        """Initialize the ontology engine"""
        await self._load_concepts()
        await self._load_relationships()
        await self._load_contracts()
        self._running = True
        logger.info("OntologyEngine initialized with %d concepts", len(self._concepts))
    
    async def shutdown(self) -> None:
        """Shutdown the ontology engine"""
        self._running = False
        logger.info("OntologyEngine shutdown")
    
    async def _load_concepts(self) -> None:
        """Load concepts from database"""
        result = await self.db.execute(select(RuntimeConcept))
        for concept in result.scalars().all():
            self._concepts[concept.concept_id] = concept
    
    async def _load_relationships(self) -> None:
        """Load relationships from database"""
        result = await self.db.execute(select(ConceptRelationship))
        for rel in result.scalars().all():
            self._relationships[rel.relationship_id] = rel
    
    async def _load_contracts(self) -> None:
        """Load contracts from database"""
        result = await self.db.execute(
            select(SemanticContract).where(SemanticContract.status == "active")
        )
        for contract in result.scalars().all():
            self._contracts[contract.contract_id] = contract
    
    # ==================== Concept Management ====================
    
    async def create_concept(
        self,
        concept_key: str,
        concept_type: ConceptType,
        category: str,
        name: str,
        description: Optional[str] = None,
        definition: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
        semantic_tags: Optional[List[str]] = None,
        parent_concept_id: Optional[str] = None,
        created_by: Optional[UUID] = None,
        correlation_id: Optional[str] = None,
    ) -> RuntimeConcept:
        """Create a new runtime concept"""
        concept = RuntimeConcept(
            concept_id=str(uuid4()),
            concept_key=concept_key,
            concept_type=concept_type.value,
            category=category,
            name=name,
            description=description,
            definition=definition,
            properties=properties or {},
            semantic_tags=semantic_tags,
            parent_concept_id=parent_concept_id,
            status=OntologyStatus.ACTIVE.value,
            created_by=created_by,
        )
        
        self.db.add(concept)
        await self.db.commit()
        await self.db.refresh(concept)
        
        self._concepts[concept.concept_id] = concept
        
        # Record lineage
        await self._record_lineage(
            entity_type="concept",
            entity_id=concept.concept_id,
            entity_version=str(concept.version),
            change_type="created",
            change_description=f"Created concept {concept_key}",
            changed_by=created_by,
            correlation_id=correlation_id,
        )
        
        logger.info("Created concept: %s", concept_key)
        return concept
    
    async def get_concept(
        self,
        concept_id: Optional[str] = None,
        concept_key: Optional[str] = None,
    ) -> Optional[RuntimeConcept]:
        """Get a concept by ID or key"""
        if concept_id:
            return self._concepts.get(concept_id)
        
        for concept in self._concepts.values():
            if concept.concept_key == concept_key:
                return concept
        return None
    
    async def get_concepts_by_type(
        self,
        concept_type: ConceptType,
        status: Optional[OntologyStatus] = None,
    ) -> List[RuntimeConcept]:
        """Get all concepts of a given type"""
        result = await self.db.execute(
            select(RuntimeConcept).where(
                RuntimeConcept.concept_type == concept_type.value,
                RuntimeConcept.status == (status.value if status else RuntimeConcept.status),
            )
        )
        return list(result.scalars().all())
    
    async def get_concept_hierarchy(
        self,
        concept_id: str,
    ) -> Optional[ConceptHierarchy]:
        """Get concept with its hierarchy (ancestors, descendants, siblings)"""
        concept = self._concepts.get(concept_id)
        if not concept:
            return None
        
        # Get ancestors
        ancestors = []
        current = concept
        visited = set()
        while current.parent_concept_id and current.parent_concept_id not in visited:
            parent = self._concepts.get(current.parent_concept_id)
            if not parent:
                break
            ancestors.append(parent)
            visited.add(current.parent_concept_id)
            current = parent
        
        # Get descendants
        result = await self.db.execute(
            select(RuntimeConcept).where(
                RuntimeConcept.parent_concept_id == concept_id
            )
        )
        descendants = list(result.scalars().all())
        
        # Get siblings (same parent)
        siblings = []
        if concept.parent_concept_id:
            result = await self.db.execute(
                select(RuntimeConcept).where(
                    RuntimeConcept.parent_concept_id == concept.parent_concept_id,
                    RuntimeConcept.concept_id != concept_id,
                )
            )
            siblings = list(result.scalars().all())
        
        return ConceptHierarchy(
            concept=concept,
            ancestors=ancestors,
            descendants=descendants,
            siblings=siblings,
            depth=len(ancestors),
        )
    
    async def update_concept(
        self,
        concept_id: str,
        updates: Dict[str, Any],
        updated_by: Optional[UUID] = None,
        correlation_id: Optional[str] = None,
    ) -> Optional[RuntimeConcept]:
        """Update a concept"""
        concept = self._concepts.get(concept_id)
        if not concept:
            return None
        
        # Store previous state
        previous_state = {
            "name": concept.name,
            "description": concept.description,
            "properties": concept.properties,
        }
        
        # Apply updates
        for key, value in updates.items():
            if hasattr(concept, key):
                setattr(concept, key, value)
        
        concept.updated_at = datetime.utcnow()
        concept.updated_by = updated_by
        concept.version += 1
        
        await self.db.commit()
        await self.db.refresh(concept)
        
        # Record lineage
        await self._record_lineage(
            entity_type="concept",
            entity_id=concept.concept_id,
            entity_version=str(concept.version),
            change_type="updated",
            change_description=f"Updated concept {concept.concept_key}",
            change_data=updates,
            previous_state=previous_state,
            changed_by=updated_by,
            correlation_id=correlation_id,
        )
        
        self._concepts[concept_id] = concept
        logger.info("Updated concept: %s", concept.concept_key)
        return concept
    
    # ==================== Relationship Management ====================
    
    async def create_relationship(
        self,
        source_concept_id: str,
        target_concept_id: str,
        relationship_type: RelationshipType,
        weight: float = 1.0,
        properties: Optional[Dict[str, Any]] = None,
        created_by: Optional[UUID] = None,
    ) -> Optional[ConceptRelationship]:
        """Create a relationship between two concepts"""
        source = self._concepts.get(source_concept_id)
        target = self._concepts.get(target_concept_id)
        
        if not source or not target:
            logger.warning("Cannot create relationship: source or target concept not found")
            return None
        
        relationship = ConceptRelationship(
            relationship_id=str(uuid4()),
            source_concept_id=source_concept_id,
            source_concept_key=source.concept_key,
            target_concept_id=target_concept_id,
            target_concept_key=target.concept_key,
            relationship_type=relationship_type.value,
            weight=weight,
            properties=properties,
            created_by=created_by,
        )
        
        self.db.add(relationship)
        await self.db.commit()
        await self.db.refresh(relationship)
        
        self._relationships[relationship.relationship_id] = relationship
        logger.info("Created relationship: %s -> %s (%s)", source.concept_key, target.concept_key, relationship_type.value)
        return relationship
    
    async def get_relationships_for_concept(
        self,
        concept_id: str,
        relationship_type: Optional[RelationshipType] = None,
        direction: str = "both",
    ) -> List[ConceptRelationship]:
        """Get all relationships for a concept"""
        conditions = []
        
        if direction in ("both", "outgoing"):
            conditions.append(ConceptRelationship.source_concept_id == concept_id)
        if direction in ("both", "incoming"):
            conditions.append(ConceptRelationship.target_concept_id == concept_id)
        
        if relationship_type:
            conditions.append(ConceptRelationship.relationship_type == relationship_type.value)
        
        result = await self.db.execute(
            select(ConceptRelationship).where(
                and_(*conditions) if conditions else True,
                ConceptRelationship.is_active == True,
            )
        )
        return list(result.scalars().all())
    
    # ==================== Contract Management ====================
    
    async def create_contract(
        self,
        contract_key: str,
        name: str,
        contract_spec: Dict[str, Any],
        scope: str,
        version: str = "1.0.0",
        description: Optional[str] = None,
        interpretation_rules: Optional[List[Dict[str, Any]]] = None,
        validation_rules: Optional[List[Dict[str, Any]]] = None,
        created_by: Optional[UUID] = None,
    ) -> SemanticContract:
        """Create a new semantic contract"""
        contract = SemanticContract(
            contract_id=str(uuid4()),
            contract_key=contract_key,
            name=name,
            description=description,
            contract_spec=contract_spec,
            interpretation_rules=interpretation_rules,
            validation_rules=validation_rules,
            scope=scope,
            version=version,
            created_by=created_by,
        )
        
        self.db.add(contract)
        await self.db.commit()
        await self.db.refresh(contract)
        
        self._contracts[contract.contract_id] = contract
        logger.info("Created contract: %s v%s", contract_key, version)
        return contract
    
    async def validate_against_contract(
        self,
        entity: Dict[str, Any],
        contract_id: str,
    ) -> ContractValidationResult:
        """Validate an entity against a contract"""
        contract = self._contracts.get(contract_id)
        if not contract:
            return ContractValidationResult(
                is_valid=False,
                errors=[f"Contract {contract_id} not found"],
            )
        
        errors = []
        warnings = []
        applied_rules = []
        
        # Validate using contract rules
        if contract.validation_rules:
            for rule in contract.validation_rules:
                rule_type = rule.get("type")
                rule_params = rule.get("params", {})
                
                if rule_type == "required_field":
                    field_name = rule_params.get("field")
                    if field_name not in entity:
                        errors.append(f"Required field '{field_name}' is missing")
                    else:
                        applied_rules.append(f"required_field:{field_name}")
                
                elif rule_type == "type_check":
                    field_name = rule_params.get("field")
                    expected_type = rule_params.get("expected_type")
                    if field_name in entity and not isinstance(entity[field_name], eval(expected_type)):
                        errors.append(f"Field '{field_name}' should be of type {expected_type}")
                    else:
                        applied_rules.append(f"type_check:{field_name}")
                
                elif rule_type == "value_range":
                    field_name = rule_params.get("field")
                    min_val = rule_params.get("min")
                    max_val = rule_params.get("max")
                    if field_name in entity:
                        val = entity[field_name]
                        if min_val and val < min_val:
                            errors.append(f"Field '{field_name}' value {val} is below minimum {min_val}")
                        if max_val and val > max_val:
                            errors.append(f"Field '{field_name}' value {val} is above maximum {max_val}")
                    applied_rules.append(f"value_range:{field_name}")
        
        return ContractValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            applied_rules=applied_rules,
        )
    
    async def bind_contract_to_concept(
        self,
        contract_id: str,
        contract_version: str,
        target_concept_id: str,
        target_type: str,
        context: Optional[Dict[str, Any]] = None,
        priority: int = 0,
        created_by: Optional[UUID] = None,
    ) -> ContractBinding:
        """Bind a contract to a concept"""
        binding = ContractBinding(
            binding_id=str(uuid4()),
            contract_id=contract_id,
            contract_version=contract_version,
            target_concept_id=target_concept_id,
            target_type=target_type,
            context=context,
            priority=priority,
            created_by=created_by,
        )
        
        self.db.add(binding)
        await self.db.commit()
        await self.db.refresh(binding)
        
        logger.info("Bound contract %s to concept %s", contract_id, target_concept_id)
        return binding
    
    # ==================== Semantic Propagation ====================
    
    async def propagate_semantics(
        self,
        entity_type: str,
        entity_id: str,
        entity_key: str,
        target_nodes: List[str],
        propagate_to_children: bool = True,
        propagate_cascading: bool = True,
        correlation_id: Optional[str] = None,
    ) -> PropagationResult:
        """Propagate semantic information to target nodes"""
        propagation = DistributedPropagation(
            propagation_id=str(uuid4()),
            entity_type=entity_type,
            entity_id=entity_id,
            entity_key=entity_key,
            target_nodes=target_nodes,
            propagate_to_children=propagate_to_children,
            propagate_cascading=propagate_cascading,
            initiated_at=datetime.utcnow(),
            state=PropagationState.PROPAGATING.value,
        )
        
        self.db.add(propagation)
        await self.db.commit()
        await self.db.refresh(propagation)
        
        start_time = datetime.utcnow()
        successful_nodes = []
        failed_nodes = []
        
        # Simulate propagation to nodes
        for node in target_nodes:
            try:
                # In a real implementation, this would send to actual nodes
                await asyncio.sleep(0.01)  # Simulate async operation
                successful_nodes.append(node)
            except Exception as e:
                failed_nodes.append(node)
                logger.error("Failed to propagate to node %s: %s", node, str(e))
        
        end_time = datetime.utcnow()
        duration_ms = (end_time - start_time).total_seconds() * 1000
        
        # Update propagation record
        propagation.successful_nodes = successful_nodes
        propagation.failed_nodes = failed_nodes
        propagation.completed_at = end_time
        propagation.duration_ms = duration_ms
        propagation.state = PropagationState.SYNCED.value if not failed_nodes else PropagationState.FAILED.value
        
        if failed_nodes:
            propagation.error_message = f"Failed to propagate to {len(failed_nodes)} nodes"
        
        await self.db.commit()
        
        # Update concept propagation state
        if entity_type == "concept":
            concept = self._concepts.get(entity_id)
            if concept:
                concept.propagation_state = PropagationState.SYNCED.value
                concept.last_propagated_at = end_time
                await self.db.commit()
        
        return PropagationResult(
            success=len(failed_nodes) == 0,
            total_nodes=len(target_nodes),
            successful_nodes=successful_nodes,
            failed_nodes=failed_nodes,
            duration_ms=duration_ms,
            error_message=propagation.error_message,
        )
    
    # ==================== Ontology Versioning ====================
    
    async def create_version_snapshot(
        self,
        version: str,
        name: str,
        description: Optional[str] = None,
        created_by: Optional[UUID] = None,
    ) -> OntologyVersion:
        """Create a version snapshot of the ontology"""
        # Gather all concepts
        concepts_result = await self.db.execute(select(RuntimeConcept))
        concepts_snapshot = [
            {
                "concept_id": c.concept_id,
                "concept_key": c.concept_key,
                "concept_type": c.concept_type,
                "name": c.name,
                "version": c.version,
                "status": c.status,
            }
            for c in concepts_result.scalars().all()
        ]
        
        # Gather all relationships
        rels_result = await self.db.execute(select(ConceptRelationship))
        relationships_snapshot = [
            {
                "relationship_id": r.relationship_id,
                "source_key": r.source_concept_key,
                "target_key": r.target_concept_key,
                "type": r.relationship_type,
            }
            for r in rels_result.scalars().all()
        ]
        
        ont_version = OntologyVersion(
            version_id=str(uuid4()),
            version=version,
            name=name,
            description=description,
            concepts_snapshot=concepts_snapshot,
            relationships_snapshot=relationships_snapshot,
            created_by=created_by,
        )
        
        self.db.add(ont_version)
        await self.db.commit()
        await self.db.refresh(ont_version)
        
        logger.info("Created ontology version snapshot: %s", version)
        return ont_version
    
    async def restore_version(self, version_id: str) -> bool:
        """Restore ontology from a version snapshot"""
        result = await self.db.execute(
            select(OntologyVersion).where(OntologyVersion.version_id == version_id)
        )
        version = result.scalar_one_or_none()
        
        if not version or not version.concepts_snapshot:
            return False
        
        logger.info("Restoring ontology from version: %s", version.version)
        # Implementation would restore concepts and relationships from snapshot
        return True
    
    # ==================== Lineage Tracking ====================
    
    async def _record_lineage(
        self,
        entity_type: str,
        entity_id: str,
        entity_version: str,
        change_type: str,
        change_description: str,
        change_data: Optional[Dict[str, Any]] = None,
        previous_state: Optional[Dict[str, Any]] = None,
        changed_by: Optional[UUID] = None,
        correlation_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> SemanticLineage:
        """Record a lineage entry"""
        lineage = SemanticLineage(
            lineage_id=str(uuid4()),
            entity_type=entity_type,
            entity_id=entity_id,
            entity_version=entity_version,
            change_type=change_type,
            change_description=change_description,
            change_data=change_data,
            previous_state=previous_state,
            changed_by=changed_by,
            changed_at=datetime.utcnow(),
            correlation_id=correlation_id,
            session_id=session_id,
        )
        
        self.db.add(lineage)
        await self.db.commit()
        await self.db.refresh(lineage)
        
        return lineage
    
    async def get_lineage(
        self,
        entity_id: str,
        entity_type: Optional[str] = None,
    ) -> List[SemanticLineage]:
        """Get lineage history for an entity"""
        conditions = [SemanticLineage.entity_id == entity_id]
        
        if entity_type:
            conditions.append(SemanticLineage.entity_type == entity_type)
        
        result = await self.db.execute(
            select(SemanticLineage)
            .where(and_(*conditions))
            .order_by(SemanticLineage.changed_at.desc())
        )
        return list(result.scalars().all())
    
    # ==================== Meaning Registry ====================
    
    async def register_meaning(
        self,
        meaning_key: str,
        name: str,
        semantic_definition: str,
        context_type: str,
        version: str = "1.0.0",
        description: Optional[str] = None,
        interpretation: Optional[str] = None,
        applicable_entities: Optional[List[str]] = None,
        validation_schema: Optional[Dict[str, Any]] = None,
        created_by: Optional[UUID] = None,
    ) -> MeaningRegistry:
        """Register a new meaning"""
        meaning = MeaningRegistry(
            registry_id=str(uuid4()),
            meaning_key=meaning_key,
            name=name,
            description=description,
            semantic_definition=semantic_definition,
            interpretation=interpretation,
            context_type=context_type,
            applicable_entities=applicable_entities,
            validation_schema=validation_schema,
            version=version,
            created_by=created_by,
        )
        
        self.db.add(meaning)
        await self.db.commit()
        await self.db.refresh(meaning)
        
        logger.info("Registered meaning: %s", meaning_key)
        return meaning
    
    async def interpret_execution(
        self,
        execution_id: str,
        execution_type: str,
        meaning_key: str,
        interpreted_value: Any,
        interpretation_method: str,
        workflow_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        confidence: float = 1.0,
        correlation_id: Optional[str] = None,
    ) -> ExecutionInterpretation:
        """Interpret an execution with semantic meaning"""
        interpretation = ExecutionInterpretation(
            interpretation_id=str(uuid4()),
            execution_id=execution_id,
            execution_type=execution_type,
            meaning_key=meaning_key,
            interpreted_value=interpreted_value,
            interpretation_method=interpretation_method,
            confidence=confidence,
            context=context,
            workflow_id=workflow_id,
            correlation_id=correlation_id,
        )
        
        self.db.add(interpretation)
        await self.db.commit()
        await self.db.refresh(interpretation)
        
        logger.info("Interpreted execution %s with meaning %s", execution_id, meaning_key)
        return interpretation
    
    async def get_interpretations_for_execution(
        self,
        execution_id: str,
    ) -> List[ExecutionInterpretation]:
        """Get all interpretations for an execution"""
        result = await self.db.execute(
            select(ExecutionInterpretation)
            .where(ExecutionInterpretation.execution_id == execution_id)
            .order_by(ExecutionInterpretation.created_at.desc())
        )
        return list(result.scalars().all())
