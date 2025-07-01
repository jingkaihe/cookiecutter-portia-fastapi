{%- if cookiecutter.include_example_tools == 'y' %}
"""Example tools for {{ cookiecutter.project_name }}."""

from portia import ToolRegistry

from .example_tools import (
    reverse_text,
    roll_dice,
    add_numbers,
    get_random_fact,
    uppercase_text,
    count_letters,
)

# Create a registry with all example tools
custom_tools = ToolRegistry([
    reverse_text(),
    roll_dice(),
    add_numbers(),
    get_random_fact(),
    uppercase_text(),
    count_letters(),
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
