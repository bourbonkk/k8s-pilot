from typing import Optional, Dict, List

from core.context import use_current_context
from core.permissions import check_readonly_permission
from server.server import mcp
from kubernetes.client import CoreV1Api
from core.kubeconfig import get_api_clients


@mcp.tool()
@use_current_context
def pod_list(context_name: str, namespace: str):
    """
    List all pods in a given namespace.

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace

    Returns:
        List of pod basic information
    """
    core_v1: CoreV1Api = get_api_clients(context_name)["core"]
    pods = core_v1.list_namespaced_pod(namespace)
    result = [{"name": pod.metadata.name} for pod in pods.items]
    return result


@mcp.tool()
@use_current_context
def pod_detail(context_name: str, namespace: str, name: str):
    """
    Get details of a specific pod.

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace
        name: The pod name

    Returns:
        Detailed information about the pod
    """
    core_v1: CoreV1Api = get_api_clients(context_name)["core"]
    pod = core_v1.read_namespaced_pod(name, namespace)

    containers = []
    for c in pod.spec.containers:
        container_info = {
            "name": c.name,
            "image": c.image,
            "ports": [{"container_port": p.container_port, "protocol": p.protocol} for p in (c.ports or [])],
            "resources": {
                "requests": c.resources.requests if c.resources and hasattr(c.resources, "requests") else {},
                "limits": c.resources.limits if c.resources and hasattr(c.resources, "limits") else {}
            },
            "environment": [{"name": env.name, "value": env.value if hasattr(env, "value") else "from secret"}
                            for env in (c.env or [])]
        }
        containers.append(container_info)

    volumes = []
    if pod.spec.volumes:
        for vol in pod.spec.volumes:
            volume_info = {"name": vol.name}
            # 볼륨 타입 확인 및 정보 추가
            if hasattr(vol, "config_map") and vol.config_map:
                volume_info["type"] = "configMap"
                volume_info["config_map_name"] = vol.config_map.name
            elif hasattr(vol, "secret") and vol.secret:
                volume_info["type"] = "secret"
                volume_info["secret_name"] = vol.secret.secret_name
            elif hasattr(vol, "persistent_volume_claim") and vol.persistent_volume_claim:
                volume_info["type"] = "pvc"
                volume_info["claim_name"] = vol.persistent_volume_claim.claim_name
            elif hasattr(vol, "host_path") and vol.host_path:
                volume_info["type"] = "hostPath"
                volume_info["path"] = vol.host_path.path
            elif hasattr(vol, "empty_dir") and vol.empty_dir:
                volume_info["type"] = "emptyDir"
            else:
                volume_info["type"] = "other"
            volumes.append(volume_info)

    conditions = []
    if pod.status.conditions:
        for condition in pod.status.conditions:
            conditions.append({
                "type": condition.type,
                "status": condition.status,
                "last_transition_time": condition.last_transition_time,
                "reason": condition.reason,
                "message": condition.message
            })

    networking = {
        "pod_ip": pod.status.pod_ip,
        "host_ip": pod.status.host_ip,
        "node_name": pod.spec.node_name
    }

    metadata = {
        "creation_timestamp": pod.metadata.creation_timestamp,
        "labels": pod.metadata.labels or {},
        "annotations": pod.metadata.annotations or {},
        "owner_references": [{
            "kind": ref.kind,
            "name": ref.name,
            "uid": ref.uid
        } for ref in (pod.metadata.owner_references or [])]
    }

    status_info = {
        "phase": pod.status.phase,
        "start_time": pod.status.start_time,
        "container_statuses": []
    }

    if pod.status.container_statuses:
        for cs in pod.status.container_statuses:
            container_status = {
                "name": cs.name,
                "ready": cs.ready,
                "restart_count": cs.restart_count,
                "image": cs.image,
                "image_id": cs.image_id,
                "container_id": cs.container_id
            }

            if cs.state:
                state_info = {}
                if hasattr(cs.state, "running") and cs.state.running:
                    state_info["current"] = "running"
                    state_info["started_at"] = cs.state.running.started_at
                elif hasattr(cs.state, "waiting") and cs.state.waiting:
                    state_info["current"] = "waiting"
                    state_info["reason"] = cs.state.waiting.reason
                    state_info["message"] = cs.state.waiting.message
                elif hasattr(cs.state, "terminated") and cs.state.terminated:
                    state_info["current"] = "terminated"
                    state_info["exit_code"] = cs.state.terminated.exit_code
                    state_info["reason"] = cs.state.terminated.reason
                    state_info["message"] = cs.state.terminated.message
                    state_info["started_at"] = cs.state.terminated.started_at
                    state_info["finished_at"] = cs.state.terminated.finished_at

                container_status["state"] = state_info

            status_info["container_statuses"].append(container_status)

    result = {
        "name": pod.metadata.name,
        "namespace": pod.metadata.namespace,
        "status": status_info,
        "spec": {
            "containers": containers,
            "volumes": volumes,
            "restart_policy": pod.spec.restart_policy,
            "service_account": pod.spec.service_account,
            "dns_policy": pod.spec.dns_policy,
            "node_selector": pod.spec.node_selector or {},
            "tolerations": [{
                "key": t.key,
                "operator": t.operator,
                "effect": t.effect,
                "toleration_seconds": t.toleration_seconds
            } for t in (pod.spec.tolerations or [])]
        },
        "metadata": metadata,
        "networking": networking,
        "conditions": conditions
    }

    return result


@mcp.tool()
@use_current_context
@check_readonly_permission
def pod_create(context_name: str, namespace: str, name: str, image: str,
               labels: Optional[Dict[str, str]] = None,
               command: Optional[List[str]] = None,
               args: Optional[List[str]] = None,
               env_vars: Optional[Dict[str, str]] = None):
    """
    Create a new pod in the specified namespace.

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace
        name: The name for the new pod
        image: The container image to use
        labels: Optional dictionary of pod labels
        command: Optional command to run in the container
        args: Optional arguments for the command
        env_vars: Optional environment variables for the container

    Returns:
        Information about the created pod
    """
    from kubernetes.client import V1Pod, V1ObjectMeta, V1PodSpec, V1Container, V1EnvVar

    core_v1: CoreV1Api = get_api_clients(context_name)["core"]

    # Prepare environment variables if provided
    container_env = None
    if env_vars:
        container_env = [V1EnvVar(name=k, value=v) for k, v in env_vars.items()]

    # Create container
    container = V1Container(
        name=name,
        image=image,
        command=command,
        args=args,
        env=container_env
    )

    # Create pod spec
    pod_spec = V1PodSpec(containers=[container])

    # Create pod metadata
    pod_metadata = V1ObjectMeta(name=name, namespace=namespace, labels=labels)

    # Create pod
    pod = V1Pod(
        api_version="v1",
        kind="Pod",
        metadata=pod_metadata,
        spec=pod_spec
    )

    # Create the pod in Kubernetes
    created_pod = core_v1.create_namespaced_pod(namespace=namespace, body=pod)

    result = {
        "name": created_pod.metadata.name,
        "namespace": created_pod.metadata.namespace,
        "status": "Created",
    }
    return result


@mcp.tool()
@use_current_context
@check_readonly_permission
def pod_update(context_name: str, namespace: str, name: str,
               labels: Optional[Dict[str, str]] = None):
    """
    Update an existing pod's metadata (only labels can be updated for an existing pod).

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace
        name: The pod name
        labels: New labels to apply to the pod

    Returns:
        Information about the updated pod
    """
    core_v1: CoreV1Api = get_api_clients(context_name)["core"]

    # Get the current pod
    pod = core_v1.read_namespaced_pod(name=name, namespace=namespace)

    # Update pod labels if provided
    if labels:
        pod.metadata.labels = labels

    # Update the pod in Kubernetes
    updated_pod = core_v1.patch_namespaced_pod(
        name=name,
        namespace=namespace,
        body={"metadata": {"labels": labels}}
    )

    result = {
        "name": updated_pod.metadata.name,
        "namespace": updated_pod.metadata.namespace,
        "status": updated_pod.status.phase,
        "labels": updated_pod.metadata.labels,
    }
    return result


@mcp.tool()
@use_current_context
@check_readonly_permission
def pod_delete(context_name: str, namespace: str, name: str):
    """
    Delete a pod from the specified namespace.

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace
        name: The pod name to delete

    Returns:
        Status of the deletion operation
    """
    core_v1: CoreV1Api = get_api_clients(context_name)["core"]

    try:
        # Delete the pod
        api_response = core_v1.delete_namespaced_pod(
            name=name,
            namespace=namespace,
            body={}  # Default deletion options
        )

        # Check if the response indicates success
        if api_response.status == "Success":
            return {
                "name": name,
                "namespace": namespace,
                "status": "Deleted",
                "message": f"Pod {name} deleted successfully"
            }
        else:
            return {
                "name": name,
                "namespace": namespace,
                "status": "Failed",
                "message": f"Failed to delete pod {name}: {api_response.status}"
            }
    except Exception as e:
        return {
            "name": name,
            "namespace": namespace,
            "status": "Error",
            "message": f"An error occurred while deleting pod {name}: {str(e)}"
        }


@mcp.tool()
@use_current_context
def pod_logs(context_name: str, namespace: str, name: str, container: str = None,
             tail_lines: int = 100, previous: bool = False):
    """
    Get logs from a pod or a specific container within the pod.

    Args:
        context_name: The Kubernetes context name
        namespace: The Kubernetes namespace
        name: The pod name
        container: Optional container name (if pod has multiple containers)
        tail_lines: Number of lines to retrieve from the end of the logs
        previous: Whether to get logs from a previous instance of the container

    Returns:
        Pod logs
    """
    core_v1: CoreV1Api = get_api_clients(context_name)["core"]

    logs = core_v1.read_namespaced_pod_log(
        name=name,
        namespace=namespace,
        container=container,
        tail_lines=tail_lines,
        previous=previous
    )

    result = {
        "name": name,
        "namespace": namespace,
        "container": container,
        "logs": logs
    }
    return result
