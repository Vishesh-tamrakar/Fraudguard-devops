#!/bin/bash

# ==============================================================================
# FraudGuard DevOps Environment Startup Script
# This script restores the environment after a reboot.
# ==============================================================================

echo "🚀 Starting FraudGuard Environment..."

# 1. Start Minikube
echo "📦 Starting Minikube..."
minikube start --driver=docker

# 2. Start Vault
echo "🔐 Starting Vault in Dev Mode..."
pkill vault || true
# Starting with 0.0.0.0 ensures the Jenkins container can reach it
vault server -dev -dev-root-token-id=root -address=0.0.0.0:8200 > vault.log 2>&1 &

echo "⏳ Waiting for Vault to initialize..."
sleep 5

# 3. Seed Vault Secrets
# Dev-mode Vault loses data on restart, so we re-seed it here.
echo "🔑 Re-seeding Vault secrets..."
export VAULT_ADDR='http://127.0.0.1:8200'
export VAULT_TOKEN='root'

vault kv put secret/dockerhub \
  username="28vishesh" \
  password="MS@97882vi"

# 4. Start ngrok
echo "🌐 Starting ngrok for GitHub Webhooks..."
pkill ngrok || true
# Runs in background, logs to ngrok.log
~/.local/bin/ngrok http 8080 > ngrok.log 2>&1 &

echo "⚠️  Check your ngrok URL: curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url'"
echo "⚠️  If the URL changed, remember to update it in GitHub Repository Settings -> Webhooks!"

# 5. Apply Kubernetes Manifests
echo "☸️  Ensuring Kubernetes workloads are running..."
kubectl apply -f k8s/
kubectl apply -f k8s/elk/

echo ""
echo "✅ Environment Startup Sequence Complete!"
echo "--------------------------------------------------"
echo "Jenkins:   http://localhost:8080"
echo "Vault:     http://localhost:8200"
echo "API:       http://$(minikube ip):30080/health"
echo "Kibana:    http://$(minikube ip):30601"
echo "--------------------------------------------------"
echo "Logs are available in vault.log and ngrok.log"
