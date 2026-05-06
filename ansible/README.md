# Ansible Provisioning Guide for FraudGuard

This directory contains the Ansible playbooks and roles for provisioning the FraudGuard infrastructure.

## Structure

```
ansible/
├── site.yml                          # Master playbook (entry point)
├── inventory/
│   ├── hosts.ini                     # Inventory with host definitions
│   └── group_vars/
│       └── minikube_vm.yml           # Group-level variables
└── roles/
    ├── common/
    │   ├── tasks/main.yml            # System baseline (packages, timezone, etc.)
    │   └── handlers/main.yml
    ├── docker/
    │   ├── tasks/main.yml            # Docker installation and configuration
    │   └── handlers/main.yml
    └── kubernetes/
        └── tasks/main.yml            # K8s/Minikube installation
```

## Prerequisites

- **Ansible 2.9+**: Install with `pip install ansible`
- **Python 3.6+** on target hosts
- **Sudo privileges** on target hosts
- **Docker** available on the system (for Minikube to use as driver)
- **~10GB free disk space** for Minikube cluster
- **~4+ vCPU** cores available

### Install Ansible

```bash
# Using pip (recommended)
pip install ansible

# Using apt (Ubuntu/Debian)
sudo apt-get install ansible

# Verify installation
ansible --version
```

## Quick Start

### 1. Verify Inventory

```bash
ansible-inventory -i ansible/inventory/hosts.ini --list
```

### 2. Run Provisioning Playbook

```bash
# Full provisioning (requires sudo password)
# The playbook needs elevated privileges for system configuration
ansible-playbook -i ansible/inventory/hosts.ini ansible/site.yml -v --ask-become-pass

# Syntax check (no password needed)
ansible-playbook -i ansible/inventory/hosts.ini ansible/site.yml --syntax-check

# Specific role only (with sudo)
ansible-playbook -i ansible/inventory/hosts.ini ansible/site.yml -t docker --ask-become-pass

# Check mode (dry run, with sudo)
ansible-playbook -i ansible/inventory/hosts.ini ansible/site.yml --check --ask-become-pass

# If you have passwordless sudo configured:
ansible-playbook -i ansible/inventory/hosts.ini ansible/site.yml -v
```

**Note**: When running the playbook, you'll be prompted for your sudo password. Enter it when prompted.

## Role Descriptions

### 1. **common** — System Baseline Configuration
Handles system-level setup:
- Updates apt package cache
- Upgrades all packages
- Installs system packages (curl, wget, git, vim, build tools, etc.)
- Sets timezone to UTC
- Configures system locale
- Disables UFW firewall (development mode)
- Creates necessary directories (`/var/log/app`, `/opt/fraudguard`, `/data`)

**Duration**: ~5 minutes
**Tags**: `common`, `packages`, `timezone`, `firewall`

### 2. **docker** — Container Runtime Installation
Sets up Docker environment:
- Adds Docker GPT key and apt repository
- Installs Docker Engine (29.4.2), Docker CLI, containerd.io
- Installs Docker Compose plugin
- Enables Docker service (systemd)
- Configures non-root user access to Docker
- Sets up Docker daemon configuration (JSON logging, overlay2 storage)
- Verifies Docker installation

**Duration**: ~3 minutes
**Tags**: `docker`, `packages`, `service`
**Verification**: `docker ps` and `docker --version` should work without sudo

### 3. **kubernetes** — Orchestration Platform Setup
Deploys Kubernetes cluster:
- Downloads and installs kubectl (v1.29.15)
- Downloads and installs Minikube (v1.32.0)
- Starts Minikube cluster with Docker driver
  - Memory: 9GB
  - CPUs: 4
  - Kubernetes version: v1.29.15
- Enables metrics-server addon (for HPA/scaling)
- Enables ingress addon (for ingress controllers)
- Creates Kubernetes namespaces (default, elk, monitoring)
- Verifies cluster readiness

**Duration**: ~5-10 minutes (cluster initialization)
**Tags**: `kubernetes`, `kubectl`, `minikube`, `addons`
**Verification**: `kubectl get nodes` and `kubectl cluster-info` should return cluster info

## Configuration Variables

Edit `ansible/inventory/group_vars/minikube_vm.yml` to customize:

```yaml
# Minikube resource allocation
minikube_memory: "9g"        # Memory for Minikube VM
minikube_cpus: "4"           # CPU cores for Minikube VM
minikube_driver: "docker"    # Driver type (docker or virtualbox)

# Kubernetes versions
kubectl_version: "v1.29.15"
minikube_version: "v1.32.0"

# Application configuration
app_replicas: 2              # Number of app pods
app_port: 8000              # Application port
app_namespace: default       # Default namespace

# ELK Stack configuration
elk_namespace: elk
elasticsearch_memory: 512m
kibana_port: 5601

# Logging
log_level: INFO
log_retention_days: 7
```

## Troubleshooting

### Issue: "Docker daemon is not running"
```bash
# Start Docker manually
sudo systemctl start docker

# Verify
docker ps
```

### Issue: "Permission denied while trying to connect to Docker daemon"
```bash
# Add user to docker group (already done by playbook)
sudo usermod -aG docker $USER
newgrp docker

# Verify
docker ps
```

### Issue: "Minikube fails to start"
```bash
# Check Docker is running and accessible
docker ps

# Delete existing cluster and retry
minikube delete
ansible-playbook -i ansible/inventory/hosts.ini ansible/site.yml -t kubernetes

# Check Minikube status
minikube status
```

### Issue: "kubectl: command not found"
```bash
# Verify kubectl was installed
which kubectl

# If not found, reinstall
ansible-playbook -i ansible/inventory/hosts.ini ansible/site.yml -t kubernetes
```

### Issue: "metrics-server not ready"
```bash
# Check metrics-server status
kubectl get deployment metrics-server -n kube-system

# Wait for it to be ready (may take 2-3 minutes)
kubectl rollout status deployment/metrics-server -n kube-system

# View logs
kubectl logs -f deployment/metrics-server -n kube-system
```

## Useful Commands After Provisioning

```bash
# View cluster info
kubectl cluster-info
kubectl get nodes
kubectl get namespaces

# View metrics (after metrics-server is ready)
kubectl top nodes
kubectl top pods

# Access Minikube dashboard
minikube dashboard

# SSH into Minikube
minikube ssh

# Create tunnel for NodePort services (in separate terminal)
minikube tunnel

# Delete entire cluster
minikube delete
```

## Verifying Successful Provisioning

After the playbook completes, verify all components:

```bash
# 1. Check system
date                    # Should show UTC timezone
uname -a               # System info

# 2. Check Docker
docker --version       # Should be 29.4.2
docker ps             # Should list containers (empty is OK)
docker run --rm hello-world  # Should run without errors

# 3. Check Kubernetes
kubectl version --client          # Should show v1.29.15
kubectl cluster-info             # Should show cluster info
kubectl get nodes                # Should show minikube node
kubectl get pods -A              # Should show all pods

# 4. Check namespaces
kubectl get namespaces           # Should show default, elk, monitoring, kube-*

# 5. Check metrics
kubectl get deployment metrics-server -n kube-system  # Should be Running
kubectl top nodes                # Should show node metrics
```

## Next Steps

After provisioning is complete:

1. **Deploy FraudGuard Application**
   ```bash
   kubectl apply -f k8s/
   ```

2. **Monitor Deployment**
   ```bash
   kubectl get deployment fraudguard-app
   kubectl logs -f deployment/fraudguard-app
   ```

3. **Access Application**
   ```bash
   minikube service fraudguard-app --url
   ```

4. **Deploy ELK Stack**
   ```bash
   kubectl apply -f k8s/elk/
   ```

5. **Access Kibana**
   ```bash
   kubectl port-forward -n elk svc/kibana 5601:5601
   # Open browser: http://localhost:5601
   ```

## Support

For issues or questions:
1. Check logs: `ansible-playbook ... -vv` (verbose mode)
2. Review IMPLEMENTATION_ROADMAP.md for detailed setup steps
3. Check SRS_VERIFICATION_REPORT.md for requirements alignment

---

**Last Updated**: 2026-05-02
**Status**: Ready for Kubernetes Manifests (Phase 2)
