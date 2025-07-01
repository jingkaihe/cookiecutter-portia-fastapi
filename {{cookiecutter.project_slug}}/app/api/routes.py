"""API routes for the Portia FastAPI integration."""

import time
from typing import Any

from fastapi import APIRouter, HTTPException, status
from loguru import logger
from portia import Config, Portia, PlanRunState, ToolRegistry
from portia.end_user import EndUser

from ..config import get_settings
from ..schemas import (
    PortiaRunRequest,
    PortiaRunResponse,
    PortiaStatusResponse,
    ClarificationResponse,
)
{%- if cookiecutter.include_example_tools == 'y' %}
from ..tools import custom_tools
{%- endif %}

router = APIRouter()

# Global Portia instance (initialized at startup)
_portia_instance: Portia | None = None


def get_portia() -> Portia:
    """Get the global Portia instance."""
    global _portia_instance

    if _portia_instance is None:
        settings = get_settings()

        # Validate that we have at least one LLM API key
        if not settings.has_llm_api_key():
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No LLM API key configured. Please set OPENAI_API_KEY or another supported LLM API key.",
            )

        # Create Portia configuration
        config = Config.from_default(
            default_log_level=settings.portia_log_level,
            storage_class=settings.get_portia_storage_class(),
        )

        # Initialize Portia with tools
        {%- if cookiecutter.include_example_tools == 'y' %}
        _portia_instance = Portia(
            config=config,
            tools=custom_tools,
        )

        logger.info(f"Initialized Portia with {len(custom_tools.get_tools())} tools")
        {%- else %}
        # Initialize without custom tools - you can add your own tools later
        _portia_instance = Portia(
            config=config,
            tools=ToolRegistry([]),  # Empty registry - add your tools here
        )

        logger.info("Initialized Portia with no tools - add your custom tools in app/tools/")
        {%- endif %}

    return _portia_instance


@router.get("/", response_model=PortiaStatusResponse)
async def get_status() -> PortiaStatusResponse:
    """Get the status of the API and available tools."""
    settings = get_settings()
    portia = get_portia()

    # Get available tool IDs
    tool_ids = [tool.id for tool in portia.tool_registry.get_tools()]

    return PortiaStatusResponse(
        status="healthy",
        version=settings.app_version,
        portia_version="0.4.3",  # You might want to get this dynamically
        available_tools=tool_ids,
    )


@router.post("/run", response_model=PortiaRunResponse)
async def run_query(request: PortiaRunRequest) -> PortiaRunResponse:
    """
    Execute a query using the Portia SDK.

    This endpoint accepts a query and optional tool list, executes it using
    the Portia SDK, and returns the result or any clarifications needed.
    """
    start_time = time.time()

    try:
        portia = get_portia()

        # Filter tools if specific ones are requested
        tools_to_use = portia.tool_registry
        if request.tools:
            # Create a new registry with only the requested tools
            filtered_tools = [
                tool for tool in portia.tool_registry.get_tools()
                if tool.id in request.tools
            ]

            if not filtered_tools:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"None of the requested tools found: {request.tools}",
                )

            tools_to_use = ToolRegistry(filtered_tools)

        # Create end user if provided
        end_user = None
        if request.user_id:
            end_user = EndUser(external_id=request.user_id)

        # Parse structured output schema if provided
        structured_output_schema = None
        if request.structured_output_schema:
            # In a real implementation, you'd convert the JSON schema to a Pydantic model
            # For now, we'll just pass it through
            structured_output_schema = request.structured_output_schema

        # Execute the query
        logger.info(f"Executing query: {request.query}")
        plan_run = portia.run(
            query=request.query,
            tools=tools_to_use,
            end_user=end_user,
            plan_run_inputs=request.plan_run_inputs,
            structured_output_schema=structured_output_schema,
        )

        # Prepare response based on plan run state
        result = None
        error = None
        clarifications = []

        if plan_run.state == PlanRunState.COMPLETE:
            if plan_run.outputs.final_output:
                result = plan_run.outputs.final_output.get_value()
        elif plan_run.state == PlanRunState.NEED_CLARIFICATION:
            # Get outstanding clarifications
            for clarification in plan_run.get_outstanding_clarifications():
                clarifications.append(
                    ClarificationResponse(
                        id=clarification.id,
                        question=clarification.question,
                        description=clarification.description,
                        options=clarification.options,
                    )
                )
        elif plan_run.state == PlanRunState.FAILED:
            error = "Plan execution failed"
            if plan_run.outputs.final_output:
                error = str(plan_run.outputs.final_output.get_value())

        # Calculate execution time
        execution_time = time.time() - start_time

        # Get tools that were actually used
        tools_used = []
        if hasattr(plan_run, "plan") and plan_run.plan:
            for step in plan_run.plan.steps:
                if hasattr(step, "tool_id") and step.tool_id:
                    tools_used.append(step.tool_id)

        return PortiaRunResponse(
            status=plan_run.state,
            result=result,
            clarifications=clarifications,
            plan_run_id=str(plan_run.id) if hasattr(plan_run, "id") else None,
            error=error,
            metadata={
                "execution_time": round(execution_time, 2),
                "tools_used": list(set(tools_used)),
                "tools_available": len(tools_to_use.get_tools()),
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error executing query")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing query: {str(e)}",
        )


@router.get("/tools", response_model=list[dict[str, Any]])
async def get_tools() -> list[dict[str, Any]]:
    """Get detailed information about available tools."""
    portia = get_portia()

    tools_info = []
    for tool in portia.tool_registry.get_tools():
        tool_info = {
            "id": tool.id,
            "name": tool.name,
            "description": tool.description,
        }

        # Add schema information if available
        if hasattr(tool, "args_schema") and tool.args_schema:
            try:
                tool_info["args_schema"] = tool.args_schema.model_json_schema()
            except Exception:
                tool_info["args_schema"] = None

        tools_info.append(tool_info)

    return tools_info
