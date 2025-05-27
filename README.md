# MedBot – Medical Misinformation Detection Chatbot (GCP Deployment)

MedBot is an AI-powered chatbot designed to detect and classify medical misinformation using a fine-tuned large language model. It is deployed on Google Cloud Platform using Kubernetes and MongoDB.

---

## 🧩 Components

- **Frontend:** React-based web UI for user interaction
- **Gateway:** FastAPI backend handling classification and history APIs
- **MongoDB:** Replica set deployed via StatefulSet for storing chat logs
- **LLM Inference:** Classification handled via Colab-hosted Mistral-7B model
- **Kubernetes:** All services containerized and orchestrated on GKE

---

## 📁 Folder Structure
```
medbot-GCP/
├── gateway-service/k8s/         # Deployment, secret, service account for gateway
├── medical-ui/k8s/              # Frontend deployment, HPA, service account
├── mongo-database-k8s/          # MongoDB StatefulSet, headless service
├── ...                          # Other app-related code
```

---

## ⚙️ Kubernetes Features
- Horizontal Pod Autoscaler (HPA) for frontend
- MongoDB replica set with headless service
- Custom service accounts for security isolation
- Ingress routing for `/`, `/classify`, and `/history`

---

## 🧪 Monitoring & Logging
- GCP Cloud Monitoring for CPU/Memory usage
- Cloud Logging for container and application logs

---

## 🚀 Deployment Notes
- Inference is done externally via Colab and exposed through a webhook
- Secrets (e.g., Mongo URI, inference endpoint) managed via Kubernetes Secrets

---

## 📌 Author
**Adeel Ahmed**  
GitHub: [@AdeelAhmedIqbal](https://github.com/AdeelAhmedIqbal)

---

