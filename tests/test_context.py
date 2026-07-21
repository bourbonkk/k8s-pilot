import pytest
import asyncio
from unittest.mock import patch
from core import context


@patch('core.context.config.list_kube_config_contexts')
def test_get_current_context_name(mock_list_contexts):
    """Test getting the current context name."""
    mock_contexts = [{"name": "context1"}, {"name": "context2"}]
    mock_active = {"name": "context1"}
    mock_list_contexts.return_value = (mock_contexts, mock_active)
    
    result = context.get_current_context_name()
    assert result == "context1"


@patch('core.context.config.list_kube_config_contexts')
def test_get_default_namespace_found(mock_list_contexts):
    """Test getting the default namespace when specified in context."""
    mock_contexts = [
        {"name": "ctx1", "context": {"namespace": "custom-ns"}},
        {"name": "ctx2", "context": {}}
    ]
    mock_list_contexts.return_value = (mock_contexts, None)
    
    result = context.get_default_namespace("ctx1")
    assert result == "custom-ns"


@patch('core.context.config.list_kube_config_contexts')
def test_get_default_namespace_not_found(mock_list_contexts):
    """Test getting default namespace fallback."""
    mock_contexts = [{"name": "ctx2", "context": {}}]
    mock_list_contexts.return_value = (mock_contexts, None)
    
    result = context.get_default_namespace("ctx2")
    assert result == "default"


@patch('core.context.get_current_context_name')
@patch('core.context.get_default_namespace')
def test_use_current_context_sync(mock_get_default_namespace, mock_get_context):
    """Test decorator on a synchronous function."""
    mock_get_context.return_value = "auto-context"
    mock_get_default_namespace.return_value = "auto-namespace"
    
    @context.use_current_context
    def dummy_func(context_name: str, namespace: str):
        return context_name, namespace

    # Test auto-injection when kwargs missing
    assert dummy_func() == ("auto-context", "auto-namespace")
    
    # Test auto-injection when kwargs are None
    assert dummy_func(context_name=None, namespace=None) == ("auto-context", "auto-namespace")
    
    # Test overriding values
    assert dummy_func(context_name="manual-ctx", namespace="manual-ns") == ("manual-ctx", "manual-ns")


@patch('core.context.get_current_context_name')
@patch('core.context.get_default_namespace')
@pytest.mark.asyncio
async def test_use_current_context_async(mock_get_default_namespace, mock_get_context):
    """Test decorator on an asynchronous function."""
    mock_get_context.return_value = "async-auto-context"
    mock_get_default_namespace.return_value = "async-auto-namespace"
    
    @context.use_current_context
    async def dummy_async_func(context_name: str, namespace: str):
        return context_name, namespace

    # Test auto-injection
    assert await dummy_async_func() == ("async-auto-context", "async-auto-namespace")
