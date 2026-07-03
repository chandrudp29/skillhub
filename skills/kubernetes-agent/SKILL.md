---
name: kubernetes-agent
description: Kubernetes production patterns — manifests, resource sizing, health probes, scaling, secrets, networking, and troubleshooting
version: 1.0.0
tags: [kubernetes, k8s, devops, containers, cloud, infrastructure]
agents: [claude, cursor, codex, gemini]
---

## When to Use
Apply when writing, reviewing, or debugging Kubernetes manifests and cluster configurations. Works for any cloud provider (EKS, GKE, AKS) and on-prem.

## Core Rules

- Always set CPU/memory `requests` AND `limits` — never leave them unset
- Always define `readinessProbe` and `livenessProbe` — they prevent bad rollouts
- Never run containers as root — set `runAsNonRoot: true`
- Store secrets in a secrets manager (Vault, AWS Secrets Manager) — not Kubernetes Secrets (they're just base64)
- Use `RollingUpdate` strategy with `maxUnavailable: 0` for zero-downtime deploys

## Deployment Template

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-server
  labels:
    app: api-server
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 0
      maxSurge: 1
  selector:
    matchLabels:
      app: api-server
  template:
    metadata:
      labels:
        app: api-server
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
      containers:
        - name: api-server
          image: myapp:1.2.3  # never use :latest in production
          ports:
            - containerPort: 8080
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 512Mi
          readinessProbe:
            httpGet:
              path: /healthz/ready
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /healthz/live
              port: 8080
            initialDelaySeconds: 15
            periodSeconds: 20
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: app-secrets
                  key: database-url
```

## Resource Sizing

```
Requests: what the scheduler guarantees (use P50 of actual usage)
Limits:   ceiling that triggers OOMKill/throttle (use P99 + 20% headroom)

Common starting points:
  Small service:  requests: 50m CPU / 64Mi RAM,  limits: 200m / 256Mi
  Medium service: requests: 100m / 128Mi,         limits: 500m / 512Mi
  Heavy service:  requests: 500m / 512Mi,         limits: 2000m / 2Gi

CPU throttling: hitting CPU limit slows the container (not killed)
Memory OOMKill: hitting memory limit kills the container immediately
→ Set memory limit generously; set CPU limit conservatively
```

## Horizontal Pod Autoscaling

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-server-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-server
  minReplicas: 2
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

## Networking

```yaml
# Service — exposes pods inside the cluster
apiVersion: v1
kind: Service
metadata:
  name: api-server
spec:
  selector:
    app: api-server
  ports:
    - port: 80
      targetPort: 8080

# Ingress — exposes services to the internet
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api-ingress
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  rules:
    - host: api.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: api-server
                port:
                  number: 80
```

## Troubleshooting

```bash
# Pod is stuck — diagnose fast
kubectl describe pod <pod-name>        # events, conditions, image pull errors
kubectl logs <pod-name> --previous     # logs from the previous (crashed) container
kubectl exec -it <pod-name> -- sh      # shell into the container

# Common causes of CrashLoopBackOff:
#   1. App crashes on startup — check logs
#   2. OOMKilled — increase memory limit
#   3. Liveness probe too aggressive — increase initialDelaySeconds
#   4. Missing env var / secret — check envFrom and secretKeyRef

# Resource pressure
kubectl top nodes                       # node CPU/memory
kubectl top pods --all-namespaces       # find resource hogs

# Rollback
kubectl rollout history deployment/api-server
kubectl rollout undo deployment/api-server --to-revision=2
```
