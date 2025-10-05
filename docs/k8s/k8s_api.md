# 📚 CoreV1Api Methods

## ConfigMaps

- create_namespaced_config_map
- delete_namespaced_config_map
- list_config_map_for_all_namespaces
- list_namespaced_config_map
- patch_namespaced_config_map
- read_namespaced_config_map
- replace_namespaced_config_map

## Endpoints

- create_namespaced_endpoints
- delete_namespaced_endpoints
- list_endpoints_for_all_namespaces
- list_namespaced_endpoints
- patch_namespaced_endpoints
- read_namespaced_endpoints
- replace_namespaced_endpoints

## Events

- list_event_for_all_namespaces
- list_namespaced_event
- read_namespaced_event

## LimitRanges

- list_namespaced_limit_range
- list_limit_range_for_all_namespaces
- read_namespaced_limit_range

## Namespaces

- create_namespace
- delete_namespace
- list_namespace
- patch_namespace
- read_namespace
- replace_namespace

## Nodes

- list_node
- patch_node
- read_node
- replace_node

## PersistentVolumes (PV)

- create_persistent_volume
- delete_persistent_volume
- list_persistent_volume
- patch_persistent_volume
- read_persistent_volume
- replace_persistent_volume

## PersistentVolumeClaims (PVC)

- create_namespaced_persistent_volume_claim
- delete_namespaced_persistent_volume_claim
- list_persistent_volume_claim_for_all_namespaces
- list_namespaced_persistent_volume_claim
- patch_namespaced_persistent_volume_claim
- read_namespaced_persistent_volume_claim
- replace_namespaced_persistent_volume_claim

## Pods

- connect_get_namespaced_pod_exec (exec into a pod)
- connect_get_namespaced_pod_portforward
- connect_post_namespaced_pod_exec
- connect_post_namespaced_pod_portforward
- create_namespaced_pod
- delete_namespaced_pod
- list_pod_for_all_namespaces
- list_namespaced_pod
- patch_namespaced_pod
- read_namespaced_pod
- replace_namespaced_pod

## PodTemplates

- list_namespaced_pod_template
- list_pod_template_for_all_namespaces
- read_namespaced_pod_template

## ReplicationControllers

- create_namespaced_replication_controller
- delete_namespaced_replication_controller
- list_namespaced_replication_controller
- list_replication_controller_for_all_namespaces
- patch_namespaced_replication_controller
- read_namespaced_replication_controller
- replace_namespaced_replication_controller

## ResourceQuotas

- list_namespaced_resource_quota
- list_resource_quota_for_all_namespaces
- read_namespaced_resource_quota

## Secrets

- create_namespaced_secret
- delete_namespaced_secret
- list_namespaced_secret
- list_secret_for_all_namespaces
- patch_namespaced_secret
- read_namespaced_secret
- replace_namespaced_secret

## ServiceAccounts

- create_namespaced_service_account
- delete_namespaced_service_account
- list_namespaced_service_account
- list_service_account_for_all_namespaces
- patch_namespaced_service_account
- read_namespaced_service_account
- replace_namespaced_service_account

## Services

- create_namespaced_service
- delete_namespaced_service
- list_namespaced_service
- list_service_for_all_namespaces
- patch_namespaced_service
- read_namespaced_service
- replace_namespaced_service

# 🛠️ Notes

Almost every resource follows the same CRUD pattern:
create_*
read_*
patch_*
replace_*
delete_*
list_*

# "Namespaced" vs. "For_all_namespaces":
- list_namespaced_pod("default") → just that namespace.
- list_pod_for_all_namespaces() → across the cluster.
- Extra helpers for exec, attach, logs, port-forward exist only for pods:
- connect_get_namespaced_pod_exec
- connect_post_namespaced_pod_exec
- connect_get_namespaced_pod_attach
- read_namespaced_pod_log
