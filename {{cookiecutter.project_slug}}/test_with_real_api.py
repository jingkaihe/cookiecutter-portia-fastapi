"""Test script to verify the FastAPI Portia integration with real API calls.

This script tests all API endpoints and example tools with actual Portia/LLM interactions.
It requires:
- The API to be running (default: http://localhost:8000)
- A valid OpenAI API key (or other LLM provider) set in the environment

Usage:
    python test_with_real_api.py
    python test_with_real_api.py --url http://your-api-url:port
"""

import os
import sys
import time
from typing import Any

import httpx
from loguru import logger

# Configure logging
logger.remove()
logger.add(sys.stderr, level="INFO", format="{time:HH:mm:ss} | {level} | {message}")


def test_endpoints(base_url: str = "http://localhost:8000") -> None:
    """Test all API endpoints."""

    # Check if we have an API key
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY not set in environment")
        logger.info("Please set OPENAI_API_KEY to run tests")
        return

    client = httpx.Client(base_url=base_url, timeout=30.0)

    try:
        # Test root endpoint
        logger.info("Testing root endpoint...")
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        logger.success(f"Root endpoint: {data['message']}")

        # Test health endpoint
        logger.info("Testing health endpoint...")
        response = client.get("/health")
        assert response.status_code == 200
        logger.success("Health check passed")

        # Test status endpoint
        logger.info("Testing API status endpoint...")
        response = client.get("/api/v1/")
        assert response.status_code == 200
        status = response.json()
        logger.success(f"API Status: {status['status']}")
        logger.info(f"Available tools ({len(status['available_tools'])}): {', '.join(status['available_tools'])}")

        # Test tools endpoint
        logger.info("Testing tools endpoint...")
        response = client.get("/api/v1/tools")
        assert response.status_code == 200
        tools = response.json()
        logger.info(f"Found {len(tools)} tools:")
        for tool in tools:
            logger.info(f"  - {tool['id']}: {tool['description']}")

        # Check if we have example tools
        has_example_tools = len(status['available_tools']) > 0
        
        if has_example_tools:
            logger.info("\nExample tools detected. Running tool-specific tests...")
            
            # Test with specific tools
            if "roll_dice" in status['available_tools']:
                logger.info("\nTesting dice rolling...")
                test_query(
                    "Roll a 20-sided die",
                    client,
                    tools=["roll_dice"]
                )
            
            # Test text manipulation
            if "reverse_text" in status['available_tools']:
                logger.info("\nTesting text manipulation...")
                test_query(
                    "Reverse the text 'Hello World'",
                    client,
                    tools=["reverse_text"]
                )
            
            # Test math operation
            if "add_numbers" in status['available_tools']:
                logger.info("\nTesting math operation...")
                test_query(
                    "Add 42.5 and 17.3",
                    client,
                    tools=["add_numbers"]
                )
            
            # Test uppercase with exclamation
            if "uppercase_text" in status['available_tools']:
                logger.info("\nTesting uppercase conversion...")
                test_query(
                    "Convert 'hello world' to uppercase with excitement",
                    client,
                    tools=["uppercase_text"]
                )
            
            # Test text analysis
            if "count_letters" in status['available_tools']:
                logger.info("\nTesting text analysis...")
                test_query(
                    "Count the letters in 'The quick brown fox jumps over the lazy dog'",
                    client,
                    tools=["count_letters"]
                )
            
            # Test multiple tools
            if "get_random_fact" in status['available_tools'] and "count_letters" in status['available_tools']:
                logger.info("\nTesting multiple tools...")
                test_query(
                    "Get a random fact and then count how many letters it has",
                    client,
                    tools=["get_random_fact", "count_letters"]
                )
        else:
            logger.warning("No example tools found. Testing with LLM-only queries...")
        
        # Test basic query (works with or without tools)
        logger.info("\nTesting basic query...")
        test_query("What is 2 + 2?", client)
        
        # Test with user ID
        logger.info("\nTesting with user ID...")
        test_query(
            "Tell me a joke about programming",
            client,
            user_id="test_user_123"
        )

        # Test error handling
        logger.info("\nTesting error handling...")
        test_error_handling(client)

        logger.success("\nAll tests passed! 🎉")

    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise
    finally:
        client.close()


def test_query(
    query: str,
    client: httpx.Client,
    tools: list[str] | None = None,
    user_id: str | None = None
) -> dict[str, Any]:
    """Test a single query."""
    logger.info(f"Query: {query}")

    payload = {"query": query}
    if tools:
        payload["tools"] = tools
    if user_id:
        payload["user_id"] = user_id

    start_time = time.time()
    response = client.post("/api/v1/run", json=payload)
    execution_time = time.time() - start_time

    assert response.status_code == 200
    result = response.json()

    logger.info(f"Status: {result['status']}")
    logger.info(f"Execution time: {execution_time:.2f}s")

    if result["result"]:
        logger.success(f"Result: {result['result']}")

    if result["clarifications"]:
        logger.warning(f"Clarifications needed: {result['clarifications']}")

    if result["error"]:
        logger.error(f"Error: {result['error']}")

    if "metadata" in result:
        logger.debug(f"Metadata: {result['metadata']}")

    return result


def test_error_handling(client: httpx.Client) -> None:
    """Test error handling."""

    # Test with invalid tools
    logger.info("Testing with invalid tools...")
    response = client.post(
        "/api/v1/run",
        json={
            "query": "Test query",
            "tools": ["nonexistent_tool"]
        }
    )
    if response.status_code == 400:
        error = response.json()
        logger.info(f"Expected error: {error['detail']}")
    else:
        # If no tools are configured, this might succeed
        logger.info(f"Response status: {response.status_code}")

    # Test with empty query
    logger.info("Testing with empty query...")
    response = client.post(
        "/api/v1/run",
        json={"query": ""}
    )
    # This might succeed with Portia, depending on how it handles empty queries
    logger.info(f"Empty query response status: {response.status_code}")
    
    # Test with invalid JSON
    logger.info("Testing with invalid request body...")
    try:
        response = client.post(
            "/api/v1/run",
            content="invalid json",
            headers={"Content-Type": "application/json"}
        )
        logger.info(f"Invalid JSON response status: {response.status_code}")
    except Exception as e:
        logger.info(f"Expected error for invalid JSON: {type(e).__name__}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test Portia FastAPI integration")
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="Base URL of the API (default: http://localhost:8000)"
    )

    args = parser.parse_args()

    logger.info(f"Testing API at {args.url}")
    logger.info("Make sure the API is running and OPENAI_API_KEY is set")

    try:
        test_endpoints(args.url)
    except KeyboardInterrupt:
        logger.warning("Tests interrupted by user")
    except Exception as e:
        logger.error(f"Tests failed: {e}")
        sys.exit(1)
