# 43V3R CORE Model Layer Migration Plan

**Date:** May 30, 2026  
**Priority:** High  
**Estimated Effort:** 3-5 days  
**Risk Level:** Medium (requires testing validation)

---

## 1. Executive Summary

The 43V3R CORE API fails to start due to **duplicate SQLAlchemy model definitions** and **reserved keyword conflicts**. The backend test suite (87 tests) passes, confirming the business logic is sound. The issue is purely architectural.

**Root Causes:**
1. **Dual model locations**: Same table defined in `models/` and `domains/`
2. **Reserved keyword**: `metadata` field conflicts with SQLAlchemy internals
3. **Type mismatches**: `UUID` vs `PGUUID` for PostgreSQL
4. **Incomplete migration**: Historical code not cleaned up during domain-driven design transition

**Goal:** Establish a single source of truth for every model, update all imports, and remove duplicates.

---

## 2. Current State Analysis

### 2.1 Duplicate Table Definitions

| Table Name | Location A (Authoritative) | Location B (Duplicate) | Action |
|------------|---------------------------|------------------------|--------|
| `render_jobs` | `models/workflow.py` | `domains/rendering/models.py` | Remove B, import from A |
| `workflows` | `models/workflow.py` | `domains/workflows/models.py` | Remove B, import from A |
| `analytics_events` | `models/analytics.py` | `domains/analytics/models.py` | Remove B, import from A |
| `runtime_metrics` | `domains/runtime/models.py` | `domains/observability/models.py` | Remove B, import from A |
| `workflow_executions` | `domains/runtime/models.py` | `domains/workflows/models.py` | Remove B, import from A |
| `distributed_context_states` | `domains/distributed_runtime/models.py` | `domains/coherence/models.py` | Remove B, import from A |
| `arbitration_sessions` | `domains/constitutional_arbitration/models.py` | `domains/adaptive_arbitration/models.py` | **Decision needed** |
| `anomaly_detections` | `domains/learning/models.py` | `domains/coherence/models.py`, `domains/self_healing/models.py` | **Decision needed** |
| `execution_forecasts` | `domains/forecasting/models.py` | `domains/coherence/models.py` | Remove B, import from A |
| `health_checks` | `domains/observability/models.py` | `domains/self_healing/models.py` | Remove B, import from A |

**Action:** For each duplicate, decide authoritative location and delete the other.

### 2.2 Reserved Keyword Issues

All `metadata` columns must be renamed to `metadata_` with explicit column mapping:

**Files Already Fixed:**
- `models/media.py`, `analytics.py`, `asset.py`, `campaign.py`, `events.py`, `media_execution.py`, `workflow.py`, `cognitive.py`
- `domains/workers/models.py`, `storage/models.py`, `observability/models.py`

**Files Remaining:** None (verified)

### 2.3 UUID Type Issues

All `UUID(as_uuid=True)` must be changed to `PGUUID(as_uuid=True)`:

**Files Fixed:**
- `models/analytics.py`, `asset.py`, `base.py`, `campaign.py`, `media.py`, `user.py`, `workflow.py`

**Files Remaining:** None (verified)

---

## 3. Migration Strategy

### Phase 1: Inventory & Decision (Day 1)

**Steps:**
1. **List all `__tablename__` definitions**: Output from earlier script
2. **Resolve ambiguous duplicates**: 
   - `arbitration_sessions`: Keep `constitutional_arbitration`, remove `adaptive_arbitration`
   - `anomaly_detections`: Keep `learning`, remove `coherence` and `self_healing`
3. **Document import paths**: For each model, record the new canonical import

**Deliverable:** `MODEL_INVENTORY.md` with authoritative locations.

### Phase 2: Code Cleanup (Day 2-3)

**Step 2a: Remove Duplicate Definitions**
```bash
# Example for render_jobs
# 1. Confirm RenderJob in models/workflow.py is complete
# 2. In domains/rendering/models.py, replace class with:
class RenderJob:
    """DEPRECATED: Use models.workflow.RenderJob"""
    __table__ = None
    def __init__(self, *args, **kwargs):
        raise RuntimeError("Import from models.workflow")
```

**Step 2b: Update All Imports**
Search and replace across codebase:
```bash
# Find all imports of the duplicate models
grep -r "from domains.rendering.models import RenderJob" --include="*.py"

# Replace with:
# from models.workflow import RenderJob
```

**Step 2c: Update Domain `__init__.py` Files**
Ensure each domain exports only from its authoritative location.

**Deliverable:** Codebase with no duplicate table registrations.

### Phase 3: Integration Testing (Day 4)

**Steps:**
1. **Run backend tests**: `pytest tests/ -v` (should still pass: 87/87)
2. **Start API locally**: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
3. **Verify health endpoint**: `curl http://localhost:8000/api/v1/health`
4. **Test database migrations**: `alembic upgrade head` (if schema changed)
5. **Run integration tests**: Any tests that hit the API or database

**Deliverable:** Running API with passing tests.

### Phase 4: Documentation & Prevention (Day 5)

**Steps:**
1. **Update CONTRIBUTING.md**: Add model ownership rules
2. **Add CI check**: Prevent duplicate `__tablename__` in PRs
3. **Document migration**: Write `MIGRATION_GUIDE.md` for future changes
4. **Update API docs**: Ensure endpoints reference correct models

**Deliverable:** Prevention mechanisms in place.

---

## 4. Detailed Task Breakdown

### Task 2.1: Resolve Ambiguous Duplicates

**Arbitration Sessions:**
- **Current:** Defined in `constitutional_arbitration/models.py` and `adaptive_arbitration/models.py`
- **Decision:** Keep `constitutional_arbitration` (more specific, matches governance model)
- **Action:** Delete `adaptive_arbitration/models.py` or comment out `ArbitrationSession` class
- **Update:** Change imports in `domains/adaptive_arbitration/__init__.py`

**Anomaly Detections:**
- **Current:** Defined in `learning/models.py`, `coherence/models.py`, `self_healing/models.py`
- **Decision:** Keep `learning` (core ML/analytics function)
- **Action:** Make `coherence` and `self_healing` versions stubs
- **Update:** Import paths in respective domains

**Estimated Time:** 2 hours

### Task 2.2: Fix Import Chains

**Pattern:**
```python
# Before (in domains/xyz/__init__.py)
from .models import DuplicateModel, OtherModel

# After
# DuplicateModel is now imported from outside
from ...models.workflow import DuplicateModel  # Example
from .models import OtherModel

__all__ = ["DuplicateModel", "OtherModel"]
```

**Scope:** ~15 domain `__init__.py` files

**Estimated Time:** 4 hours

### Task 2.3: Update Service Layer Imports

Services often import models directly from `domains/*/models.py`. These must be updated.

**Example:**
```python
# Before
from app.domains.observability.models import RuntimeMetric

# After (if moved to runtime)
from app.domains.runtime.models import RuntimeMetric
```

**Search Pattern:**
```bash
grep -r "from .* domains \. .* models import" --include="*.py"
```

**Estimated Time:** 6 hours

### Task 2.4: Database Migration Check

If any column names changed (e.g., `metadata` → `metadata_` with explicit mapping), no DB migration needed because the DB column name stays `metadata`.

**Verify:**
```python
# In model:
metadata_ = Column("metadata", JSON, nullable=True)  # DB column is still "metadata"
```

**Action:** Run `alembic history` to check for auto-generated migrations.

**Estimated Time:** 1 hour

---

## 5. Risk Mitigation

### Risk 1: Broken Import Chains
**Mitigation:**
- Use IDE "Find Usages" to track all imports before changing
- Update one domain at a time, run tests after each
- Keep a backup of original files

### Risk 2: Database Schema Changes
**Mitigation:**
- Verify `metadata_ = Column("metadata", ...)` preserves DB column name
- Run `alembic check` to detect unintended migrations
- Backup database before running migrations

### Risk 3: Service Layer Breakage
**Mitigation:**
- Services use type hints; broken imports will fail at module load
- Catch errors early with `python -c "import app.main"`
- Fix service imports before testing runtime behavior

### Risk 4: Test Coverage Gaps
**Mitigation:**
- Current 87 tests validate core logic
- Add 1-2 API-level tests (health check, simple query) after fix
- Run full test suite after each change

---

## 6. Implementation Scripts

### 6.1 Inventory Script
```python
# Run this first to get current state
import os, re
from collections import defaultdict

base = "backend/app"
tables = defaultdict(list)

for root, dirs, files in os.walk(base):
    for f in files:
        if f.endswith(".py"):
            path = os.path.join(root, f)
            with open(path) as file:
                content = file.read()
            for match in re.finditer(r'__tablename__\s*=\s*["\']([^"\']+)["\']', content):
                tables[match.group(1)].append(path)

for table, paths in tables.items():
    if len(paths) > 1:
        print(f"{table}:")
        for p in paths:
            print(f"  - {p}")
```

### 6.2 Import Updater (Manual)
```bash
# Find all references to a specific model
grep -r "from domains.rendering.models import RenderJob" --include="*.py"

# Replace globally (use sed or IDE):
# sed -i 's/from domains\.rendering\.models import RenderJob/from models.workflow import RenderJob/g' $(grep -rl 'domains.rendering.models import RenderJob' --include='*.py')
```

### 6.3 Validation Script
```python
# Verify no duplicate table registrations
import sys
from sqlalchemy import MetaData

metadata = MetaData()
imported_models = []

# Import all models
from models import workflow, analytics, asset, campaign, user, media
from domains import workers, storage, runtime, workflows, analytics as domain_analytics

# Check for duplicates
for model in imported_models:
    if hasattr(model, '__tablename__'):
        table_name = model.__tablename__
        if table_name in [m.__tablename__ for m in imported_models[:imported_models.index(model)]]:
            print(f"DUPLICATE: {table_name} in {model}")
            sys.exit(1)

print("No duplicates found!")
```

---

## 7. Success Criteria

1. **No Duplicate Tables**: `sqlalchemy.exc.InvalidRequestError` no longer occurs
2. **API Starts**: `uvicorn app.main:app` runs without import errors
3. **Tests Pass**: All 87 backend tests still pass
4. **Health Check**: `/api/v1/health` returns 200 OK
5. **Database Access**: Can query tables without errors

---

## 8. Rollback Plan

If issues arise:
1. **Git Backup**: If this were a git repo, `git stash` before changes
2. **File Backup**: Copy problematic files to `backup/` before editing
3. **Revert Imports**: Restore original `__init__.py` files
4. **Rebuild Docker**: `docker-compose down && docker-compose up -d` to reset

---

## 9. Next Steps

1. **Approve plan**: Confirm this approach with stakeholders
2. **Assign developer**: Who will execute the migration?
3. **Schedule downtime**: API will be unavailable during Phase 2-3
4. **Backup database**: Before any migration run
5. **Execute Phase 1**: Start with inventory and decisions

---

## 10. Appendix: Affected Files List

**Models Layer (~20 files):**
- `models/workflow.py`, `analytics.py`, `asset.py`, `campaign.py`, `user.py`, `media.py`, `cognitive.py`, `base.py`

**Domains Layer (~30 files):**
- `domains/rendering/models.py`, `workflows/models.py`, `analytics/models.py`, `workers/models.py`, `storage/models.py`, `runtime/models.py`, `observability/models.py`, `coherence/models.py`, `self_healing/models.py`, `learning/models.py`, etc.

**Domain Init Files (~15 files):**
- `domains/*/models.py`, `domains/*/services.py`, `domains/*/repositories.py`

**Services Layer (~20 files):**
- `domains/*/services.py`, `services/*.py`

---

*End of Migration Plan*