import pytest
from unittest.mock import patch, MagicMock
from core import kubeconfig
import yaml
import os


@pytest.fixture(autouse=True)
def clear_client_cache():
    """Clear the client cache before and after each test."""
    kubeconfig._client_cache.clear()
    yield
    kubeconfig._client_cache.clear()


@patch('core.kubeconfig.config.load_kube_config')
@patch('core.kubeconfig.client.ApiClient')
@patch('core.kubeconfig.client.CoreV1Api')
@patch('core.kubeconfig.client.AppsV1Api')
@patch('core.kubeconfig.client.BatchV1Api')
@patch('core.kubeconfig.client.NetworkingV1Api')
@patch('core.kubeconfig.client.RbacAuthorizationV1Api')
def test_get_api_clients_creates_new(
    mock_rbac, mock_networking, mock_batch, mock_apps, mock_core, mock_api_client, mock_load_kube_config
):
    """Test that get_api_clients initializes and returns clients if not in cache."""
    context_name = "minikube"
    
    clients = kubeconfig.get_api_clients(context_name)
    
    assert mock_load_kube_config.called
    assert mock_api_client.called
    assert mock_core.called
    assert mock_apps.called
    assert mock_batch.called
    assert mock_networking.called
    assert mock_rbac.called
    
    assert "core" in clients
    assert "apps" in clients
    assert "batch" in clients
    assert "networking" in clients
    assert "rbac" in clients
    
    # Check that it's in the cache now
    assert context_name in kubeconfig._client_cache


@patch('core.kubeconfig.config.load_kube_config')
def test_get_api_clients_uses_cache(mock_load_kube_config):
    """Test that get_api_clients returns from cache without reloading."""
    context_name = "test-cluster"
    
    # Pre-populate cache
    fake_clients = {"core": "fake-core-client"}
    kubeconfig._client_cache[context_name] = fake_clients
    
    clients = kubeconfig.get_api_clients(context_name)
    
    # It should not call load_kube_config
    assert not mock_load_kube_config.called
    assert clients == fake_clients


@patch('builtins.open')
@patch('yaml.safe_load')
@patch('os.path.expanduser')
def test_get_kubeconfig(mock_expanduser, mock_safe_load, mock_open):
    """Test get_kubeconfig loading the default file."""
    mock_expanduser.return_value = "/path/to/fake/kube/config"
    mock_safe_load.return_value = {"clusters": [], "contexts": []}
    
    result = kubeconfig.get_kubeconfig()
    
    mock_expanduser.assert_called_once()
    mock_open.assert_called_once_with("/path/to/fake/kube/config", "r")
    assert result == {"clusters": [], "contexts": []}
