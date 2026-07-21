import os

import yaml
from kubernetes import client, config
from typing import Dict

_client_cache: Dict[str, Dict[str, any]] = {}


def get_api_clients(context_name: str) -> Dict[str, any]:
    """
    Get Kubernetes API clients for the specified context.
    This function caches the clients to avoid reloading the kubeconfig
    and reinitializing the clients multiple times.
    :param context_name:
    :return:
    """
    if context_name not in _client_cache:
        configuration = client.Configuration()
        config.load_kube_config(context=context_name, client_configuration=configuration)
        api_client = client.ApiClient(configuration=configuration)
        _client_cache[context_name] = {
            "api_client": api_client,
            "core": client.CoreV1Api(api_client),
            "apps": client.AppsV1Api(api_client),
            "batch": client.BatchV1Api(api_client),
            "networking": client.NetworkingV1Api(api_client),
            "rbac": client.RbacAuthorizationV1Api(api_client),
        }
    return _client_cache[context_name]


def get_kubeconfig():
    """
    Load the kubeconfig file from the default location.
    The default location is usually ~/.kube/config.
    This function returns the parsed kubeconfig data.
    If the file does not exist or is not readable, it raises an exception.

    if you want to load a different kubeconfig file, you can set the KUBECONFIG environment variable
    to the path of the kubeconfig file you want to use.
    """
    kubeconfig_path = os.path.expanduser(config.KUBE_CONFIG_DEFAULT_LOCATION)
    with open(kubeconfig_path, "r") as f:
        config_data = yaml.safe_load(f)
    return config_data
