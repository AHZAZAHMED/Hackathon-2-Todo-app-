# Hackathon Phase-4 Todo App - Minikube Deployment Guide

## Prerequisites

- Minikube installed and running
- kubectl configured to use Minikube
- Helm 3.x installed
- Docker images built locally:
  - `hackathon-backend:latest`
  - `hackathon-frontend:latest`

## Step 1: Start Minikube

```bash
# Start Minikube (if not already running)
minikube start

# Verify Minikube is running
minikube status
```

## Step 2: Load Docker Images into Minikube

Since we're using local Docker images, we need to load them into Minikube's Docker environment.

```bash
# Load backend image into Minikube
minikube image load hackathon-backend:latest

# Load frontend image into Minikube
minikube image load hackathon-frontend:latest

# Verify images are loaded
minikube image ls | grep hackathon
```

## Step 3: Update values.yaml (if needed)

Review and update the following in `values.yaml`:

- Database URL (already configured for Neon PostgreSQL)
- Better Auth Secret
- OpenRouter API Key
- OpenAI Domain Key

All sensitive values are stored in Kubernetes Secrets.

## Step 4: Install the Helm Chart

```bash
# Navigate to the chart directory
cd Ai-Todo-App

# Install the chart
helm install todo-app . --namespace default

# Or upgrade if already installed
helm upgrade --install todo-app . --namespace default
```

## Step 5: Verify Deployment

```bash
# Check pod status
kubectl get pods

# Check services
kubectl get services

# Check deployments
kubectl get deployments

# View pod logs (backend)
kubectl logs -l app.kubernetes.io/component=backend

# View pod logs (frontend)
kubectl logs -l app.kubernetes.io/component=frontend
```

## Step 6: Access the Application

Get Minikube IP and access the application:

```bash
# Get Minikube IP
minikube ip

# Access frontend
# http://<minikube-ip>:30300

# Access backend API
# http://<minikube-ip>:30800/api/health
```

Example:
```bash
# If Minikube IP is 192.168.49.2
# Frontend: http://192.168.49.2:30300
# Backend: http://192.168.49.2:30800
```

## Step 7: Update Frontend Environment Variables

After getting the Minikube IP, you may need to update the frontend deployment to use the correct backend URL:

```bash
# Get Minikube IP
MINIKUBE_IP=$(minikube ip)

# Update frontend deployment with correct backend URL
kubectl set env deployment/todo-app-frontend \
  NEXT_PUBLIC_API_URL=http://$MINIKUBE_IP:30800 \
  BETTER_AUTH_URL=http://$MINIKUBE_IP:30300 \
  NEXT_PUBLIC_APP_URL=http://$MINIKUBE_IP:30300

# Restart frontend pods to apply changes
kubectl rollout restart deployment/todo-app-frontend
```

## Troubleshooting

### Pods not starting

```bash
# Describe pod to see events
kubectl describe pod <pod-name>

# Check pod logs
kubectl logs <pod-name>

# Check if images are loaded
minikube image ls | grep hackathon
```

### ImagePullBackOff error

This means Kubernetes can't find the image. Make sure:
1. Images are built locally with correct names
2. Images are loaded into Minikube using `minikube image load`
3. `imagePullPolicy` is set to `Never` in values.yaml

### Health check failures

```bash
# Check if backend is responding
kubectl exec -it <backend-pod-name> -- curl http://localhost:8000/api/health

# Check if frontend is responding
kubectl exec -it <frontend-pod-name> -- curl http://localhost:3000
```

### Database connection issues

```bash
# Check if DATABASE_URL secret is correct
kubectl get secret todo-app-secret -o jsonpath='{.data.database-url}' | base64 -d

# Test database connection from backend pod
kubectl exec -it <backend-pod-name> -- python -c "import os; print(os.getenv('DATABASE_URL'))"
```

## Useful Commands

```bash
# View all resources
kubectl get all

# View secrets
kubectl get secrets

# View configmaps
kubectl get configmaps

# Port forward to access services locally
kubectl port-forward service/todo-app-frontend 3000:3000
kubectl port-forward service/todo-app-backend 8000:8000

# Delete deployment
helm uninstall todo-app

# View Helm release status
helm status todo-app

# View Helm release values
helm get values todo-app
```

## Uninstall

```bash
# Uninstall the Helm release
helm uninstall todo-app

# Verify all resources are deleted
kubectl get all
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Minikube Cluster                                       │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │  Frontend Deployment                            │  │
│  │  - hackathon-frontend:latest                    │  │
│  │  - Port: 3000                                   │  │
│  │  - NodePort: 30300                              │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │  Backend Deployment                             │  │
│  │  - hackathon-backend:latest                     │  │
│  │  - Port: 8000                                   │  │
│  │  - NodePort: 30800                              │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │  ConfigMap (todo-app-config)                    │  │
│  │  - AI Model                                     │  │
│  │  - App Name                                     │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │  Secret (todo-app-secret)                       │  │
│  │  - Database URL                                 │  │
│  │  - Better Auth Secret                           │  │
│  │  - OpenRouter API Key                           │  │
│  │  - OpenAI Domain Key                            │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
              External PostgreSQL
              (Neon Database)
```

## Notes

- Both frontend and backend use NodePort services for easy access from host machine
- Images use `pullPolicy: Never` to use local images from Minikube's Docker daemon
- Health checks are configured for both services
- Resource limits are set to work well with Minikube's default resources
- All sensitive data is stored in Kubernetes Secrets
- Non-sensitive configuration is stored in ConfigMaps
