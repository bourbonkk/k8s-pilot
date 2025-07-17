from kubernetes.client import AppsV1Api, V1ReplicaSet, V1ObjectMeta, V1PodTemplateSpec, V1PodSpec, V1Container, V1LabelSelector
from core.context import use_current_context
from core.permissions import check_readonly_permission
from core.kubeconfig import get_api_clients
from server.server import mcp


@mcp.tool()
@use_current_context
def replicaset_list(context_name: str, namespace: str):
    """
    List all ReplicaSets in a given namespace.

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace

    Returns:
        List of ReplicaSet basic information
    """
    apps_v1: AppsV1Api = get_api_clients(context_name)["apps"]
    replicasets = apps_v1.list_namespaced_replica_set(namespace)
    result = [{"name": rs.metadata.name, "replicas": rs.status.replicas} for rs in replicasets.items]
    return result


@mcp.tool()
@use_current_context
@check_readonly_permission
def replicaset_create(context_name: str, namespace: str, name: str, image: str, replicas: int, labels: dict):
    """
    Create a ReplicaSet in the specified namespace.

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace
        name: The ReplicaSet name
        image: The container image to use
        replicas: Number of replicas
        labels: Labels to apply to the ReplicaSet

    Returns:
        Status of the creation operation
    """
    apps_v1: AppsV1Api = get_api_clients(context_name)["apps"]
    replicaset = V1ReplicaSet(
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
    created_replicaset = apps_v1.create_namespaced_replica_set(namespace=namespace, body=replicaset)
    return {"name": created_replicaset.metadata.name, "status": "Created"}


@mcp.tool()
@use_current_context
def replicaset_get(context_name: str, namespace: str, name: str):
    """
    Get details of a specific ReplicaSet.

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace
        name: The ReplicaSet name

    Returns:
        Detailed information about the ReplicaSet
    """
    apps_v1: AppsV1Api = get_api_clients(context_name)["apps"]
    replicaset = apps_v1.read_namespaced_replica_set(name=name, namespace=namespace)
    return {
        "name": replicaset.metadata.name,
        "replicas": replicaset.status.replicas,
        "labels": replicaset.metadata.labels,
        "containers": [c.image for c in replicaset.spec.template.spec.containers]
    }


@mcp.tool()
@use_current_context
@check_readonly_permission
def replicaset_update(context_name: str, namespace: str, name: str, image: str, replicas: int):
    """
    Update an existing ReplicaSet in the specified namespace.

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace
        name: The ReplicaSet name
        image: The new container image to update
        replicas: The new number of replicas

    Returns:
        Status of the update operation
    """
    apps_v1: AppsV1Api = get_api_clients(context_name)["apps"]
    replicaset = apps_v1.read_namespaced_replica_set(name=name, namespace=namespace)
    replicaset.spec.template.spec.containers[0].image = image
    replicaset.spec.replicas = replicas
    updated_replicaset = apps_v1.replace_namespaced_replica_set(name=name, namespace=namespace, body=replicaset)
    return {"name": updated_replicaset.metadata.name, "status": "Updated"}


@mcp.tool()
@use_current_context
@check_readonly_permission
def replicaset_delete(context_name: str, namespace: str, name: str):
    """
    Delete a ReplicaSet from the specified namespace.

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace
        name: The ReplicaSet name

    Returns:
        Status of the deletion operation
    """
    apps_v1: AppsV1Api = get_api_clients(context_name)["apps"]
    apps_v1.delete_namespaced_replica_set(name=name, namespace=namespace)
    return {"name": name, "status": "Deleted"}