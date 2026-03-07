"""
MCP Lektor Server implementation.
Registers tools and starts background tasks.
"""

import logging
import os
import asyncio
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

from mcp_lektor.tools.extract_document import extract_document
from mcp_lektor.tools.proofread_text import proofread_text
from mcp_lektor.tools.validate_bible_refs import validate_bible_refs
from mcp_lektor.tools.write_corrected_docx import write_corrected_docx
from mcp_lektor.core.session_manager import session_manager

# Load environment variables from .env if present
load_dotenv()

# Configure logging
log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
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

if __name__ == "__main__":
    # Get port from environment or default to 8080
    port = int(os.getenv("PORT", "8080"))
    
    # Run the server using SSE transport
    # Note: FastMCP.run() handles the event loop and transport setup
    mcp.run(transport="sse")
