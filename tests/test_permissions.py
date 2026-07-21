import pytest
from core.permissions import check_readonly_permission, is_write_operation
from core import config


@pytest.fixture(autouse=True)
def reset_config_state():
    """Ensure config state is reset before and after each test."""
    config._readonly_mode = False
    yield
    config._readonly_mode = False


def test_is_write_operation():
    """Test the is_write_operation helper function."""
    # Write operations
    assert is_write_operation("pod_create") is True
    assert is_write_operation("update_deployment") is True
    assert is_write_operation("delete_namespace") is True
    assert is_write_operation("patch_node") is True
    assert is_write_operation("replace_secret") is True
    
    # Read operations
    assert is_write_operation("get_pods") is False
    assert is_write_operation("list_namespaces") is False
    assert is_write_operation("describe_node") is False


def test_check_readonly_permission_sync_allowed():
    """Test that a sync function is allowed when readonly is False."""
    @check_readonly_permission
    def test_func():
        return "success"
        
    config._readonly_mode = False
    assert test_func() == "success"


def test_check_readonly_permission_sync_blocked():
    """Test that a sync function is blocked when readonly is True."""
    @check_readonly_permission
    def test_func():
        return "success"
        
    config._readonly_mode = True
    with pytest.raises(PermissionError) as exc_info:
        test_func()
    assert "not allowed in readonly mode" in str(exc_info.value)


@pytest.mark.asyncio
async def test_check_readonly_permission_async_allowed():
    """Test that an async function is allowed when readonly is False."""
    @check_readonly_permission
    async def async_test_func():
        return "success"
        
    config._readonly_mode = False
    result = await async_test_func()
    assert result == "success"


@pytest.mark.asyncio
async def test_check_readonly_permission_async_blocked():
    """Test that an async function is blocked when readonly is True."""
    @check_readonly_permission
    async def async_test_func():
        return "success"
        
    config._readonly_mode = True
    with pytest.raises(PermissionError) as exc_info:
        await async_test_func()
    assert "not allowed in readonly mode" in str(exc_info.value)
