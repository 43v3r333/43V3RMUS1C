"""Semantic cognitive infrastructure tables

Revision ID: 004_semantic_cognition
Revises: 003_execution_fabric
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Any, Optional
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '004_semantic_cognition'
down_revision: str = '003_execution_fabric'
branch_labels: Optional[str] = None
depends_on: Optional[str] = None


def upgrade() -> None:
    # ==================== RUNTIME ONTOLOGY TABLES ====================
    
    # Runtime concepts
    op.create_table(
        'runtime_concepts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('concept_id', sa.String(100), nullable=False, unique=True),
        sa.Column('concept_key', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('concept_type', sa.String(50), nullable=False, index=True),
        sa.Column('category', sa.String(50), nullable=False, index=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('definition', sa.Text, nullable=True),
        sa.Column('properties', postgresql.JSON, nullable=True),
        sa.Column('attributes', postgresql.JSON, nullable=True),
        sa.Column('constraints', postgresql.JSON, nullable=True),
        sa.Column('semantic_tags', postgresql.JSON, nullable=True),
        sa.Column('interpretation_rules', postgresql.JSON, nullable=True),
        sa.Column('version', sa.Integer, default=1),
        sa.Column('version_history', postgresql.JSON, nullable=True),
        sa.Column('parent_concept_id', sa.String(100), nullable=True, index=True),
        sa.Column('status', sa.String(20), default='active', index=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=True),
        sa.Column('deprecated_at', sa.DateTime, nullable=True),
        sa.Column('propagation_state', sa.String(20), default='synced', index=True),
        sa.Column('last_propagated_at', sa.DateTime, nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
    )
    
    # Concept relationships
    op.create_table(
        'concept_relationships',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('relationship_id', sa.String(100), nullable=False, unique=True),
        sa.Column('source_concept_id', sa.String(100), nullable=False, index=True),
        sa.Column('source_concept_key', sa.String(255), nullable=False),
        sa.Column('target_concept_id', sa.String(100), nullable=False, index=True),
        sa.Column('target_concept_key', sa.String(255), nullable=False),
        sa.Column('relationship_type', sa.String(50), nullable=False, index=True),
        sa.Column('weight', sa.Float, default=1.0),
        sa.Column('confidence', sa.Float, default=1.0),
        sa.Column('directionality', sa.String(20), default='directed'),
        sa.Column('properties', postgresql.JSON, nullable=True),
        sa.Column('constraints', postgresql.JSON, nullable=True),
        sa.Column('version', sa.Integer, default=1),
        sa.Column('is_active', sa.Boolean, default=True, index=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
    )
    
    # Semantic contracts
    op.create_table(
        'semantic_contracts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('contract_id', sa.String(100), nullable=False, unique=True),
        sa.Column('contract_key', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('version', sa.String(50), nullable=False, index=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('contract_spec', postgresql.JSON, nullable=False),
        sa.Column('interpretation_rules', postgresql.JSON, nullable=True),
        sa.Column('validation_rules', postgresql.JSON, nullable=True),
        sa.Column('scope', sa.String(50), nullable=False, index=True),
        sa.Column('applicability', postgresql.JSON, nullable=True),
        sa.Column('exclusions', postgresql.JSON, nullable=True),
        sa.Column('status', sa.String(20), default='active', index=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=True),
        sa.Column('deprecated_at', sa.DateTime, nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
    )
    
    # Contract bindings
    op.create_table(
        'contract_bindings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('binding_id', sa.String(100), nullable=False, unique=True),
        sa.Column('contract_id', sa.String(100), nullable=False, index=True),
        sa.Column('contract_version', sa.String(50), nullable=False),
        sa.Column('target_concept_id', sa.String(100), nullable=False, index=True),
        sa.Column('target_type', sa.String(50), nullable=False),
        sa.Column('context', postgresql.JSON, nullable=True),
        sa.Column('priority', sa.Integer, default=0),
        sa.Column('is_active', sa.Boolean, default=True, index=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
    )
    
    # Ontology versions
    op.create_table(
        'ontology_versions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('version_id', sa.String(100), nullable=False, unique=True),
        sa.Column('version', sa.String(50), nullable=False, index=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('changelog', postgresql.JSON, nullable=True),
        sa.Column('concepts_snapshot', postgresql.JSON, nullable=True),
        sa.Column('relationships_snapshot', postgresql.JSON, nullable=True),
        sa.Column('is_compatible_with_previous', sa.Boolean, default=True),
        sa.Column('breaking_changes', postgresql.JSON, nullable=True),
        sa.Column('status', sa.String(20), default='draft', index=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('activated_at', sa.DateTime, nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
    )
    
    # Distributed propagations
    op.create_table(
        'distributed_propagations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('propagation_id', sa.String(100), nullable=False, unique=True),
        sa.Column('entity_type', sa.String(50), nullable=False, index=True),
        sa.Column('entity_id', sa.String(100), nullable=False, index=True),
        sa.Column('entity_key', sa.String(255), nullable=False, index=True),
        sa.Column('target_nodes', postgresql.JSON, nullable=False),
        sa.Column('successful_nodes', postgresql.JSON, nullable=True),
        sa.Column('failed_nodes', postgresql.JSON, nullable=True),
        sa.Column('state', sa.String(20), default='pending', index=True),
        sa.Column('retry_count', sa.Integer, default=0),
        sa.Column('propagate_to_children', sa.Boolean, default=True),
        sa.Column('propagate_cascading', sa.Boolean, default=True),
        sa.Column('timeout_seconds', sa.Integer, default=30),
        sa.Column('initiated_at', sa.DateTime, nullable=False),
        sa.Column('completed_at', sa.DateTime, nullable=True),
        sa.Column('duration_ms', sa.Float, nullable=True),
        sa.Column('error_message', sa.Text, nullable=True),
    )
    
    # Semantic lineage
    op.create_table(
        'semantic_lineage',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('lineage_id', sa.String(100), nullable=False, unique=True),
        sa.Column('entity_type', sa.String(50), nullable=False, index=True),
        sa.Column('entity_id', sa.String(100), nullable=False, index=True),
        sa.Column('entity_version', sa.String(50), nullable=False),
        sa.Column('change_type', sa.String(50), nullable=False, index=True),
        sa.Column('change_description', sa.Text, nullable=False),
        sa.Column('change_data', postgresql.JSON, nullable=True),
        sa.Column('previous_state', postgresql.JSON, nullable=True),
        sa.Column('changed_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('changed_at', sa.DateTime, nullable=False, index=True),
        sa.Column('correlation_id', sa.String(100), nullable=True, index=True),
        sa.Column('session_id', sa.String(100), nullable=True, index=True),
    )
    
    # Meaning registry
    op.create_table(
        'meaning_registry',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('registry_id', sa.String(100), nullable=False, unique=True),
        sa.Column('meaning_key', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('semantic_definition', sa.Text, nullable=False),
        sa.Column('interpretation', sa.Text, nullable=True),
        sa.Column('context_type', sa.String(50), nullable=False, index=True),
        sa.Column('applicable_entities', postgresql.JSON, nullable=True),
        sa.Column('validation_schema', postgresql.JSON, nullable=True),
        sa.Column('default_value', postgresql.JSON, nullable=True),
        sa.Column('required_meanings', postgresql.JSON, nullable=True),
        sa.Column('related_meanings', postgresql.JSON, nullable=True),
        sa.Column('version', sa.String(50), nullable=False),
        sa.Column('status', sa.String(20), default='active', index=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
    )
    
    # Execution interpretations
    op.create_table(
        'execution_interpretations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('interpretation_id', sa.String(100), nullable=False, unique=True),
        sa.Column('execution_id', sa.String(100), nullable=False, index=True),
        sa.Column('execution_type', sa.String(50), nullable=False, index=True),
        sa.Column('meaning_key', sa.String(255), nullable=False, index=True),
        sa.Column('meaning_version', sa.String(50), nullable=True),
        sa.Column('interpreted_value', postgresql.JSON, nullable=False),
        sa.Column('confidence', sa.Float, default=1.0),
        sa.Column('context', postgresql.JSON, nullable=True),
        sa.Column('rationale', sa.Text, nullable=True),
        sa.Column('interpretation_method', sa.String(50), nullable=False),
        sa.Column('method_params', postgresql.JSON, nullable=True),
        sa.Column('is_validated', sa.Boolean, default=False, index=True),
        sa.Column('validated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=True),
        sa.Column('workflow_id', sa.String(100), nullable=True, index=True),
        sa.Column('lineage_id', sa.String(100), nullable=True, index=True),
    )
    
    # ==================== SEMANTIC CONTRACTS TABLES ====================
    
    # Contract definitions
    op.create_table(
        'contract_definitions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('contract_id', sa.String(100), nullable=False, unique=True),
        sa.Column('contract_key', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('version', sa.String(50), nullable=False, index=True),
        sa.Column('major_version', sa.Integer, default=1),
        sa.Column('minor_version', sa.Integer, default=0),
        sa.Column('patch_version', sa.Integer, default=0),
        sa.Column('contract_type', sa.String(50), nullable=False, index=True),
        sa.Column('domain', sa.String(50), nullable=False, index=True),
        sa.Column('priority', sa.Integer, default=5),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('specification', postgresql.JSON, nullable=False),
        sa.Column('schema', postgresql.JSON, nullable=True),
        sa.Column('constraints', postgresql.JSON, nullable=True),
        sa.Column('interpretation_rules', postgresql.JSON, nullable=True),
        sa.Column('validation_rules', postgresql.JSON, nullable=True),
        sa.Column('transformation_rules', postgresql.JSON, nullable=True),
        sa.Column('applicability', postgresql.JSON, nullable=True),
        sa.Column('exclusions', postgresql.JSON, nullable=True),
        sa.Column('dependencies', postgresql.JSON, nullable=True),
        sa.Column('status', sa.String(20), default='draft', index=True),
        sa.Column('is_backward_compatible', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=True),
        sa.Column('activated_at', sa.DateTime, nullable=True),
        sa.Column('deprecated_at', sa.DateTime, nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
    )
    
    # Contract exec bindings
    op.create_table(
        'contract_exec_bindings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('binding_id', sa.String(100), nullable=False, unique=True),
        sa.Column('contract_id', sa.String(100), nullable=False, index=True),
        sa.Column('contract_version', sa.String(50), nullable=False),
        sa.Column('target_entity_type', sa.String(50), nullable=False, index=True),
        sa.Column('target_entity_id', sa.String(100), nullable=False, index=True),
        sa.Column('binding_context', postgresql.JSON, nullable=True),
        sa.Column('priority', sa.Integer, default=0),
        sa.Column('is_mandatory', sa.Boolean, default=False),
        sa.Column('value_overrides', postgresql.JSON, nullable=True),
        sa.Column('disabled_rules', postgresql.JSON, nullable=True),
        sa.Column('is_active', sa.Boolean, default=True, index=True),
        sa.Column('bound_at', sa.DateTime, nullable=False),
        sa.Column('unbound_at', sa.DateTime, nullable=True),
        sa.Column('bound_by', postgresql.UUID(as_uuid=True), nullable=True),
    )
    
    # Semantic interpretations
    op.create_table(
        'semantic_interpretations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('interpretation_id', sa.String(100), nullable=False, unique=True),
        sa.Column('execution_id', sa.String(100), nullable=False, index=True),
        sa.Column('execution_type', sa.String(50), nullable=False, index=True),
        sa.Column('workflow_id', sa.String(100), nullable=True, index=True),
        sa.Column('meaning_key', sa.String(255), nullable=False, index=True),
        sa.Column('meaning_version', sa.String(50), nullable=True),
        sa.Column('interpretation_method', sa.String(50), nullable=False, index=True),
        sa.Column('interpreted_value', postgresql.JSON, nullable=False),
        sa.Column('confidence', sa.Float, default=1.0),
        sa.Column('context', postgresql.JSON, nullable=True),
        sa.Column('rationale', sa.Text, nullable=True),
        sa.Column('method_config', postgresql.JSON, nullable=True),
        sa.Column('derivation_chain', postgresql.JSON, nullable=True),
        sa.Column('is_validated', sa.Boolean, default=False),
        sa.Column('validated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=True),
        sa.Column('invalidated_at', sa.DateTime, nullable=True),
    )
    
    # Propagated semantics
    op.create_table(
        'propagated_semantics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('propagation_id', sa.String(100), nullable=False, unique=True),
        sa.Column('source_type', sa.String(50), nullable=False, index=True),
        sa.Column('source_id', sa.String(100), nullable=False, index=True),
        sa.Column('source_meaning_key', sa.String(255), nullable=False, index=True),
        sa.Column('target_type', sa.String(50), nullable=False, index=True),
        sa.Column('target_id', sa.String(100), nullable=False, index=True),
        sa.Column('target_meaning_key', sa.String(255), nullable=False, index=True),
        sa.Column('propagation_strategy', sa.String(20), default='immediate'),
        sa.Column('propagation_depth', sa.Integer, default=1),
        sa.Column('hops_traversed', postgresql.JSON, nullable=True),
        sa.Column('state', sa.String(20), default='pending', index=True),
        sa.Column('is_reverted', sa.Boolean, default=False),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('propagated_at', sa.DateTime, nullable=True),
    )
    
    # Context inheritances
    op.create_table(
        'context_inheritances',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('inheritance_id', sa.String(100), nullable=False, unique=True),
        sa.Column('source_entity_type', sa.String(50), nullable=False, index=True),
        sa.Column('source_entity_id', sa.String(100), nullable=False, index=True),
        sa.Column('source_context_key', sa.String(255), nullable=False, index=True),
        sa.Column('target_entity_type', sa.String(50), nullable=False, index=True),
        sa.Column('target_entity_id', sa.String(100), nullable=False, index=True),
        sa.Column('target_context_key', sa.String(255), nullable=False, index=True),
        sa.Column('inheritance_type', sa.String(50), nullable=False),
        sa.Column('transformation_rule', postgresql.JSON, nullable=True),
        sa.Column('filter_rule', postgresql.JSON, nullable=True),
        sa.Column('is_active', sa.Boolean, default=True, index=True),
        sa.Column('weight', sa.Float, default=1.0),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('inherited_at', sa.DateTime, nullable=True),
    )
    
    # Meaning synchronizations
    op.create_table(
        'meaning_synchronizations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('sync_id', sa.String(100), nullable=False, unique=True),
        sa.Column('meaning_key', sa.String(255), nullable=False, index=True),
        sa.Column('node_id', sa.String(100), nullable=False, index=True),
        sa.Column('current_value', postgresql.JSON, nullable=False),
        sa.Column('synchronized_value', postgresql.JSON, nullable=True),
        sa.Column('sync_strategy', sa.String(20), default='last_write_wins'),
        sa.Column('conflict_resolution', sa.String(50), nullable=True),
        sa.Column('has_conflict', sa.Boolean, default=False),
        sa.Column('last_synced_at', sa.DateTime, nullable=False, index=True),
        sa.Column('next_sync_at', sa.DateTime, nullable=True),
        sa.Column('sync_latency_ms', sa.Float, nullable=True),
    )
    
    # Contract versions
    op.create_table(
        'contract_versions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('version_record_id', sa.String(100), nullable=False, unique=True),
        sa.Column('contract_id', sa.String(100), nullable=False, index=True),
        sa.Column('version', sa.String(50), nullable=False),
        sa.Column('specification_snapshot', postgresql.JSON, nullable=False),
        sa.Column('schema_snapshot', postgresql.JSON, nullable=True),
        sa.Column('changelog', postgresql.JSON, nullable=True),
        sa.Column('breaking_changes', postgresql.JSON, nullable=True),
        sa.Column('migration_guide', sa.Text, nullable=True),
        sa.Column('previous_version', sa.String(50), nullable=True),
        sa.Column('is_compatible', sa.Boolean, default=True),
        sa.Column('status', sa.String(20), default='draft'),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('activated_at', sa.DateTime, nullable=True),
    )
    
    # Execution semantics
    op.create_table(
        'execution_semantics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('execution_id', sa.String(100), nullable=False, unique=True),
        sa.Column('semantic_state', postgresql.JSON, nullable=False),
        sa.Column('semantic_hash', sa.String(64), nullable=True, index=True),
        sa.Column('interpretations', postgresql.JSON, nullable=True),
        sa.Column('semantic_tags', postgresql.JSON, nullable=True),
        sa.Column('related_execution_ids', postgresql.JSON, nullable=True),
        sa.Column('semantic_dependencies', postgresql.JSON, nullable=True),
        sa.Column('workflow_id', sa.String(100), nullable=True, index=True),
        sa.Column('session_id', sa.String(100), nullable=True, index=True),
        sa.Column('consistency_score', sa.Float, default=1.0),
        sa.Column('alignment_score', sa.Float, default=1.0),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False),
    )
    
    # ==================== COGNITION CONSISTENCY TABLES ====================
    
    # Semantic memories
    op.create_table(
        'semantic_cognition_memories',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('memory_id', sa.String(100), nullable=False, unique=True),
        sa.Column('memory_key', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('scope', sa.String(20), nullable=False, index=True),
        sa.Column('memory_type', sa.String(50), nullable=False),
        sa.Column('subject', sa.String(255), nullable=False, index=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('content', postgresql.JSON, nullable=False),
        sa.Column('importance', sa.Float, default=0.5, index=True),
        sa.Column('recency', sa.Float, default=1.0),
        sa.Column('stability', sa.Float, default=1.0),
        sa.Column('confidence', sa.Float, default=1.0),
        sa.Column('access_count', sa.Integer, default=0),
        sa.Column('last_accessed_at', sa.DateTime, nullable=True),
        sa.Column('is_pinned', sa.Boolean, default=False, index=True),
        sa.Column('is_verified', sa.Boolean, default=False),
        sa.Column('version', sa.Integer, default=1),
        sa.Column('created_at', sa.DateTime, nullable=False, index=True),
        sa.Column('updated_at', sa.DateTime, nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
    )
    
    # Cognition consistency states
    op.create_table(
        'cognition_consistency_states',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('state_id', sa.String(100), nullable=False, unique=True),
        sa.Column('scope', sa.String(20), nullable=False, index=True),
        sa.Column('domain', sa.String(50), nullable=False, index=True),
        sa.Column('consistency_state', sa.String(20), default='aligned', index=True),
        sa.Column('alignment_score', sa.Float, default=1.0),
        sa.Column('coherence_score', sa.Float, default=1.0),
        sa.Column('divergence_score', sa.Float, default=0.0),
        sa.Column('reconciliation_progress', sa.Float, nullable=True),
        sa.Column('deviation_sources', postgresql.JSON, nullable=True),
        sa.Column('reconciliation_attempts', postgresql.JSON, nullable=True),
        sa.Column('last_assessed_at', sa.DateTime, nullable=False, index=True),
        sa.Column('last_reconciled_at', sa.DateTime, nullable=True),
        sa.Column('stable_since', sa.DateTime, nullable=True),
    )
    
    # Shared reasoning standards
    op.create_table(
        'shared_reasoning_standards',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('reasoning_id', sa.String(100), nullable=False, unique=True),
        sa.Column('reasoning_key', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('reasoning_type', sa.String(20), nullable=False, index=True),
        sa.Column('scope', sa.String(20), nullable=False, index=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('inference_rules', postgresql.JSON, nullable=False),
        sa.Column('validation_rules', postgresql.JSON, nullable=True),
        sa.Column('constraint_rules', postgresql.JSON, nullable=True),
        sa.Column('confidence_threshold', sa.Float, default=0.8),
        sa.Column('reasoning_depth_limit', sa.Integer, default=10),
        sa.Column('is_active', sa.Boolean, default=True, index=True),
        sa.Column('version', sa.Integer, default=1),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=True),
    )
    
    # Cognition graph edges
    op.create_table(
        'cognition_graph_edges',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('edge_id', sa.String(100), nullable=False, unique=True),
        sa.Column('source_node_id', sa.String(100), nullable=False, index=True),
        sa.Column('source_type', sa.String(50), nullable=False),
        sa.Column('target_node_id', sa.String(100), nullable=False, index=True),
        sa.Column('target_type', sa.String(50), nullable=False),
        sa.Column('edge_type', sa.String(50), nullable=False, index=True),
        sa.Column('weight', sa.Float, default=1.0),
        sa.Column('confidence', sa.Float, default=1.0),
        sa.Column('relation_key', sa.String(255), nullable=True),
        sa.Column('context', postgresql.JSON, nullable=True),
        sa.Column('is_active', sa.Boolean, default=True, index=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
    )
    
    # Distributed semantic memories
    op.create_table(
        'distributed_semantic_memories',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('memory_id', sa.String(100), nullable=False, unique=True),
        sa.Column('memory_key', sa.String(255), nullable=False, index=True),
        sa.Column('owner_node', sa.String(100), nullable=False, index=True),
        sa.Column('scope', sa.String(20), nullable=False, index=True),
        sa.Column('knowledge', postgresql.JSON, nullable=False),
        sa.Column('metadata', postgresql.JSON, nullable=True),
        sa.Column('replicas', postgresql.JSON, nullable=True),
        sa.Column('sync_strategy', sa.String(20), default='eager'),
        sa.Column('consistency_version', sa.Integer, default=1),
        sa.Column('last_synced_at', sa.DateTime, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=True),
    )
    
    # Adaptive cognition profiles
    op.create_table(
        'adaptive_cognition_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('profile_id', sa.String(100), nullable=False, unique=True),
        sa.Column('profile_key', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('target_entity_type', sa.String(50), nullable=False, index=True),
        sa.Column('target_entity_id', sa.String(100), nullable=False, index=True),
        sa.Column('reasoning_patterns', postgresql.JSON, nullable=False),
        sa.Column('inference_effectiveness', postgresql.JSON, nullable=True),
        sa.Column('confidence_weights', postgresql.JSON, nullable=True),
        sa.Column('hit_rate', sa.Float, default=0.0),
        sa.Column('adaptation_rate', sa.Float, default=0.1),
        sa.Column('last_adapted_at', sa.DateTime, nullable=True),
        sa.Column('is_active', sa.Boolean, default=True, index=True),
        sa.Column('version', sa.Integer, default=1),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=True),
    )
    
    # Cognition audits
    op.create_table(
        'cognition_audits',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('audit_id', sa.String(100), nullable=False, unique=True),
        sa.Column('operation_type', sa.String(50), nullable=False, index=True),
        sa.Column('scope', sa.String(20), nullable=False, index=True),
        sa.Column('target_type', sa.String(50), nullable=False, index=True),
        sa.Column('target_id', sa.String(100), nullable=False, index=True),
        sa.Column('operation_details', postgresql.JSON, nullable=False),
        sa.Column('result', sa.String(50), nullable=True),
        sa.Column('error', sa.Text, nullable=True),
        sa.Column('alignment_impact', sa.Float, nullable=True),
        sa.Column('consistency_impact', sa.Float, nullable=True),
        sa.Column('performed_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('performed_at', sa.DateTime, nullable=False, index=True),
        sa.Column('correlation_id', sa.String(100), nullable=True, index=True),
    )
    
    # ==================== SEMANTIC RECOVERY TABLES ====================
    
    # Semantic conflicts
    op.create_table(
        'semantic_conflicts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('conflict_id', sa.String(100), nullable=False, unique=True),
        sa.Column('conflict_type', sa.String(50), nullable=False, index=True),
        sa.Column('severity', sa.String(20), default='warning', index=True),
        sa.Column('entity_type', sa.String(50), nullable=False, index=True),
        sa.Column('entity_id', sa.String(100), nullable=False, index=True),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('conflicting_values', postgresql.JSON, nullable=False),
        sa.Column('divergence_score', sa.Float, default=0.0),
        sa.Column('context', postgresql.JSON, nullable=True),
        sa.Column('affected_nodes', postgresql.JSON, nullable=True),
        sa.Column('resolution_strategy', sa.String(50), nullable=True),
        sa.Column('resolved_value', postgresql.JSON, nullable=True),
        sa.Column('state', sa.String(20), default='idle', index=True),
        sa.Column('is_resolved', sa.Boolean, default=False, index=True),
        sa.Column('detected_at', sa.DateTime, nullable=False, index=True),
        sa.Column('resolved_at', sa.DateTime, nullable=True),
        sa.Column('duration_ms', sa.Float, nullable=True),
    )
    
    # Reconciliation sessions
    op.create_table(
        'reconciliation_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('session_id', sa.String(100), nullable=False, unique=True),
        sa.Column('conflict_type', sa.String(50), nullable=False, index=True),
        sa.Column('strategy', sa.String(50), nullable=False, index=True),
        sa.Column('target_entity_type', sa.String(50), nullable=False),
        sa.Column('target_entity_id', sa.String(100), nullable=False, index=True),
        sa.Column('involved_entities', postgresql.JSON, nullable=False),
        sa.Column('conflicting_states', postgresql.JSON, nullable=False),
        sa.Column('resolved_state', postgresql.JSON, nullable=True),
        sa.Column('resolution_confidence', sa.Float, default=1.0),
        sa.Column('state', sa.String(20), default='idle', index=True),
        sa.Column('state_history', postgresql.JSON, nullable=True),
        sa.Column('started_at', sa.DateTime, nullable=False),
        sa.Column('completed_at', sa.DateTime, nullable=True),
        sa.Column('initiated_by', postgresql.UUID(as_uuid=True), nullable=True),
    )
    
    # Semantic recovery actions
    op.create_table(
        'semantic_recovery_actions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('action_id', sa.String(100), nullable=False, unique=True),
        sa.Column('conflict_id', sa.String(100), nullable=True, index=True),
        sa.Column('session_id', sa.String(100), nullable=True, index=True),
        sa.Column('action_type', sa.String(50), nullable=False, index=True),
        sa.Column('action_description', sa.Text, nullable=True),
        sa.Column('target_entity_type', sa.String(50), nullable=False),
        sa.Column('target_entity_id', sa.String(100), nullable=False, index=True),
        sa.Column('action_config', postgresql.JSON, nullable=True),
        sa.Column('state', sa.String(20), default='idle', index=True),
        sa.Column('attempts', sa.Integer, default=0),
        sa.Column('max_attempts', sa.Integer, default=3),
        sa.Column('success', sa.Boolean, default=False),
        sa.Column('result', postgresql.JSON, nullable=True),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('started_at', sa.DateTime, nullable=True),
        sa.Column('completed_at', sa.DateTime, nullable=True),
        sa.Column('duration_ms', sa.Float, nullable=True),
    )
    
    # Semantic stabilization loops
    op.create_table(
        'semantic_stabilization_loops',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('loop_id', sa.String(100), nullable=False, unique=True),
        sa.Column('loop_type', sa.String(50), nullable=False, index=True),
        sa.Column('target_entity_type', sa.String(50), nullable=False, index=True),
        sa.Column('target_entity_id', sa.String(100), nullable=False, index=True),
        sa.Column('mode', sa.String(20), default='active'),
        sa.Column('interval_seconds', sa.Integer, default=60),
        sa.Column('target_metric', sa.String(50), nullable=False),
        sa.Column('target_threshold', sa.Float, default=0.9),
        sa.Column('current_value', sa.Float, default=0.0),
        sa.Column('state', sa.String(20), default='running', index=True),
        sa.Column('iteration_count', sa.Integer, default=0),
        sa.Column('max_iterations', sa.Integer, default=10),
        sa.Column('iteration_history', postgresql.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('last_iteration', sa.DateTime, nullable=True),
        sa.Column('completed_at', sa.DateTime, nullable=True),
    )
    
    # Predictive semantic recovery
    op.create_table(
        'predictive_semantic_recovery',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('prediction_id', sa.String(100), nullable=False, unique=True),
        sa.Column('prediction_type', sa.String(50), nullable=False, index=True),
        sa.Column('target_entity_type', sa.String(50), nullable=False),
        sa.Column('target_entity_id', sa.String(100), nullable=False, index=True),
        sa.Column('predicted_issue', sa.String(255), nullable=False),
        sa.Column('probability', sa.Float, default=0.0),
        sa.Column('severity', sa.String(20), default='warning'),
        sa.Column('predicted_time', sa.DateTime, nullable=True),
        sa.Column('time_horizon_minutes', sa.Integer, default=60),
        sa.Column('evidence', postgresql.JSON, nullable=True),
        sa.Column('confidence', sa.Float, default=0.5),
        sa.Column('recommended_actions', postgresql.JSON, nullable=True),
        sa.Column('is_acted_upon', sa.Boolean, default=False, index=True),
        sa.Column('actual_occurred', sa.Boolean, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, index=True),
        sa.Column('validated_at', sa.DateTime, nullable=True),
    )
    
    # Semantic consistency checkpoints
    op.create_table(
        'semantic_consistency_checkpoints',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('checkpoint_id', sa.String(100), nullable=False, unique=True),
        sa.Column('target_entity_type', sa.String(50), nullable=False, index=True),
        sa.Column('target_entity_id', sa.String(100), nullable=False, index=True),
        sa.Column('semantic_state', postgresql.JSON, nullable=False),
        sa.Column('interpretation_snapshot', postgresql.JSON, nullable=True),
        sa.Column('consistency_score', sa.Float, default=1.0),
        sa.Column('validation_rules_passed', postgresql.JSON, nullable=True),
        sa.Column('validation_rules_failed', postgresql.JSON, nullable=True),
        sa.Column('checkpoint_type', sa.String(50), nullable=False),
        sa.Column('reason', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, index=True),
    )
    
    # Semantic recovery policies
    op.create_table(
        'semantic_recovery_policies',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('policy_id', sa.String(100), nullable=False, unique=True),
        sa.Column('policy_key', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('conflict_type', sa.String(50), nullable=False, index=True),
        sa.Column('target_entity_type', sa.String(50), nullable=True),
        sa.Column('trigger_conditions', postgresql.JSON, nullable=False),
        sa.Column('actions', postgresql.JSON, nullable=False),
        sa.Column('action_order', postgresql.JSON, nullable=True),
        sa.Column('enabled', sa.Boolean, default=True),
        sa.Column('priority', sa.Integer, default=5),
        sa.Column('auto_recover', sa.Boolean, default=True),
        sa.Column('trigger_count', sa.Integer, default=0),
        sa.Column('success_count', sa.Integer, default=0),
        sa.Column('failure_count', sa.Integer, default=0),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
    )
    
    # Semantic violations
    op.create_table(
        'semantic_violations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('violation_id', sa.String(100), nullable=False, unique=True),
        sa.Column('violation_type', sa.String(50), nullable=False, index=True),
        sa.Column('severity', sa.String(20), default='warning'),
        sa.Column('target_entity_type', sa.String(50), nullable=False, index=True),
        sa.Column('target_entity_id', sa.String(100), nullable=False, index=True),
        sa.Column('rule_violated', sa.String(255), nullable=False),
        sa.Column('expected_value', postgresql.JSON, nullable=True),
        sa.Column('actual_value', postgresql.JSON, nullable=True),
        sa.Column('deviation', sa.Float, nullable=True),
        sa.Column('context', postgresql.JSON, nullable=True),
        sa.Column('is_resolved', sa.Boolean, default=False, index=True),
        sa.Column('resolution_action', sa.String(255), nullable=True),
        sa.Column('detected_at', sa.DateTime, nullable=False, index=True),
        sa.Column('resolved_at', sa.DateTime, nullable=True),
        sa.Column('auto_resolved', sa.Boolean, default=False),
    )


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('semantic_violations')
    op.drop_table('semantic_recovery_policies')
    op.drop_table('semantic_consistency_checkpoints')
    op.drop_table('predictive_semantic_recovery')
    op.drop_table('semantic_stabilization_loops')
    op.drop_table('semantic_recovery_actions')
    op.drop_table('reconciliation_sessions')
    op.drop_table('semantic_conflicts')
    op.drop_table('cognition_audits')
    op.drop_table('adaptive_cognition_profiles')
    op.drop_table('distributed_semantic_memories')
    op.drop_table('cognition_graph_edges')
    op.drop_table('shared_reasoning_standards')
    op.drop_table('cognition_consistency_states')
    op.drop_table('semantic_cognition_memories')
    op.drop_table('execution_semantics')
    op.drop_table('contract_versions')
    op.drop_table('meaning_synchronizations')
    op.drop_table('context_inheritances')
    op.drop_table('propagated_semantics')
    op.drop_table('semantic_interpretations')
    op.drop_table('contract_exec_bindings')
    op.drop_table('contract_definitions')
    op.drop_table('execution_interpretations')
    op.drop_table('meaning_registry')
    op.drop_table('semantic_lineage')
    op.drop_table('distributed_propagations')
    op.drop_table('ontology_versions')
    op.drop_table('contract_bindings')
    op.drop_table('semantic_contracts')
    op.drop_table('concept_relationships')
    op.drop_table('runtime_concepts')
