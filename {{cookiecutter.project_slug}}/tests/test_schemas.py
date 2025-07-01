"""Tests for Pydantic schemas."""

import pytest
from pydantic import ValidationError

from app.schemas.request import PortiaRunRequest
from app.schemas.response import (
    ClarificationResponse,
    PortiaRunResponse,
    PortiaStatusResponse,
)


class TestPortiaRunRequest:
    """Test the PortiaRunRequest schema."""

    def test_valid_request_minimal(self):
        """Test valid minimal request."""
        data = {"query": "What is 2+2?"}
        request = PortiaRunRequest(**data)  # type: ignore[arg-type]
        assert request.query == "What is 2+2?"
        assert request.tools is None
        assert request.user_id is None
        assert request.plan_run_inputs is None
        assert request.structured_output_schema is None

    def test_valid_request_full(self):
        """Test valid request with all fields."""
        data = {
            "query": "Add these numbers",
            "tools": ["add_numbers"],
            "user_id": "user123",
            "plan_run_inputs": {"x": 5, "y": 10},
            "structured_output_schema": {"type": "object"}
        }
        request = PortiaRunRequest(**data)
        assert request.query == "Add these numbers"
        assert request.tools == ["add_numbers"]
        assert request.user_id == "user123"
        assert request.plan_run_inputs == {"x": 5, "y": 10}
        assert request.structured_output_schema == {"type": "object"}

    def test_invalid_request_missing_query(self):
        """Test invalid request missing query."""
        with pytest.raises(ValidationError) as exc_info:
            PortiaRunRequest(tools=["some_tool"])  # type: ignore[call-arg]
        
        assert "query" in str(exc_info.value)

    def test_invalid_request_empty_query(self):
        """Test request with empty query."""
        data = {"query": ""}
        request = PortiaRunRequest(**data)  # type: ignore[arg-type]
        assert request.query == ""  # Empty string is valid

    def test_invalid_request_wrong_types(self):
        """Test request with wrong field types."""
        with pytest.raises(ValidationError):
            PortiaRunRequest(query=123)  # type: ignore[arg-type]  # Should be string
        
        with pytest.raises(ValidationError):
            PortiaRunRequest(query="test", tools="not_a_list")  # type: ignore[arg-type]  # Should be list


class TestPortiaStatusResponse:
    """Test the PortiaStatusResponse schema."""

    def test_valid_status_response(self):
        """Test valid status response."""
        data = {
            "status": "healthy",
            "version": "1.0.0",
            "portia_version": "0.4.3",
            "available_tools": ["tool1", "tool2"]
        }
        response = PortiaStatusResponse(**data)
        assert response.status == "healthy"
        assert response.version == "1.0.0"
        assert response.portia_version == "0.4.3"
        assert response.available_tools == ["tool1", "tool2"]
        assert response.timestamp is not None

    def test_status_response_with_timestamp(self):
        """Test status response with explicit timestamp."""
        from datetime import datetime
        timestamp = datetime.now()
        
        data = {
            "status": "healthy",
            "version": "1.0.0",
            "portia_version": "0.4.3",
            "available_tools": [],
            "timestamp": timestamp
        }
        response = PortiaStatusResponse(**data)
        assert response.timestamp == timestamp


class TestPortiaRunResponse:
    """Test the PortiaRunResponse schema."""

    def test_valid_run_response_complete(self):
        """Test valid run response for completed execution."""
        data = {
            "status": "COMPLETE",
            "result": "The answer is 42",
            "clarifications": [],
            "plan_run_id": "prun-123",
            "error": None,
            "metadata": {"execution_time": 5.2}
        }
        response = PortiaRunResponse(**data)
        assert response.status == "COMPLETE"
        assert response.result == "The answer is 42"
        assert response.clarifications == []
        assert response.plan_run_id == "prun-123"
        assert response.error is None
        assert response.metadata == {"execution_time": 5.2}

    def test_valid_run_response_with_clarifications(self):
        """Test valid run response with clarifications."""
        clarification_data = {
            "id": "clarif-123",
            "question": "Which option?",
            "description": "Please choose",
            "options": ["A", "B"]
        }
        
        data = {
            "status": "NEED_CLARIFICATION",
            "result": None,
            "clarifications": [clarification_data],
            "plan_run_id": "prun-456",
            "error": None,
            "metadata": {}
        }
        response = PortiaRunResponse(**data)
        assert response.status == "NEED_CLARIFICATION"
        assert len(response.clarifications) == 1
        assert response.clarifications[0].id == "clarif-123"

    def test_valid_run_response_failed(self):
        """Test valid run response for failed execution."""
        data = {
            "status": "FAILED",
            "result": None,
            "clarifications": [],
            "plan_run_id": "prun-789",
            "error": "Something went wrong",
            "metadata": {"execution_time": 1.5}
        }
        response = PortiaRunResponse(**data)
        assert response.status == "FAILED"
        assert response.result is None
        assert response.error == "Something went wrong"

    def test_invalid_run_response_missing_required(self):
        """Test invalid run response missing required fields."""
        with pytest.raises(ValidationError):
            PortiaRunResponse(result="test")  # type: ignore[call-arg]  # Missing status


class TestClarificationResponse:
    """Test the ClarificationResponse schema."""

    def test_valid_clarification_with_options(self):
        """Test valid clarification with options."""
        data = {
            "id": "clarif-123",
            "question": "Which color?",
            "description": "Choose your favorite color",
            "options": ["Red", "Blue", "Green"]
        }
        clarification = ClarificationResponse(**data)
        assert clarification.id == "clarif-123"
        assert clarification.question == "Which color?"
        assert clarification.description == "Choose your favorite color"
        assert clarification.options == ["Red", "Blue", "Green"]

    def test_valid_clarification_without_options(self):
        """Test valid clarification without options."""
        data = {
            "id": "clarif-456",
            "question": "What is your name?",
            "description": "Please provide your name",
            "options": None
        }
        clarification = ClarificationResponse(**data)
        assert clarification.options is None

    def test_invalid_clarification_missing_required(self):
        """Test invalid clarification missing required fields."""
        with pytest.raises(ValidationError):
            ClarificationResponse(question="Test?")  # type: ignore[call-arg]  # Missing id