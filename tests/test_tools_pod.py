import pytest
from unittest.mock import patch, MagicMock
from tools import pod


@pytest.fixture
def mock_core_v1():
    with patch('tools.pod.get_api_clients') as mock_get_clients:
        mock_api = MagicMock()
        mock_get_clients.return_value = {"core": mock_api}
        yield mock_api


def test_pod_list(mock_core_v1):
    """Test pod_list functionality."""
    # Setup mock response
    mock_pod = MagicMock()
    mock_pod.metadata.name = "test-pod-1"
    mock_core_v1.list_namespaced_pod.return_value.items = [mock_pod]

    result = pod.pod_list(context_name="ctx", namespace="default")
    
    assert len(result) == 1
    assert result[0]["name"] == "test-pod-1"
    mock_core_v1.list_namespaced_pod.assert_called_once_with("default")


@pytest.mark.asyncio
async def test_pod_delete(mock_core_v1):
    """Test async pod_delete functionality."""
    # Setup mock response
    mock_response = MagicMock()
    mock_response.status = "Success"
    mock_core_v1.delete_namespaced_pod.return_value = mock_response

    # Test without ctx to skip logging side-effects
    result = await pod.pod_delete(context_name="ctx", namespace="default", name="target-pod")

    assert result["status"] == "Deleted"
    assert result["name"] == "target-pod"
    mock_core_v1.delete_namespaced_pod.assert_called_once_with(
        name="target-pod",
        namespace="default",
        body={}
    )
