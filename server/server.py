from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "k8s-pilot",
    instructions="""
    k8s-pilot is a Kubernetes cluster management MCP server.
    
    Key concepts:
    - Context: A Kubernetes context from ~/.kube/config. If not specified, the current active context is used.
    - Namespace: The Kubernetes namespace. If not specified, the default namespace for the context is used.
    - Readonly mode: When enabled via --readonly flag, all write operations (create/update/delete) are blocked.
    
    The server supports managing: Pods, Deployments, Services, ConfigMaps, Secrets, Ingresses,
    StatefulSets, DaemonSets, ReplicaSets, Roles, ClusterRoles, PersistentVolumes, PersistentVolumeClaims,
    Namespaces, Nodes, and ServiceAccounts across multiple clusters.
    """
)


# Tool/resource registration (required to trigger @mcp.tool/@mcp.resource)
def load_modules():
    import prompts.k8s  # noqa: F401
    import resources.contexts  # noqa: F401
    import tools.cluster  # noqa: F401
    import tools.configmap  # noqa: F401
    import tools.daemonset  # noqa: F401
    import tools.deployment  # noqa: F401
    import tools.ingress  # noqa: F401
    import tools.namespace  # noqa: F401
    import tools.node  # noqa: F401
    import tools.pod  # noqa: F401
    import tools.pv  # noqa: F401
    import tools.pvc  # noqa: F401
    import tools.replicaset  # noqa: F401
    import tools.role  # noqa: F401
    import tools.secret  # noqa: F401
    import tools.service  # noqa: F401
    import tools.serviceaccount  # noqa: F401
    import tools.statefulset  # noqa: F401


load_modules()
