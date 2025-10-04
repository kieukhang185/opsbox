export interface Namespace {
  name: string;
  status: string;
  creation_timestamp: string;
}

export interface PodContainer {
  name: string;
  image: string;
  restarts: number;
  state: string;
}

export interface Pod {
  name: string;
  namespace: string;
  node: string;
  phase: string;
  start_time: string;
  containers: PodContainer[];
}

export interface NodeAddress {
  internal: string;
}

export interface Node {
  name: string;
  ready: boolean;
  addresses: NodeAddress;
  allocatable: { cpu: string; memory: string };
  usage?: { cpu: string; memory: string };
}

export interface Event {
  type: string;
  reason: string;
  message: string;
  involved_object: { kind: string; name: string; namespace?: string };
  last_timestamp: string;
}

export type ListResponse<T> = { items: T[]; continue?: string; total?: number };
