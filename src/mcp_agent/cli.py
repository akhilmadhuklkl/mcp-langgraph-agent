import argparse
import asyncio

from .graph import build_graph
from .mcp_client import MCPToolRegistry


async def run(request: str) -> None:
    registry = MCPToolRegistry()
    await registry.connect(["calendar", "tasks", "weather"])
    try:
        print("Discovered tools:")
        for name in sorted(registry.tools):
            print(f"  - {name}")
        result = await build_graph(registry).ainvoke({"request": request})
        print("\n" + result["answer"])
    finally:
        await registry.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("request")
    parser.add_argument("--model", action="store_true", help="Reserved for the model-backed planner")
    args = parser.parse_args()
    asyncio.run(run(args.request))


if __name__ == "__main__":
    main()
