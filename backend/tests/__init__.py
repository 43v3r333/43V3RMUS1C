"""
43V3R CORE - Test Package
==========================

This package contains all test infrastructure for 43V3R CORE.

Structure:
- conftest.py: Shared fixtures and configuration
- pytest.ini: Pytest configuration
- pyproject.toml: Project configuration

Domains:
- unit/: Unit tests for individual components
- integration/: Integration tests for service interactions
- chaos/: Chaos engineering tests
- simulation/: Distributed simulation tests
- performance/: Performance and load tests

Markers:
- unit: Unit tests
- integration: Integration tests
- chaos: Chaos engineering tests
- simulation: Distributed simulation tests
- performance: Performance tests
- runtime: Runtime orchestration tests
- semantic: Semantic analysis tests
- governance: Governance system tests
- websocket: WebSocket communication tests
"""

__version__ = "1.0.0"
