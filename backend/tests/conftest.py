"""Pytest fixtures and test-wide setup.

This centralizes `sys.path` insertion and provides a `client` fixture
so tests don't need to duplicate path hacks or TestClient creation.
"""

import os
import sys
import pytest
from fastapi.testclient import TestClient

# Ensure the `backend` package directory is on sys.path so top-level
# `app` imports resolve during pytest collection. Insert the backend
# root before attempting to import `app`.
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.main import create_app


@pytest.fixture(scope="session")
def app():
    """Create and return the FastAPI application for the test session.

    Using the fixture name `app` matches common pytest patterns used in
    the test suite and allows tests to request `app` directly.
    """
    return create_app()


@pytest.fixture(scope="session")
def test_app(app):
    """Alias fixture kept for backward compatibility with tests that
    might request `test_app` specifically.
    """
    return app


@pytest.fixture
def client(app):
    """Provide a TestClient instance for tests using the application.

    Accepts the `app` fixture and returns a configured TestClient.
    """
    return TestClient(app)
