from kubernetes.client import NetworkingV1Api, V1Ingress, V1ObjectMeta, V1IngressSpec, V1IngressRule, \
    V1HTTPIngressRuleValue, V1HTTPIngressPath, V1IngressBackend
from core.context import use_current_context
from core.kubeconfig import get_api_clients
from server.server import mcp
from core.permissions import check_readonly_permission


@mcp.tool()
@use_current_context
def ingress_list(context_name: str, namespace: str):
    """
    List all Ingresses in a given namespace.

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace

    Returns:
        List of Ingress basic information
    """
    networking_v1: NetworkingV1Api = get_api_clients(context_name)["networking"]
    ingresses = networking_v1.list_namespaced_ingress(namespace)
    result = [{"name": ingress.metadata.name} for ingress in ingresses.items]
    return result


@mcp.tool()
@use_current_context
@check_readonly_permission
def ingress_create(context_name: str, namespace: str, name: str, host: str, service_name: str, service_port: int):
    """
    Create an Ingress in the specified namespace.

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace
        name: The Ingress name
        host: The host for the Ingress
        service_name: The backend service name
        service_port: The backend service port

    Returns:
        Status of the creation operation
    """
    networking_v1: NetworkingV1Api = get_api_clients(context_name)["networking"]
    ingress = V1Ingress(
        metadata=V1ObjectMeta(name=name),
        spec=V1IngressSpec(
            rules=[
                V1IngressRule(
                    host=host,
                    http=V1HTTPIngressRuleValue(
                        paths=[
                            V1HTTPIngressPath(
                                path="/",
                                path_type="Prefix",
                                backend=V1IngressBackend(
                                    service={"name": service_name, "port": {"number": service_port}}
                                )
                            )
                        ]
                    )
                )
            ]
        )
    )
    created_ingress = networking_v1.create_namespaced_ingress(namespace=namespace, body=ingress)
    return {"name": created_ingress.metadata.name, "status": "Created"}


@mcp.tool()
@use_current_context
def ingress_get(context_name: str, namespace: str, name: str):
    """
    Get details of a specific Ingress.

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace
        name: The Ingress name

    Returns:
        Detailed information about the Ingress
    """
    networking_v1: NetworkingV1Api = get_api_clients(context_name)["networking"]
    ingress = networking_v1.read_namespaced_ingress(name=name, namespace=namespace)
    return {
        "name": ingress.metadata.name,
        "host": ingress.spec.rules[0].host if ingress.spec.rules else None,
        "paths": [
            {
                "path": path.path,
                "service_name": path.backend.service.name,
                "service_port": path.backend.service.port.number
            }
            for path in ingress.spec.rules[0].http.paths
        ] if ingress.spec.rules else []
    }


@mcp.tool()
@use_current_context
@check_readonly_permission
def ingress_update(context_name: str, namespace: str, name: str, host: str, service_name: str, service_port: int):
    """
    Update an existing Ingress in the specified namespace.

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace
        name: The Ingress name
        host: The new host for the Ingress
        service_name: The new backend service name
        service_port: The new backend service port

    Returns:
        Status of the update operation
    """
    networking_v1: NetworkingV1Api = get_api_clients(context_name)["networking"]
    ingress = networking_v1.read_namespaced_ingress(name=name, namespace=namespace)
    ingress.spec.rules[0].host = host
    ingress.spec.rules[0].http.paths[0].backend.service.name = service_name
    ingress.spec.rules[0].http.paths[0].backend.service.port.number = service_port
    updated_ingress = networking_v1.replace_namespaced_ingress(name=name, namespace=namespace, body=ingress)
    return {"name": updated_ingress.metadata.name, "status": "Updated"}


@mcp.tool()
@use_current_context
@check_readonly_permission
def ingress_delete(context_name: str, namespace: str, name: str):
    """
    Delete an Ingress from the specified namespace.

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace
        name: The Ingress name

    Returns:
        Status of the deletion operation
    """
    networking_v1: NetworkingV1Api = get_api_clients(context_name)["networking"]
    networking_v1.delete_namespaced_ingress(name=name, namespace=namespace)
    return {"name": name, "status": "Deleted"}
