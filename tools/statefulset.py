from kubernetes.client import AppsV1Api, V1StatefulSet, V1ObjectMeta, V1LabelSelector, V1PodTemplateSpec, V1PodSpec, V1Container, V1StatefulSetSpec
from core.context import use_current_context
from core.permissions import check_readonly_permission
from core.kubeconfig import get_api_clients
from server.server import mcp
from mcp.server.fastmcp import Context


@mcp.tool()
@use_current_context
def statefulset_list(context_name: str, namespace: str):
    """
    List all StatefulSets in a given namespace.

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace

    Returns:
        List of StatefulSet basic information
    """
    apps_v1: AppsV1Api = get_api_clients(context_name)["apps"]
    statefulsets = apps_v1.list_namespaced_stateful_set(namespace)
    result = [{"name": ss.metadata.name, "replicas": ss.status.replicas} for ss in statefulsets.items]
    return result


@mcp.tool()
@use_current_context
@check_readonly_permission
async def statefulset_create(context_name: str, namespace: str, name: str, image: str, replicas: int, labels: dict, ctx: Context):
    """
    Create a StatefulSet in the specified namespace.

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace
        name: The StatefulSet name
        image: The container image to use
        replicas: Number of replicas
        labels: Labels to apply to the StatefulSet

    Returns:
        Status of the creation operation
    """
    await ctx.info(f"Creating statefulset '{name}' in namespace '{namespace}'")
    apps_v1: AppsV1Api = get_api_clients(context_name)["apps"]
    statefulset = V1StatefulSet(
        metadata=V1ObjectMeta(name=name, labels=labels),
        spec=V1StatefulSetSpec(
            replicas=replicas,
            selector=V1LabelSelector(match_labels=labels),
            service_name=name,
            template=V1PodTemplateSpec(
                metadata=V1ObjectMeta(labels=labels),
                spec=V1PodSpec(containers=[V1Container(name=name, image=image)])
            )
        )
    )
    created_statefulset = apps_v1.create_namespaced_stateful_set(namespace=namespace, body=statefulset)
    await ctx.info(f"Successfully created statefulset '{name}'")
    return {"name": created_statefulset.metadata.name, "status": "Created"}


@mcp.tool()
@use_current_context
def statefulset_get(context_name: str, namespace: str, name: str):
    """
    Get details of a specific StatefulSet.

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace
        name: The StatefulSet name

    Returns:
        Detailed information about the StatefulSet
    """
    apps_v1: AppsV1Api = get_api_clients(context_name)["apps"]
    statefulset = apps_v1.read_namespaced_stateful_set(name=name, namespace=namespace)
    return {
        "name": statefulset.metadata.name,
        "replicas": statefulset.status.replicas,
        "labels": statefulset.metadata.labels,
        "containers": [c.image for c in statefulset.spec.template.spec.containers]
    }


@mcp.tool()
@use_current_context
@check_readonly_permission
async def statefulset_update(context_name: str, namespace: str, name: str, image: str, replicas: int, ctx: Context):
    """
    Update an existing StatefulSet in the specified namespace.

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace
        name: The StatefulSet name
        image: The new container image to update
        replicas: The new number of replicas

    Returns:
        Status of the update operation
    """
    await ctx.info(f"Updating statefulset '{name}' in namespace '{namespace}'")
    apps_v1: AppsV1Api = get_api_clients(context_name)["apps"]
    statefulset = apps_v1.read_namespaced_stateful_set(name=name, namespace=namespace)
    statefulset.spec.template.spec.containers[0].image = image
    statefulset.spec.replicas = replicas
    updated_statefulset = apps_v1.replace_namespaced_stateful_set(name=name, namespace=namespace, body=statefulset)
    await ctx.info(f"Successfully updated statefulset '{name}'")
    return {"name": updated_statefulset.metadata.name, "status": "Updated"}


@mcp.tool()
@use_current_context
@check_readonly_permission
async def statefulset_delete(context_name: str, namespace: str, name: str, ctx: Context):
    """
    Delete a StatefulSet from the specified namespace.

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace
        name: The StatefulSet name

    Returns:
        Status of the deletion operation
    """
    await ctx.warning(f"Deleting statefulset '{name}' from namespace '{namespace}'")
    apps_v1: AppsV1Api = get_api_clients(context_name)["apps"]
    apps_v1.delete_namespaced_stateful_set(name=name, namespace=namespace)
    await ctx.info(f"Successfully deleted statefulset '{name}'")
    return {"name": name, "status": "Deleted"}