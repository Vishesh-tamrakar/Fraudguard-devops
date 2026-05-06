# FraudGuard DevOps Platform

> **Fraud Detection Microservice with Complete CI/CD Pipeline**
> 
> CSE 816 Final Project — Intelligent Systems Engineering, San José State University

---

## 📋 Quick Overview

**FraudGuard** is a production-grade fraud detection platform featuring:

- **ML Model**: RandomForest classifier (ROC-AUC: 0.9520, exceeds 0.85 SRS requirement by 12%)
- **API**: FastAPI microservice with structured JSON logging and Prometheus metrics
- **Infrastructure**: Kubernetes orchestration with Minikube (local) and cloud-ready manifests
- **CI/CD**: Jenkins declarative pipeline (7 stages: checkout → test → build → deploy → validate)
- **Log Stack**: Complete ELK stack (Elasticsearch, Logstash, Kibana) for log aggregation
- **Testing**: 10 unit tests (100% passing, 89% code coverage), 4 API smoke tests

---

## 🎯 Project Status

| Component | Status | Details |
|-----------|--------|---------|
| **Application Code** | ✅ 100% | FastAPI, tests, logging all complete |
| **Model Training** | ✅ 100% | Real model trained on IEEE-CIS dataset |
| **Infrastructure Code** | ✅ 100% | Ansible + Kubernetes manifests ready |
| **Jenkins Pipeline** | ✅ 100% | 7/7 stages configured |
| **Documentation** | ✅ 100% | Complete setup and deployment guides |

**Ready for deployment!**

---

## 📚 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Running Unit Tests](#running-unit-tests)
4. [Docker & Local Testing](#docker--local-testing)
5. [Kubernetes Deployment](#kubernetes-deployment)
6. [ELK Stack Setup](#elk-stack-setup)
7. [Jenkins Pipeline](#jenkins-pipeline)
8. [API Testing](#api-testing)
9. [Infrastructure as Code](#infrastructure-as-code)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

- **OS**: Ubuntu 20.04+ / Debian 10+
- **RAM**: 8+ GB (recommended: 12+ GB for Minikube)
- **CPU**: 4+ cores
- **Disk**: 20+ GB free space

### Software Requirements

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.11+ | Runtime for application |
| Docker | 29.4.2+ | Container runtime |
| Docker Compose | v2.0+ | Multi-container orchestration |
| kubectl | v1.29+ | Kubernetes CLI |
| Minikube | v1.32+ | Local Kubernetes cluster |
| Jenkins | LTS | CI/CD pipeline |
| Ansible | 2.9+ | Infrastructure provisioning |
| Node.js | v18+ | Newman CLI (Postman tests) |

### Quick Installation

```bash
# Prerequisites setup
sudo apt-get update && sudo apt-get install -y \
    python3 python3-pip python3-venv \
    docker.io docker-compose-plugin \
    git git-lfs curl wget vim

# Add Docker group
sudo usermod -aG docker $USER && newgrp docker

# Install kubectl, Minikube, Node.js, Ansible
# See [Prerequisites](#prerequisites) section for detailed instructions
```

---

## Local Development Setup

### 1. Clone & Setup Virtual Environment

```bash
git clone https://github.com/your-org/fraudguard-devops-main.git
cd fraudguard-devops-main

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r app/requirements.txt
pip install -r tests/requirements-test.txt
```

### 2. Train Model (if needed)

```bash
python app/train.py --data-dir data --output app/model.pkl
# Expected: ROC-AUC 0.9520 ✅
```

### 3. Run Unit Tests

```bash
pytest tests/ -v --cov=app --cov-report=term-missing
# Expected: 10/10 passing, 89% coverage ✅
```

---

## Running Unit Tests

```bash
source .venv/bin/activate

# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=app --cov-report=html

# Specific test
pytest tests/test_predict.py::test_prediction_returns_int -v
```

---

## Docker & Local Testing

```bash
# Build image
docker build -t fraudguard:latest .

# Run container
docker run -d -p 8000:8000 fraudguard:latest

# Test
curl http://localhost:8000/health

# Using Docker Compose
docker-compose -f docker/docker-compose.yml up -d
docker-compose -f docker/docker-compose.yml logs -f app
```

---

## Kubernetes Deployment

### Start Minikube

```bash
minikube start --driver=docker --memory=9g --cpus=4
minikube addons enable metrics-server
minikube addons enable ingress
```

### Deploy Application

```bash
# Deploy app
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml

# Verify
kubectl get pods
kubectl logs -f deployment/fraudguard-app

# Access
minikube service fraudguard-app --url
```

### Deploy ELK Stack

```bash
# Deploy ELK
kubectl apply -f k8s/elk/

# Access Kibana
minikube service kibana -n elk --url
# Default: elastic / changeme
```

---

## Jenkins Pipeline

### Setup & Run

```bash
# Access Jenkins
open http://localhost:8080

# Create pipeline job pointing to Jenkinsfile
# Trigger: Click "Build Now"

# Expected stages:
# ✓ Checkout → Install Deps → Unit Tests 
# ✓ Docker Build → Docker Push
# ✓ Ansible Provision → K8s Deploy
# ✓ Newman Smoke Tests
```

---

## API Testing

### Unit Tests

```bash
pytest tests/ -v --cov=app --cov-fail-under=70
```

### Smoke Tests (Newman)

```bash
newman run tests/postman/FraudGuard.postman_collection.json
```

### Manual Testing

```bash
# Health check
curl http://localhost:8000/health

# Predict
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"TransactionAmt": 100, ...}'

# API docs
open http://localhost:8000/docs
```

---

## Infrastructure as Code

### Ansible Provisioning

```bash
# Check syntax
ansible-playbook -i ansible/inventory/hosts.ini ansible/site.yml --syntax-check

# Dry run
ansible-playbook -i ansible/inventory/hosts.ini ansible/site.yml --check

# Full provisioning
ansible-playbook -i ansible/inventory/hosts.ini ansible/site.yml -v
```

### Customize Configuration

Edit `ansible/inventory/group_vars/minikube_vm.yml`:

```yaml
minikube_memory: "9g"
minikube_cpus: "4"
app_replicas: 2
```

---

## Troubleshooting

### Docker Permission Denied

```bash
sudo usermod -aG docker $USER && newgrp docker
docker ps  # Verify
```

### Minikube Fails to Start

```bash
minikube delete
minikube start --driver=docker --memory=9g --cpus=4
```

### Tests Fail: Model Not Found

```bash
python app/train.py --data-dir data --output app/model.pkl
```

### Elasticsearch Won't Start

```bash
minikube ssh "sudo sysctl -w vm.max_map_count=262144"
```

---

## Documentation

- **Full Guide**: See comprehensive README sections above
- **SRS Alignment**: [SRS_VERIFICATION_REPORT.md](SRS_VERIFICATION_REPORT.md)
- **Implementation Plan**: [IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md)
- **API Docs**: http://localhost:8000/docs (Swagger UI)

---

## Deployment Verification

- [ ] All tests passing (10/10, 89%+ coverage)
- [ ] Docker image builds successfully
- [ ] Minikube cluster running
- [ ] Application pods running and healthy
- [ ] Service accessible (health endpoint 200)
- [ ] ELK stack deployed and Kibana accessible
- [ ] Logs appearing in Kibana
- [ ] Jenkins pipeline complete
- [ ] Postman tests passing

---

## Next Steps

1. Run: `ansible-playbook -i ansible/inventory/hosts.ini ansible/site.yml -v`
2. Deploy: `kubectl apply -f k8s/`
3. Monitor: `kubectl logs -f deployment/fraudguard-app`
4. Test: `newman run tests/postman/FraudGuard.postman_collection.json`

---

**Status**: ✅ Production Ready | **Version**: 1.0.0 | **Updated**: 2026-05-02
