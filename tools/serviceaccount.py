from kubernetes.client import CoreV1Api, V1ServiceAccount, V1ObjectMeta
from core.context import use_current_context
from core.kubeconfig import get_api_clients
from server.server import mcp
from core.permissions import check_readonly_permission


@mcp.tool()
@use_current_context
def serviceaccount_list(context_name: str, namespace: str):
    """
    List all ServiceAccounts in a given namespace.

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace

    Returns:
        List of ServiceAccount basic information
    """
    core_v1: CoreV1Api = get_api_clients(context_name)["core"]
    serviceaccounts = core_v1.list_namespaced_service_account(namespace)
    result = [{"name": sa.metadata.name} for sa in serviceaccounts.items]
    return result


@mcp.tool()
@use_current_context
@check_readonly_permission
def serviceaccount_create(context_name: str, namespace: str, name: str, labels: dict = None):
    """
    Create a ServiceAccount in the specified namespace.

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace
        name: The ServiceAccount name
        labels: Optional labels to apply to the ServiceAccount

    Returns:
        Status of the creation operation
    """
    core_v1: CoreV1Api = get_api_clients(context_name)["core"]
    serviceaccount = V1ServiceAccount(
        metadata=V1ObjectMeta(name=name, labels=labels)
    )
    created_serviceaccount = core_v1.create_namespaced_service_account(namespace=namespace, body=serviceaccount)
    return {"name": created_serviceaccount.metadata.name, "status": "Created"}


@mcp.tool()
@use_current_context
def serviceaccount_get(context_name: str, namespace: str, name: str):
    """
    Get details of a specific ServiceAccount.

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace
        name: The ServiceAccount name

    Returns:
        Detailed information about the ServiceAccount
    """
    core_v1: CoreV1Api = get_api_clients(context_name)["core"]
    serviceaccount = core_v1.read_namespaced_service_account(name=name, namespace=namespace)
    return {
        "name": serviceaccount.metadata.name,
        "labels": serviceaccount.metadata.labels,
        "secrets": serviceaccount.secrets
    }


@mcp.tool()
@use_current_context
@check_readonly_permission
def serviceaccount_delete(context_name: str, namespace: str, name: str):
    """
    Delete a ServiceAccount from the specified namespace.

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace
        name: The ServiceAccount name

    Returns:
        Status of the deletion operation
    """
    core_v1: CoreV1Api = get_api_clients(context_name)["core"]
    core_v1.delete_namespaced_service_account(name=name, namespace=namespace)
    return {"name": name, "status": "Deleted"}