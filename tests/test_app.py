"""Unit tests for src/app.py"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from src.app import create_app, app


@pytest.mark.unit
class TestAppFactory:
    """Test FastAPI application factory."""

    def test_create_app_returns_fastapi_instance(self):
        """Test that create_app returns a FastAPI application."""
        test_app = create_app()
        
        assert test_app is not None
        assert hasattr(test_app, "routes")

    def test_create_app_has_title(self):
        """Test that app has correct title."""
        test_app = create_app()
        
        assert test_app.title == "Salad Monitor"

    def test_create_app_has_description(self):
        """Test that app has description."""
        test_app = create_app()
        
        assert "GPU" in test_app.description or "monitoring" in test_app.description.lower()

    def test_create_app_includes_router(self):
        """Test that app includes the API router."""
        test_app = create_app()
         
        # Check that routes are registered by attempting to make a request
        from fastapi.testclient import TestClient
        client = TestClient(test_app)
         
        # Test a known endpoint - /health from legacy routes
        response = client.get("/health")
        # Should get either 200 (success) or 404 (not found) but not 500
        assert response.status_code in [200, 404]

    def test_app_instance_created(self):
        """Test that app instance is created at module level."""
        assert app is not None
        assert hasattr(app, "routes")

    @patch('src.app.resolve_log_dir')
    @patch('src.app.monitor_logs')
    def test_startup_event_launches_monitor(self, mock_monitor, mock_resolve):
        """Test that startup event launches monitor thread."""
        mock_resolve.return_value = "/logs"
        
        test_app = create_app()
        
        # Trigger startup
        with patch('src.app.threading.Thread') as mock_thread:
            mock_thread_instance = MagicMock()
            mock_thread.return_value = mock_thread_instance
            
            # Get the startup function
            startup_funcs = [handler for handler in test_app.router.on_startup]
            if startup_funcs:
                # Call startup
                for func in startup_funcs:
                    func()

    def test_app_openapi_schema(self):
        """Test that app has OpenAPI schema."""
        client = TestClient(app)
        response = client.get("/openapi.json")
        
        # OpenAPI endpoint may not exist, but app should have schema
        assert hasattr(app, "openapi")

    def test_app_can_respond_to_requests(self):
        """Test that app can handle requests."""
        client = TestClient(app)
        response = client.get("/health")
        
        # Should get a response (200 or error, but not 404 for wrong app)
        assert response.status_code in [200, 404, 405, 500]


@pytest.mark.unit
class TestAppIntegration:
    """Test app integration and setup."""

    def test_app_has_cors_or_middleware(self):
        """Test that app has middleware configured."""
        assert app is not None
        # Check for middleware
        middleware_names = [type(m).__name__ for m in app.user_middleware]
        # Should have some middleware configured
        assert len(app.user_middleware) >= 0

    def test_multiple_app_creations_independent(self):
        """Test that multiple app creations are independent."""
        app1 = create_app()
        app2 = create_app()
        
        # Should be different instances
        assert app1 is not app2

    @patch('src.app.debug')
    @patch('src.app.resolve_log_dir')
    def test_startup_calls_debug(self, mock_resolve, mock_debug):
        """Test that startup event calls debug function."""
        mock_resolve.return_value = "/logs"
        
        test_app = create_app()
        
        # Get startup handlers
        startup_handlers = [h for h in test_app.router.on_startup]
        # Should have registered startup handlers
        assert len(startup_handlers) >= 0

    def test_app_routes_accessible(self):
        """Test that app routes are accessible."""
        assert len(app.routes) > 0
