{%- if cookiecutter.include_example_tools == 'y' %}
"""Example tools for {{ cookiecutter.project_name }}."""

from portia import ToolRegistry

from .example_tools import (
    add_numbers,
    count_letters,
    get_random_fact,
    reverse_text,
    roll_dice,
    uppercase_text,
)

# Create a registry with all example tools
custom_tools = ToolRegistry([
    add_numbers(),  # type: ignore[call-arg]
    count_letters(),  # type: ignore[call-arg]
    get_random_fact(),  # type: ignore[call-arg]
    reverse_text(),  # type: ignore[call-arg]
    roll_dice(),  # type: ignore[call-arg]
    uppercase_text(),  # type: ignore[call-arg]
])

__all__ = ["custom_tools"]
{%- else %}
"""Custom tools for {{ cookiecutter.project_name }}.

Add your custom tools in this module and register them in a ToolRegistry.

Example:
    from portia import ToolRegistry, tool
    from typing import Annotated

    @tool
    def my_tool(param: Annotated[str, "Parameter description"]) -> str:
        '''Tool description.'''
        return f"Result: {param}"

    custom_tools = ToolRegistry([my_tool()])
"""

from portia import ToolRegistry

# Create an empty registry - add your tools here
custom_tools = ToolRegistry([])

__all__ = ["custom_tools"]
{%- endif %}
