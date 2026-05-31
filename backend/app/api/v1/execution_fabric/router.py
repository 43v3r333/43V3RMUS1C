"""
Execution Fabric Router - API routes for unified execution fabric.

Provides:
- Event topology governance endpoints
- Distributed runtime propagation endpoints
- Cognition fabric endpoints
- Self-healing orchestration endpoints
- Semantic execution endpoints
- Predictive observability endpoints
"""
import logging
from typing import Dict, List, Optional, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from ...schemas.base import BaseResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/execution-fabric", tags=["execution-fabric"])


# ==================== Event Topology Governance ====================

@router.get("/topology/summary")
async def get_topology_summary(
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Get event topology summary"""
    try:
        from app.domains.event_topology.services import EventTopologyService
        
        service = EventTopologyService(db)
        await service.initialize()
        
        summary = await service.get_topology_summary()
        await service.shutdown()
        
        return {
            "status": "success",
            "data": summary,
        }
    except Exception as e:
        logger.error(f"Failed to get topology summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/contracts")
async def list_event_contracts(
    status_filter: Optional[str] = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """List event contracts"""
    try:
        from app.domains.event_topology.models import ContractStatus
        from app.domains.event_topology.services import EventTopologyService
        from sqlalchemy import select
        
        service = EventTopologyService(db)
        await service.initialize()
        
        contracts = await service.contract_registry.get_active_contracts()
        
        if status_filter:
            contracts = [c for c in contracts if c.status == status_filter]
        
        await service.shutdown()
        
        return {
            "status": "success",
            "data": {
                "contracts": [
                    {
                        "id": str(c.id),
                        "name": c.name,
                        "version": c.version,
                        "contract_type": c.contract_type,
                        "status": c.status,
                        "publish_count": c.publish_count,
                        "consume_count": c.consume_count,
                    }
                    for c in contracts[:limit]
                ],
                "total": len(contracts),
            },
        }
    except Exception as e:
        logger.error(f"Failed to list contracts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/contracts")
async def register_contract(
    name: str,
    contract_type: str,
    schema: Dict[str, Any],
    category: Optional[str] = None,
    description: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Register new event contract"""
    try:
        from app.domains.event_topology.services import EventTopologyService
        
        service = EventTopologyService(db)
        await service.initialize()
        
        contract = await service.contract_registry.register_contract(
            name=name,
            contract_type=contract_type,
            schema=schema,
            category=category,
            description=description,
        )
        
        await service.shutdown()
        
        return {
            "status": "success",
            "data": {
                "id": str(contract.id),
                "name": contract.name,
                "version": contract.version,
            },
        }
    except Exception as e:
        logger.error(f"Failed to register contract: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Distributed Runtime ====================

@router.get("/runtime/summary")
async def get_runtime_summary(
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Get distributed runtime summary"""
    try:
        from app.domains.distributed_runtime.services import DistributedRuntimeService
        
        service = DistributedRuntimeService(db)
        await service.initialize()
        
        summary = await service.get_runtime_summary()
        await service.shutdown()
        
        return {
            "status": "success",
            "data": summary,
        }
    except Exception as e:
        logger.error(f"Failed to get runtime summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/contexts")
async def create_context(
    scope: str,
    context_data: Optional[Dict[str, Any]] = None,
    ttl_seconds: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Create distributed context"""
    try:
        from app.domains.distributed_runtime.services import DistributedRuntimeService
        
        service = DistributedRuntimeService(db)
        await service.initialize()
        
        context = await service.context_manager.create_context(
            scope=scope,
            context_data=context_data,
            ttl_seconds=ttl_seconds,
        )
        
        await service.shutdown()
        
        return {
            "status": "success",
            "data": {
                "context_id": context.context_id,
                "scope": context.scope,
            },
        }
    except Exception as e:
        logger.error(f"Failed to create context: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Cognition Fabric ====================

@router.get("/cognition/summary")
async def get_cognition_summary(
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Get cognition fabric summary"""
    try:
        from app.domains.cognition_fabric.services import CognitionFabricService
        
        service = CognitionFabricService(db)
        await service.initialize()
        
        summary = await service.get_cognition_summary()
        await service.shutdown()
        
        return {
            "status": "success",
            "data": summary,
        }
    except Exception as e:
        logger.error(f"Failed to get cognition summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/memories")
async def list_memories(
    scope: Optional[str] = None,
    memory_kind: Optional[str] = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """List cognition memories"""
    try:
        from app.domains.cognition_fabric.services import CognitionFabricService
        
        service = CognitionFabricService(db)
        await service.initialize()
        
        memories = await service.shared_memory.recall(
            scope=scope,
            memory_kind=memory_kind,
            limit=limit,
        )
        
        await service.shutdown()
        
        return {
            "status": "success",
            "data": {
                "memories": [
                    {
                        "memory_id": m.memory_id,
                        "title": m.title,
                        "scope": m.scope,
                        "memory_kind": m.memory_kind,
                        "importance": m.importance,
                        "confidence": m.confidence,
                    }
                    for m in memories
                ],
                "total": len(memories),
            },
        }
    except Exception as e:
        logger.error(f"Failed to list memories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/memories")
async def store_memory(
    scope: str,
    memory_kind: str,
    title: str,
    content: Dict[str, Any],
    importance: float = 0.5,
    confidence: float = 0.8,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Store new cognition memory"""
    try:
        from app.domains.cognition_fabric.services import CognitionFabricService
        
        service = CognitionFabricService(db)
        await service.initialize()
        
        memory = await service.shared_memory.store(
            scope=scope,
            memory_kind=memory_kind,
            title=title,
            content=content,
            importance=importance,
            confidence=confidence,
        )
        
        await service.shutdown()
        
        return {
            "status": "success",
            "data": {
                "memory_id": memory.memory_id,
            },
        }
    except Exception as e:
        logger.error(f"Failed to store memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Self-Healing ====================

@router.get("/health/summary")
async def get_health_summary(
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Get self-healing health summary"""
    try:
        from app.domains.self_healing.services import SelfHealingOrchestrationService
        
        service = SelfHealingOrchestrationService(db)
        await service.initialize()
        
        summary = await service.get_health_summary()
        await service.shutdown()
        
        return {
            "status": "success",
            "data": summary,
        }
    except Exception as e:
        logger.error(f"Failed to get health summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/anomalies")
async def list_anomalies(
    min_severity: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """List active anomalies"""
    try:
        from app.domains.self_healing.services import SelfHealingOrchestrationService
        
        service = SelfHealingOrchestrationService(db)
        await service.initialize()
        
        anomalies = await service.anomaly_detector.get_active_anomalies(
            min_severity=min_severity,
        )
        
        await service.shutdown()
        
        return {
            "status": "success",
            "data": {
                "anomalies": [
                    {
                        "anomaly_id": a.anomaly_id,
                        "title": a.title,
                        "severity": a.severity,
                        "target_id": a.target_id,
                        "deviation": a.deviation,
                    }
                    for a in anomalies
                ],
                "total": len(anomalies),
            },
        }
    except Exception as e:
        logger.error(f"Failed to list anomalies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Semantic Execution ====================

@router.get("/execution/summary")
async def get_execution_summary(
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Get semantic execution summary"""
    try:
        from app.domains.semantic_execution.services import SemanticExecutionService
        
        service = SemanticExecutionService(db)
        await service.initialize()
        
        summary = await service.get_execution_summary()
        await service.shutdown()
        
        return {
            "status": "success",
            "data": summary,
        }
    except Exception as e:
        logger.error(f"Failed to get execution summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Predictive Observability ====================

@router.get("/observability/summary")
async def get_observability_summary(
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Get predictive observability summary"""
    try:
        from app.domains.predictive_observability.services import PredictiveObservabilityService
        
        service = PredictiveObservabilityService(db)
        await service.initialize()
        
        summary = await service.get_observability_summary()
        await service.shutdown()
        
        return {
            "status": "success",
            "data": summary,
        }
    except Exception as e:
        logger.error(f"Failed to get observability summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/forecasts")
async def list_forecasts(
    target_id: Optional[str] = None,
    forecast_type: Optional[str] = None,
    horizon: Optional[str] = None,
    min_confidence: float = 0.0,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """List runtime forecasts"""
    try:
        from app.domains.predictive_observability.services import PredictiveObservabilityService
        
        service = PredictiveObservabilityService(db)
        await service.initialize()
        
        forecasts = await service.forecasting_engine.get_forecasts(
            target_id=target_id,
            forecast_type=forecast_type,
            horizon=horizon,
            min_confidence=min_confidence,
        )
        
        await service.shutdown()
        
        return {
            "status": "success",
            "data": {
                "forecasts": [
                    {
                        "forecast_id": f.forecast_id,
                        "forecast_type": f.forecast_type,
                        "predicted_value": f.predicted_value,
                        "confidence": f.confidence,
                        "horizon": f.horizon,
                    }
                    for f in forecasts
                ],
                "total": len(forecasts),
            },
        }
    except Exception as e:
        logger.error(f"Failed to list forecasts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Unified Summary ====================

@router.get("/summary")
async def get_unified_fabric_summary(
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Get unified execution fabric summary"""
    try:
        from app.domains.event_topology.services import EventTopologyService
        from app.domains.distributed_runtime.services import DistributedRuntimeService
        from app.domains.cognition_fabric.services import CognitionFabricService
        from app.domains.self_healing.services import SelfHealingOrchestrationService
        from app.domains.semantic_execution.services import SemanticExecutionService
        from app.domains.predictive_observability.services import PredictiveObservabilityService
        
        # Gather all summaries
        summaries = {}
        
        # Event topology
        try:
            et_service = EventTopologyService(db)
            await et_service.initialize()
            summaries["event_topology"] = await et_service.get_topology_summary()
            await et_service.shutdown()
        except Exception as e:
            logger.error(f"Event topology summary failed: {e}")
            summaries["event_topology"] = {"error": str(e)}
        
        # Distributed runtime
        try:
            dr_service = DistributedRuntimeService(db)
            await dr_service.initialize()
            summaries["distributed_runtime"] = await dr_service.get_runtime_summary()
            await dr_service.shutdown()
        except Exception as e:
            logger.error(f"Distributed runtime summary failed: {e}")
            summaries["distributed_runtime"] = {"error": str(e)}
        
        # Cognition fabric
        try:
            cf_service = CognitionFabricService(db)
            await cf_service.initialize()
            summaries["cognition_fabric"] = await cf_service.get_cognition_summary()
            await cf_service.shutdown()
        except Exception as e:
            logger.error(f"Cognition fabric summary failed: {e}")
            summaries["cognition_fabric"] = {"error": str(e)}
        
        # Self-healing
        try:
            sh_service = SelfHealingOrchestrationService(db)
            await sh_service.initialize()
            summaries["self_healing"] = await sh_service.get_health_summary()
            await sh_service.shutdown()
        except Exception as e:
            logger.error(f"Self-healing summary failed: {e}")
            summaries["self_healing"] = {"error": str(e)}
        
        # Semantic execution
        try:
            se_service = SemanticExecutionService(db)
            await se_service.initialize()
            summaries["semantic_execution"] = await se_service.get_execution_summary()
            await se_service.shutdown()
        except Exception as e:
            logger.error(f"Semantic execution summary failed: {e}")
            summaries["semantic_execution"] = {"error": str(e)}
        
        # Predictive observability
        try:
            po_service = PredictiveObservabilityService(db)
            await po_service.initialize()
            summaries["predictive_observability"] = await po_service.get_observability_summary()
            await po_service.shutdown()
        except Exception as e:
            logger.error(f"Predictive observability summary failed: {e}")
            summaries["predictive_observability"] = {"error": str(e)}
        
        return {
            "status": "success",
            "data": summaries,
        }
    except Exception as e:
        logger.error(f"Failed to get unified fabric summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))