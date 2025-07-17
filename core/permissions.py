import functools
from typing import Callable, Any
from core.config import is_readonly_mode


def check_readonly_permission(func: Callable) -> Callable:
    """
    Decorator to check if an operation is allowed in readonly mode.
    
    This decorator should be applied to all write operations (create, update, delete).
    In readonly mode, these operations will raise a PermissionError.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        if is_readonly_mode():
            operation_name = func.__name__
            raise PermissionError(
                f"Operation '{operation_name}' is not allowed in readonly mode. "
                f"Only read/get operations are permitted when --readonly flag is used."
            )
        return func(*args, **kwargs)
    return wrapper


def is_write_operation(func_name: str) -> bool:
    """
    Check if a function name represents a write operation.
    
    Args:
        func_name: The name of the function to check
        
    Returns:
        True if the function is a write operation, False otherwise
    """
    write_operations = ['create', 'update', 'delete', 'patch', 'replace']
    return any(op in func_name.lower() for op in write_operations) 