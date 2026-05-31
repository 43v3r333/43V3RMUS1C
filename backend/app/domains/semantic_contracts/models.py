"""
Semantic Execution Contracts Domain Models.

Provides:
- Semantic contract registry
- Execution interpretation standards
- Context inheritance systems
- Semantic propagation engine
- Orchestration meaning synchronization
- Distributed cognition coordination
- Semantic continuity
- Adaptive semantic synchronization
- Workflow cognition alignment
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID
from enum import Enum

from sqlalchemy import Column, String, Text, Integer, Float, Boolean, ForeignKey, JSON, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from ...models.base import BaseModel


class ContractType(str, Enum):
    """Semantic contract types"""
    EXECUTION = "execution"
    DATA_FLOW = "data_flow"
    TELEMETRY = "telemetry"
    POLICY = "policy"
    ORCHESTRATION = "orchestration"
    SEMANTIC = "semantic"


class ContractStatus(str, Enum):
    """Contract lifecycle status"""
    DRAFT = "draft"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DEPRECATED = "deprecated"
    VERSIONED = "versioned"


class PropagationStrategy(str, Enum):
    """Semantic propagation strategies"""
    IMMEDIATE = "immediate"
    DEFERRED = "deferred"
    BATCH = "batch"
    ADAPTIVE = "adaptive"


class InterpretationMethod(str, Enum):
    """Meaning interpretation methods"""
    DIRECT = "direct"
    DERIVED = "derived"
    INFERRED = "inferred"
    LEARNED = "learned"


class ContractDefinition(BaseModel):
    """Contract definition model - formal semantic contract"""
    __tablename__ = "contract_definitions"
    
    # Contract identification
    contract_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    contract_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    
    # Versioning
    version: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    major_version: Mapped[int] = mapped_column(Integer, default=1)
    minor_version: Mapped[int] = mapped_column(Integer, default=0)
    patch_version: Mapped[int] = mapped_column(Integer, default=0)
    
    # Classification
    contract_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    domain: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    priority: Mapped[int] = mapped_column(Integer, default=5)
    
    # Definition
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Specification
    specification: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    schema: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    constraints: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    
    # Semantic rules
    interpretation_rules: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    validation_rules: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    transformation_rules: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    
    # Scope
    applicability: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    exclusions: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    dependencies: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # Lifecycle
    status: Mapped[str] = mapped_column(String(20), default=ContractStatus.DRAFT.value, index=True)
    is_backward_compatible: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Audit
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    activated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deprecated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)


class ContractBinding(BaseModel):
    """Contract binding to execution entities"""
    __tablename__ = "contract_exec_bindings"
    
    # Binding identification
    binding_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Contract reference
    contract_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    contract_version: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Target entity
    target_entity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    target_entity_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # Binding configuration
    binding_context: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    priority: Mapped[int] = mapped_column(Integer, default=0)
    is_mandatory: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Override rules
    value_overrides: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    disabled_rules: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # Lifecycle
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    bound_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    unbound_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    bound_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)


class SemanticInterpretation(BaseModel):
    """Semantic interpretation - meaning assignment to execution"""
    __tablename__ = "semantic_interpretations"
    
    # Interpretation identification
    interpretation_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Execution reference
    execution_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    execution_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    workflow_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    
    # Meaning
    meaning_key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    meaning_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Interpretation
    interpretation_method: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    interpreted_value: Mapped[Any] = mapped_column(JSON, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    
    # Context
    context: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    rationale: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Metadata
    method_config: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    derivation_chain: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # Validation
    is_validated: Mapped[bool] = mapped_column(Boolean, default=False)
    validated_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    
    # Lifecycle
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    invalidated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class PropagatedSemantics(BaseModel):
    """Propagated semantics - tracks semantic propagation"""
    __tablename__ = "propagated_semantics"
    
    # Propagation identification
    propagation_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Source
    source_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    source_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    source_meaning_key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    
    # Target
    target_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    target_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    target_meaning_key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    
    # Propagation details
    propagation_strategy: Mapped[str] = mapped_column(String(20), default=PropagationStrategy.IMMEDIATE.value)
    propagation_depth: Mapped[int] = mapped_column(Integer, default=1)
    hops_traversed: Mapped[List[int]] = mapped_column(JSON, nullable=True)
    
    # State
    state: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    is_reverted: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Audit
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    propagated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class ContextInheritance(BaseModel):
    """Context inheritance - semantic context propagation"""
    __tablename__ = "context_inheritances"
    
    # Inheritance identification
    inheritance_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Source context
    source_entity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    source_entity_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    source_context_key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    
    # Target context
    target_entity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    target_entity_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    target_context_key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    
    # Inheritance rules
    inheritance_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    transformation_rule: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    filter_rule: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # State
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    
    # Audit
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    inherited_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class MeaningSynchronization(BaseModel):
    """Meaning synchronization state"""
    __tablename__ = "meaning_synchronizations"
    
    # Synchronization identification
    sync_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Sync pair
    meaning_key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    node_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # State
    current_value: Mapped[Any] = mapped_column(JSON, nullable=False)
    synchronized_value: Mapped[Any] = mapped_column(JSON, nullable=True)
    
    # Sync details
    sync_strategy: Mapped[str] = mapped_column(String(20), default="last_write_wins")
    conflict_resolution: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    has_conflict: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Timing
    last_synced_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    next_sync_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    sync_latency_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)


class ContractVersion(BaseModel):
    """Contract version history"""
    __tablename__ = "contract_versions"
    
    # Version identification
    version_record_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Contract reference
    contract_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Version data
    specification_snapshot: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    schema_snapshot: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Change info
    changelog: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    breaking_changes: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    migration_guide: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Compatibility
    previous_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_compatible: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Lifecycle
    status: Mapped[str] = mapped_column(String(20), default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    activated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class ExecutionSemantics(BaseModel):
    """Execution semantics - runtime meaning tracking"""
    __tablename__ = "execution_semantics"
    
    # Execution identification
    execution_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Semantic state
    semantic_state: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    semantic_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    
    # Interpretations
    interpretations: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    semantic_tags: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # Relationships
    related_execution_ids: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    semantic_dependencies: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # Workflow context
    workflow_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    
    # Consistency
    consistency_score: Mapped[float] = mapped_column(Float, default=1.0)
    alignment_score: Mapped[float] = mapped_column(Float, default=1.0)
    
    # Audit
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
