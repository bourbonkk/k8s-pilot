from server.server import mcp


@mcp.prompt()
def troubleshoot_pod(pod_name: str, namespace: str = "default") -> str:
    """Generate a troubleshooting guide for a problematic pod."""
    return f"""Please help me troubleshoot the pod '{pod_name}' in namespace '{namespace}'.

Please follow these steps:
1. First, get the pod details using pod_detail to check its current status
2. Check the pod logs using pod_logs for any error messages
3. Look at the events and conditions for any issues
4. If the pod is in CrashLoopBackOff, check the previous container logs
5. Check if the namespace has any resource quotas that might be limiting the pod
6. Provide a summary of findings and recommended actions"""


@mcp.prompt()
def deployment_guide(app_name: str, image: str, namespace: str = "default", replicas: int = 1) -> str:
    """Generate a step-by-step guide to deploy an application."""
    return f"""Please help me deploy the application '{app_name}' to Kubernetes.

Deployment details:
- Application name: {app_name}
- Container image: {image}
- Target namespace: {namespace}
- Desired replicas: {replicas}

Please follow these steps:
1. First, check if the namespace '{namespace}' exists. If not, create it.
2. Create a Deployment named '{app_name}' with image '{image}' and {replicas} replicas
3. Create a ClusterIP Service to expose the deployment
4. Verify the deployment is running correctly by checking pod status
5. Provide a summary of all created resources"""


@mcp.prompt()
def cluster_health_check(context_name: str = "") -> str:
    """Generate a comprehensive cluster health check prompt."""
    context_hint = f" for context '{context_name}'" if context_name else ""
    return f"""Please perform a comprehensive health check on the Kubernetes cluster{context_hint}.

Please check the following:
1. List all nodes and check their status (Ready/NotReady)
2. Check node resource capacity and allocatable resources
3. List all namespaces and their status
4. For each namespace with workloads, check:
   - Deployment health (desired vs ready replicas)
   - Pod status (any CrashLoopBackOff, Pending, or Failed pods)
   - Any resource quota violations
5. Check for any nodes with taints or cordoned status
6. Provide an overall health summary with any issues found and recommended actions"""


@mcp.prompt()
def namespace_cleanup(namespace: str) -> str:
    """Generate a guide to safely clean up a namespace."""
    return f"""Please help me safely clean up the namespace '{namespace}'.

Please follow these steps:
1. First, list all resources in the namespace '{namespace}'
2. Show me the current deployments, pods, services, configmaps, and secrets
3. Ask for confirmation before proceeding with deletion
4. If confirmed, delete resources in the correct order:
   - First, scale down all deployments to 0 replicas
   - Delete deployments, statefulsets, and daemonsets
   - Delete services and ingresses
   - Delete configmaps and secrets (except default service account token)
   - Finally, delete the namespace itself
5. Verify the namespace has been deleted"""
