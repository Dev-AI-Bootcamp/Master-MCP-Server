import asyncio
import sys
import traceback
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    try:
        # Define the stdio transport parameters correctly
        server_params = StdioServerParameters(
            command="python",
            args=["weather-mcp-server.py"],
        )

        # Use the stdio_client transport
        async with stdio_client(server_params) as (read, write):
            # Create a session over the transport
            async with ClientSession(read, write) as session:
                # Initialize the session (must do this first)
                await session.initialize()

                # List tools available on the server
                tools = await session.list_tools()
                print("Available tools:", [tool.name for tool in tools.tools])

                # Call your “get_weather” tool
                result = await session.call_tool("get_weather", {"city": "Miami"})
                print("Weather result:", result)
    except Exception as e:
        print("SERVER ERROR:", e, file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
