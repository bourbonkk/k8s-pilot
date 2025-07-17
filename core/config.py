import argparse

# Global readonly state
_readonly_mode: bool = False

def parse_arguments() -> None:
    """Parse command line arguments and set global configuration."""
    global _readonly_mode
    
    parser = argparse.ArgumentParser(description='K8s Pilot - Kubernetes management tool')
    parser.add_argument('--readonly', action='store_true', 
                       help='Enable readonly mode - only allow read/get operations')
    
    # Parse arguments from sys.argv
    args, unknown = parser.parse_known_args()
    
    _readonly_mode = args.readonly


def is_readonly_mode() -> bool:
    """Check if readonly mode is enabled."""
    return _readonly_mode


def get_readonly_mode() -> bool:
    """Get the current readonly mode setting."""
    return _readonly_mode 