from kubernetes.client import CoreV1Api, V1PersistentVolume, V1ObjectMeta, V1PersistentVolumeSpec
from core.context import use_current_context
from core.kubeconfig import get_api_clients
from server.server import mcp
from core.permissions import check_readonly_permission


@mcp.tool()
@use_current_context
def pv_list(context_name: str):
    """
    List all PersistentVolumes in the cluster.

    Args:
        context_name: The Kubernetes context name

    Returns:
        List of PersistentVolume basic information
    """
    core_v1: CoreV1Api = get_api_clients(context_name)["core"]
    pvs = core_v1.list_persistent_volume()
    result = [{"name": pv.metadata.name, "capacity": pv.spec.capacity, "access_modes": pv.spec.access_modes} for pv in pvs.items]
    return result


@mcp.tool()
@use_current_context
@check_readonly_permission
def pv_create(context_name: str, name: str, capacity: str, access_modes: list, storage_class: str, host_path: str):
    """
    Create a PersistentVolume in the cluster.

    Args:
        context_name: The Kubernetes context name
        name: The PersistentVolume name
        capacity: The storage capacity (e.g., "10Gi")
        access_modes: List of access modes (e.g., ["ReadWriteOnce"])
        storage_class: The storage class name
        host_path: The host path for the volume

    Returns:
        Status of the creation operation
    """
    core_v1: CoreV1Api = get_api_clients(context_name)["core"]
    pv = V1PersistentVolume(
        metadata=V1ObjectMeta(name=name),
        spec=V1PersistentVolumeSpec(
            capacity={"storage": capacity},
            access_modes=access_modes,
            storage_class_name=storage_class,
            host_path={"path": host_path}
        )
    )
    created_pv = core_v1.create_persistent_volume(body=pv)
    return {"name": created_pv.metadata.name, "status": "Created"}


@mcp.tool()
@use_current_context
def pv_get(context_name: str, name: str):
    """
    Get details of a specific PersistentVolume.

    Args:
        context_name: The Kubernetes context name
        name: The PersistentVolume name

    Returns:
        Detailed information about the PersistentVolume
    """
    core_v1: CoreV1Api = get_api_clients(context_name)["core"]
    pv = core_v1.read_persistent_volume(name=name)
    return {
        "name": pv.metadata.name,
        "capacity": pv.spec.capacity,
        "access_modes": pv.spec.access_modes,
        "storage_class": pv.spec.storage_class_name,
        "host_path": pv.spec.host_path.path if pv.spec.host_path else None
    }


@mcp.tool()
@use_current_context
@check_readonly_permission
def pv_update(context_name: str, name: str, labels: dict):
    """
    Update an existing PersistentVolume's metadata (e.g., labels).

    Args:
        context_name: The Kubernetes context name
        name: The PersistentVolume name
        labels: New labels to apply to the PersistentVolume

    Returns:
        Status of the update operation
    """
    core_v1: CoreV1Api = get_api_clients(context_name)["core"]
    pv = core_v1.read_persistent_volume(name=name)
    pv.metadata.labels = labels
    updated_pv = core_v1.patch_persistent_volume(name=name, body={"metadata": {"labels": labels}})
    return {"name": updated_pv.metadata.name, "status": "Updated", "labels": updated_pv.metadata.labels}


@mcp.tool()
@use_current_context
@check_readonly_permission
def pv_delete(context_name: str, name: str):
    """
    Delete a PersistentVolume from the cluster.

    Args:
        context_name: The Kubernetes context name
        name: The PersistentVolume name

    Returns:
        Status of the deletion operation
    """
    core_v1: CoreV1Api = get_api_clients(context_name)["core"]
    core_v1.delete_persistent_volume(name=name)
    return {"name": name, "status": "Deleted"}