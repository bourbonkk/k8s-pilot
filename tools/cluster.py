import os

import yaml

from core.kubeconfig import get_kubeconfig
from core.permissions import check_readonly_permission
from mcp.server.fastmcp import Context
from models.context import ContextInfo
from server.server import mcp


@mcp.tool()
def get_clusters():
    """
    Get all clusters from the kubeconfig file.
    :return:
    """
    config_data = get_kubeconfig()
    current_context = config_data.get("current-context")
    contexts = config_data.get("contexts", [])

    return [
        ContextInfo(
            name=ctx["name"],
            cluster=ctx["context"].get("cluster"),
            user=ctx["context"].get("user"),
            current=ctx["name"] == current_context,
        )
        for ctx in contexts]


@mcp.tool()
def get_current_cluster():
    """
    Get the current cluster from the kubeconfig file.
    :return:
    """
    config_data = get_kubeconfig()
    current_context = config_data.get("current-context")
    contexts = config_data.get("contexts", [])

    for ctx in contexts:
        if ctx["name"] == current_context:
            return ContextInfo(
                name=ctx["name"],
                cluster=ctx["context"].get("cluster"),
                user=ctx["context"].get("user"),
                current=True,
            )
    return None


@mcp.tool()
@check_readonly_permission
async def set_current_cluster(cluster_name: str, ctx: Context):
    """
    Set the current cluster in the kubeconfig file.
    :param cluster_name:
    :return:
    """
    await ctx.warning(f"Switching current cluster context to '{cluster_name}'")
    config_data = get_kubeconfig()
    contexts = config_data.get("contexts", [])

    for c in contexts:
        if c["name"] == cluster_name:
            config_data["current-context"] = cluster_name
            with open(os.path.expanduser("~/.kube/config"), "w") as f:
                yaml.dump(config_data, f)
            await ctx.info(f"Successfully switched to cluster '{cluster_name}'")
            return {"status": "success", "message": f"Current context set to {cluster_name}"}

    return {"status": "error", "message": f"Context {cluster_name} not found"}
