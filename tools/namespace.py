import json
from typing import Dict, Optional

from kubernetes.client import CoreV1Api, V1Namespace, V1ObjectMeta
from kubernetes.client.rest import ApiException

from core.context import use_current_context
from core.permissions import check_readonly_permission
from core.kubeconfig import get_api_clients
from server.server import mcp


@mcp.tool()
@use_current_context
def list_namespaces(context_name: str):
    """
    List all namespaces in the Kubernetes cluster.

    Args:
        context_name: The Kubernetes context name

    Returns:
        JSON string containing basic information about all namespaces
    """
    core_v1: CoreV1Api = get_api_clients(context_name)["core"]
    namespaces = core_v1.list_namespace()
    result = [{"name": ns.metadata.name} for ns in namespaces.items]
    return json.dumps(result)


@mcp.tool()
@use_current_context
def get_namespace_details(context_name: str, namespace: str):
    """
    Get detailed information about a specific namespace.

    Args:
        context_name: The Kubernetes context name
        namespace: The name of the namespace to get details for

    Returns:
        JSON string containing detailed information about the namespace
    """
    core_v1: CoreV1Api = get_api_clients(context_name)["core"]

    try:
        ns = core_v1.read_namespace(namespace)

        # Extract useful information
        result = {
            "name": ns.metadata.name,
            "status": ns.status.phase,
            "labels": ns.metadata.labels if ns.metadata.labels else {},
            "annotations": ns.metadata.annotations if ns.metadata.annotations else {},
            "created": ns.metadata.creation_timestamp.strftime(
                "%Y-%m-%dT%H:%M:%SZ") if ns.metadata.creation_timestamp else None
        }

        return json.dumps(result)
    except ApiException as e:
        if e.status == 404:
            return json.dumps({"error": f"Namespace '{namespace}' not found"})
        else:
            return json.dumps({"error": f"API error: {str(e)}"})


@mcp.tool()
@use_current_context
@check_readonly_permission
def create_namespace(context_name: str, namespace: str, labels: Optional[Dict[str, str]] = None):
    """
    Create a new namespace.

    Args:
        context_name: The Kubernetes context name
        namespace: The name for the new namespace
        labels: Optional dictionary of labels to apply to the namespace

    Returns:
        JSON string containing information about the created namespace
    """
    core_v1: CoreV1Api = get_api_clients(context_name)["core"]

    try:
        # Check if namespace already exists
        try:
            core_v1.read_namespace(namespace)
            return json.dumps({"error": f"Namespace '{namespace}' already exists"})
        except ApiException as e:
            if e.status != 404:
                return json.dumps({"error": f"API error: {str(e)}"})
            # 404 means namespace doesn't exist, so we can proceed

        # Create namespace object
        ns_metadata = V1ObjectMeta(name=namespace, labels=labels)
        ns_body = V1Namespace(metadata=ns_metadata)

        # Create the namespace
        created_ns = core_v1.create_namespace(body=ns_body)

        result = {
            "name": created_ns.metadata.name,
            "status": created_ns.status.phase,
            "labels": created_ns.metadata.labels if created_ns.metadata.labels else {},
            "message": f"Namespace '{namespace}' created successfully"
        }

        return json.dumps(result)
    except ApiException as e:
        return json.dumps({"error": f"Failed to create namespace: {str(e)}"})


@mcp.tool()
@use_current_context
@check_readonly_permission
def delete_namespace(context_name: str, namespace: str):
    """
    Delete a namespace and all resources within it.

    Args:
        context_name: The Kubernetes context name
        namespace: The name of the namespace to delete

    Returns:
        JSON string containing the result of the operation
    """
    core_v1: CoreV1Api = get_api_clients(context_name)["core"]

    try:
        # Check if namespace exists
        try:
            core_v1.read_namespace(namespace)
        except ApiException as e:
            if e.status == 404:
                return json.dumps({"error": f"Namespace '{namespace}' not found"})
            else:
                return json.dumps({"error": f"API error: {str(e)}"})

        # Delete the namespace
        core_v1.delete_namespace(namespace)

        result = {
            "name": namespace,
            "status": "Deleting",
            "message": f"Namespace '{namespace}' is being deleted"
        }

        return json.dumps(result)
    except ApiException as e:
        return json.dumps({"error": f"Failed to delete namespace: {str(e)}"})


@mcp.tool()
@use_current_context
@check_readonly_permission
def add_namespace_label(context_name: str, namespace: str, label_key: str, label_value: str):
    """
    Add or update a label on a namespace.

    Args:
        context_name: The Kubernetes context name
        namespace: The name of the namespace
        label_key: The label key to add
        label_value: The label value to set

    Returns:
        JSON string containing the updated namespace labels
    """
    core_v1: CoreV1Api = get_api_clients(context_name)["core"]

    try:
        # Get the current namespace
        ns = core_v1.read_namespace(namespace)

        # Prepare the patch
        if not ns.metadata.labels:
            ns.metadata.labels = {}

        # Update the labels
        labels = dict(ns.metadata.labels)
        labels[label_key] = label_value

        # Apply the patch
        body = {
            "metadata": {
                "labels": labels
            }
        }

        patched_ns = core_v1.patch_namespace(namespace, body)

        result = {
            "name": patched_ns.metadata.name,
            "labels": patched_ns.metadata.labels
        }

        return json.dumps(result)
    except ApiException as e:
        if e.status == 404:
            return json.dumps({"error": f"Namespace '{namespace}' not found"})
        else:
            return json.dumps({"error": f"Failed to add label: {str(e)}"})


@mcp.tool()
@use_current_context
@check_readonly_permission
def remove_namespace_label(context_name: str, namespace: str, label_key: str):
    """
    Remove a label from a namespace.

    Args:
        context_name: The Kubernetes context name
        namespace: The name of the namespace
        label_key: The label key to remove

    Returns:
        JSON string containing the updated namespace labels
    """
    core_v1: CoreV1Api = get_api_clients(context_name)["core"]

    try:
        # Get the current namespace
        ns = core_v1.read_namespace(namespace)

        # Check if the namespace has labels
        if not ns.metadata.labels or label_key not in ns.metadata.labels:
            result = {
                "name": namespace,
                "labels": ns.metadata.labels,
                "message": f"Label '{label_key}' not found on namespace"
            }
            return json.dumps(result)

        # Update the labels
        labels = dict(ns.metadata.labels)
        del labels[label_key]

        # Apply the patch
        body = {
            "metadata": {
                "labels": labels
            }
        }

        patched_ns = core_v1.patch_namespace(namespace, body)

        result = {
            "name": patched_ns.metadata.name,
            "labels": patched_ns.metadata.labels
        }

        return json.dumps(result)
    except ApiException as e:
        if e.status == 404:
            return json.dumps({"error": f"Namespace '{namespace}' not found"})
        else:
            return json.dumps({"error": f"Failed to remove label: {str(e)}"})


@mcp.tool()
@use_current_context
def list_namespace_resources(context_name: str, namespace: str):
    """
    List resources (pods, services, deployments, etc.) in a namespace.

    Args:
        context_name: The Kubernetes context name
        namespace: The name of the namespace

    Returns:
        JSON string containing a summary of resources in the namespace
    """
    from kubernetes.client import AppsV1Api

    core_v1: CoreV1Api = get_api_clients(context_name)["core"]
    apps_v1 = get_api_clients(context_name).get("apps", AppsV1Api(get_api_clients(context_name)["api_client"]))

    try:
        # Check if namespace exists
        try:
            core_v1.read_namespace(namespace)
        except ApiException as e:
            if e.status == 404:
                return json.dumps({"error": f"Namespace '{namespace}' not found"})
            else:
                return json.dumps({"error": f"API error: {str(e)}"})

        # Get pods
        pods = core_v1.list_namespaced_pod(namespace)

        # Get services
        services = core_v1.list_namespaced_service(namespace)

        # Get deployments
        deployments = apps_v1.list_namespaced_deployment(namespace)

        # Get stateful sets
        stateful_sets = apps_v1.list_namespaced_stateful_set(namespace)

        # Get daemon sets
        daemon_sets = apps_v1.list_namespaced_daemon_set(namespace)

        # Get config maps
        config_maps = core_v1.list_namespaced_config_map(namespace)

        # Get secrets
        secrets = core_v1.list_namespaced_secret(namespace)

        # Get persistent volume claims
        pvcs = core_v1.list_namespaced_persistent_volume_claim(namespace)

        result = {
            "namespace": namespace,
            "resource_counts": {
                "pods": len(pods.items),
                "services": len(services.items),
                "deployments": len(deployments.items),
                "statefulSets": len(stateful_sets.items),
                "daemonSets": len(daemon_sets.items),
                "configMaps": len(config_maps.items),
                "secrets": len(secrets.items),
                "persistentVolumeClaims": len(pvcs.items)
            },
            "pods": [{"name": pod.metadata.name, "status": pod.status.phase} for pod in pods.items],
            "services": [{"name": svc.metadata.name, "type": svc.spec.type, "cluster_ip": svc.spec.cluster_ip} for svc
                         in services.items],
            "deployments": [{"name": deploy.metadata.name, "replicas": deploy.spec.replicas} for deploy in
                            deployments.items]
        }

        return json.dumps(result)
    except ApiException as e:
        return json.dumps({"error": f"Failed to list namespace resources: {str(e)}"})


@mcp.tool()
@use_current_context
@check_readonly_permission
def set_namespace_resource_quota(context_name: str, namespace: str,
                                 cpu_limit: Optional[str] = None,
                                 memory_limit: Optional[str] = None,
                                 pod_count: Optional[int] = None):
    """
    Set or update resource quotas for a namespace.

    Args:
        context_name: The Kubernetes context name
        namespace: The name of the namespace
        cpu_limit: Optional CPU limit (e.g., "2", "500m")
        memory_limit: Optional memory limit (e.g., "1Gi", "500Mi")
        pod_count: Optional maximum number of pods

    Returns:
        JSON string containing the resource quota status
    """
    from kubernetes.client.models.v1_resource_quota import V1ResourceQuota
    from kubernetes.client.models.v1_resource_quota_spec import V1ResourceQuotaSpec

    core_v1: CoreV1Api = get_api_clients(context_name)["core"]

    try:
        # Check if namespace exists
        try:
            core_v1.read_namespace(namespace)
        except ApiException as e:
            if e.status == 404:
                return json.dumps({"error": f"Namespace '{namespace}' not found"})
            else:
                return json.dumps({"error": f"API error: {str(e)}"})

        # If no limits are provided, return error
        if not any([cpu_limit, memory_limit, pod_count]):
            return json.dumps({"error": "At least one resource limit must be specified"})

        # Prepare the resource quota
        quota_name = f"{namespace}-resource-quota"
        hard_quotas = {}

        if cpu_limit:
            hard_quotas["limits.cpu"] = cpu_limit

        if memory_limit:
            hard_quotas["limits.memory"] = memory_limit

        if pod_count:
            hard_quotas["pods"] = str(pod_count)

        # Check if quota already exists
        try:
            existing_quota = core_v1.read_namespaced_resource_quota(quota_name, namespace)
            # Update existing quota
            body = {
                "spec": {
                    "hard": hard_quotas
                }
            }
            updated_quota = core_v1.patch_namespaced_resource_quota(quota_name, namespace, body)

            result = {
                "name": updated_quota.metadata.name,
                "namespace": namespace,
                "quotas": updated_quota.spec.hard,
                "message": "Resource quota updated successfully"
            }
        except ApiException as e:
            if e.status == 404:
                # Create new quota
                quota_spec = V1ResourceQuotaSpec(hard=hard_quotas)
                quota_metadata = V1ObjectMeta(name=quota_name)
                quota_body = V1ResourceQuota(metadata=quota_metadata, spec=quota_spec)

                created_quota = core_v1.create_namespaced_resource_quota(namespace, quota_body)

                result = {
                    "name": created_quota.metadata.name,
                    "namespace": namespace,
                    "quotas": created_quota.spec.hard,
                    "message": "Resource quota created successfully"
                }
            else:
                return json.dumps({"error": f"API error: {str(e)}"})

        return json.dumps(result)
    except ApiException as e:
        return json.dumps({"error": f"Failed to set resource quota: {str(e)}"})


@mcp.tool()
@use_current_context
def get_namespace_resource_quota(context_name: str, namespace: str):
    """
    Get current resource quotas for a namespace.

    Args:
        context_name: The Kubernetes context name
        namespace: The name of the namespace

    Returns:
        JSON string containing the current resource quotas and their usage
    """
    core_v1: CoreV1Api = get_api_clients(context_name)["core"]

    try:
        # Check if namespace exists
        try:
            core_v1.read_namespace(namespace)
        except ApiException as e:
            if e.status == 404:
                return json.dumps({"error": f"Namespace '{namespace}' not found"})
            else:
                return json.dumps({"error": f"API error: {str(e)}"})

        # Get all resource quotas in the namespace
        quotas = core_v1.list_namespaced_resource_quota(namespace)

        if not quotas.items:
            return json.dumps({
                "namespace": namespace,
                "message": "No resource quotas defined for this namespace"
            })

        quota_info = []
        for quota in quotas.items:
            quota_data = {
                "name": quota.metadata.name,
                "hard": quota.spec.hard,
                "used": quota.status.used if hasattr(quota.status, 'used') else {}
            }
            quota_info.append(quota_data)

        result = {
            "namespace": namespace,
            "quotas": quota_info
        }

        return json.dumps(result)
    except ApiException as e:
        return json.dumps({"error": f"Failed to get resource quotas: {str(e)}"})
