"""
Creative Intelligence Domain - Cinematic cognition and narrative sequencing.

Drives the creative layer of the orchestration engine:

  - NarrativeSequences     : structured scene/story arc plans
  - EmotionMappings        : audio-mood ↔ visual-mood bridges
  - PacingHeuristics       : tempo / energy curves per composition class
  - AudienceEngagementHeuristics : predicted retention signals
  - CreativeProfiles       : per-campaign creative brief + style guide
"""
from .models import (
    NarrativeStructure,
    EmotionalArc,
    PacingProfile,
    AudienceSegment,
    CreativeProfile,
    NarrativeSequence,
    EmotionMapping,
    PacingHeuristic,
    AudienceEngagementHeuristic,
)
from .services import (
    CreativeIntelligenceService,
    CinematicSequencerService,
    CreativeProfileService,
    NarrativeArc,
    SequenceRecommendation,
)

__all__ = [
    # Enums
    # Models
    "NarrativeStructure",
    "EmotionalArc",
    "PacingProfile",
    "AudienceSegment",
    "CreativeProfile",
    "NarrativeSequence",
    "EmotionMapping",
    "PacingHeuristic",
    "AudienceEngagementHeuristic",
    # Services
    "CreativeIntelligenceService",
    "CinematicSequencerService",
    "CreativeProfileService",
    # Data
    "NarrativeArc",
    "SequenceRecommendation",
]
