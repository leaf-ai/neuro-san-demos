#!/bin/bash
set -euo pipefail

IMAGE=${1:-ghcr.io/your-org/neuro-san-studio:latest}
NAMESPACE=production

kubectl set image deployment/neuro-san-studio neuro-san-studio="$IMAGE" -n "$NAMESPACE"
kubectl rollout status deployment/neuro-san-studio -n "$NAMESPACE"
