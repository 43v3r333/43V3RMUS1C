"""
Cognitive Kernel Database Schema Migration

This migration creates the cognitive kernel tables for 43V3R CORE:
- Orchestration Memories (persistent orchestration cognition)
- Strategic Execution Plans (predictive orchestration planning)
- Creative Reasoning Profiles (cinematic creative cognition)
- Agent Governance Sessions (multi-agent civilization governance)
- Agent Decisions (distributed negotiation tracking)
- Runtime Evolution Metrics (adaptive runtime evolution)
- Adaptive Optimization Cycles (autonomous optimization)
- Orchestration Forecasts (predictive runtime intelligence)
- Semantic Context Archives (knowledge expansion)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Revision identifiers
revision: str = '002_cognitive_kernel'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ========== ORCHESTRATION MEMORIES ==========
    
    op.create_table(
        'orchestration_memories',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('scope', sa.String(20), nullable=False),
        sa.Column('memory_kind', sa.String(40), nullable=False),
        sa.Column('subject', sa.String(255), nullable=True),
        sa.Column('subject_kind', sa.String(50), nullable=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('content', postgresql.JSON(), nullable=False),
        sa.Column('importance', sa.Float(), nullable=False, default=0.5),
        sa.Column('recency', sa.Float(), nullable=False, default=1.0),
        sa.Column('confidence', sa.Float(), nullable=False, default=0.8),
        sa.Column('access_count', sa.Integer(), nullable=False, default=0),
        sa.Column('last_accessed_at', sa.DateTime(), nullable=True),
        sa.Column('is_pinned', sa.Boolean(), nullable=False, default=False),
        sa.Column('tags', postgresql.JSON(), nullable=True),
        sa.Column('related_memory_ids', postgresql.JSON(), nullable=True),
        sa.Column('parent_memory_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('execution_context', postgresql.JSON(), nullable=True),
        sa.Column('outcome', postgresql.JSON(), nullable=True),
    )
    op.create_index('ix_orchestration_memories_scope', 'orchestration_memories', ['scope'])
    op.create_index('ix_orchestration_memories_memory_kind', 'orchestration_memories', ['memory_kind'])
    op.create_index('ix_orchestration_memories_subject', 'orchestration_memories', ['subject'])
    op.create_index('ix_memory_subject_scope', 'orchestration_memories', ['subject', 'scope'])
    op.create_index('ix_memory_kind_importance', 'orchestration_memories', ['memory_kind', 'importance'])
    op.create_index('ix_memory_recency_importance', 'orchestration_memories', ['recency', 'importance'])
    op.create_index('ix_orchestration_memories_deleted_at', 'orchestration_memories', ['deleted_at'])
    
    # Self-referential FK for parent_memory_id
    op.create_foreign_key(
        'fk_orchestration_memories_parent',
        'orchestration_memories', 'orchestration_memories',
        ['parent_memory_id'], ['id'], ondelete='SET NULL'
    )
    
    # ========== STRATEGIC EXECUTION PLANS ==========
    
    op.create_table(
        'strategic_execution_plans',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('plan_type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, default='draft'),
        sa.Column('horizon', sa.String(20), nullable=False),
        sa.Column('planning_depth', sa.Integer(), nullable=False, default=3),
        sa.Column('strategy_kind', sa.String(40), nullable=False),
        sa.Column('objectives', postgresql.JSON(), nullable=False),
        sa.Column('expected_outcomes', postgresql.JSON(), nullable=True),
        sa.Column('actual_outcomes', postgresql.JSON(), nullable=True),
        sa.Column('dependencies', postgresql.JSON(), nullable=True),
        sa.Column('constraints', postgresql.JSON(), nullable=True),
        sa.Column('risks', postgresql.JSON(), nullable=True),
        sa.Column('required_resources', postgresql.JSON(), nullable=True),
        sa.Column('allocated_resources', postgresql.JSON(), nullable=True),
        sa.Column('estimated_start', sa.DateTime(), nullable=True),
        sa.Column('estimated_end', sa.DateTime(), nullable=True),
        sa.Column('actual_start', sa.DateTime(), nullable=True),
        sa.Column('actual_end', sa.DateTime(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=False, default=0.5),
        sa.Column('priority', sa.Integer(), nullable=False, default=5),
        sa.Column('estimated_impact', sa.Float(), nullable=False, default=0.0),
        sa.Column('parent_plan_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('related_workflow_ids', postgresql.JSON(), nullable=True),
    )
    op.create_index('ix_strategic_execution_plans_status', 'strategic_execution_plans', ['status'])
    op.create_index('ix_strategic_execution_plans_plan_type', 'strategic_execution_plans', ['plan_type'])
    op.create_index('ix_strategic_execution_plans_horizon', 'strategic_execution_plans', ['horizon'])
    op.create_index('ix_strategic_execution_plans_strategy_kind', 'strategic_execution_plans', ['strategy_kind'])
    op.create_index('ix_plan_status_horizon', 'strategic_execution_plans', ['status', 'horizon'])
    op.create_index('ix_plan_strategy_priority', 'strategic_execution_plans', ['strategy_kind', 'priority'])
    op.create_index('ix_plan_confidence', 'strategic_execution_plans', ['confidence_score'])
    op.create_index('ix_strategic_execution_plans_deleted_at', 'strategic_execution_plans', ['deleted_at'])
    
    # Self-referential FK for parent_plan_id
    op.create_foreign_key(
        'fk_strategic_plans_parent',
        'strategic_execution_plans', 'strategic_execution_plans',
        ['parent_plan_id'], ['id'], ondelete='SET NULL'
    )
    
    # ========== CREATIVE REASONING PROFILES ==========
    
    op.create_table(
        'creative_reasoning_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('profile_type', sa.String(50), nullable=False),
        sa.Column('campaign_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('narrative_structure', sa.String(50), nullable=True),
        sa.Column('emotional_arc', sa.String(50), nullable=True),
        sa.Column('pacing_profile', sa.String(50), nullable=True),
        sa.Column('pacing_intensity', sa.Float(), nullable=False, default=0.5),
        sa.Column('visual_keywords', postgresql.JSON(), nullable=True),
        sa.Column('color_palette', postgresql.JSON(), nullable=True),
        sa.Column('visual_style', sa.String(100), nullable=True),
        sa.Column('audio_keywords', postgresql.JSON(), nullable=True),
        sa.Column('music_mood', sa.String(100), nullable=True),
        sa.Column('sound_design', sa.String(100), nullable=True),
        sa.Column('target_segments', postgresql.JSON(), nullable=True),
        sa.Column('attention_span_seconds', sa.Integer(), nullable=False, default=60),
        sa.Column('completion_rate_target', sa.Float(), nullable=False, default=0.7),
        sa.Column('engagement_rate_target', sa.Float(), nullable=False, default=0.15),
        sa.Column('retention_target', sa.Float(), nullable=False, default=0.5),
        sa.Column('max_duration', sa.Integer(), nullable=True),
        sa.Column('min_duration', sa.Integer(), nullable=True),
        sa.Column('content_guidelines', postgresql.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('version', sa.Integer(), nullable=False, default=1),
        sa.Column('scene_templates', postgresql.JSON(), nullable=True),
        sa.Column('transition_rules', postgresql.JSON(), nullable=True),
    )
    op.create_index('ix_creative_reasoning_profiles_profile_type', 'creative_reasoning_profiles', ['profile_type'])
    op.create_index('ix_creative_campaign_active', 'creative_reasoning_profiles', ['campaign_id', 'is_active'])
    op.create_index('ix_creative_profile_type', 'creative_reasoning_profiles', ['profile_type', 'version'])
    op.create_index('ix_creative_reasoning_profiles_deleted_at', 'creative_reasoning_profiles', ['deleted_at'])
    
    # FK to campaigns
    op.create_foreign_key(
        'fk_creative_profiles_campaign',
        'creative_reasoning_profiles', 'campaigns',
        ['campaign_id'], ['id'], ondelete='SET NULL'
    )
    
    # ========== AGENT GOVERNANCE SESSIONS ==========
    
    op.create_table(
        'agent_governance_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('session_type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, default='active'),
        sa.Column('coordinator_id', sa.String(255), nullable=True),
        sa.Column('participant_ids', postgresql.JSON(), nullable=True),
        sa.Column('authority_level', sa.String(20), nullable=False, default='orchestrator'),
        sa.Column('decision_authority', postgresql.JSON(), nullable=True),
        sa.Column('scope_kind', sa.String(50), nullable=True),
        sa.Column('scope_id', sa.String(255), nullable=True),
        sa.Column('actions_taken', postgresql.JSON(), nullable=True),
        sa.Column('decisions_made', postgresql.JSON(), nullable=True),
        sa.Column('negotiation_rounds', sa.Integer(), nullable=False, default=0),
        sa.Column('consensus_reached', sa.Boolean(), nullable=False, default=False),
        sa.Column('disagreements', postgresql.JSON(), nullable=True),
        sa.Column('resolution', postgresql.JSON(), nullable=True),
        sa.Column('execution_plan', postgresql.JSON(), nullable=True),
        sa.Column('session_start', sa.DateTime(), nullable=True),
        sa.Column('session_end', sa.DateTime(), nullable=True),
        sa.Column('expected_duration', sa.Integer(), nullable=True),
        sa.Column('efficiency_score', sa.Float(), nullable=False, default=0.0),
        sa.Column('consensus_time', sa.Integer(), nullable=True),
        sa.Column('parent_session_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('related_workflow_ids', postgresql.JSON(), nullable=True),
    )
    op.create_index('ix_agent_governance_sessions_session_type', 'agent_governance_sessions', ['session_type'])
    op.create_index('ix_agent_governance_sessions_status', 'agent_governance_sessions', ['status'])
    op.create_index('ix_governance_status_coordinator', 'agent_governance_sessions', ['status', 'coordinator_id'])
    op.create_index('ix_governance_scope', 'agent_governance_sessions', ['scope_kind', 'scope_id'])
    op.create_index('ix_agent_governance_sessions_deleted_at', 'agent_governance_sessions', ['deleted_at'])
    
    # Self-referential FK for parent_session_id
    op.create_foreign_key(
        'fk_governance_sessions_parent',
        'agent_governance_sessions', 'agent_governance_sessions',
        ['parent_session_id'], ['id'], ondelete='SET NULL'
    )
    
    # ========== AGENT DECISIONS ==========
    
    op.create_table(
        'agent_decisions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('decision_type', sa.String(50), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False, default=0.8),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('agent_id', sa.String(255), nullable=False),
        sa.Column('agent_role', sa.String(20), nullable=False),
        sa.Column('context', postgresql.JSON(), nullable=False),
        sa.Column('rationale', sa.Text(), nullable=True),
        sa.Column('alternatives_considered', postgresql.JSON(), nullable=True),
        sa.Column('outcome', postgresql.JSON(), nullable=True),
        sa.Column('impact_score', sa.Float(), nullable=False, default=0.0),
        sa.Column('decision_time', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('execution_time', sa.Integer(), nullable=True),
        sa.Column('is_validated', sa.Boolean(), nullable=False, default=False),
        sa.Column('validation_notes', sa.Text(), nullable=True),
        sa.Column('related_decision_ids', postgresql.JSON(), nullable=True),
    )
    op.create_index('ix_agent_decisions_decision_type', 'agent_decisions', ['decision_type'])
    op.create_index('ix_agent_decisions_agent_id', 'agent_decisions', ['agent_id'])
    op.create_index('ix_agent_decisions_agent_role', 'agent_decisions', ['agent_role'])
    op.create_index('ix_agent_decisions_session_id', 'agent_decisions', ['session_id'])
    op.create_index('ix_agent_decisions_deleted_at', 'agent_decisions', ['deleted_at'])
    
    # FK to governance sessions
    op.create_foreign_key(
        'fk_agent_decisions_session',
        'agent_decisions', 'agent_governance_sessions',
        ['session_id'], ['id'], ondelete='SET NULL'
    )
    
    # ========== RUNTIME EVOLUTION METRICS ==========
    
    op.create_table(
        'runtime_evolution_metrics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('metric_type', sa.String(50), nullable=False),
        sa.Column('metric_name', sa.String(100), nullable=False),
        sa.Column('subject_kind', sa.String(50), nullable=True),
        sa.Column('subject_id', sa.String(255), nullable=True),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('previous_value', sa.Float(), nullable=True),
        sa.Column('baseline_value', sa.Float(), nullable=True),
        sa.Column('delta', sa.Float(), nullable=True),
        sa.Column('delta_percentage', sa.Float(), nullable=True),
        sa.Column('change_direction', sa.String(10), nullable=True),
        sa.Column('context', postgresql.JSON(), nullable=True),
        sa.Column('tags', postgresql.JSON(), nullable=True),
        sa.Column('recorded_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('period_start', sa.DateTime(), nullable=True),
        sa.Column('period_end', sa.DateTime(), nullable=True),
        sa.Column('aggregation_level', sa.String(20), nullable=False, default='point'),
        sa.Column('sample_count', sa.Integer(), nullable=False, default=1),
        sa.Column('linked_metric_ids', postgresql.JSON(), nullable=True),
    )
    op.create_index('ix_runtime_evolution_metrics_metric_type', 'runtime_evolution_metrics', ['metric_type'])
    op.create_index('ix_runtime_evolution_metrics_metric_name', 'runtime_evolution_metrics', ['metric_name'])
    op.create_index('ix_runtime_evolution_metrics_subject_id', 'runtime_evolution_metrics', ['subject_id'])
    op.create_index('ix_metric_subject_time', 'runtime_evolution_metrics', ['subject_kind', 'subject_id', 'recorded_at'])
    op.create_index('ix_metric_type_recorded', 'runtime_evolution_metrics', ['metric_type', 'recorded_at'])
    op.create_index('ix_runtime_evolution_metrics_recorded_at', 'runtime_evolution_metrics', ['recorded_at'])
    op.create_index('ix_runtime_evolution_metrics_deleted_at', 'runtime_evolution_metrics', ['deleted_at'])
    
    # ========== ADAPTIVE OPTIMIZATION CYCLES ==========
    
    op.create_table(
        'adaptive_optimization_cycles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('cycle_id', sa.String(50), nullable=False, unique=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('cycle_state', sa.String(20), nullable=False, default='pending'),
        sa.Column('context_key', sa.String(100), nullable=False),
        sa.Column('context_data', postgresql.JSON(), nullable=True),
        sa.Column('target_metric', sa.String(100), nullable=False),
        sa.Column('target_improvement', sa.Float(), nullable=False, default=0.1),
        sa.Column('parameter_space', postgresql.JSON(), nullable=False),
        sa.Column('current_parameters', postgresql.JSON(), nullable=True),
        sa.Column('best_parameters', postgresql.JSON(), nullable=True),
        sa.Column('max_iterations', sa.Integer(), nullable=False, default=10),
        sa.Column('iteration', sa.Integer(), nullable=False, default=0),
        sa.Column('patience', sa.Integer(), nullable=False, default=3),
        sa.Column('current_score', sa.Float(), nullable=True),
        sa.Column('best_score', sa.Float(), nullable=True),
        sa.Column('baseline_score', sa.Float(), nullable=True),
        sa.Column('convergence_threshold', sa.Float(), nullable=False, default=0.01),
        sa.Column('exploration_history', postgresql.JSON(), nullable=True),
        sa.Column('exploitation_history', postgresql.JSON(), nullable=True),
        sa.Column('improvements_found', postgresql.JSON(), nullable=True),
        sa.Column('failed_attempts', postgresql.JSON(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('estimated_duration', sa.Integer(), nullable=True),
        sa.Column('resources_consumed', postgresql.JSON(), nullable=True),
        sa.Column('linked_plan_id', postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index('ix_adaptive_optimization_cycles_cycle_id', 'adaptive_optimization_cycles', ['cycle_id'])
    op.create_index('ix_adaptive_optimization_cycles_cycle_state', 'adaptive_optimization_cycles', ['cycle_state'])
    op.create_index('ix_adaptive_optimization_cycles_context_key', 'adaptive_optimization_cycles', ['context_key'])
    op.create_index('ix_cycle_state_context', 'adaptive_optimization_cycles', ['cycle_state', 'context_key'])
    op.create_index('ix_cycle_iteration', 'adaptive_optimization_cycles', ['iteration', 'max_iterations'])
    op.create_index('ix_adaptive_optimization_cycles_deleted_at', 'adaptive_optimization_cycles', ['deleted_at'])
    
    # FK to strategic plans
    op.create_foreign_key(
        'fk_optimization_cycles_plan',
        'adaptive_optimization_cycles', 'strategic_execution_plans',
        ['linked_plan_id'], ['id'], ondelete='SET NULL'
    )
    
    # ========== ORCHESTRATION FORECASTS ==========
    
    op.create_table(
        'orchestration_forecasts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('forecast_kind', sa.String(50), nullable=False),
        sa.Column('subject_kind', sa.String(50), nullable=False),
        sa.Column('subject_key', sa.String(255), nullable=False),
        sa.Column('horizon', sa.String(20), nullable=False),
        sa.Column('predicted_for', sa.DateTime(), nullable=False),
        sa.Column('predicted_value', sa.Float(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False, default=0.5),
        sa.Column('lower_bound', sa.Float(), nullable=True),
        sa.Column('upper_bound', sa.Float(), nullable=True),
        sa.Column('prediction_method', sa.String(50), nullable=True),
        sa.Column('model_version', sa.String(50), nullable=True),
        sa.Column('training_data_size', sa.Integer(), nullable=True),
        sa.Column('features_used', postgresql.JSON(), nullable=True),
        sa.Column('context_data', postgresql.JSON(), nullable=True),
        sa.Column('actual_value', sa.Float(), nullable=True),
        sa.Column('prediction_error', sa.Float(), nullable=True),
        sa.Column('validated_at', sa.DateTime(), nullable=True),
        sa.Column('lifecycle_state', sa.String(20), nullable=False, default='pending'),
        sa.Column('related_plan_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('related_memory_ids', postgresql.JSON(), nullable=True),
    )
    op.create_index('ix_orchestration_forecasts_forecast_kind', 'orchestration_forecasts', ['forecast_kind'])
    op.create_index('ix_orchestration_forecasts_horizon', 'orchestration_forecasts', ['horizon'])
    op.create_index('ix_orchestration_forecasts_subject_key', 'orchestration_forecasts', ['subject_key'])
    op.create_index('ix_forecast_subject_horizon', 'orchestration_forecasts', ['subject_kind', 'subject_key', 'horizon'])
    op.create_index('ix_forecast_validated', 'orchestration_forecasts', ['lifecycle_state', 'validated_at'])
    op.create_index('ix_forecast_confidence', 'orchestration_forecasts', ['confidence', 'horizon'])
    op.create_index('ix_orchestration_forecasts_predicted_for', 'orchestration_forecasts', ['predicted_for'])
    op.create_index('ix_orchestration_forecasts_deleted_at', 'orchestration_forecasts', ['deleted_at'])
    
    # FK to strategic plans
    op.create_foreign_key(
        'fk_orchestration_forecasts_plan',
        'orchestration_forecasts', 'strategic_execution_plans',
        ['related_plan_id'], ['id'], ondelete='SET NULL'
    )
    
    # ========== SEMANTIC CONTEXT ARCHIVES ==========
    
    op.create_table(
        'semantic_context_archives',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('archive_type', sa.String(50), nullable=False),
        sa.Column('domain', sa.String(100), nullable=True),
        sa.Column('schema_version', sa.String(20), nullable=True),
        sa.Column('entities', postgresql.JSON(), nullable=True),
        sa.Column('relationships', postgresql.JSON(), nullable=True),
        sa.Column('attributes', postgresql.JSON(), nullable=True),
        sa.Column('embeddings', postgresql.JSON(), nullable=True),
        sa.Column('semantic_tags', postgresql.JSON(), nullable=True),
        sa.Column('source_type', sa.String(50), nullable=True),
        sa.Column('source_id', sa.String(255), nullable=True),
        sa.Column('created_by', sa.String(255), nullable=True),
        sa.Column('archive_state', sa.String(20), nullable=False, default='active'),
        sa.Column('use_count', sa.Integer(), nullable=False, default=0),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.Column('completeness', sa.Float(), nullable=False, default=0.5),
        sa.Column('accuracy', sa.Float(), nullable=False, default=0.8),
        sa.Column('relevance', sa.Float(), nullable=False, default=0.7),
        sa.Column('parent_archive_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('linked_workflow_ids', postgresql.JSON(), nullable=True),
    )
    op.create_index('ix_semantic_context_archives_archive_type', 'semantic_context_archives', ['archive_type'])
    op.create_index('ix_semantic_context_archives_domain', 'semantic_context_archives', ['domain'])
    op.create_index('ix_semantic_context_archives_archive_state', 'semantic_context_archives', ['archive_state'])
    op.create_index('ix_archive_type_domain', 'semantic_context_archives', ['archive_type', 'domain'])
    op.create_index('ix_archive_state_use', 'semantic_context_archives', ['archive_state', 'use_count'])
    op.create_index('ix_semantic_context_archives_deleted_at', 'semantic_context_archives', ['deleted_at'])
    
    # Self-referential FK for parent_archive_id
    op.create_foreign_key(
        'fk_semantic_archives_parent',
        'semantic_context_archives', 'semantic_context_archives',
        ['parent_archive_id'], ['id'], ondelete='SET NULL'
    )


def downgrade() -> None:
    # Drop tables in reverse order (due to foreign keys)
    op.drop_table('semantic_context_archives')
    op.drop_table('orchestration_forecasts')
    op.drop_table('adaptive_optimization_cycles')
    op.drop_table('runtime_evolution_metrics')
    op.drop_table('agent_decisions')
    op.drop_table('agent_governance_sessions')
    op.drop_table('creative_reasoning_profiles')
    op.drop_table('strategic_execution_plans')
    op.drop_table('orchestration_memories')