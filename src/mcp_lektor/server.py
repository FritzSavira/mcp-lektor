"""
MCP Lektor Server implementation.
Registers tools and starts background tasks.
"""

import logging
import asyncio
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

from mcp_lektor.tools.extract_document import extract_document
from mcp_lektor.tools.proofread_text import proofread_text
from mcp_lektor.tools.validate_bible_refs import validate_bible_refs
from mcp_lektor.tools.write_corrected_docx import write_corrected_docx
from mcp_lektor.core.session_manager import session_manager
from mcp_lektor.config.settings import get_settings

# Load environment variables from .env if present
load_dotenv()

# Get settings
settings = get_settings()

# Configure logging
log_level_str = settings.server.log_level.upper()
logging.basicConfig(
    level=log_level_str,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("mcp-lektor")

# Initialize FastMCP server
mcp = FastMCP("MCP Lektor")

# Register tools
mcp.tool()(extract_document)
mcp.tool()(proofread_text)
mcp.tool()(validate_bible_refs)
mcp.tool()(write_corrected_docx)

async def main():
    """Main entry point for the server."""
    # Start background tasks
    await session_manager.start_cleanup_task()
    
    # Run the server using SSE transport
    # Note: FastMCP.run() handles the event loop and transport setup internally
    # but if we want to run background tasks we might need a custom runner or 
    # use FastMCP's app directly.
    # For now, we follow the established pattern.
    mcp.run(transport="sse")

if __name__ == "__main__":
    # We use mcp.run() directly as it is standard for FastMCP
    # Background tasks should ideally be started via a lifespan handler
    # but FastMCP doesn't expose it easily in this version.
    # However, since mcp.run starts the loop, we start tasks before.
    
    # Run background cleanup (async task started in current loop)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(session_manager.start_cleanup_task())
    
    mcp.run(transport="sse")
