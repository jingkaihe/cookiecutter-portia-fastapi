"""Test script to verify the FastAPI Portia integration with real API calls."""

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
        logger.info(f"Available tools: {', '.join(status['available_tools'])}")

        # Test tools endpoint
        logger.info("Testing tools endpoint...")
        response = client.get("/api/v1/tools")
        assert response.status_code == 200
        tools = response.json()
        for tool in tools:
            logger.info(f"  - {tool['id']}: {tool['description']}")

        # Test basic query
        logger.info("\nTesting basic query...")
        test_query("Tell me a programming joke", client)

        # Test with specific tools
        logger.info("\nTesting with specific tools...")
        test_query(
            "Roll 2 six-sided dice",
            client,
            tools=["roll_dice"]
        )

        # Test multiple tools
        logger.info("\nTesting multiple tools...")
        test_query(
            "Roll some dice and then tell me my fortune",
            client,
            tools=["roll_dice", "tell_fortune"]
        )

        # Test with user ID
        logger.info("\nTesting with user ID...")
        test_query(
            "Generate a joke about food",
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
    assert response.status_code == 400
    error = response.json()
    logger.info(f"Expected error: {error['detail']}")

    # Test with empty query
    logger.info("Testing with empty query...")
    response = client.post(
        "/api/v1/run",
        json={"query": ""}
    )
    # This might succeed with Portia, depending on how it handles empty queries
    logger.info(f"Empty query response status: {response.status_code}")


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
