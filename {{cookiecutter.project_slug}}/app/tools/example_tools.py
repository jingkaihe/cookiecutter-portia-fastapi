{%- if cookiecutter.include_example_tools == 'y' %}
"""Simple example tools demonstrating Portia tool patterns.

Each tool is kept under 15 lines to focus on core concepts:
- Using the @tool decorator
- Annotated parameters for documentation
- Different return types (str, dict, list)
- Basic error handling with ToolHardError
"""

import random
from typing import Annotated

from portia import tool, ToolHardError


@tool
def reverse_text(
    text: Annotated[str, "Text to reverse"],
) -> str:
    """Reverse the given text string."""
    return text[::-1]


@tool
def roll_dice(
    sides: Annotated[int, "Number of sides (4, 6, 8, 10, 12, 20)"] = 6,
) -> int:
    """Roll a single die and return the result."""
    if sides not in [4, 6, 8, 10, 12, 20]:
        raise ToolHardError(f"Invalid sides: {sides}")
    return random.randint(1, sides)


@tool
def add_numbers(
    a: Annotated[float, "First number"],
    b: Annotated[float, "Second number"],
) -> float:
    """Add two numbers together."""
    return a + b


@tool
def get_random_fact() -> str:
    """Get a random fun fact."""
    facts = [
        "Honey never spoils.",
        "Octopuses have three hearts.",
        "Bananas are berries, but strawberries aren't.",
        "A group of flamingos is called a 'flamboyance'.",
        "The moon is moving away from Earth at 1.5 inches per year.",
    ]
    return random.choice(facts)


@tool
def uppercase_text(
    text: Annotated[str, "Text to convert"],
    exclaim: Annotated[bool, "Add exclamation mark"] = False,
) -> str:
    """Convert text to uppercase."""
    result = text.upper()
    return f"{result}!" if exclaim else result


@tool
def count_letters(
    text: Annotated[str, "Text to analyze"],
) -> dict[str, int]:
    """Count letters and words in text."""
    return {
        "letters": len([c for c in text if c.isalpha()]),
        "words": len(text.split()),
        "total_chars": len(text),
    }
{%- else %}
# This file is not included when include_example_tools is 'n'
{%- endif %}
