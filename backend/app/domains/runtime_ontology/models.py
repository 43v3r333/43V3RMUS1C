"""
Runtime Ontology Domain Models - Unified runtime semantic registry.

Provides:
- Centralized semantic ontology engine
- Execution meaning registry
- Workflow semantic definitions
- Runtime concept graphs
- Execution relationship schemas
- Orchestra cognition models
- Typed semantic contracts
- Ontology versioning
- Distributed semantic propagation
- Auditability and lineage support
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID
from enum import Enum

from sqlalchemy import Column, String, Text, Integer, Float, Boolean, ForeignKey, JSON, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from ...models.base import BaseModel


class OntologyStatus(str, Enum):
    """Ontology entity status"""
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"
    DRAFT = "draft"


class ConceptType(str, Enum):
    """Runtime concept types"""
    EXECUTION = "execution"
    WORKFLOW = "workflow"
    ORCHESTRATION = "orchestration"
    RESOURCE = "resource"
    SEMANTIC = "semantic"
    COGNITION = "cognition"
    TELEMETRY = "telemetry"
    POLICY = "policy"


class RelationshipType(str, Enum):
    """Relationship types in ontology"""
    DEPENDS_ON = "depends_on"
    PRODUCES = "produces"
    CONSUMES = "consumes"
    ENABLES = "enables"
    REQUIRES = "requires"
    EXTENDS = "extends"
    IMPLEMENTS = "implements"
    COMPOSES = "composes"
    RELATES_TO = "relates_to"


class PropagationState(str, Enum):
    """Semantic propagation state"""
    PENDING = "pending"
    PROPAGATING = "propagating"
    SYNCED = "synced"
    FAILED = "failed"
    IGNORED = "ignored"


class RuntimeConcept(BaseModel):
    """Runtime concept - core semantic primitive"""
    __tablename__ = "runtime_concepts"
    
    concept_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    concept_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    concept_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    definition: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    properties: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    attributes: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    constraints: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    semantic_tags: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    interpretation_rules: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    version_history: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    parent_concept_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(20), default=OntologyStatus.ACTIVE.value, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deprecated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    propagation_state: Mapped[str] = mapped_column(String(20), default=PropagationState.SYNCED.value, index=True)
    last_propagated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    updated_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)


class ConceptRelationship(BaseModel):
    """Concept relationship - semantic links between concepts"""
    __tablename__ = "concept_relationships"
    
    relationship_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    source_concept_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    source_concept_key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    target_concept_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    target_concept_key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    relationship_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    directionality: Mapped[str] = mapped_column(String(20), default="directed")
    properties: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    constraints: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    created_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)


class SemanticContract(BaseModel):
    """Semantic contract - execution interpretation standard"""
    __tablename__ = "semantic_contracts"
    
    contract_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    contract_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    version: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    contract_spec: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    interpretation_rules: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    validation_rules: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    scope: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    applicability: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    exclusions: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deprecated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)


class ContractBinding(BaseModel):
    """Contract binding - links contracts to concepts"""
    __tablename__ = "contract_bindings"
    
    binding_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    contract_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    contract_version: Mapped[str] = mapped_column(String(50), nullable=False)
    target_concept_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    target_type: Mapped[str] = mapped_column(String(50), nullable=False)
    context: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    priority: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    created_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)


class OntologyVersion(BaseModel):
    """Ontology version - temporal versioning of ontology"""
    __tablename__ = "ontology_versions"
    
    version_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    version: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    changelog: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    concepts_snapshot: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    relationships_snapshot: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    is_compatible_with_previous: Mapped[bool] = mapped_column(Boolean, default=True)
    breaking_changes: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="draft", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    activated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)


class DistributedPropagation(BaseModel):
    """Distributed propagation - tracks semantic propagation across nodes"""
    __tablename__ = "distributed_propagations"
    
    propagation_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    entity_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    entity_key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    target_nodes: Mapped[List[str]] = mapped_column(JSON, nullable=False)
    successful_nodes: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    failed_nodes: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    state: Mapped[str] = mapped_column(String(20), default=PropagationState.PENDING.value, index=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    propagate_to_children: Mapped[bool] = mapped_column(Boolean, default=True)
    propagate_cascading: Mapped[bool] = mapped_column(Boolean, default=True)
    timeout_seconds: Mapped[int] = mapped_column(Integer, default=30)
    initiated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class SemanticLineage(BaseModel):
    """Semantic lineage - audit trail for semantic changes"""
    __tablename__ = "semantic_lineage"
    
    lineage_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    entity_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    entity_version: Mapped[str] = mapped_column(String(50), nullable=False)
    change_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    change_description: Mapped[str] = mapped_column(Text, nullable=False)
    change_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    previous_state: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    changed_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    changed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class MeaningRegistry(BaseModel):
    """Meaning registry - execution meaning definitions"""
    __tablename__ = "meaning_registry"
    
    registry_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    meaning_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    semantic_definition: Mapped[str] = mapped_column(Text, nullable=False)
    interpretation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    context_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    applicable_entities: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    validation_schema: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    default_value: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    required_meanings: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    related_meanings: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)


class ExecutionInterpretation(BaseModel):
    """Execution interpretation - runtime meaning assignment"""
    __tablename__ = "execution_interpretations"
    
    interpretation_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    execution_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    execution_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    meaning_key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    meaning_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    interpreted_value: Mapped[Any] = mapped_column(JSON, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    context: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    rationale: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    interpretation_method: Mapped[str] = mapped_column(String(50), nullable=False)
    method_params: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    is_validated: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    validated_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    workflow_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    lineage_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
