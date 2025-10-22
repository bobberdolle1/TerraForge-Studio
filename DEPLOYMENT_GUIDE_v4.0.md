# 🚀 TerraForge Studio v4.0 - Deployment Guide

**Version**: 4.0.0  
**Date**: October 22, 2025  
**Status**: Production Ready

---

## 📋 Prerequisites

### System Requirements

**Frontend**:
- Node.js 18+ 
- npm 9+
- Modern browser (Chrome, Firefox, Safari, Edge)

**Backend**:
- Python 3.9+
- 4GB RAM minimum
- 20GB disk space (for cache + storage)

### Optional Dependencies

**Cloud Storage**:
- AWS account (for S3)
- Azure account (for Blob Storage)

**Multi-User**:
- Database (optional, currently uses JSON files)

---

## 🔧 Installation

### 1. Frontend Setup

```bash
cd frontend-new

# Install dependencies
npm install

# Development
npm run dev

# Production build
npm run build

# Preview production build
npm run preview
```

**Environment**: No .env needed for frontend (proxies to backend)

---

### 2. Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Optional: Cloud storage
pip install boto3 azure-storage-blob

# Optional: Secure auth
pip install bcrypt

# Run server
python -m realworldmapgen.api.main
```

**Default Port**: 8000

---

### 3. Configuration

Create `.env` file in project root:

```env
# Core Settings
OUTPUT_DIR=./output
CACHE_DIR=./cache
PLUGIN_DIR=./plugins
MAX_AREA_KM2=100.0
DEFAULT_RESOLUTION=2048

# Data Sources (Optional)
OPENTOPOGRAPHY_API_KEY=your_key_here
SENTINELHUB_CLIENT_ID=your_id_here
SENTINELHUB_CLIENT_SECRET=your_secret_here
AZURE_MAPS_SUBSCRIPTION_KEY=your_key_here

# Cache Settings
CACHE_MAX_SIZE_GB=10
CACHE_MAX_AGE_DAYS=30

# Cloud Storage - S3 (Optional)
S3_ENABLED=false
S3_BUCKET_NAME=terraforge-data
S3_REGION=us-east-1
S3_ACCESS_KEY=your_access_key
S3_SECRET_KEY=your_secret_key

# Cloud Storage - Azure Blob (Optional)
AZURE_BLOB_ENABLED=false
AZURE_BLOB_CONTAINER=terraforge
AZURE_BLOB_CONNECTION_STRING=your_connection_string
# OR
AZURE_BLOB_ACCOUNT_NAME=your_account
AZURE_BLOB_ACCOUNT_KEY=your_key

# Authentication (Optional for single-user)
AUTH_ENABLED=false
```

---

## 📦 Production Deployment

### Option 1: Docker (Recommended)

```bash
# Build and run
docker-compose up -d

# Access
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

**docker-compose.yml**:
```yaml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./output:/app/output
      - ./cache:/app/cache
    env_file:
      - .env

  frontend:
    build: ./frontend-new
    ports:
      - "3000:3000"
    depends_on:
      - backend
```

---

### Option 2: Manual Deployment

**Backend** (with Gunicorn):
```bash
pip install gunicorn
gunicorn realworldmapgen.api.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

**Frontend** (with Nginx):
```bash
# Build
cd frontend-new
npm run build

# Copy dist/ to nginx
cp -r dist/* /var/www/terraforge/

# Nginx config
server {
    listen 80;
    server_name terraforge.example.com;
    
    root /var/www/terraforge;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

## 🔐 Security Considerations

### Authentication

**Production Recommendations**:
1. Replace SHA256 with **bcrypt** for passwords
2. Use **JWT tokens** instead of session IDs
3. Implement **HTTPS** for all connections
4. Add **rate limiting**
5. Enable **CORS** restrictions

**Install bcrypt**:
```bash
pip install bcrypt
```

**Update auth_manager.py**:
```python
import bcrypt

# Hashing
password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

# Verification  
bcrypt.checkpw(password.encode(), stored_hash)
```

---

### Cloud Storage

**S3 Security**:
- Use **IAM roles** instead of access keys (on EC2/ECS)
- Enable **bucket encryption**
- Restrict **bucket policies**
- Use **VPC endpoints**

**Azure Blob Security**:
- Use **Managed Identity** instead of connection strings
- Enable **encryption at rest**
- Configure **network rules**
- Use **Azure Key Vault** for secrets

---

## 🧪 Testing

### Frontend

```bash
cd frontend-new

# Type check
npm run lint

# Build test
npm run build

# Manual testing checklist
- [ ] Toast notifications appear
- [ ] Presets load and apply
- [ ] History saves/loads
- [ ] Keyboard shortcuts work
- [ ] WebSocket connects
- [ ] Cache UI functional
- [ ] Share links generate
- [ ] Mobile layout responsive
```

### Backend

```bash
# Run tests (if available)
pytest tests/

# Manual API testing
curl http://localhost:8000/api/health
curl http://localhost:8000/api/cache/stats
curl http://localhost:8000/api/plugins/list
curl http://localhost:8000/api/cloud/providers

# WebSocket test
wscat -c ws://localhost:8000/ws/status
```

---

## 📊 Monitoring

### Logs

**Backend Logs**:
```bash
# View logs
tail -f logs/terraforge.log

# Log levels
export LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
```

**Frontend**:
- Browser console для client errors
- Network tab для API calls
- Application tab для PWA/cache

### Metrics

**Track**:
- Generation count
- Cache hit rate
- WebSocket connections
- Cloud storage usage
- User активность

---

## 🔄 Updates & Maintenance

### Updating

**Frontend**:
```bash
cd frontend-new
npm install  # Update dependencies
npm run build
```

**Backend**:
```bash
pip install -r requirements.txt --upgrade
```

### Cache Cleanup

```bash
# Via API
curl -X POST http://localhost:8000/api/cache/optimize

# Manual
rm -rf ./cache/*
```

### Session Cleanup

```bash
# Via API (admin only)
curl -X POST http://localhost:8000/api/auth/sessions/cleanup \
  -H "Authorization: Bearer {admin_token}"
```

---

## 🐛 Troubleshooting

### Common Issues

**1. WebSocket не подключается**
- Проверьте CORS settings
- Убедитесь что proxy настроен (Nginx/Vite)
- Проверьте firewall

**2. Cache не работает**
- Проверьте права на папку `./cache`
- Проверьте disk space
- Проверьте CACHE_MAX_SIZE_GB

**3. Cloud upload fails**
- Verify credentials в `.env`
- Check network connectivity
- Verify bucket/container permissions

**4. Mobile layout broken**
- Clear browser cache
- Check viewport meta tag
- Verify mobile.css loaded

**5. Plugins не загружаются**
- Check `./plugins` directory exists
- Verify plugin syntax
- Check logs for errors

---

## 📈 Scaling

### Horizontal Scaling

**Backend**:
```bash
# Multiple workers
gunicorn -w 8 --bind 0.0.0.0:8000 \
  --worker-class uvicorn.workers.UvicornWorker \
  realworldmapgen.api.main:app
```

**Load Balancer** (Nginx):
```nginx
upstream backend {
    server localhost:8001;
    server localhost:8002;
    server localhost:8003;
    server localhost:8004;
}

server {
    location /api {
        proxy_pass http://backend;
    }
}
```

### Database Migration

For high user counts, migrate from JSON to PostgreSQL/MongoDB:

```python
# Replace file storage with DB
# Update auth_manager.py, share_routes.py
```

---

## 🎯 Post-Deployment Checklist

- [ ] Frontend builds без errors
- [ ] Backend starts и health check passes
- [ ] WebSocket endpoint accessible
- [ ] Cache directory writable
- [ ] Plugin directory exists
- [ ] SSL/TLS configured (production)
- [ ] CORS configured correctly
- [ ] Backup strategy in place
- [ ] Monitoring setup
- [ ] Rate limiting configured
- [ ] Cloud storage tested (if enabled)
- [ ] Multi-user auth tested (if enabled)

---

## 📞 Support

**Issues**: GitHub Issues  
**Docs**: `/docs` folder  
**API Docs**: http://localhost:8000/docs

---

**🎉 TerraForge Studio v4.0 - Ready for Production!**

<div align="center">

**Complete Professional Terrain Generation Platform**

[Docs](docs/) • [GitHub](https://github.com/yourusername/TerraForge-Studio) • [API](http://localhost:8000/docs)

</div>

