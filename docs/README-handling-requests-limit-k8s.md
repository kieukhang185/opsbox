# 🧠 Handling Resource Requests & Limits in Kubernetes

This guide explains how to **measure**, **set**, and **tune** CPU and Memory resources for real applications running on Kubernetes.  
It is designed for DevOps engineers who want to ensure performance, stability, and cost efficiency.

---

## 📘 1. What Are Requests & Limits?

| Term | Description |
|------|--------------|
| **Request** | The minimum amount of CPU/memory that the container is guaranteed to get. The Kubernetes scheduler uses this to place the pod on a suitable node. |
| **Limit** | The maximum amount the container is allowed to use. If it exceeds this, the process will be throttled (for CPU) or killed (for memory). |
| **CPU unit** | `1` = 1 core, `500m` = 0.5 core |
| **Memory unit** | `512Mi` = 512 Mebibytes, `1Gi` = 1 Gibibyte |

---

## ⚙️ 2. Why It Matters

- **Performance:** Prevents noisy-neighbor issues.
- **Stability:** Avoids OOMKills and throttling.
- **Efficiency:** Reduces over-provisioning and wasted cost.
- **Scalability:** Enables accurate autoscaling (HPA/VPA).

---

## 🧩 3. Step-by-Step Workflow

### Step 1 — Start with Baseline Values
If you don’t have usage data yet, use conservative defaults:

| Application Type | CPU Request | Memory Request | CPU Limit | Memory Limit |
|------------------|--------------|----------------|------------|---------------|
| Web API | 250m | 256Mi | 500m | 512Mi |
| Worker/Job | 500m | 512Mi | 1000m | 1Gi |
| Cache/DB | 500m | 1Gi | 1000m | 2Gi |

Example manifest:
```yaml
resources:
  requests:
    cpu: "250m"
    memory: "256Mi"
  limits:
    cpu: "500m"
    memory: "512Mi"
```

---

### Step 2 — Measure Actual Usage
Use metrics tools to observe real consumption:
```bash
kubectl top pods
kubectl top pod <pod-name> --containers
```

Or install Prometheus + Grafana for continuous metrics.

Look at:
- **CPU(m)** — average and max usage
- **Memory(Mi)** — average and peak usage
- **Throttling** (check in Grafana or `kubectl describe pod`)

---

### Step 3 — Adjust Based on Metrics
Formulas:
```
request_cpu = avg_cpu_usage × 1.2
limit_cpu   = request_cpu × 2

request_mem = peak_mem_usage × 1.3
limit_mem   = request_mem × 2
```

Example:
If a pod averages 180m CPU and peaks at 320Mi memory:
```yaml
resources:
  requests:
    cpu: "220m"
    memory: "416Mi"
  limits:
    cpu: "440m"
    memory: "832Mi"
```

---

### Step 4 — Validate Under Load
Run load tests with tools like **k6** or **hey**:
```bash
hey -z 2m -q 50 http://app-url/endpoint
```

Observe:
- Latency (p95, p99)
- CPU throttling
- Memory OOM events

If the app becomes slow or unstable, increase limits gradually.

---

### Step 5 — Automate Tuning (Optional)
#### Horizontal Pod Autoscaler (HPA)
Scale out based on CPU usage:
```bash
kubectl autoscale deployment myapp --cpu-percent=70 --min=2 --max=8
```

#### Vertical Pod Autoscaler (VPA)
Let Kubernetes recommend or adjust resources automatically:
```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: myapp
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp
  updatePolicy:
    updateMode: "Off"  # Recommend only
```

---

### Step 6 — Use Goldilocks for Insights
[Goldilocks](https://github.com/FairwindsOps/goldilocks) analyzes real usage and suggests optimal requests/limits.

Install via Helm:
```bash
helm repo add fairwinds-stable https://charts.fairwinds.com/stable
helm install goldilocks fairwinds-stable/goldilocks --namespace goldilocks --create-namespace
```

Access dashboard → see which deployments are over- or under-provisioned.

---

## 🧮 4. Troubleshooting

| Symptom | Likely Cause | Fix |
|----------|---------------|------|
| Pod OOMKilled | Memory limit too low | Increase memory limit |
| CPU throttling | CPU limit too low | Raise limit or remove temporarily |
| Pods not scheduled | Requests too high | Reduce requests to fit nodes |
| Node pressure | Over-committed cluster | Adjust limits or add nodes |

---

## 🧠 5. Best Practices
✅ Always define both **requests** and **limits**  
✅ Start low, measure, then tune upward  
✅ Keep a **10–30% buffer** for bursts  
✅ Separate **staging vs production** sizing  
✅ Review resource configs every 2–4 weeks  
✅ Use dashboards and alerts for anomalies  

---

## 📊 6. Example Grafana Panels
- CPU Usage (container_cpu_usage_seconds_total)
- Memory Usage (container_memory_working_set_bytes)
- CPU Throttling (container_cpu_cfs_throttled_periods_total)
- OOMKills (container_oom_events_total)
- Requests vs Limits comparison table

---

## 📁 7. Deliverables
- Resource tuning dashboard in Grafana  
- Sizing runbook (`runbook/sizing.md`)  
- Load test results and tuning notes  
