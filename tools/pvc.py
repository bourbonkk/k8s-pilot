from kubernetes.client import CoreV1Api, V1PersistentVolumeClaim, V1ObjectMeta, V1PersistentVolumeClaimSpec, V1ResourceRequirements
from core.context import use_current_context
from core.kubeconfig import get_api_clients
from server.server import mcp
from core.permissions import check_readonly_permission


@mcp.tool()
@use_current_context
def pvc_list(context_name: str, namespace: str):
    """
    List all PersistentVolumeClaims in a given namespace.

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace

    Returns:
        List of PersistentVolumeClaim basic information
    """
    core_v1: CoreV1Api = get_api_clients(context_name)["core"]
    pvcs = core_v1.list_namespaced_persistent_volume_claim(namespace)
    result = [{"name": pvc.metadata.name, "status": pvc.status.phase, "storage": pvc.spec.resources.requests.get("storage")} for pvc in pvcs.items]
    return result


@mcp.tool()
@use_current_context
@check_readonly_permission
def pvc_create(context_name: str, namespace: str, name: str, storage: str, access_modes: list, storage_class: str = None):
    """
    Create a PersistentVolumeClaim in the specified namespace.

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace
        name: The PersistentVolumeClaim name
        storage: The storage size (e.g., "10Gi")
        access_modes: List of access modes (e.g., ["ReadWriteOnce"])
        storage_class: The storage class name (optional)

    Returns:
        Status of the creation operation
    """
    core_v1: CoreV1Api = get_api_clients(context_name)["core"]
    pvc = V1PersistentVolumeClaim(
        metadata=V1ObjectMeta(name=name),
        spec=V1PersistentVolumeClaimSpec(
            access_modes=access_modes,
            resources=V1ResourceRequirements(requests={"storage": storage}),
            storage_class_name=storage_class
        )
    )
    created_pvc = core_v1.create_namespaced_persistent_volume_claim(namespace=namespace, body=pvc)
    return {"name": created_pvc.metadata.name, "status": "Created"}


@mcp.tool()
@use_current_context
def pvc_get(context_name: str, namespace: str, name: str):
    """
    Get details of a specific PersistentVolumeClaim.

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace
        name: The PersistentVolumeClaim name

    Returns:
        Detailed information about the PersistentVolumeClaim
    """
    core_v1: CoreV1Api = get_api_clients(context_name)["core"]
    pvc = core_v1.read_namespaced_persistent_volume_claim(name=name, namespace=namespace)
    return {
        "name": pvc.metadata.name,
        "status": pvc.status.phase,
        "storage": pvc.spec.resources.requests.get("storage"),
        "access_modes": pvc.spec.access_modes,
        "storage_class": pvc.spec.storage_class_name
    }


@mcp.tool()
@use_current_context
@check_readonly_permission
def pvc_update(context_name: str, namespace: str, name: str, labels: dict):
    """
    Update an existing PersistentVolumeClaim's metadata (e.g., labels).

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace
        name: The PersistentVolumeClaim name
        labels: New labels to apply to the PersistentVolumeClaim

    Returns:
        Status of the update operation
    """
    core_v1: CoreV1Api = get_api_clients(context_name)["core"]
    pvc = core_v1.read_namespaced_persistent_volume_claim(name=name, namespace=namespace)
    pvc.metadata.labels = labels
    updated_pvc = core_v1.patch_namespaced_persistent_volume_claim(name=name, namespace=namespace, body={"metadata": {"labels": labels}})
    return {"name": updated_pvc.metadata.name, "status": "Updated", "labels": updated_pvc.metadata.labels}


@mcp.tool()
@use_current_context
@check_readonly_permission
def pvc_delete(context_name: str, namespace: str, name: str):
    """
    Delete a PersistentVolumeClaim from the specified namespace.

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace
        name: The PersistentVolumeClaim name

    Returns:
        Status of the deletion operation
    """
    core_v1: CoreV1Api = get_api_clients(context_name)["core"]
    core_v1.delete_namespaced_persistent_volume_claim(name=name, namespace=namespace)
    return {"name": name, "status": "Deleted"}