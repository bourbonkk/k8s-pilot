from kubernetes.client import AppsV1Api, V1DaemonSet, V1ObjectMeta, V1PodTemplateSpec, V1PodSpec, V1Container
from core.context import use_current_context
from core.kubeconfig import get_api_clients
from server.server import mcp
from core.permissions import check_readonly_permission


@mcp.tool()
@use_current_context
def daemonset_list(context_name: str, namespace: str):
    """
    List all DaemonSets in a given namespace.

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace

    Returns:
        List of DaemonSet basic information
    """
    apps_v1: AppsV1Api = get_api_clients(context_name)["apps"]
    daemonsets = apps_v1.list_namespaced_daemon_set(namespace)
    result = [{"name": ds.metadata.name} for ds in daemonsets.items]
    return result


@mcp.tool()
@use_current_context
@check_readonly_permission
def daemonset_create(context_name: str, namespace: str, name: str, image: str, labels: dict):
    """
    Create a DaemonSet in the specified namespace.

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace
        name: The DaemonSet name
        image: The container image to use
        labels: Labels to apply to the DaemonSet

    Returns:
        Status of the creation operation
    """
    apps_v1: AppsV1Api = get_api_clients(context_name)["apps"]
    daemonset = V1DaemonSet(
        metadata=V1ObjectMeta(name=name, labels=labels),
        spec={
            "selector": {"matchLabels": labels},
            "template": V1PodTemplateSpec(
                metadata=V1ObjectMeta(labels=labels),
                spec=V1PodSpec(containers=[V1Container(name=name, image=image)])
            )
        }
    )
    created_daemonset = apps_v1.create_namespaced_daemon_set(namespace=namespace, body=daemonset)
    return {"name": created_daemonset.metadata.name, "status": "Created"}


@mcp.tool()
@use_current_context
def daemonset_get(context_name: str, namespace: str, name: str):
    """
    Get details of a specific DaemonSet.

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace
        name: The DaemonSet name

    Returns:
        Detailed information about the DaemonSet
    """
    apps_v1: AppsV1Api = get_api_clients(context_name)["apps"]
    daemonset = apps_v1.read_namespaced_daemon_set(name=name, namespace=namespace)
    return {"name": daemonset.metadata.name, "labels": daemonset.metadata.labels, "containers": [c.image for c in daemonset.spec.template.spec.containers]}


@mcp.tool()
@use_current_context
@check_readonly_permission
def daemonset_update(context_name: str, namespace: str, name: str, image: str):
    """
    Update an existing DaemonSet in the specified namespace.

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace
        name: The DaemonSet name
        image: The new container image to update

    Returns:
        Status of the update operation
    """
    apps_v1: AppsV1Api = get_api_clients(context_name)["apps"]
    daemonset = apps_v1.read_namespaced_daemon_set(name=name, namespace=namespace)
    daemonset.spec.template.spec.containers[0].image = image
    updated_daemonset = apps_v1.replace_namespaced_daemon_set(name=name, namespace=namespace, body=daemonset)
    return {"name": updated_daemonset.metadata.name, "status": "Updated"}


@mcp.tool()
@use_current_context
@check_readonly_permission
def daemonset_delete(context_name: str, namespace: str, name: str):
    """
    Delete a DaemonSet from the specified namespace.

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace
        name: The DaemonSet name

    Returns:
        Status of the deletion operation
    """
    apps_v1: AppsV1Api = get_api_clients(context_name)["apps"]
    apps_v1.delete_namespaced_daemon_set(name=name, namespace=namespace)
    return {"name": name, "status": "Deleted"}