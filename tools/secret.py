from kubernetes.client import CoreV1Api, V1Secret, V1ObjectMeta
from core.context import use_current_context
from core.kubeconfig import get_api_clients
from server.server import mcp
from core.permissions import check_readonly_permission
import base64


@mcp.tool()
@use_current_context
def secret_list(context_name: str, namespace: str):
    """
    List all Secrets in a given namespace.

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace

    Returns:
        List of Secret basic information
    """
    core_v1: CoreV1Api = get_api_clients(context_name)["core"]
    secrets = core_v1.list_namespaced_secret(namespace)
    result = [{"name": secret.metadata.name, "type": secret.type} for secret in secrets.items]
    return result


@mcp.tool()
@use_current_context
@check_readonly_permission
def secret_create(context_name: str, namespace: str, name: str, data: dict, secret_type: str = "Opaque"):
    """
    Create a Secret in the specified namespace.

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace
        name: The Secret name
        data: A dictionary of key-value pairs (values will be base64 encoded)
        secret_type: The type of the Secret (default is "Opaque")

    Returns:
        Status of the creation operation
    """
    core_v1: CoreV1Api = get_api_clients(context_name)["core"]
    encoded_data = {key: base64.b64encode(value.encode()).decode() for key, value in data.items()}
    secret = V1Secret(
        metadata=V1ObjectMeta(name=name),
        data=encoded_data,
        type=secret_type
    )
    created_secret = core_v1.create_namespaced_secret(namespace=namespace, body=secret)
    return {"name": created_secret.metadata.name, "status": "Created"}


@mcp.tool()
@use_current_context
def secret_get(context_name: str, namespace: str, name: str):
    """
    Get details of a specific Secret.

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace
        name: The Secret name

    Returns:
        Detailed information about the Secret
    """
    core_v1: CoreV1Api = get_api_clients(context_name)["core"]
    secret = core_v1.read_namespaced_secret(name=name, namespace=namespace)
    decoded_data = {key: base64.b64decode(value).decode() for key, value in secret.data.items()}
    return {
        "name": secret.metadata.name,
        "type": secret.type,
        "data": decoded_data
    }


@mcp.tool()
@use_current_context
@check_readonly_permission
def secret_update(context_name: str, namespace: str, name: str, data: dict):
    """
    Update an existing Secret in the specified namespace.

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace
        name: The Secret name
        data: A dictionary of key-value pairs (values will be base64 encoded)

    Returns:
        Status of the update operation
    """
    core_v1: CoreV1Api = get_api_clients(context_name)["core"]
    secret = core_v1.read_namespaced_secret(name=name, namespace=namespace)
    encoded_data = {key: base64.b64encode(value.encode()).decode() for key, value in data.items()}
    secret.data.update(encoded_data)
    updated_secret = core_v1.replace_namespaced_secret(name=name, namespace=namespace, body=secret)
    return {"name": updated_secret.metadata.name, "status": "Updated"}


@mcp.tool()
@use_current_context
@check_readonly_permission
def secret_delete(context_name: str, namespace: str, name: str):
    """
    Delete a Secret from the specified namespace.

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace
        name: The Secret name

    Returns:
        Status of the deletion operation
    """
    core_v1: CoreV1Api = get_api_clients(context_name)["core"]
    core_v1.delete_namespaced_secret(name=name, namespace=namespace)
    return {"name": name, "status": "Deleted"}