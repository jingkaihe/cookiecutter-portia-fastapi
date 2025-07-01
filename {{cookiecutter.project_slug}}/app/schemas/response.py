"""Response schemas for the Portia FastAPI integration."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class PlanRunState(str, Enum):
    """Possible states of a plan run."""

    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    NEED_CLARIFICATION = "NEED_CLARIFICATION"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"


class ClarificationResponse(BaseModel):
    """Schema for clarification requests."""

    id: str = Field(..., description="Unique ID of the clarification")
    question: str = Field(..., description="The question that needs clarification")
    description: str | None = Field(
        default=None, description="Additional context for the clarification"
    )
    options: list[str] | None = Field(
        default=None, description="Optional list of valid choices"
    )


class PortiaRunResponse(BaseModel):
    """Response schema for a Portia query execution."""

    status: PlanRunState = Field(..., description="Current status of the plan run")
    result: Any | None = Field(
        default=None,
        description="The final result if the run is complete",
    )
    clarifications: list[ClarificationResponse] = Field(
        default_factory=list,
        description="List of clarifications needed from the user",
    )
    plan_run_id: str | None = Field(
        default=None,
        description="ID of the plan run for tracking",
    )
    error: str | None = Field(
        default=None,
        description="Error message if the run failed",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the execution",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status": "COMPLETE",
                    "result": "Why do programmers prefer dark mode? Because light attracts bugs!",
                    "clarifications": [],
                    "plan_run_id": "run_abc123",
                    "error": None,
                    "metadata": {"execution_time": 1.2, "tools_used": ["generate_joke"]},
                },
                {
                    "status": "NEED_CLARIFICATION",
                    "result": None,
                    "clarifications": [
                        {
                            "id": "clarify_1",
                            "question": "Which type of dice would you like to roll?",
                            "description": "Please specify the dice configuration",
                            "options": ["d6", "d20", "2d6"],
                        }
                    ],
                    "plan_run_id": "run_def456",
                    "error": None,
                    "metadata": {},
                },
            ]
        }
    }


class PortiaStatusResponse(BaseModel):
    """Response schema for API status check."""

    status: str = Field(default="healthy", description="API health status")
    version: str = Field(..., description="API version")
    portia_version: str = Field(..., description="Portia SDK version")
    available_tools: list[str] = Field(..., description="List of available tool IDs")
    timestamp: datetime = Field(default_factory=datetime.now, description="Current timestamp")
