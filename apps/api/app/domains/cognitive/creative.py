"""
Creative Reasoning Service

Cinematic creative cognition with narrative continuity intelligence,
engagement prediction, aesthetic consistency analysis, and semantic pacing.
"""
import logging
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime

from sqlalchemy import select, and_, or_, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cognitive import (
    CreativeReasoningProfile, SemanticContextArchive, ArchiveState
)

logger = logging.getLogger(__name__)


class CreativeReasoningService:
    """
    Cinematic creative reasoning system.
    
    Capabilities:
    - Narrative continuity: Maintain story coherence across segments
    - Engagement prediction: Predict audience engagement
    - Aesthetic consistency: Ensure visual/audio consistency
    - Semantic pacing: Optimize content pacing
    - Audience adaptation: Adapt content to target segments
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ---- Creative Profile Management ----
    
    async def create_profile(
        self,
        name: str,
        profile_type: str,
        campaign_id: Optional[UUID] = None,
        narrative_structure: Optional[str] = None,
        emotional_arc: Optional[str] = None,
        pacing_profile: str = "steady",
        pacing_intensity: float = 0.5,
        visual_keywords: Optional[List[str]] = None,
        color_palette: Optional[List[str]] = None,
        audio_keywords: Optional[List[str]] = None,
        target_segments: Optional[List[str]] = None,
        attention_span_seconds: int = 60,
        completion_rate_target: float = 0.7,
        engagement_rate_target: float = 0.15,
        max_duration: Optional[int] = None,
        min_duration: Optional[int] = None,
        content_guidelines: Optional[Dict[str, Any]] = None,
        visual_style: Optional[str] = None,
        music_mood: Optional[str] = None,
    ) -> CreativeReasoningProfile:
        """
        Create a new creative reasoning profile.
        
        Args:
            name: Profile name
            profile_type: Type (campaign, series, content)
            campaign_id: Associated campaign
            narrative_structure: Story structure type
            emotional_arc: Emotional journey pattern
            pacing_profile: Pacing style
            pacing_intensity: Energy level (0-1)
            visual_keywords: Visual themes
            color_palette: Color schemes
            audio_keywords: Audio themes
            target_segments: Audience segments
            attention_span_seconds: Target attention span
            completion_rate_target: Target completion rate
            engagement_rate_target: Target engagement rate
            max_duration: Maximum content duration
            min_duration: Minimum content duration
            content_guidelines: Creative constraints
            visual_style: Visual style description
            music_mood: Music mood description
            
        Returns:
            Created CreativeReasoningProfile
        """
        profile = CreativeReasoningProfile(
            name=name,
            profile_type=profile_type,
            campaign_id=campaign_id,
            narrative_structure=narrative_structure,
            emotional_arc=emotional_arc,
            pacing_profile=pacing_profile,
            pacing_intensity=pacing_intensity,
            visual_keywords=visual_keywords,
            color_palette=color_palette,
            audio_keywords=audio_keywords,
            target_segments=target_segments,
            attention_span_seconds=attention_span_seconds,
            completion_rate_target=completion_rate_target,
            engagement_rate_target=engagement_rate_target,
            max_duration=max_duration,
            min_duration=min_duration,
            content_guidelines=content_guidelines,
            visual_style=visual_style,
            music_mood=music_mood,
            is_active=True,
            version=1,
        )
        self.db.add(profile)
        await self.db.flush()
        logger.info(f"Created creative profile: {profile.id} [{name}]")
        return profile
    
    async def get_profile(self, profile_id: UUID) -> Optional[CreativeReasoningProfile]:
        """Get a profile by ID."""
        return await self.db.get(CreativeReasoningProfile, profile_id)
    
    async def update_profile(
        self,
        profile_id: UUID,
        **kwargs,
    ) -> Optional[CreativeReasoningProfile]:
        """Update a profile's attributes."""
        profile = await self.db.get(CreativeReasoningProfile, profile_id)
        if not profile:
            return None
        
        for key, value in kwargs.items():
            if hasattr(profile, key) and value is not None:
                setattr(profile, key, value)
        
        # Increment version on update
        profile.version += 1
        
        await self.db.flush()
        return profile
    
    async def list_profiles(
        self,
        profile_type: Optional[str] = None,
        campaign_id: Optional[UUID] = None,
        is_active: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[CreativeReasoningProfile]:
        """List profiles with filtering."""
        query = select(CreativeReasoningProfile).where(
            CreativeReasoningProfile.deleted_at.is_(None)
        )
        
        if profile_type:
            query = query.where(CreativeReasoningProfile.profile_type == profile_type)
        if campaign_id:
            query = query.where(CreativeReasoningProfile.campaign_id == campaign_id)
        if is_active is not None:
            query = query.where(CreativeReasoningProfile.is_active == is_active)
        
        query = query.order_by(desc(CreativeReasoningProfile.version))
        query = query.offset(offset).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def archive_profile(
        self,
        profile_id: UUID,
    ) -> Optional[CreativeReasoningProfile]:
        """Archive a profile (deactivate)."""
        profile = await self.db.get(CreativeReasoningProfile, profile_id)
        if not profile:
            return None
        
        profile.is_active = False
        await self.db.flush()
        return profile
    
    # ---- Narrative Intelligence ----
    
    async def analyze_narrative_structure(
        self,
        profile_id: UUID,
        content_segments: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Analyze content segments against the profile's narrative structure.
        
        Args:
            profile_id: Creative profile to use
            content_segments: Content segments to analyze
            
        Returns:
            Narrative analysis results
        """
        profile = await self.get_profile(profile_id)
        if not profile:
            return {'error': 'Profile not found'}
        
        structure = profile.narrative_structure
        emotional_arc = profile.emotional_arc
        
        analysis = {
            'structure_compliance': 0.0,
            'emotional_arc_compliance': 0.0,
            'pacing_score': 0.0,
            'segment_assessments': [],
        }
        
        total_segments = len(content_segments)
        if total_segments == 0:
            return analysis
        
        # Analyze each segment
        for i, segment in enumerate(content_segments):
            # Map segment position to narrative stage
            position = i / total_segments
            expected_stage = self._map_position_to_stage(position, structure)
            
            # Calculate compliance
            segment_emotion = segment.get('emotional_tone', 'neutral')
            expected_emotion = self._get_expected_emotion(expected_stage, emotional_arc)
            
            emotion_match = 1.0 if segment_emotion == expected_emotion else 0.5
            
            analysis['segment_assessments'].append({
                'index': i,
                'position': position,
                'expected_stage': expected_stage,
                'segment_data': segment,
                'emotion_match': emotion_match,
            })
        
        # Calculate aggregate scores
        emotion_scores = [s['emotion_match'] for s in analysis['segment_assessments']]
        analysis['structure_compliance'] = sum(emotion_scores) / len(emotion_scores)
        analysis['emotional_arc_compliance'] = sum(emotion_scores) / len(emotion_scores)
        
        # Pacing analysis
        analysis['pacing_score'] = self._calculate_pacing_score(
            content_segments, profile.pacing_profile
        )
        
        return analysis
    
    def _map_position_to_stage(
        self,
        position: float,
        structure: Optional[str],
    ) -> str:
        """Map content position to narrative stage."""
        if structure == 'three_act':
            if position < 0.25:
                return 'setup'
            elif position < 0.75:
                return 'confrontation'
            else:
                return 'resolution'
        elif structure == 'hero_journey':
            stages = ['departure', 'initiation', 'return']
            idx = int(position * len(stages))
            return stages[min(idx, len(stages) - 1)]
        else:  # episodic or default
            return 'development'
    
    def _get_expected_emotion(
        self,
        stage: str,
        emotional_arc: Optional[str],
    ) -> str:
        """Get expected emotional tone for a narrative stage."""
        if emotional_arc == 'rags_to_riches':
            emotions = {
                'setup': 'melancholy',
                'confrontation': 'determined',
                'resolution': 'triumphant',
            }
        elif emotional_arc == 'tragedy':
            emotions = {
                'setup': 'hopeful',
                'confrontation': 'conflicted',
                'resolution': 'sorrowful',
            }
        elif emotional_arc == 'redemption':
            emotions = {
                'setup': 'guilty',
                'confrontation': 'struggling',
                'resolution': 'peaceful',
            }
        else:
            emotions = {
                'setup': 'neutral',
                'confrontation': 'intense',
                'resolution': 'resolved',
            }
        return emotions.get(stage, 'neutral')
    
    def _calculate_pacing_score(
        self,
        segments: List[Dict[str, Any]],
        pacing_profile: str,
    ) -> float:
        """Calculate pacing compliance score."""
        if not segments:
            return 0.0
        
        intensities = [s.get('intensity', 0.5) for s in segments]
        
        if pacing_profile == 'rollercoaster':
            # High variance expected
            variance = sum((i - 0.5) ** 2 for i in intensities) / len(intensities)
            expected_variance = 0.15
            variance_score = 1 - min(1, abs(variance - expected_variance) / expected_variance)
            return variance_score
        elif pacing_profile == 'build':
            # Monotonically increasing
            increasing = all(
                intensities[i] <= intensities[i + 1]
                for i in range(len(intensities) - 1)
            )
            return 1.0 if increasing else 0.5
        elif pacing_profile == 'steady':
            # Low variance
            variance = sum((i - 0.5) ** 2 for i in intensities) / len(intensities)
            return 1 - min(1, variance * 5)
        else:  # alternating
            changes = sum(
                1 for i in range(len(intensities) - 1)
                if abs(intensities[i] - intensities[i + 1]) > 0.2
            )
            expected_changes = len(intensities) * 0.5
            return min(1, changes / expected_changes)
    
    # ---- Engagement Prediction ----
    
    async def predict_engagement(
        self,
        profile_id: UUID,
        content_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Predict engagement metrics for content.
        
        Args:
            profile_id: Creative profile to use
            content_data: Content to evaluate
            
        Returns:
            Predicted engagement metrics
        """
        profile = await self.get_profile(profile_id)
        if not profile:
            return {'error': 'Profile not found'}
        
        # Extract content features
        duration = content_data.get('duration', 60)
        segments = content_data.get('segments', [])
        
        # Calculate alignment scores
        duration_fit = self._calculate_duration_fit(
            duration, profile.min_duration, profile.max_duration
        )
        
        visual_alignment = self._calculate_keyword_alignment(
            content_data.get('visual_elements', []),
            profile.visual_keywords or [],
        )
        
        audio_alignment = self._calculate_keyword_alignment(
            content_data.get('audio_elements', []),
            profile.audio_keywords or [],
        )
        
        # Predict completion rate
        predicted_completion = min(
            profile.completion_rate_target * 1.2,
            duration_fit * 0.4 + visual_alignment * 0.3 + audio_alignment * 0.3,
        )
        
        # Predict engagement rate
        predicted_engagement = min(
            profile.engagement_rate_target * 1.2,
            visual_alignment * 0.5 + audio_alignment * 0.5,
        )
        
        return {
            'predicted_completion_rate': round(predicted_completion, 3),
            'predicted_engagement_rate': round(predicted_engagement, 3),
            'attention_span_fit': duration / profile.attention_span_seconds if profile.attention_span_seconds else 1.0,
            'duration_fit': duration_fit,
            'visual_alignment': visual_alignment,
            'audio_alignment': audio_alignment,
            'overall_score': (predicted_completion + predicted_engagement) / 2,
            'recommendations': self._generate_recommendations(
                duration_fit, visual_alignment, audio_alignment
            ),
        }
    
    def _calculate_duration_fit(
        self,
        duration: int,
        min_duration: Optional[int],
        max_duration: Optional[int],
    ) -> float:
        """Calculate how well duration fits within constraints."""
        if min_duration and duration < min_duration:
            return 0.5 + (duration / min_duration) * 0.5
        if max_duration and duration > max_duration:
            return 0.5 + (max_duration / duration) * 0.5
        return 1.0
    
    def _calculate_keyword_alignment(
        self,
        content_keywords: List[str],
        profile_keywords: List[str],
    ) -> float:
        """Calculate keyword alignment score."""
        if not profile_keywords:
            return 1.0
        
        matches = sum(1 for kw in content_keywords if kw in profile_keywords)
        return min(1, matches / len(profile_keywords))
    
    def _generate_recommendations(
        self,
        duration_fit: float,
        visual_alignment: float,
        audio_alignment: float,
    ) -> List[str]:
        """Generate content recommendations based on alignment scores."""
        recommendations = []
        
        if duration_fit < 0.8:
            recommendations.append("Adjust content duration to fit target range")
        if visual_alignment < 0.7:
            recommendations.append("Increase visual element alignment with profile")
        if audio_alignment < 0.7:
            recommendations.append("Adjust audio elements to match profile mood")
        
        if not recommendations:
            recommendations.append("Content aligns well with creative profile")
        
        return recommendations
    
    # ---- Aesthetic Consistency ----
    
    async def check_aesthetic_consistency(
        self,
        profile_id: UUID,
        assets: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Check aesthetic consistency across assets.
        
        Args:
            profile_id: Creative profile to use
            assets: List of assets to check
            
        Returns:
            Consistency assessment
        """
        profile = await self.get_profile(profile_id)
        if not profile:
            return {'error': 'Profile not found'}
        
        # Extract visual features
        colors = [a.get('dominant_colors', []) for a in assets]
        styles = [a.get('visual_style', 'unknown') for a in assets]
        
        # Check color palette consistency
        palette_consistency = self._check_color_consistency(
            colors, profile.color_palette or []
        )
        
        # Check style consistency
        style_consistency = self._check_style_consistency(
            styles, profile.visual_style
        )
        
        # Overall consistency
        overall = (palette_consistency + style_consistency) / 2
        
        return {
            'palette_consistency': palette_consistency,
            'style_consistency': style_consistency,
            'overall_consistency': overall,
            'inconsistent_assets': self._find_inconsistent_assets(
                colors, styles, profile
            ),
            'recommendations': self._generate_consistency_recommendations(
                palette_consistency, style_consistency
            ),
        }
    
    def _check_color_consistency(
        self,
        asset_colors: List[List[str]],
        target_palette: List[str],
    ) -> float:
        """Check color consistency against target palette."""
        if not target_palette or not asset_colors:
            return 1.0
        
        consistent_count = 0
        for colors in asset_colors:
            if any(c in target_palette for c in colors):
                consistent_count += 1
        
        return consistent_count / len(asset_colors)
    
    def _check_style_consistency(
        self,
        styles: List[str],
        target_style: Optional[str],
    ) -> float:
        """Check style consistency against target style."""
        if not target_style or not styles:
            return 1.0
        
        consistent_count = sum(1 for s in styles if s == target_style)
        return consistent_count / len(styles)
    
    def _find_inconsistent_assets(
        self,
        colors: List[List[str]],
        styles: List[str],
        profile: CreativeReasoningProfile,
    ) -> List[int]:
        """Find indices of inconsistent assets."""
        inconsistent = []
        
        for i, (asset_colors, style) in enumerate(zip(colors, styles)):
            if profile.color_palette:
                if not any(c in profile.color_palette for c in asset_colors):
                    inconsistent.append(i)
            if profile.visual_style and style != profile.visual_style:
                if i not in inconsistent:
                    inconsistent.append(i)
        
        return inconsistent
    
    def _generate_consistency_recommendations(
        self,
        palette_consistency: float,
        style_consistency: float,
    ) -> List[str]:
        """Generate recommendations for improving consistency."""
        recommendations = []
        
        if palette_consistency < 0.7:
            recommendations.append("Apply color grading to align with target palette")
        if style_consistency < 0.7:
            recommendations.append("Apply consistent visual style treatment")
        
        return recommendations if recommendations else ["Aesthetic consistency is good"]
    
    # ---- Profile Statistics ----
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get creative reasoning system statistics."""
        # Count by type
        type_query = select(
            CreativeReasoningProfile.profile_type,
            func.count(CreativeReasoningProfile.id).label('count'),
        ).where(CreativeReasoningProfile.deleted_at.is_(None)).group_by(
            CreativeReasoningProfile.profile_type
        )
        
        type_result = await self.db.execute(type_query)
        by_type = {row.profile_type: row.count for row in type_result.all()}
        
        # Active profiles
        active_query = select(func.count(CreativeReasoningProfile.id)).where(
            and_(
                CreativeReasoningProfile.deleted_at.is_(None),
                CreativeReasoningProfile.is_active == True,
            )
        )
        active_result = await self.db.execute(active_query)
        active_count = active_result.scalar() or 0
        
        # By narrative structure
        structure_query = select(
            CreativeReasoningProfile.narrative_structure,
            func.count(CreativeReasoningProfile.id).label('count'),
        ).where(
            and_(
                CreativeReasoningProfile.deleted_at.is_(None),
                CreativeReasoningProfile.narrative_structure.isnot(None),
            )
        ).group_by(CreativeReasoningProfile.narrative_structure)
        
        structure_result = await self.db.execute(structure_query)
        by_structure = {
            row.narrative_structure: row.count
            for row in structure_result.all()
        }
        
        return {
            'total_profiles': sum(by_type.values()),
            'active_profiles': active_count,
            'by_type': by_type,
            'by_narrative_structure': by_structure,
            'avg_pacing_intensity': await self._get_avg_pacing_intensity(),
        }
    
    async def _get_avg_pacing_intensity(self) -> float:
        """Calculate average pacing intensity."""
        query = select(func.avg(CreativeReasoningProfile.pacing_intensity)).where(
            CreativeReasoningProfile.deleted_at.is_(None)
        )
        result = await self.db.execute(query)
        return float(result.scalar() or 0.5)


# ---- Semantic Context Archives ----

class SemanticArchiveService:
    """
    Semantic knowledge expansion and context archiving.
    
    Capabilities:
    - Knowledge graph management
    - Workflow context storage
    - Creative intelligence memory
    - Semantic search
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_archive(
        self,
        name: str,
        archive_type: str,
        domain: Optional[str] = None,
        entities: Optional[Dict[str, Any]] = None,
        relationships: Optional[List[Dict[str, Any]]] = None,
        attributes: Optional[Dict[str, Any]] = None,
        semantic_tags: Optional[List[str]] = None,
        source_type: Optional[str] = None,
        source_id: Optional[str] = None,
        created_by: Optional[str] = None,
        parent_archive_id: Optional[UUID] = None,
    ) -> SemanticContextArchive:
        """Create a new semantic archive."""
        archive = SemanticContextArchive(
            name=name,
            archive_type=archive_type,
            domain=domain,
            entities=entities,
            relationships=relationships,
            attributes=attributes,
            semantic_tags=semantic_tags,
            source_type=source_type,
            source_id=source_id,
            created_by=created_by,
            archive_state=ArchiveState.ACTIVE.value,
            parent_archive_id=parent_archive_id,
        )
        self.db.add(archive)
        await self.db.flush()
        return archive
    
    async def search_archives(
        self,
        query: str,
        archive_type: Optional[str] = None,
        domain: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 20,
    ) -> List[SemanticContextArchive]:
        """Search archives by content."""
        conditions = [
            SemanticContextArchive.deleted_at.is_(None),
            SemanticContextArchive.archive_state == ArchiveState.ACTIVE.value,
        ]
        
        # Text search on name (simplified - in production use full-text search)
        conditions.append(SemanticContextArchive.name.ilike(f"%{query}%"))
        
        if archive_type:
            conditions.append(SemanticContextArchive.archive_type == archive_type)
        if domain:
            conditions.append(SemanticContextArchive.domain == domain)
        
        query_obj = select(SemanticContextArchive).where(and_(*conditions))
        
        if tags:
            for tag in tags:
                query_obj = query_obj.where(
                    SemanticContextArchive.semantic_tags.contains([tag])
                )
        
        query_obj = query_obj.order_by(
            desc(SemanticContextArchive.use_count),
            desc(SemanticContextArchive.completeness),
        ).limit(limit)
        
        result = await self.db.execute(query_obj)
        archives = list(result.scalars().all())
        
        # Update use counts
        for archive in archives:
            archive.use_count += 1
            archive.last_used_at = datetime.utcnow()
        
        await self.db.flush()
        return archives
    
    async def link_workflow(
        self,
        archive_id: UUID,
        workflow_id: str,
    ) -> Optional[SemanticContextArchive]:
        """Link a workflow to an archive."""
        archive = await self.db.get(SemanticContextArchive, archive_id)
        if not archive:
            return None
        
        linked = archive.linked_workflow_ids or []
        if workflow_id not in linked:
            linked.append(workflow_id)
            archive.linked_workflow_ids = linked
        
        await self.db.flush()
        return archive
    
    async def archive_semantic(
        self,
        archive_id: UUID,
    ) -> Optional[SemanticContextArchive]:
        """Move archive to archived state."""
        archive = await self.db.get(SemanticContextArchive, archive_id)
        if not archive:
            return None
        
        archive.archive_state = ArchiveState.ARCHIVED.value
        await self.db.flush()
        return archive