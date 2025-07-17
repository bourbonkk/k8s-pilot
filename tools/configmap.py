from core.context import use_current_context
from core.permissions import check_readonly_permission
from core.kubeconfig import get_api_clients
from server.server import mcp
from kubernetes.client import CoreV1Api


@mcp.tool()
@use_current_context
def configmap_list(context_name: str, namespace: str):
    """
    List all ConfigMaps in a given namespace.

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace

    Returns:
        List of ConfigMap basic information
    """
    core_v1: CoreV1Api = get_api_clients(context_name)["core"]
    configmaps = core_v1.list_namespaced_config_map(namespace)
    result = [{"name": cm.metadata.name} for cm in configmaps.items]
    return result


@mcp.tool()
@use_current_context
@check_readonly_permission
def configmap_create(context_name: str, namespace: str, name: str, data: dict):
    """
    Create a ConfigMap in the specified namespace.

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace
        name: The ConfigMap name
        data: The data to store in the ConfigMap

    Returns:
        Status of the creation operation
    """
    from kubernetes.client import V1ConfigMap, V1ObjectMeta

    core_v1: CoreV1Api = get_api_clients(context_name)["core"]
    configmap = V1ConfigMap(
        metadata=V1ObjectMeta(name=name),
        data=data
    )
    created_configmap = core_v1.create_namespaced_config_map(namespace=namespace, body=configmap)
    return {"name": created_configmap.metadata.name, "status": "Created"}


@mcp.tool()
@use_current_context
def configmap_get(context_name: str, namespace: str, name: str):
    """
    Get details of a specific ConfigMap.

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace
        name: The ConfigMap name

    Returns:
        Detailed information about the ConfigMap
    """
    core_v1: CoreV1Api = get_api_clients(context_name)["core"]
    configmap = core_v1.read_namespaced_config_map(name=name, namespace=namespace)
    return {"name": configmap.metadata.name, "data": configmap.data}


@mcp.tool()
@use_current_context
@check_readonly_permission
def configmap_update(context_name: str, namespace: str, name: str, data: dict):
    """
    Update an existing ConfigMap in the specified namespace.

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace
        name: The ConfigMap name
        data: The new data to update in the ConfigMap

    Returns:
        Status of the update operation
    """
    core_v1: CoreV1Api = get_api_clients(context_name)["core"]
    configmap = core_v1.read_namespaced_config_map(name=name, namespace=namespace)
    configmap.data = data
    updated_configmap = core_v1.replace_namespaced_config_map(name=name, namespace=namespace, body=configmap)
    return {"name": updated_configmap.metadata.name, "status": "Updated"}


@mcp.tool()
@use_current_context
@check_readonly_permission
def configmap_delete(context_name: str, namespace: str, name: str):
    """
    Delete a ConfigMap from the specified namespace.

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace
        name: The ConfigMap name

    Returns:
        Status of the deletion operation
    """
    core_v1: CoreV1Api = get_api_clients(context_name)["core"]
    core_v1.delete_namespaced_config_map(name=name, namespace=namespace)
    return {"name": name, "status": "Deleted"}
