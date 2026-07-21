import argparse

# Global readonly state
_readonly_mode: bool = False
_transport: str = 'stdio'

def parse_arguments() -> None:
    """Parse command line arguments and set global configuration."""
    global _readonly_mode, _transport
    
    parser = argparse.ArgumentParser(description='K8s Pilot - Kubernetes management tool')
    parser.add_argument('--readonly', action='store_true', 
                       help='Enable readonly mode - only allow read/get operations')
    parser.add_argument('--transport', choices=['stdio', 'streamable-http'], default='stdio',
                       help='MCP transport protocol')
    
    # Parse arguments from sys.argv
    args, unknown = parser.parse_known_args()
    
    _readonly_mode = args.readonly
    _transport = args.transport


def is_readonly_mode() -> bool:
    """Check if readonly mode is enabled."""
    return _readonly_mode


def get_readonly_mode() -> bool:
    """Get the current readonly mode setting."""
    return _readonly_mode


def get_transport() -> str:
    """Get the current transport protocol."""
    return _transport