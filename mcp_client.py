import os
import sys
import asyncio
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()


class MCPManager:
    _client = None
    _tools = None

    @classmethod
    async def get_tools(cls):
        if cls._tools is not None:
            return cls._tools

        # 1. Fallback check for token under common variable names
        token = (
            os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
            or os.getenv("GITHUB_TOKEN")
            or os.getenv("GITHUB_PAT")
        )

        if not token:
            print("⚠️ GITHUB_PERSONAL_ACCESS_TOKEN is missing in .env!")
            cls._tools = []
            return cls._tools

        # 2. Use npx.cmd on Windows, npx on Linux/macOS
        npx_command = "npx.cmd" if sys.platform == "win32" else "npx"

        # 3. Preserve existing system environment (including PATH)
        full_env = {
            **os.environ,
            "GITHUB_PERSONAL_ACCESS_TOKEN": token,
        }

        if cls._client is None:
            cls._client = MultiServerMCPClient(
                {
                    "github": {
                        "command": npx_command,
                        "args": [
                            "-y",  # Auto-confirm package installation
                            "@modelcontextprotocol/server-github",
                        ],
                        "transport": "stdio",
                        "env": full_env,
                    }
                }
            )

        try:
            # 4. Increased timeout to 30 seconds for initial npx download
            cls._tools = await asyncio.wait_for(
                cls._client.get_tools(), timeout=50.0
            )
            print(f"✅ Loaded {len(cls._tools)} MCP tools successfully.")
        except asyncio.TimeoutError:
            print("⚠️ MCP Server connection timed out. Falling back to local tools.")
            cls._tools = []
        except Exception as e:
            print(f"⚠️ Failed to connect to MCP Server: {e}")
            cls._tools = []

        return cls._tools