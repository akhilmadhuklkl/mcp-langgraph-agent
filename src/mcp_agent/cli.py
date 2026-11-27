import argparse
import asyncio

from .graph import build_graph
from .catalog import format_catalog
from .mcp_client import MCPToolRegistry
from .state import initial_state
from .trace import format_trace


async def run(request: str, planner_mode: str = "deterministic") -> None:
    registry = MCPToolRegistry()
    await registry.connect(["github", "gmail", "notion"])
    try:
        print(format_catalog(registry.catalog()))
        result = await build_graph(registry).ainvoke(initial_state(request, planner_mode))
        print("\n" + format_trace(result.get("trace", [])))
        print("\n" + result["answer"])
    finally:
        await registry.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("request")
    parser.add_argument("--model", action="store_true", help="Use the LLM planner; requires OPENAI_API_KEY and the model extra")
    args = parser.parse_args()
    asyncio.run(run(args.request, "llm" if args.model else "deterministic"))


if __name__ == "__main__":
    main()
