#!/bin/bash

echo "Enter your new ngrok URL (e.g., https://abc123.ngrok.io):"
read NGROK_URL

cat <<EOF > gateway-service/k8s/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: gateway-secret
type: Opaque
stringData:
  INFERENCE_API_URL: "$NGROK_URL"
EOF

# Use full path to kubectl
KUBECTL=$(which kubectl)

$KUBECTL delete secret gateway-secret --ignore-not-found
$KUBECTL apply -f gateway-service/k8s/secret.yaml
$KUBECTL rollout restart deployment gateway-deployment

echo "✅ Gateway service updated to use: $NGROK_URL"

