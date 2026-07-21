import asyncio
import inspect
from functools import wraps
from typing import Callable

from kubernetes import config


def get_current_context_name() -> str:
    """
    Get the name of the current Kubernetes context.

    Returns:
        The name of the current Kubernetes context
    """
    # Load the kube config
    _, active_context = config.list_kube_config_contexts()

    # Return the name of the active context
    return active_context['name']


def get_default_namespace(context_name: str) -> str:
    """
    Get the default namespace for a given context.
    If no default namespace is set, return "default".

    Args:
        context_name: The Kubernetes context name

    Returns:
        The default namespace for the context
    """
    # Load the kube config
    contexts, _ = config.list_kube_config_contexts()

    # Find the specified context
    for ctx in contexts:
        if ctx['name'] == context_name:
            # Get the default namespace if set
            context_data = ctx['context']
            return context_data.get('namespace', 'default')

    # If context not found or no namespace specified, return "default"
    return 'default'


def use_current_context(func: Callable) -> Callable:
    """
    Decorator that automatically uses the current Kubernetes context
    if context_name is None or not provided.

    Args:
        func: The function to decorate

    Returns:
        The decorated function
    """
    def _inject_defaults(kwargs):
        sig = inspect.signature(func)
        if 'context_name' in sig.parameters:
            if 'context_name' not in kwargs or kwargs['context_name'] is None:
                kwargs['context_name'] = get_current_context_name()
            context_name = kwargs['context_name']
            if 'namespace' in sig.parameters:
                if 'namespace' not in kwargs or kwargs['namespace'] is None:
                    kwargs['namespace'] = get_default_namespace(context_name)

    if asyncio.iscoroutinefunction(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            _inject_defaults(kwargs)
            return await func(*args, **kwargs)
        return async_wrapper
    else:
        @wraps(func)
        def wrapper(*args, **kwargs):
            _inject_defaults(kwargs)
            return func(*args, **kwargs)
        return wrapper
