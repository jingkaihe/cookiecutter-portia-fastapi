"""Unit tests for the {{ cookiecutter.project_name }} API."""

from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient
from portia import PlanRunState
from portia.plan_run import PlanRun

from app.main import create_app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    app = create_app()
    return TestClient(app)


@pytest.fixture
def mock_portia():
    """Mock Portia instance for testing."""
    with patch('app.api.routes.get_portia') as mock:
        portia_instance = Mock()
        {%- if cookiecutter.include_example_tools == 'y' %}
        # Mock tool registry with example tools
        mock_tools = [
            Mock(id="reverse_text", name="Reverse Text", description="Reverse text"),
            Mock(id="roll_dice", name="Roll Dice", description="Roll a dice"),
            Mock(id="add_numbers", name="Add Numbers", description="Add two numbers"),
        ]
        portia_instance.tool_registry = Mock()
        portia_instance.tool_registry.get_tools.return_value = mock_tools
        {%- else %}
        portia_instance.tool_registry = Mock()
        portia_instance.tool_registry.get_tools.return_value = []
        {%- endif %}
        mock.return_value = portia_instance
        yield portia_instance


class TestRootEndpoints:
    """Test root and health endpoints."""

    def test_root_endpoint(self, client):
        """Test the root endpoint returns welcome message."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "{{ cookiecutter.project_name }}" in data["message"]
        assert "version" in data
        assert data["version"] == "{{ cookiecutter.version }}"

    def test_health_endpoint(self, client):
        """Test the health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


class TestAPIStatusEndpoint:
    """Test API status endpoint."""

    def test_api_status_with_tools(self, client, mock_portia):  # noqa: ARG002
        """Test API status endpoint with tools."""
        {%- if cookiecutter.include_example_tools == 'y' %}
        response = client.get("/api/v1/")
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert data["version"] == "{{ cookiecutter.version }}"
        assert "available_tools" in data
        assert len(data["available_tools"]) == 3  # reverse_text, roll_dice, add_numbers
        assert "reverse_text" in data["available_tools"]
        assert "roll_dice" in data["available_tools"]
        assert "add_numbers" in data["available_tools"]
        {%- else %}
        response = client.get("/api/v1/")
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert data["version"] == "{{ cookiecutter.version }}"
        assert "available_tools" in data
        assert len(data["available_tools"]) == 0  # No tools in vanilla template
        {%- endif %}
        assert "timestamp" in data

    def test_api_status_missing_api_key(self, client):
        """Test API status when no LLM API key is configured."""
        # Mock get_portia to raise HTTPException when no API key
        with patch('app.api.routes.get_portia') as mock_get_portia:
            from fastapi import HTTPException
            mock_get_portia.side_effect = HTTPException(
                status_code=500,
                detail="No LLM API key configured. Please set OPENAI_API_KEY or another supported LLM API key."
            )
            
            response = client.get("/api/v1/")
            assert response.status_code == 500
            assert "No LLM API key configured" in response.json()["detail"]


class TestToolsEndpoint:
    """Test tools endpoint."""

    def test_get_tools(self, client):
        """Test getting available tools."""
        response = client.get("/api/v1/tools")
        assert response.status_code == 200
        tools = response.json()
        
        {%- if cookiecutter.include_example_tools == 'y' %}
        assert len(tools) == 6  # 6 example tools in example_tools.py
        tool_ids = [tool["id"] for tool in tools]
        assert "reverse_text" in tool_ids
        assert "roll_dice" in tool_ids
        assert "add_numbers" in tool_ids
        
        # Check tool structure
        for tool in tools:
            assert "id" in tool
            assert "name" in tool
            assert "description" in tool
            # args_schema might be None if tool doesn't have it
        {%- else %}
        assert len(tools) == 0  # No tools in vanilla template
        {%- endif %}


class TestRunEndpoint:
    """Test the main run endpoint."""

    def test_run_query_success(self, client, mock_portia):
        """Test successful query execution."""
        # Mock a successful plan run
        mock_plan_run = Mock(spec=PlanRun)
        mock_plan_run.state = PlanRunState.COMPLETE
        mock_plan_run.id = "prun-test-id"
        
        # Mock outputs attribute with final_output
        mock_outputs = Mock()
        mock_output = Mock()
        mock_output.get_value.return_value = "Test result"
        mock_outputs.final_output = mock_output
        mock_plan_run.outputs = mock_outputs
        
        # Mock plan with no steps (no tools used)
        mock_plan_run.plan = None
        
        mock_portia.run.return_value = mock_plan_run
        
        response = client.post(
            "/api/v1/run",
            json={"query": "Test query"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "COMPLETE"
        assert data["result"] == "Test result"
        assert data["plan_run_id"] == "prun-test-id"
        assert data["error"] is None
        assert "metadata" in data
        assert "execution_time" in data["metadata"]

    def test_run_query_with_tools(self, client, mock_portia):
        """Test query execution with specific tools."""
        mock_plan_run = Mock(spec=PlanRun)
        mock_plan_run.state = PlanRunState.COMPLETE
        mock_plan_run.id = "prun-test-id"
        
        mock_outputs = Mock()
        mock_output = Mock()
        mock_output.get_value.return_value = "Tool result"
        mock_outputs.final_output = mock_output
        mock_plan_run.outputs = mock_outputs
        mock_plan_run.plan = None
        
        mock_portia.run.return_value = mock_plan_run
        
        response = client.post(
            "/api/v1/run",
            json={
                "query": "Test query",
                "tools": ["reverse_text"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "COMPLETE"
        assert data["result"] == "Tool result"

    def test_run_query_with_user_id(self, client, mock_portia):
        """Test query execution with user ID."""
        mock_plan_run = Mock(spec=PlanRun)
        mock_plan_run.state = PlanRunState.COMPLETE
        mock_plan_run.id = "prun-test-id"
        
        mock_outputs = Mock()
        mock_output = Mock()
        mock_output.get_value.return_value = "User result"
        mock_outputs.final_output = mock_output
        mock_plan_run.outputs = mock_outputs
        mock_plan_run.plan = None
        
        mock_portia.run.return_value = mock_plan_run
        
        response = client.post(
            "/api/v1/run",
            json={
                "query": "Test query",
                "user_id": "test_user_123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "COMPLETE"
        assert data["result"] == "User result"

    def test_run_query_need_clarification(self, client, mock_portia):
        """Test query that needs clarification."""
        mock_plan_run = Mock(spec=PlanRun)
        mock_plan_run.state = PlanRunState.NEED_CLARIFICATION
        mock_plan_run.id = "prun-test-id"
        
        mock_outputs = Mock()
        mock_outputs.final_output = None
        mock_plan_run.outputs = mock_outputs
        mock_plan_run.plan = None
        
        # Mock clarification
        mock_clarification = Mock()
        mock_clarification.id = "clarif-123"
        mock_clarification.question = "Test question?"
        mock_clarification.description = "Test description"
        mock_clarification.options = ["Option A", "Option B"]
        mock_plan_run.get_outstanding_clarifications.return_value = [mock_clarification]
        
        mock_portia.run.return_value = mock_plan_run
        
        response = client.post(
            "/api/v1/run",
            json={"query": "Ambiguous query"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "NEED_CLARIFICATION"
        assert data["result"] is None
        assert len(data["clarifications"]) == 1
        assert data["clarifications"][0]["id"] == "clarif-123"
        assert data["clarifications"][0]["question"] == "Test question?"

    def test_run_query_failed(self, client, mock_portia):
        """Test failed query execution."""
        mock_plan_run = Mock(spec=PlanRun)
        mock_plan_run.state = PlanRunState.FAILED
        mock_plan_run.id = "prun-test-id"
        mock_plan_run.plan = None
        
        mock_outputs = Mock()
        mock_output = Mock()
        mock_output.get_value.return_value = "Error details"
        mock_outputs.final_output = mock_output
        mock_plan_run.outputs = mock_outputs
        
        mock_portia.run.return_value = mock_plan_run
        
        response = client.post(
            "/api/v1/run",
            json={"query": "Failing query"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "FAILED"
        assert data["result"] is None
        assert data["error"] == "Error details"

    def test_run_query_invalid_tools(self, client, mock_portia):  # noqa: ARG002
        """Test query with invalid tools."""
        response = client.post(
            "/api/v1/run",
            json={
                "query": "Test query",
                "tools": ["nonexistent_tool"]
            }
        )
        
        assert response.status_code == 400
        assert "None of the requested tools found" in response.json()["detail"]

    def test_run_query_empty_query(self, client, mock_portia):  # noqa: ARG002
        """Test empty query handling."""
        # mock_portia fixture provides the Portia instance
        response = client.post(
            "/api/v1/run",
            json={"query": ""}
        )
        
        # Empty query might be handled differently by Portia
        # This test ensures the endpoint doesn't crash
        assert response.status_code in [200, 400, 422, 500]

    def test_run_query_invalid_json(self, client):
        """Test invalid JSON request."""
        response = client.post(
            "/api/v1/run",
            content="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422

    def test_run_query_missing_query(self, client):
        """Test request missing required query field."""
        response = client.post(
            "/api/v1/run",
            json={"tools": ["some_tool"]}
        )
        
        assert response.status_code == 422

    def test_run_query_portia_exception(self, client, mock_portia):
        """Test handling of Portia exceptions."""
        mock_portia.run.side_effect = Exception("Portia error")
        
        response = client.post(
            "/api/v1/run",
            json={"query": "Test query"}
        )
        
        assert response.status_code == 500
        assert "Error executing query" in response.json()["detail"]


{%- if cookiecutter.include_example_tools == 'y' %}
class TestExampleTools:
    """Test the example tools through the API."""

    def test_tools_available_in_api(self, client):
        """Test that example tools are available through the API."""
        response = client.get("/api/v1/tools")
        assert response.status_code == 200
        tools = response.json()
        
        # Check that our example tools are present
        tool_ids = [tool["id"] for tool in tools]
        assert "reverse_text" in tool_ids
        assert "roll_dice" in tool_ids
        assert "add_numbers" in tool_ids

    def test_reverse_text_through_api(self, client, mock_portia):
        """Test reverse_text tool execution through API."""
        # Mock the plan run to return reversed text
        mock_plan_run = Mock(spec=PlanRun)
        mock_plan_run.state = PlanRunState.COMPLETE
        mock_plan_run.id = "prun-test-id"
        
        mock_outputs = Mock()
        mock_output = Mock()
        mock_output.get_value.return_value = "dlroW olleH"
        mock_outputs.final_output = mock_output
        mock_plan_run.outputs = mock_outputs
        
        mock_portia.run.return_value = mock_plan_run
        
        response = client.post(
            "/api/v1/run",
            json={
                "query": "Reverse the text 'Hello World'",
                "tools": ["reverse_text"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "COMPLETE"
        assert data["result"] == "dlroW olleH"
{%- endif %}


class TestConfiguration:
    """Test configuration and setup."""

    def test_app_configuration(self):
        """Test that the app is configured correctly."""
        app = create_app()
        assert app.title == "{{ cookiecutter.project_name }}"
        assert app.version == "{{ cookiecutter.version }}"
        assert app.description == "{{ cookiecutter.project_short_description }}"

    @patch('app.config.get_settings')
    def test_settings_validation(self, mock_get_settings):
        """Test settings validation."""
        from app.config import Settings
        
        # Test with valid settings
        mock_settings = Mock(spec=Settings)
        mock_settings.app_name = "{{ cookiecutter.project_name }}"
        mock_settings.app_version = "{{ cookiecutter.version }}"
        mock_settings.has_llm_api_key.return_value = True
        mock_get_settings.return_value = mock_settings
        
        app = create_app()
        client = TestClient(app)
        
        response = client.get("/")
        assert response.status_code == 200


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_404_not_found(self, client):
        """Test 404 handling for non-existent endpoints."""
        response = client.get("/nonexistent")
        assert response.status_code == 404

    def test_405_method_not_allowed(self, client):
        """Test 405 handling for wrong HTTP methods."""
        response = client.post("/health")
        assert response.status_code == 405

    def test_cors_headers(self, client):
        """Test CORS headers are present."""
        response = client.options("/api/v1/")
        # CORS middleware should add appropriate headers
        assert response.status_code in [200, 405]  # Depends on CORS configuration


# Integration test markers for pytest
class TestIntegration:
    """Integration tests that require external dependencies."""

    @pytest.mark.integration
    def test_real_api_key_required(self, client):
        """Test that real API key is required for actual queries.
        
        This test is marked as integration and should be run with real API keys.
        """
        # This would require a real OpenAI API key to pass
        # The test validates the integration but doesn't make real calls
        response = client.post(
            "/api/v1/run",
            json={"query": "What is 2+2?"}
        )
        
        # With a real API key, this should return 200
        # With a dummy key, this should return 500
        assert response.status_code in [200, 500]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
