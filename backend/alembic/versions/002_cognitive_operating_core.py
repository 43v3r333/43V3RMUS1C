"""002_cognitive_operating_core - Knowledge graph, forecasting, creative, governance, feedback

Revision ID: 002_cognitive_operating_core
Revises: 001_initial
Create Date: 2024-01-15

Creates the full cognitive operating core tables:
  - kg_nodes / kg_edges                     : knowledge graph vertices and edges
  - semantic_relationships                 : curated semantic relationships
  - orchestration_memory                    : scoped, ranked memory items
  - execution_graph_snapshots               : materialized graph views
  - execution_forecasts                     : execution outcome predictions
  - predictive_runtime_metrics              : rolling metric forecasts
  - multi_stage_execution_graphs            : planned execution DAGs
  - orchestration_strategies                : selected strategy history
  - creative_profiles                       : campaign/artist creative briefs
  - narrative_sequences                     : scene/story arc plans
  - emotion_mappings                        : audio mood -> visual style bridges
  - pacing_heuristics                       : tempo/energy curves
  - audience_engagement_heuristics          : retention signal predictions
  - agent_governance_rules                  : configurable per-agent rules
  - authority_hierarchies                    : static authority chains
  - arbitration_policies                    : conflict resolution policies
  - conflict_resolutions                    : recorded conflict outcomes
  - agent_policy_violations                 : runtime policy violation log
  - orchestration_feedback                  : runtime feedback signals
  - adaptive_learning_states                : learned parameter state
  - autonomous_tuning_records               : parameter adjustments
  - tuning_cycles                           : grouped tuning batches
  - optimization_histories                  : tracked optimization runs
  - execution_patterns                      : learned execution patterns
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '002_cognitive_operating_core'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # =====================================================================
    # Enums
    # =====================================================================
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE knowledgenodekind AS ENUM (
                'workflow', 'execution', 'execution_step', 'render_job',
                'media_asset', 'agent', 'prompt', 'model',
                'composition', 'scene', 'policy', 'heuristic',
                'insight', 'decision', 'observation'
            );
        EXCEPTION WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE knowledgeedgekind AS ENUM (
                'depends_on', 'produces', 'consumes', 'derived_from',
                'similar_to', 'precedes', 'succeeds', 'triggers',
                'governs', 'optimizes', 'explains', 'conflicts_with'
            );
        EXCEPTION WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE memoriescope AS ENUM ('episodic', 'semantic', 'procedural', 'evaluative', 'strategic');
        EXCEPTION WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE forecastkind AS ENUM (
                'duration', 'queue_time', 'failure_probability',
                'resource_need', 'throughput', 'saturation', 'cost', 'quality'
            );
        EXCEPTION WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE forecasthorizon AS ENUM ('immediate', 'near_term', 'short', 'long', 'extended');
        EXCEPTION WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE strategykind AS ENUM (
                'latency_first', 'throughput_first', 'cost_aware',
                'quality_first', 'balanced', 'conservative', 'aggressive_scale'
            );
        EXCEPTION WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE narrativestructure AS ENUM (
                'linear', 'branching', 'looping', 'hero_journey',
                'three_act', 'five_act', 'montage', 'mashup'
            );
        EXCEPTION WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE emotionalarc AS ENUM (
                'rags_to_riches', 'riches_to_rags', 'man_in_hole',
                'boy_meets_girl', 'cinderella', 'tragedy',
                'overcoming_the_monster', 'comedy', 'rebirth', 'quest', 'steady'
            );
        EXCEPTION WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE pacingprofile AS ENUM (
                'bruiser', 'rollercoaster', 'building', 'fragmented', 'minimalist', 'maximalist'
            );
        EXCEPTION WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE audiencesegment AS ENUM (
                'gen_z', 'millennial', 'gen_x', 'boomer',
                'music_superfan', 'casual_listener',
                'videocast_fan', 'tiktok_native', 'youtube_regular'
            );
        EXCEPTION WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE authoritylevel AS ENUM ('observer', 'executor', 'coordinator', 'supervisor', 'administrator', 'master');
        EXCEPTION WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE arbitrationstrategy AS ENUM (
                'priority', 'round_robin', 'first_commit',
                'weighted_vote', 'mediated', 'retry', 'merge'
            );
        EXCEPTION WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE feedbacktype AS ENUM (
                'duration', 'quality', 'cost', 'throughput',
                'error_rate', 'satisfaction', 'resource_efficiency', 'custom'
            );
        EXCEPTION WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE tuningaction AS ENUM (
                'scale_up', 'scale_down', 'retry_strategy', 'resource_rebalance',
                'batch_size_adjust', 'cache_bypass', 'model_switch',
                'parameter_tune', 'policy_update', 'threshold_adjust'
            );
        EXCEPTION WHEN duplicate_object THEN null;
        END $$;
    """)

    # =====================================================================
    # Knowledge Graph
    # =====================================================================

    # kg_nodes
    op.create_table(
        'kg_nodes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('node_kind', sa.String(50), nullable=False, index=True),
        sa.Column('node_key', sa.String(255), nullable=False, index=True),
        sa.Column('label', sa.String(255), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('properties', postgresql.JSON(), nullable=False, server_default='{}'),
        sa.Column('tags', postgresql.JSON(), nullable=False, server_default='[]'),
        sa.Column('vector', postgresql.JSON(), nullable=True),
        sa.Column('vector_dim', sa.Integer(), nullable=True),
        sa.Column('relevance_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('centrality', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('lifecycle_state', sa.String(32), nullable=False, server_default='active', index=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('last_seen_at', sa.DateTime(), nullable=False),
        sa.Column('seen_count', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('source_domain', sa.String(64), nullable=True),
        sa.Column('correlation_id', sa.String(100), nullable=True, index=True),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index('ix_kg_nodes_kind_status', 'kg_nodes', ['node_kind', 'lifecycle_state'])
    op.create_index('ix_kg_nodes_relevance', 'kg_nodes', ['relevance_score'])
    op.create_index('uq_kg_nodes_kind_key', 'kg_nodes', ['node_kind', 'node_key'], unique=True)

    # kg_edges
    op.create_table(
        'kg_edges',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('source_node_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('kg_nodes.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('target_node_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('kg_nodes.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('edge_kind', sa.String(50), nullable=False, index=True),
        sa.Column('label', sa.String(255), nullable=True),
        sa.Column('weight', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('evidence_count', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('attributes', postgresql.JSON(), nullable=False, server_default='{}'),
        sa.Column('lifecycle_state', sa.String(32), nullable=False, server_default='active'),
        sa.Column('last_reinforced_at', sa.DateTime(), nullable=False),
        sa.Column('correlation_id', sa.String(100), nullable=True, index=True),
    )
    op.create_index('ix_kg_edges_kind_state', 'kg_edges', ['edge_kind', 'lifecycle_state'])
    op.create_index('ix_kg_edges_weight', 'kg_edges', ['weight'])
    op.create_index('uq_kg_edges_triplet', 'kg_edges', ['source_node_id', 'target_node_id', 'edge_kind'], unique=True)

    # semantic_relationships
    op.create_table(
        'semantic_relationships',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('subject_kind', sa.String(50), nullable=False),
        sa.Column('subject_key', sa.String(255), nullable=False),
        sa.Column('predicate', sa.String(80), nullable=False),
        sa.Column('object_kind', sa.String(50), nullable=False),
        sa.Column('object_key', sa.String(255), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('weight', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('evidence', postgresql.JSON(), nullable=False, server_default='{}'),
        sa.Column('derived_from', sa.String(100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true', index=True),
    )
    op.create_index('ix_sem_rel_subject', 'semantic_relationships', ['subject_kind', 'subject_key'])
    op.create_index('ix_sem_rel_object', 'semantic_relationships', ['object_kind', 'object_key'])
    op.create_index('ix_sem_rel_predicate', 'semantic_relationships', ['predicate'])

    # orchestration_memory
    op.create_table(
        'orchestration_memory',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('scope', sa.String(32), nullable=False, index=True),
        sa.Column('memory_kind', sa.String(64), nullable=False, index=True),
        sa.Column('subject', sa.String(255), nullable=False, index=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('content', postgresql.JSON(), nullable=False),
        sa.Column('importance', sa.Float(), nullable=False, server_default='0.5'),
        sa.Column('recency', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('access_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_accessed_at', sa.DateTime(), nullable=True),
        sa.Column('correlation_id', sa.String(100), nullable=True, index=True),
        sa.Column('workflow_id', sa.String(100), nullable=True, index=True),
        sa.Column('agent_id', sa.String(100), nullable=True, index=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('is_pinned', sa.Boolean(), nullable=False, server_default='false'),
    )
    op.create_index('ix_orch_memory_scope_kind', 'orchestration_memory', ['scope', 'memory_kind'])
    op.create_index('ix_orch_memory_importance', 'orchestration_memory', ['importance'])
    op.create_index('ix_orch_memory_correlation', 'orchestration_memory', ['correlation_id'])

    # execution_graph_snapshots
    op.create_table(
        'execution_graph_snapshots',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('root_kind', sa.String(50), nullable=False),
        sa.Column('root_key', sa.String(255), nullable=False),
        sa.Column('purpose', sa.String(100), nullable=False, index=True),
        sa.Column('depth', sa.Integer(), nullable=False, server_default='2'),
        sa.Column('nodes', postgresql.JSON(), nullable=False, server_default='[]'),
        sa.Column('edges', postgresql.JSON(), nullable=False, server_default='[]'),
        sa.Column('node_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('edge_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('critical_path', postgresql.JSON(), nullable=False, server_default='[]'),
        sa.Column('insights', postgresql.JSON(), nullable=False, server_default='[]'),
        sa.Column('correlation_id', sa.String(100), nullable=True, index=True),
    )
    op.create_index('ix_kg_snapshot_root', 'execution_graph_snapshots', ['root_kind', 'root_key'])

    # =====================================================================
    # Forecasting
    # =====================================================================

    # execution_forecasts
    op.create_table(
        'execution_forecasts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('subject_kind', sa.String(50), nullable=False),
        sa.Column('subject_key', sa.String(255), nullable=False),
        sa.Column('forecast_kind', sa.String(50), nullable=False, index=True),
        sa.Column('horizon', sa.String(32), nullable=False, index=True),
        sa.Column('predicted_value', sa.Float(), nullable=False),
        sa.Column('lower_bound', sa.Float(), nullable=True),
        sa.Column('upper_bound', sa.Float(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='0.5'),
        sa.Column('features', postgresql.JSON(), nullable=False, server_default='{}'),
        sa.Column('model_version', sa.String(50), nullable=True),
        sa.Column('method', sa.String(50), nullable=True),
        sa.Column('predicted_for', sa.DateTime(), nullable=False),
        sa.Column('generated_at', sa.DateTime(), nullable=False, index=True),
        sa.Column('actual_value', sa.Float(), nullable=True),
        sa.Column('realized_at', sa.DateTime(), nullable=True),
        sa.Column('error_pct', sa.Float(), nullable=True),
        sa.Column('lifecycle_state', sa.String(32), nullable=False, server_default='pending', index=True),
        sa.Column('correlation_id', sa.String(100), nullable=True, index=True),
    )
    op.create_index('ix_forecast_subject', 'execution_forecasts', ['subject_kind', 'subject_key'])
    op.create_index('ix_forecast_kind_horizon', 'execution_forecasts', ['forecast_kind', 'horizon'])
    op.create_index('ix_forecast_predicted_for', 'execution_forecasts', ['predicted_for'])

    # predictive_runtime_metrics
    op.create_table(
        'predictive_runtime_metrics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('metric_name', sa.String(120), nullable=False),
        sa.Column('metric_kind', sa.String(50), nullable=False, server_default='gauge'),
        sa.Column('scope_key', sa.String(120), nullable=False, server_default='global'),
        sa.Column('window_start', sa.DateTime(), nullable=False),
        sa.Column('window_end', sa.DateTime(), nullable=False),
        sa.Column('bucket_seconds', sa.Integer(), nullable=False, server_default='60'),
        sa.Column('predicted_value', sa.Float(), nullable=False),
        sa.Column('lower_bound', sa.Float(), nullable=True),
        sa.Column('upper_bound', sa.Float(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='0.5'),
        sa.Column('baseline_value', sa.Float(), nullable=True),
        sa.Column('observed_value', sa.Float(), nullable=True),
        sa.Column('error_pct', sa.Float(), nullable=True),
        sa.Column('method', sa.String(50), nullable=True),
        sa.Column('features', postgresql.JSON(), nullable=False, server_default='{}'),
        sa.Column('is_anomalous', sa.Boolean(), nullable=False, server_default='false'),
    )
    op.create_index('ix_pred_metric_name_window', 'predictive_runtime_metrics', ['metric_name', 'window_start'])
    op.create_index('ix_pred_metric_kind', 'predictive_runtime_metrics', ['metric_kind'])
    op.create_index('uq_pred_metric_window', 'predictive_runtime_metrics', ['metric_name', 'window_start', 'scope_key'], unique=True)

    # multi_stage_execution_graphs
    op.create_table(
        'multi_stage_execution_graphs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('subject_kind', sa.String(50), nullable=False),
        sa.Column('subject_key', sa.String(255), nullable=False),
        sa.Column('plan_label', sa.String(255), nullable=False),
        sa.Column('stages', postgresql.JSON(), nullable=False, server_default='[]'),
        sa.Column('edges', postgresql.JSON(), nullable=False, server_default='[]'),
        sa.Column('stage_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('parallelism_factor', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('estimated_duration', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('estimated_cost', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('risk_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('selected_strategy', sa.String(50), nullable=True, index=True),
        sa.Column('lifecycle_state', sa.String(32), nullable=False, server_default='planned', index=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('correlation_id', sa.String(100), nullable=True, index=True),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index('ix_msx_graph_subject', 'multi_stage_execution_graphs', ['subject_kind', 'subject_key'])
    op.create_index('ix_msx_graph_state', 'multi_stage_execution_graphs', ['lifecycle_state'])

    # orchestration_strategies
    op.create_table(
        'orchestration_strategies',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('subject_kind', sa.String(50), nullable=False),
        sa.Column('subject_key', sa.String(255), nullable=False),
        sa.Column('strategy_kind', sa.String(50), nullable=False, index=True),
        sa.Column('rationale', sa.Text(), nullable=False),
        sa.Column('scores', postgresql.JSON(), nullable=False, server_default='{}'),
        sa.Column('parameters', postgresql.JSON(), nullable=False, server_default='{}'),
        sa.Column('expected_improvement', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='0.5'),
        sa.Column('activated_at', sa.DateTime(), nullable=True),
        sa.Column('superseded_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true', index=True),
        sa.Column('correlation_id', sa.String(100), nullable=True, index=True),
    )
    op.create_index('ix_strategy_subject', 'orchestration_strategies', ['subject_kind', 'subject_key'])
    op.create_index('ix_strategy_kind', 'orchestration_strategies', ['strategy_kind'])

    # =====================================================================
    # Creative Intelligence
    # =====================================================================

    # creative_profiles
    op.create_table(
        'creative_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('campaign_id', sa.String(100), nullable=True, index=True),
        sa.Column('artist_id', sa.String(100), nullable=True, index=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('narrative_structure', sa.String(32), nullable=False, server_default='linear'),
        sa.Column('emotional_arc', sa.String(32), nullable=False, server_default='steady'),
        sa.Column('pacing_profile', sa.String(32), nullable=False, server_default='bruiser'),
        sa.Column('visual_keywords', postgresql.JSON(), nullable=False, server_default='[]'),
        sa.Column('audio_keywords', postgresql.JSON(), nullable=False, server_default='[]'),
        sa.Column('color_palette', postgresql.JSON(), nullable=False, server_default='[]'),
        sa.Column('motion_style', sa.String(100), nullable=True),
        sa.Column('tone_keywords', postgresql.JSON(), nullable=False, server_default='[]'),
        sa.Column('target_segments', postgresql.JSON(), nullable=False, server_default='[]'),
        sa.Column('attention_span_seconds', sa.Float(), nullable=False, server_default='45.0'),
        sa.Column('drop_off_point_seconds', sa.Float(), nullable=True),
        sa.Column('completion_rate_target', sa.Float(), nullable=False, server_default='0.6'),
        sa.Column('engagement_rate_target', sa.Float(), nullable=False, server_default='0.15'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index('ix_creative_profile_campaign', 'creative_profiles', ['campaign_id'])
    op.create_index('ix_creative_profile_artist', 'creative_profiles', ['artist_id'])

    # narrative_sequences
    op.create_table(
        'narrative_sequences',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('profile_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('creative_profiles.id', ondelete='SET NULL'), nullable=True),
        sa.Column('campaign_id', sa.String(100), nullable=True, index=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('structure', sa.String(32), nullable=False, server_default='linear'),
        sa.Column('emotional_arc', sa.String(32), nullable=False, server_default='steady'),
        sa.Column('beats', postgresql.JSON(), nullable=False, server_default='[]'),
        sa.Column('beat_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('target_duration', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('target_bpm', sa.Float(), nullable=True),
        sa.Column('target_key', sa.String(20), nullable=True),
        sa.Column('creative_score', sa.Float(), nullable=False, server_default='0.5'),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='0.5'),
        sa.Column('is_locked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index('ix_narr_seq_campaign', 'narrative_sequences', ['campaign_id'])
    op.create_index('ix_narr_seq_profile', 'narrative_sequences', ['profile_id'])

    # emotion_mappings
    op.create_table(
        'emotion_mappings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('source_type', sa.String(50), nullable=False),
        sa.Column('source_value', sa.String(100), nullable=False),
        sa.Column('target_type', sa.String(50), nullable=False),
        sa.Column('target_value', sa.String(100), nullable=False),
        sa.Column('strength', sa.Float(), nullable=False, server_default='0.5'),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='0.5'),
        sa.Column('trigger_threshold', sa.Float(), nullable=True),
        sa.Column('fade_duration', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('profile_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index('ix_emotion_map_source', 'emotion_mappings', ['source_type', 'source_value'])
    op.create_index('ix_emotion_map_target', 'emotion_mappings', ['target_type', 'target_value'])

    # pacing_heuristics
    op.create_table(
        'pacing_heuristics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('name', sa.String(255), nullable=False, unique=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('composition_class', sa.String(50), nullable=False, index=True),
        sa.Column('genre', sa.String(100), nullable=True, index=True),
        sa.Column('campaign_type', sa.String(100), nullable=True),
        sa.Column('energy_curve', postgresql.JSON(), nullable=False, server_default='[]'),
        sa.Column('tempo_curve', postgresql.JSON(), nullable=False, server_default='[]'),
        sa.Column('target_bpm', sa.Float(), nullable=False, server_default='120.0'),
        sa.Column('avg_energy_level', sa.Float(), nullable=False, server_default='0.5'),
        sa.Column('hit_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('success_rate', sa.Float(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index('ix_pacing_heuristic_composition', 'pacing_heuristics', ['composition_class'])
    op.create_index('ix_pacing_heuristic_genre', 'pacing_heuristics', ['genre'])

    # audience_engagement_heuristics
    op.create_table(
        'audience_engagement_heuristics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('name', sa.String(255), nullable=False, unique=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('audience_segment', sa.String(50), nullable=False, index=True),
        sa.Column('content_type', sa.String(50), nullable=False, index=True),
        sa.Column('retention_curve', postgresql.JSON(), nullable=False, server_default='[]'),
        sa.Column('expected_completion_rate', sa.Float(), nullable=False, server_default='0.5'),
        sa.Column('expected_engagement_score', sa.Float(), nullable=False, server_default='0.5'),
        sa.Column('first_drop_seconds', sa.Float(), nullable=False, server_default='5.0'),
        sa.Column('critical_drop_seconds', sa.Float(), nullable=True),
        sa.Column('platform_weights', postgresql.JSON(), nullable=False, server_default='{}'),
        sa.Column('hit_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('observed_completion_rate', sa.Float(), nullable=True),
        sa.Column('observed_engagement_score', sa.Float(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
    )
    op.create_index('ix_audience_heuristic_segment', 'audience_engagement_heuristics', ['audience_segment'])
    op.create_index('ix_audience_heuristic_content', 'audience_engagement_heuristics', ['content_type'])

    # =====================================================================
    # Governance
    # =====================================================================

    # agent_governance_rules
    op.create_table(
        'agent_governance_rules',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('name', sa.String(255), nullable=False, unique=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('agent_kind', sa.String(50), nullable=True, index=True),
        sa.Column('agent_type', sa.String(50), nullable=True),
        sa.Column('rule_type', sa.String(50), nullable=False),
        sa.Column('conditions', postgresql.JSON(), nullable=False, server_default='{}'),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('action_config', postgresql.JSON(), nullable=False, server_default='{}'),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true', index=True),
        sa.Column('trigger_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('success_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('failure_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
    )
    op.create_index('ix_gov_rule_agent_kind', 'agent_governance_rules', ['agent_kind'])
    op.create_index('ix_gov_rule_active', 'agent_governance_rules', ['is_active'])

    # authority_hierarchies
    op.create_table(
        'authority_hierarchies',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('agent_kind', sa.String(50), nullable=False, index=True),
        sa.Column('role_name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('authority_level', sa.Integer(), nullable=False),
        sa.Column('can_delegate', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('can_escalate', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('parent_authority_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index('ix_auth_hierarchy_parent', 'authority_hierarchies', ['parent_authority_id'])
    op.create_index('uq_auth_hierarchy_kind_role', 'authority_hierarchies', ['agent_kind', 'role_name'], unique=True)

    # arbitration_policies
    op.create_table(
        'arbitration_policies',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('name', sa.String(255), nullable=False, unique=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('domain', sa.String(50), nullable=False, index=True),
        sa.Column('workflow_class', sa.String(100), nullable=True),
        sa.Column('strategy', sa.String(32), nullable=False),
        sa.Column('strategy_config', postgresql.JSON(), nullable=False, server_default='{}'),
        sa.Column('escalation_threshold', sa.Integer(), nullable=False, server_default='3'),
        sa.Column('fallback_strategy', sa.String(32), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true', index=True),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='0'),
    )
    op.create_index('ix_arb_policy_domain', 'arbitration_policies', ['domain'])
    op.create_index('ix_arb_policy_active', 'arbitration_policies', ['is_active'])

    # conflict_resolutions
    op.create_table(
        'conflict_resolutions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('conflict_id', sa.String(100), nullable=False, unique=True, index=True),
        sa.Column('domain', sa.String(50), nullable=False, index=True),
        sa.Column('agent_ids', postgresql.JSON(), nullable=False, server_default='[]'),
        sa.Column('authority_levels', postgresql.JSON(), nullable=False, server_default='[]'),
        sa.Column('conflict_type', sa.String(50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('conflicting_actions', postgresql.JSON(), nullable=False, server_default='[]'),
        sa.Column('strategy_used', sa.String(32), nullable=False),
        sa.Column('resolution_outcome', sa.String(32), nullable=False),
        sa.Column('winning_agent_id', sa.String(100), nullable=True),
        sa.Column('merge_output', postgresql.JSON(), nullable=True),
        sa.Column('resolution_state', sa.String(32), nullable=False, server_default='resolved', index=True),
        sa.Column('escalation_required', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('human_review', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('detected_at', sa.DateTime(), nullable=False),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('resolution_time_ms', sa.Float(), nullable=True),
        sa.Column('correlation_id', sa.String(100), nullable=True, index=True),
    )
    op.create_index('ix_conflict_resolution_domain', 'conflict_resolutions', ['domain'])
    op.create_index('ix_conflict_resolution_state', 'conflict_resolutions', ['resolution_state'])

    # agent_policy_violations
    op.create_table(
        'agent_policy_violations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('violation_id', sa.String(100), nullable=False, unique=True, index=True),
        sa.Column('agent_id', sa.String(100), nullable=True, index=True),
        sa.Column('agent_kind', sa.String(50), nullable=True),
        sa.Column('rule_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('rule_name', sa.String(255), nullable=False),
        sa.Column('violation_type', sa.String(50), nullable=False),
        sa.Column('severity', sa.String(20), nullable=False, server_default='warning'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('context', postgresql.JSON(), nullable=False, server_default='{}'),
        sa.Column('action_taken', sa.String(50), nullable=False, server_default='logged'),
        sa.Column('escalated', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('resolved', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('detected_at', sa.DateTime(), nullable=False, index=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_violation_agent', 'agent_policy_violations', ['agent_id'])
    op.create_index('ix_violation_rule', 'agent_policy_violations', ['rule_id'])

    # =====================================================================
    # Feedback / Tuning
    # =====================================================================

    # orchestration_feedback
    op.create_table(
        'orchestration_feedback',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('subject_kind', sa.String(50), nullable=False),
        sa.Column('subject_key', sa.String(255), nullable=False),
        sa.Column('feedback_type', sa.String(50), nullable=False, index=True),
        sa.Column('expected_value', sa.Float(), nullable=True),
        sa.Column('actual_value', sa.Float(), nullable=True),
        sa.Column('delta_pct', sa.Float(), nullable=True),
        sa.Column('quality_score', sa.Float(), nullable=True),
        sa.Column('error_rate', sa.Float(), nullable=True),
        sa.Column('context', postgresql.JSON(), nullable=False, server_default='{}'),
        sa.Column('workflow_id', sa.String(100), nullable=True, index=True),
        sa.Column('agent_id', sa.String(100), nullable=True, index=True),
        sa.Column('policy_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('heuristic_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('execution_start', sa.DateTime(), nullable=False),
        sa.Column('execution_end', sa.DateTime(), nullable=True),
        sa.Column('observed_at', sa.DateTime(), nullable=False, index=True),
        sa.Column('correlation_id', sa.String(100), nullable=True, index=True),
    )
    op.create_index('ix_feedback_subject', 'orchestration_feedback', ['subject_kind', 'subject_key'])
    op.create_index('ix_feedback_type', 'orchestration_feedback', ['feedback_type'])
    op.create_index('ix_feedback_correlation', 'orchestration_feedback', ['correlation_id'])

    # adaptive_learning_states
    op.create_table(
        'adaptive_learning_states',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('context_key', sa.String(255), nullable=False, index=True),
        sa.Column('parameter_name', sa.String(100), nullable=False),
        sa.Column('current_value', sa.Float(), nullable=False),
        sa.Column('min_value', sa.Float(), nullable=True),
        sa.Column('max_value', sa.Float(), nullable=True),
        sa.Column('value_source', sa.String(32), nullable=False, server_default='initial'),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='0.5'),
        sa.Column('sample_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('history', postgresql.JSON(), nullable=False, server_default='[]'),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('last_updated', sa.DateTime(), nullable=False),
        sa.Column('correlation_id', sa.String(100), nullable=True),
    )
    op.create_index('ix_learning_state_context', 'adaptive_learning_states', ['context_key'])
    op.create_index('uq_learning_state_key_param', 'adaptive_learning_states', ['context_key', 'parameter_name'], unique=True)

    # autonomous_tuning_records
    op.create_table(
        'autonomous_tuning_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('cycle_id', sa.String(100), nullable=False, index=True),
        sa.Column('parameter_name', sa.String(100), nullable=False, index=True),
        sa.Column('before_value', sa.Float(), nullable=False),
        sa.Column('after_value', sa.Float(), nullable=False),
        sa.Column('delta', sa.Float(), nullable=False),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('action_config', postgresql.JSON(), nullable=False, server_default='{}'),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('triggered_by', sa.String(100), nullable=True),
        sa.Column('heuristic_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('outcome_score', sa.Float(), nullable=True),
        sa.Column('improvement_pct', sa.Float(), nullable=True),
        sa.Column('tuning_state', sa.String(32), nullable=False, server_default='applied', index=True),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='0.5'),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('evaluated_at', sa.DateTime(), nullable=True),
        sa.Column('correlation_id', sa.String(100), nullable=True, index=True),
    )
    op.create_index('ix_tuning_record_cycle', 'autonomous_tuning_records', ['cycle_id'])
    op.create_index('ix_tuning_record_param', 'autonomous_tuning_records', ['parameter_name'])
    op.create_index('ix_tuning_record_state', 'autonomous_tuning_records', ['tuning_state'])

    # tuning_cycles
    op.create_table(
        'tuning_cycles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('cycle_id', sa.String(100), nullable=False, unique=True, index=True),
        sa.Column('context_key', sa.String(255), nullable=False, index=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('target_metric', sa.String(50), nullable=False),
        sa.Column('target_improvement', sa.Float(), nullable=False, server_default='0.1'),
        sa.Column('max_iterations', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('iteration', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('cycle_state', sa.String(32), nullable=False, server_default='running', index=True),
        sa.Column('best_score', sa.Float(), nullable=True),
        sa.Column('best_parameters', postgresql.JSON(), nullable=True),
        sa.Column('tuning_records', postgresql.JSON(), nullable=False, server_default='[]'),
        sa.Column('started_at', sa.DateTime(), nullable=False, index=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_tuning_cycle_state', 'tuning_cycles', ['cycle_state'])
    op.create_index('ix_tuning_cycle_context', 'tuning_cycles', ['context_key'])

    # =====================================================================
    # Support tables (Cognitive domain existing tables)
    # =====================================================================

    # optimization_histories (unique constraint)
    op.create_table(
        'optimization_histories',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('optimization_id', sa.String(100), nullable=False, unique=True, index=True),
        sa.Column('optimization_type', sa.String(50), nullable=False, index=True),
        sa.Column('before_state', postgresql.JSON(), nullable=True),
        sa.Column('before_metrics', postgresql.JSON(), nullable=True),
        sa.Column('after_state', postgresql.JSON(), nullable=True),
        sa.Column('after_metrics', postgresql.JSON(), nullable=True),
        sa.Column('improvement_percent', sa.Float(), nullable=True),
        sa.Column('trigger_reason', sa.String(255), nullable=False),
        sa.Column('policy_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
    )

    # execution_patterns
    op.create_table(
        'execution_patterns',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('pattern_id', sa.String(100), nullable=False, unique=True, index=True),
        sa.Column('pattern_type', sa.String(50), nullable=False, index=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('pattern_data', postgresql.JSON(), nullable=False),
        sa.Column('frequency', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('avg_duration', sa.Float(), nullable=True),
        sa.Column('success_rate', sa.Float(), nullable=True),
        sa.Column('conditions', postgresql.JSON(), nullable=True),
        sa.Column('first_seen', sa.DateTime(), nullable=False),
        sa.Column('last_seen', sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    # Drop in reverse dependency order
    op.drop_table('execution_patterns')
    op.drop_table('optimization_histories')
    op.drop_table('tuning_cycles')
    op.drop_table('autonomous_tuning_records')
    op.drop_table('adaptive_learning_states')
    op.drop_table('orchestration_feedback')
    op.drop_table('agent_policy_violations')
    op.drop_table('conflict_resolutions')
    op.drop_table('arbitration_policies')
    op.drop_table('authority_hierarchies')
    op.drop_table('agent_governance_rules')
    op.drop_table('audience_engagement_heuristics')
    op.drop_table('pacing_heuristics')
    op.drop_table('emotion_mappings')
    op.drop_table('narrative_sequences')
    op.drop_table('creative_profiles')
    op.drop_table('orchestration_strategies')
    op.drop_table('multi_stage_execution_graphs')
    op.drop_table('predictive_runtime_metrics')
    op.drop_table('execution_forecasts')
    op.drop_table('execution_graph_snapshots')
    op.drop_table('orchestration_memory')
    op.drop_table('semantic_relationships')
    op.drop_table('kg_edges')
    op.drop_table('kg_nodes')

    # Drop enums
    for name in [
        'knowledgenodekind', 'knowledgeedgekind', 'memoriescope',
        'forecastkind', 'forecasthorizon', 'strategykind',
        'narrativestructure', 'emotionalarc', 'pacingprofile',
        'audiencesegment', 'authoritylevel', 'arbitrationstrategy',
        'feedbacktype', 'tuningaction',
    ]:
        op.execute(f"DROP TYPE IF EXISTS {name}")