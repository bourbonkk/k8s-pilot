from core.config import parse_arguments
from server.server import mcp  # noqa: F401

if __name__ == "__main__":
    # Parse command line arguments first
    parse_arguments()
    
    # Start the MCP server
    mcp.run(transport='stdio')