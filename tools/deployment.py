from kubernetes.client import AppsV1Api, V1Deployment, V1ObjectMeta, V1PodTemplateSpec, V1PodSpec, V1Container, V1LabelSelector
from core.context import use_current_context
from core.permissions import check_readonly_permission
from core.kubeconfig import get_api_clients
from server.server import mcp


@mcp.tool()
@use_current_context
def deployment_list(context_name: str, namespace: str):
    """
    List all Deployments in a given namespace.

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace

    Returns:
        List of Deployment basic information
    """
    apps_v1: AppsV1Api = get_api_clients(context_name)["apps"]
    deployments = apps_v1.list_namespaced_deployment(namespace)
    result = [{"name": dep.metadata.name} for dep in deployments.items]
    return result


@mcp.tool()
@use_current_context
@check_readonly_permission
def deployment_create(context_name: str, namespace: str, name: str, image: str, replicas: int, labels: dict):
    """
    Create a Deployment in the specified namespace.

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace
        name: The Deployment name
        image: The container image to use
        replicas: Number of replicas
        labels: Labels to apply to the Deployment

    Returns:
        Status of the creation operation
    """
    apps_v1: AppsV1Api = get_api_clients(context_name)["apps"]
    deployment = V1Deployment(
        metadata=V1ObjectMeta(name=name, labels=labels),
        spec={
            "replicas": replicas,
            "selector": V1LabelSelector(match_labels=labels),
            "template": V1PodTemplateSpec(
                metadata=V1ObjectMeta(labels=labels),
                spec=V1PodSpec(containers=[V1Container(name=name, image=image)])
            )
        }
    )
    created_deployment = apps_v1.create_namespaced_deployment(namespace=namespace, body=deployment)
    return {"name": created_deployment.metadata.name, "status": "Created"}


@mcp.tool()
@use_current_context
def deployment_get(context_name: str, namespace: str, name: str):
    """
    Get details of a specific Deployment.

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace
        name: The Deployment name

    Returns:
        Detailed information about the Deployment
    """
    apps_v1: AppsV1Api = get_api_clients(context_name)["apps"]
    deployment = apps_v1.read_namespaced_deployment(name=name, namespace=namespace)
    return {
        "name": deployment.metadata.name,
        "replicas": deployment.spec.replicas,
        "labels": deployment.metadata.labels,
        "containers": [c.image for c in deployment.spec.template.spec.containers]
    }


@mcp.tool()
@use_current_context
@check_readonly_permission
def deployment_update(context_name: str, namespace: str, name: str, image: str, replicas: int):
    """
    Update an existing Deployment in the specified namespace.

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace
        name: The Deployment name
        image: The new container image to update
        replicas: The new number of replicas

    Returns:
        Status of the update operation
    """
    apps_v1: AppsV1Api = get_api_clients(context_name)["apps"]
    deployment = apps_v1.read_namespaced_deployment(name=name, namespace=namespace)
    deployment.spec.template.spec.containers[0].image = image
    deployment.spec.replicas = replicas
    updated_deployment = apps_v1.replace_namespaced_deployment(name=name, namespace=namespace, body=deployment)
    return {"name": updated_deployment.metadata.name, "status": "Updated"}


@mcp.tool()
@use_current_context
@check_readonly_permission
def deployment_delete(context_name: str, namespace: str, name: str):
    """
    Delete a Deployment from the specified namespace.

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace
        name: The Deployment name

    Returns:
        Status of the deletion operation
    """
    apps_v1: AppsV1Api = get_api_clients(context_name)["apps"]
    apps_v1.delete_namespaced_deployment(name=name, namespace=namespace)
    return {"name": name, "status": "Deleted"}