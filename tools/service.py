from kubernetes.client import CoreV1Api, V1Service, V1ObjectMeta, V1ServiceSpec, V1ServicePort
from core.context import use_current_context
from core.kubeconfig import get_api_clients
from server.server import mcp
from core.permissions import check_readonly_permission


@mcp.tool()
@use_current_context
def service_list(context_name: str, namespace: str):
    """
    List all Services in a given namespace.

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace

    Returns:
        List of Service basic information
    """
    core_v1: CoreV1Api = get_api_clients(context_name)["core"]
    services = core_v1.list_namespaced_service(namespace)
    result = [{"name": svc.metadata.name, "type": svc.spec.type, "cluster_ip": svc.spec.cluster_ip} for svc in services.items]
    return result


@mcp.tool()
@use_current_context
@check_readonly_permission
def service_create(context_name: str, namespace: str, name: str, selector: dict, ports: list, service_type: str = "ClusterIP"):
    """
    Create a Service in the specified namespace.

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace
        name: The Service name
        selector: A dictionary of labels to select the target pods
        ports: A list of ports (e.g., [{"port": 80, "target_port": 8080}])
        service_type: The type of the Service (default is "ClusterIP")

    Returns:
        Status of the creation operation
    """
    core_v1: CoreV1Api = get_api_clients(context_name)["core"]
    service = V1Service(
        metadata=V1ObjectMeta(name=name),
        spec=V1ServiceSpec(
            selector=selector,
            ports=[V1ServicePort(port=port["port"], target_port=port["target_port"]) for port in ports],
            type=service_type
        )
    )
    created_service = core_v1.create_namespaced_service(namespace=namespace, body=service)
    return {"name": created_service.metadata.name, "status": "Created"}


@mcp.tool()
@use_current_context
def service_get(context_name: str, namespace: str, name: str):
    """
    Get details of a specific Service.

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace
        name: The Service name

    Returns:
        Detailed information about the Service
    """
    core_v1: CoreV1Api = get_api_clients(context_name)["core"]
    service = core_v1.read_namespaced_service(name=name, namespace=namespace)
    return {
        "name": service.metadata.name,
        "type": service.spec.type,
        "cluster_ip": service.spec.cluster_ip,
        "ports": [{"port": port.port, "target_port": port.target_port} for port in service.spec.ports],
        "selector": service.spec.selector
    }


@mcp.tool()
@use_current_context
@check_readonly_permission
def service_update(context_name: str, namespace: str, name: str, labels: dict):
    """
    Update an existing Service's metadata (e.g., labels).

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace
        name: The Service name
        labels: New labels to apply to the Service

    Returns:
        Status of the update operation
    """
    core_v1: CoreV1Api = get_api_clients(context_name)["core"]
    service = core_v1.read_namespaced_service(name=name, namespace=namespace)
    service.metadata.labels = labels
    updated_service = core_v1.patch_namespaced_service(name=name, namespace=namespace, body={"metadata": {"labels": labels}})
    return {"name": updated_service.metadata.name, "status": "Updated", "labels": updated_service.metadata.labels}


@mcp.tool()
@use_current_context
@check_readonly_permission
def service_delete(context_name: str, namespace: str, name: str):
    """
    Delete a Service from the specified namespace.

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace
        name: The Service name

    Returns:
        Status of the deletion operation
    """
    core_v1: CoreV1Api = get_api_clients(context_name)["core"]
    core_v1.delete_namespaced_service(name=name, namespace=namespace)
    return {"name": name, "status": "Deleted"}