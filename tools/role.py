from kubernetes.client import RbacAuthorizationV1Api, V1Role, V1ClusterRole, V1ObjectMeta, V1PolicyRule
from core.context import use_current_context
from core.kubeconfig import get_api_clients
from server.server import mcp
from core.permissions import check_readonly_permission


@mcp.tool()
@use_current_context
def role_list(context_name: str, namespace: str):
    """
    List all Roles in a given namespace.

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace

    Returns:
        List of Role basic information
    """
    rbac_v1: RbacAuthorizationV1Api = get_api_clients(context_name)["rbac"]
    roles = rbac_v1.list_namespaced_role(namespace)
    result = [{"name": role.metadata.name} for role in roles.items]
    return result


@mcp.tool()
@use_current_context
@check_readonly_permission
def role_create(context_name: str, namespace: str, name: str, rules: list):
    """
    Create a Role in the specified namespace.

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace
        name: The Role name
        rules: List of policy rules

    Returns:
        Status of the creation operation
    """
    rbac_v1: RbacAuthorizationV1Api = get_api_clients(context_name)["rbac"]
    role = V1Role(
        metadata=V1ObjectMeta(name=name),
        rules=[V1PolicyRule(**rule) for rule in rules]
    )
    created_role = rbac_v1.create_namespaced_role(namespace=namespace, body=role)
    return {"name": created_role.metadata.name, "status": "Created"}


@mcp.tool()
@use_current_context
def role_get(context_name: str, namespace: str, name: str):
    """
    Get details of a specific Role.

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace
        name: The Role name

    Returns:
        Detailed information about the Role
    """
    rbac_v1: RbacAuthorizationV1Api = get_api_clients(context_name)["rbac"]
    role = rbac_v1.read_namespaced_role(name=name, namespace=namespace)
    return {
        "name": role.metadata.name,
        "rules": [{"api_groups": rule.api_groups, "resources": rule.resources, "verbs": rule.verbs} for rule in role.rules]
    }


@mcp.tool()
@use_current_context
@check_readonly_permission
def role_delete(context_name: str, namespace: str, name: str):
    """
    Delete a Role from the specified namespace.

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace
        name: The Role name

    Returns:
        Status of the deletion operation
    """
    rbac_v1: RbacAuthorizationV1Api = get_api_clients(context_name)["rbac"]
    rbac_v1.delete_namespaced_role(name=name, namespace=namespace)
    return {"name": name, "status": "Deleted"}


@mcp.tool()
@use_current_context
def clusterrole_list(context_name: str):
    """
    List all ClusterRoles in the cluster.

    Args:
        context_name: The Kubernetes context name

    Returns:
        List of ClusterRole basic information
    """
    rbac_v1: RbacAuthorizationV1Api = get_api_clients(context_name)["rbac"]
    clusterroles = rbac_v1.list_cluster_role()
    result = [{"name": clusterrole.metadata.name} for clusterrole in clusterroles.items]
    return result


@mcp.tool()
@use_current_context
@check_readonly_permission
def clusterrole_create(context_name: str, name: str, rules: list):
    """
    Create a ClusterRole in the cluster.

    Args:
        context_name: The Kubernetes context name
        name: The ClusterRole name
        rules: List of policy rules

    Returns:
        Status of the creation operation
    """
    rbac_v1: RbacAuthorizationV1Api = get_api_clients(context_name)["rbac"]
    clusterrole = V1ClusterRole(
        metadata=V1ObjectMeta(name=name),
        rules=[V1PolicyRule(**rule) for rule in rules]
    )
    created_clusterrole = rbac_v1.create_cluster_role(body=clusterrole)
    return {"name": created_clusterrole.metadata.name, "status": "Created"}


@mcp.tool()
@use_current_context
def clusterrole_get(context_name: str, name: str):
    """
    Get details of a specific ClusterRole.

    Args:
        context_name: The Kubernetes context name
        name: The ClusterRole name

    Returns:
        Detailed information about the ClusterRole
    """
    rbac_v1: RbacAuthorizationV1Api = get_api_clients(context_name)["rbac"]
    clusterrole = rbac_v1.read_cluster_role(name=name)
    return {
        "name": clusterrole.metadata.name,
        "rules": [{"api_groups": rule.api_groups, "resources": rule.resources, "verbs": rule.verbs} for rule in clusterrole.rules]
    }


@mcp.tool()
@use_current_context
@check_readonly_permission
def clusterrole_delete(context_name: str, name: str):
    """
    Delete a ClusterRole from the cluster.

    Args:
        context_name: The Kubernetes context name
        name: The ClusterRole name

    Returns:
        Status of the deletion operation
    """
    rbac_v1: RbacAuthorizationV1Api = get_api_clients(context_name)["rbac"]
    rbac_v1.delete_cluster_role(name=name)
    return {"name": name, "status": "Deleted"}