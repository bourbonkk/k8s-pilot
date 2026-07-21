import json

from kubernetes.client import CoreV1Api
from kubernetes.client.models.v1_taint import V1Taint

from core.context import use_current_context
from core.kubeconfig import get_api_clients
from server.server import mcp
from mcp.server.fastmcp import Context
from core.permissions import check_readonly_permission


@mcp.tool()
@use_current_context
def list_nodes(context_name: str):
    """
    List all nodes in the Kubernetes cluster.

    Args:
        context_name: The Kubernetes context name

    Returns:
        JSON string containing basic information about all nodes
    """
    core_v1: CoreV1Api = get_api_clients(context_name)["core"]
    nodes = core_v1.list_node()
    result = [{"name": node.metadata.name} for node in nodes.items]
    return json.dumps(result)


@mcp.tool()
@use_current_context
def get_node_details(context_name: str, node_name: str):
    """
    Get detailed information about a specific node.

    Args:
        context_name: The Kubernetes context name
        node_name: The name of the node to get details for

    Returns:
        JSON string containing detailed information about the node
    """
    core_v1: CoreV1Api = get_api_clients(context_name)["core"]
    node = core_v1.read_node(node_name)

    # Extract useful information
    node_info = node.status.node_info
    conditions = {cond.type: cond.status for cond in node.status.conditions}
    capacity = {k: v for k, v in node.status.capacity.items()}
    allocatable = {k: v for k, v in node.status.allocatable.items()}

    # Format taints if present
    taints = []
    if node.spec.taints:
        taints = [{
            "key": taint.key,
            "value": taint.value,
            "effect": taint.effect
        } for taint in node.spec.taints]

    # Extract labels and annotations
    labels = {}
    annotations = {}
    if node.metadata.labels:
        labels = node.metadata.labels
    if node.metadata.annotations:
        annotations = node.metadata.annotations

    result = {
        "name": node.metadata.name,
        "info": {
            "architecture": node_info.architecture,
            "bootID": node_info.boot_id,
            "containerRuntimeVersion": node_info.container_runtime_version,
            "kernelVersion": node_info.kernel_version,
            "kubeProxyVersion": node_info.kube_proxy_version,
            "kubeletVersion": node_info.kubelet_version,
            "machineID": node_info.machine_id,
            "operatingSystem": node_info.operating_system,
            "osImage": node_info.os_image,
            "systemUUID": node_info.system_uuid
        },
        "conditions": conditions,
        "capacity": capacity,
        "allocatable": allocatable,
        "labels": labels,
        "annotations": annotations,
        "taints": taints,
        "addresses": [{"type": addr.type, "address": addr.address} for addr in node.status.addresses],
        "created": node.metadata.creation_timestamp.strftime(
            "%Y-%m-%dT%H:%M:%SZ") if node.metadata.creation_timestamp else None
    }

    return json.dumps(result)


@mcp.tool()
@use_current_context
@check_readonly_permission
async def add_node_label(context_name: str, node_name: str, label_key: str, label_value: str, ctx: Context):
    """
    Add or update a label to a node.

    Args:
        context_name: The Kubernetes context name
        node_name: The name of the node to modify
        label_key: The label key to add
        label_value: The label value to set

    Returns:
        JSON string containing the updated node labels
    """
    await ctx.info(f"Adding label '{label_key}={label_value}' to node '{node_name}'")
    core_v1: CoreV1Api = get_api_clients(context_name)["core"]

    # Get the current node
    node = core_v1.read_node(node_name)

    # Prepare the patch
    if not node.metadata.labels:
        node.metadata.labels = {}

    # Update the labels
    labels = dict(node.metadata.labels)
    labels[label_key] = label_value

    # Apply the patch
    body = {
        "metadata": {
            "labels": labels
        }
    }

    patched_node = core_v1.patch_node(node_name, body)

    result = {
        "name": patched_node.metadata.name,
        "labels": patched_node.metadata.labels
    }

    await ctx.info(f"Successfully added label '{label_key}' to node '{node_name}'")
    return json.dumps(result)


@mcp.tool()
@use_current_context
@check_readonly_permission
async def remove_node_label(context_name: str, node_name: str, label_key: str, ctx: Context):
    """
    Remove a label from a node.

    Args:
        context_name: The Kubernetes context name
        node_name: The name of the node to modify
        label_key: The label key to remove

    Returns:
        JSON string containing the updated node labels
    """
    await ctx.warning(f"Removing label '{label_key}' from node '{node_name}'")
    core_v1: CoreV1Api = get_api_clients(context_name)["core"]

    # Get the current node
    node = core_v1.read_node(node_name)

    # Check if the node has labels
    if not node.metadata.labels or label_key not in node.metadata.labels:
        result = {
            "name": node_name,
            "labels": node.metadata.labels,
            "message": f"Label '{label_key}' not found on node"
        }
        return json.dumps(result)

    # Update the labels
    labels = dict(node.metadata.labels)
    del labels[label_key]

    # Apply the patch
    body = {
        "metadata": {
            "labels": labels
        }
    }

    patched_node = core_v1.patch_node(node_name, body)

    result = {
        "name": patched_node.metadata.name,
        "labels": patched_node.metadata.labels
    }

    await ctx.info(f"Successfully removed label '{label_key}' from node '{node_name}'")
    return json.dumps(result)


@mcp.tool()
@use_current_context
@check_readonly_permission
async def add_node_taint(context_name: str, node_name: str, taint_key: str,
                   taint_value: str, taint_effect: str, ctx: Context):
    """
    Add a taint to a node.

    Args:
        context_name: The Kubernetes context name
        node_name: The name of the node to modify
        taint_key: The taint key to add
        taint_value: The taint value to set
        taint_effect: The taint effect (NoSchedule, PreferNoSchedule, or NoExecute)

    Returns:
        JSON string containing the updated node taints
    """
    await ctx.info(f"Adding taint '{taint_key}={taint_value}:{taint_effect}' to node '{node_name}'")
    core_v1: CoreV1Api = get_api_clients(context_name)["core"]

    # Validate the taint effect
    valid_effects = ["NoSchedule", "PreferNoSchedule", "NoExecute"]
    if taint_effect not in valid_effects:
        result = {
            "error": f"Invalid taint effect. Must be one of {', '.join(valid_effects)}"
        }
        return json.dumps(result)

    # Get the current node
    node = core_v1.read_node(node_name)

    # Prepare the taints
    current_taints = []
    if node.spec.taints:
        current_taints = node.spec.taints

    # Check if taint with this key already exists
    exists = False
    for i, taint in enumerate(current_taints):
        if taint.key == taint_key:
            # Update existing taint
            current_taints[i] = V1Taint(
                key=taint_key,
                value=taint_value,
                effect=taint_effect
            )
            exists = True
            break

    # Add new taint if it doesn't exist
    if not exists:
        current_taints.append(V1Taint(
            key=taint_key,
            value=taint_value,
            effect=taint_effect
        ))

    # Apply the patch
    body = {
        "spec": {
            "taints": [
                {
                    "key": taint.key,
                    "value": taint.value,
                    "effect": taint.effect
                } for taint in current_taints
            ]
        }
    }

    patched_node = core_v1.patch_node(node_name, body)

    # Format the taints for response
    response_taints = []
    if patched_node.spec.taints:
        response_taints = [
            {
                "key": taint.key,
                "value": taint.value,
                "effect": taint.effect
            } for taint in patched_node.spec.taints
        ]

    result = {
        "name": patched_node.metadata.name,
        "taints": response_taints
    }

    await ctx.info(f"Successfully added taint '{taint_key}' to node '{node_name}'")
    return json.dumps(result)


@mcp.tool()
@use_current_context
@check_readonly_permission
async def remove_node_taint(context_name: str, node_name: str, taint_key: str, ctx: Context):
    """
    Remove a taint from a node.

    Args:
        context_name: The Kubernetes context name
        node_name: The name of the node to modify
        taint_key: The taint key to remove

    Returns:
        JSON string containing the updated node taints
    """
    await ctx.warning(f"Removing taint '{taint_key}' from node '{node_name}'")
    core_v1: CoreV1Api = get_api_clients(context_name)["core"]

    # Get the current node
    node = core_v1.read_node(node_name)

    # Check if the node has taints
    if not node.spec.taints:
        result = {
            "name": node_name,
            "taints": [],
            "message": "Node has no taints"
        }
        return json.dumps(result)

    # Filter out the taint to remove
    updated_taints = [taint for taint in node.spec.taints if taint.key != taint_key]

    # Check if taint was found
    if len(updated_taints) == len(node.spec.taints):
        result = {
            "name": node_name,
            "taints": [{"key": taint.key, "value": taint.value, "effect": taint.effect}
                       for taint in node.spec.taints],
            "message": f"Taint with key '{taint_key}' not found"
        }
        return json.dumps(result)

    # Apply the patch
    body = {
        "spec": {
            "taints": [
                {
                    "key": taint.key,
                    "value": taint.value,
                    "effect": taint.effect
                } for taint in updated_taints
            ]
        }
    }

    patched_node = core_v1.patch_node(node_name, body)

    # Format the taints for response
    response_taints = []
    if patched_node.spec.taints:
        response_taints = [
            {
                "key": taint.key,
                "value": taint.value,
                "effect": taint.effect
            } for taint in patched_node.spec.taints
        ]

    result = {
        "name": patched_node.metadata.name,
        "taints": response_taints
    }

    await ctx.info(f"Successfully removed taint '{taint_key}' from node '{node_name}'")
    return json.dumps(result)


@mcp.tool()
@use_current_context
@check_readonly_permission
async def cordon_node(context_name: str, node_name: str, ctx: Context):
    """
    Cordon a node (mark as unschedulable).

    Args:
        context_name: The Kubernetes context name
        node_name: The name of the node to cordon

    Returns:
        JSON string containing the result of the operation
    """
    await ctx.warning(f"Cordoning node '{node_name}' - marking as unschedulable")
    core_v1: CoreV1Api = get_api_clients(context_name)["core"]

    # Get the current node
    node = core_v1.read_node(node_name)

    # Check if already cordoned
    if node.spec.unschedulable:
        result = {
            "name": node_name,
            "status": "already cordoned",
            "unschedulable": True
        }
        return json.dumps(result)

    # Apply the patch
    body = {
        "spec": {
            "unschedulable": True
        }
    }

    patched_node = core_v1.patch_node(node_name, body)

    result = {
        "name": patched_node.metadata.name,
        "status": "cordoned",
        "unschedulable": patched_node.spec.unschedulable
    }

    await ctx.info(f"Successfully cordoned node '{node_name}'")
    return json.dumps(result)


@mcp.tool()
@use_current_context
@check_readonly_permission
async def uncordon_node(context_name: str, node_name: str, ctx: Context):
    """
    Uncordon a node (mark as schedulable).

    Args:
        context_name: The Kubernetes context name
        node_name: The name of the node to uncordon

    Returns:
        JSON string containing the result of the operation
    """
    await ctx.info(f"Uncordoning node '{node_name}' - marking as schedulable")
    core_v1: CoreV1Api = get_api_clients(context_name)["core"]

    # Get the current node
    node = core_v1.read_node(node_name)

    # Check if already uncordoned
    if not node.spec.unschedulable:
        result = {
            "name": node_name,
            "status": "already schedulable",
            "unschedulable": False
        }
        return json.dumps(result)

    # Apply the patch
    body = {
        "spec": {
            "unschedulable": False
        }
    }

    patched_node = core_v1.patch_node(node_name, body)

    result = {
        "name": patched_node.metadata.name,
        "status": "uncordoned",
        "unschedulable": patched_node.spec.unschedulable
    }

    await ctx.info(f"Successfully uncordoned node '{node_name}'")
    return json.dumps(result)


@mcp.tool()
@use_current_context
def get_node_pods(context_name: str, node_name: str):
    """
    Get all pods running on a specific node.

    Args:
        context_name: The Kubernetes context name
        node_name: The name of the node to get pods for

    Returns:
        JSON string containing the pods running on the node
    """
    core_v1: CoreV1Api = get_api_clients(context_name)["core"]

    # Get all pods in all namespaces
    pods = core_v1.list_pod_for_all_namespaces(field_selector=f"spec.nodeName={node_name}")

    pod_list = [
        {
            "name": pod.metadata.name,
            "namespace": pod.metadata.namespace,
            "status": pod.status.phase,
            "containers": [c.name for c in pod.spec.containers]
        } for pod in pods.items
    ]

    result = {
        "node": node_name,
        "pods": pod_list,
        "pod_count": len(pod_list)
    }

    return json.dumps(result)
