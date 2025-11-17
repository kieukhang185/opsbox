# 🧭 OpsBox — FastAPI + Vite React + NGINX on Kubernetes (kind)

This project deploys a FastAPI backend and a Vite React frontend (served by NGINX) to a Kubernetes cluster using **Ingress** for routing.
It’s tested locally with **kind (Kubernetes-in-Docker)**, but the same setup works on Minikube, EKS, or GKE.

---

## 🚀 Stack Overview

| Component | Description | Port | Ingress Path |
|------------|--------------|------|---------------|
| **FastAPI** | Backend API (`uvicorn`) | 8000 | `/api` |
| **Vite React (NGINX)** | Frontend static site | 80 | `/` |
| **Ingress (nginx)** | Routes traffic to services | 8080 / 8443 | `/` → web, `/api` → FastAPI |

---

## 🧩 Architecture

Browser ──▶ Ingress (nginx)
              ├── /api/*  → FastAPI Service (ClusterIP)
              └── /       → NGINX Service (ClusterIP, serving React)

> **Ingress** acts as a reverse proxy inside Kubernetes, routing external HTTP(S) requests to the correct internal services based on path or host rules.

---

## 🛠️ Local Development (kind)

### 1️⃣ Create kind cluster
```yaml
# kind-config.yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
  - role: control-plane
    extraPortMappings:
      - containerPort: 80
        hostPort: 8080
      - containerPort: 443
        hostPort: 8443
```

```bash
kind create cluster --config kind-config.yaml
```

### 2️⃣ Install nginx ingress controller
```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
kubectl -n ingress-nginx get pods
```

### 3️⃣ Deploy the app
```bash
kubectl apply -n dev -f fastapi-deployment.yaml
kubectl apply -n dev -f web-deployment.yaml
kubectl apply -n dev -f ingress.yaml
```

### 4️⃣ Access locally
```
http://localhost:8080/          → React frontend
http://localhost:8080/api/...   → FastAPI endpoints
http://localhost:8080/api/docs  → Swagger UI
```

---

## ⚙️ Environment Variables

| Variable | Example | Description |
|-----------|----------|-------------|
| `VITE_API_BASE_URL` | `/api` | Frontend base path for API calls |
| `UVICORN_PORT` | `8000` | FastAPI listening port |
| `UVICORN_HOST` | `0.0.0.0` | Bind address |
| `FASTAPI_ROOT_PATH` | `/api` | (Optional) Root path if Ingress prefixes routes |

---

## 🧠 Short Theory: Ingress in Kubernetes

**Ingress** is a Kubernetes resource that controls external access to Services inside the cluster—typically HTTP(S).

- Without Ingress, you’d expose each service using a `NodePort` or `LoadBalancer`.
- With Ingress, you can:
  - Route by **path** (`/api` → backend, `/` → frontend)
  - Terminate **TLS**
  - Use a single external IP for multiple services
  - Add features like URL rewrites, redirects, and authentication via annotations

Ingress relies on an **Ingress Controller** (e.g., nginx, Traefik, Istio) that actually processes the traffic.

### Ingress on kind
Since **kind** runs Kubernetes inside Docker, it has no cloud LoadBalancer.
Instead, we:
- Install the **nginx ingress controller** manually.
- Map ports 8080 (HTTP) and 8443 (HTTPS) from the host to ports 80/443 inside the ingress controller pod via `extraPortMappings`.
- Access services at `http://localhost:8080` or `https://localhost:8443`.

---

## 🧾 Example Ingress (api + web)

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: opsbox-api
  namespace: dev
  annotations:
    nginx.ingress.kubernetes.io/use-regex: "true"
    nginx.ingress.kubernetes.io/rewrite-target: "/$2"
spec:
  ingressClassName: nginx
  rules:
    - http:
        paths:
          - path: /api(/|$)(.*)
            pathType: ImplementationSpecific
            backend:
              service:
                name: opsbox-api
                port:
                  number: 8000
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: opsbox-web
  namespace: dev
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "false"
spec:
  ingressClassName: nginx
  rules:
    - http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: opsbox-web
                port:
                  number: 80
```

---

## ✅ Testing checklist

| Endpoint | Expected | Notes |
|-----------|-----------|-------|
| `/` | React SPA loads | |
| `/api/kubectl/namespaces` | JSON from FastAPI | |
| `/api/docs` | Swagger UI loads | Works if `root_path="/api"` |
| `/assets/...` | JS/CSS files | MIME type = JS/CSS (not HTML) |

---

## 🧩 Troubleshooting

| Issue | Cause | Fix |
|--------|--------|-----|
| 404 on `/api/*` | Wrong Ingress path / rewrite | Use `/api(/|$)(.*)` + rewrite |
| MIME type “text/html” for JS | SPA fallback serving HTML | Tighten NGINX config for static assets |
| 308 redirect on `:8080` | HTTPS redirect on | Disable `ssl-redirect` for local |
| `docs` 404 via Ingress | FastAPI missing `root_path` | Add `root_path="/api"` or set `X-Forwarded-Prefix` |
| `Failed to load module script` | Asset path mismatch | Set `base: '/'` in Vite config |

---

## 🧾 License
MIT © 2025 — OpsBox Demo
