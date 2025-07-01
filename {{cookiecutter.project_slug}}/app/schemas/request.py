"""Request schemas for the Portia FastAPI integration."""

from typing import Any

from pydantic import BaseModel, Field


class PortiaRunRequest(BaseModel):
    """Request schema for running a Portia query."""

    query: str = Field(
        ...,
        description="The query or task to execute",
        examples=["Tell me a joke about programming", "Roll 2d6 dice"],
    )
    tools: list[str] | None = Field(
        default=None,
        description="Optional list of tool IDs to use. If not provided, all available tools will be used.",
        examples=[["generate_joke", "roll_dice"]],
    )
    user_id: str | None = Field(
        default=None,
        description="Optional user ID for attribution and tracking",
        examples=["user_123"],
    )
    plan_run_inputs: dict[str, Any] | None = Field(
        default=None,
        description="Optional input variables for the plan run",
        examples=[{"$city": "London", "$temperature_unit": "celsius"}],
    )
    structured_output_schema: dict[str, Any] | None = Field(
        default=None,
        description="Optional JSON schema for structured output validation",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "query": "Tell me a programming joke",
                    "tools": ["generate_joke"],
                },
                {
                    "query": "Roll 3d6 and tell me my fortune",
                    "tools": ["roll_dice", "tell_fortune"],
                    "user_id": "player_456",
                },
                {
                    "query": "Generate a joke about food",
                    "plan_run_inputs": {"$topic": "food"},
                },
            ]
        }
    }
