# 🐳 TerraForge Studio - Docker Deployment Guide

## Quick Start

### Development Mode (Simple)

```bash
# Start the application
docker-compose up -d

# View logs
docker-compose logs -f terraforge

# Stop the application
docker-compose down
```

The application will be available at:
- **Frontend + API**: http://localhost:8000
- **Nginx Proxy** (if enabled): http://localhost:80

### Production Mode (with Nginx & Redis)

```bash
# Build and start all services
docker-compose up -d

# Check health
curl http://localhost:8000/api/health

# View logs
docker-compose logs -f
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Environment
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=info

# Directories
CACHE_DIR=/app/cache
OUTPUT_DIR=/app/output

# Optional: API Keys for premium data sources
OPENTOPOGRAPHY_API_KEY=your_key_here
SENTINELHUB_CLIENT_ID=your_client_id
SENTINELHUB_CLIENT_SECRET=your_client_secret
AZURE_MAPS_KEY=your_azure_key

# Optional: Ollama for AI features
OLLAMA_HOST=http://host.docker.internal:11434
```

Then use it with docker-compose:

```bash
docker-compose --env-file .env up -d
```

### Volume Management

Data is persisted in Docker volumes:

```bash
# List volumes
docker volume ls | grep terraforge

# Inspect volume
docker volume inspect terraforge_cache

# Backup cache
docker run --rm -v terraforge_cache:/data -v $(pwd):/backup alpine tar czf /backup/cache-backup.tar.gz /data

# Restore cache
docker run --rm -v terraforge_cache:/data -v $(pwd):/backup alpine tar xzf /backup/cache-backup.tar.gz -C /
```

## Build Options

### Custom Build

```bash
# Build with specific tag
docker build -t terraforge:latest .

# Build without cache
docker build --no-cache -t terraforge:latest .

# Multi-platform build
docker buildx build --platform linux/amd64,linux/arm64 -t terraforge:latest .
```

### Build Arguments

```dockerfile
# Example: Use different Python version
docker build --build-arg PYTHON_VERSION=3.12 -t terraforge:latest .
```

## Production Deployment

### SSL Configuration

1. Place your SSL certificates in the `ssl/` directory:
   ```
   ssl/
     ├── cert.pem
     └── key.pem
   ```

2. Uncomment the SSL server block in `nginx.conf`

3. Restart nginx:
   ```bash
   docker-compose restart nginx
   ```

### Scaling

Scale workers for higher throughput:

```bash
# Scale to 4 workers
docker-compose up -d --scale terraforge=4
```

Update `docker-compose.yml` to use load balancing:

```yaml
services:
  terraforge:
    deploy:
      replicas: 4
```

### Resource Limits

Add resource constraints in `docker-compose.yml`:

```yaml
services:
  terraforge:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

## Monitoring

### Health Checks

```bash
# Check service health
docker-compose ps

# Manual health check
curl http://localhost:8000/api/health

# Watch health status
watch -n 5 'curl -s http://localhost:8000/api/health | jq'
```

### Logs

```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f terraforge

# Last 100 lines
docker-compose logs --tail=100 terraforge

# Export logs
docker-compose logs --no-color > terraforge.log
```

### Performance Monitoring

```bash
# Resource usage
docker stats

# Specific container
docker stats terraforge-studio
```

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Change port in docker-compose.yml
   ports:
     - "8001:8000"  # Use 8001 instead of 8000
   ```

2. **Permission denied**
   ```bash
   # Fix volume permissions
   docker-compose run --rm terraforge chown -R terraforge:terraforge /app/cache /app/output
   ```

3. **Out of memory**
   ```bash
   # Increase memory limit
   docker-compose down
   # Edit docker-compose.yml to increase memory limit
   docker-compose up -d
   ```

4. **Build fails**
   ```bash
   # Clean build
   docker-compose down -v
   docker system prune -a
   docker-compose build --no-cache
   ```

### Debug Mode

Run container interactively:

```bash
# Start bash shell
docker-compose run --rm terraforge /bin/bash

# Check Python environment
docker-compose run --rm terraforge python --version

# Test API manually
docker-compose run --rm -p 8000:8000 terraforge uvicorn realworldmapgen.api.main:app --host 0.0.0.0
```

## Maintenance

### Updates

```bash
# Pull latest code
git pull

# Rebuild images
docker-compose build

# Restart services
docker-compose up -d
```

### Cleanup

```bash
# Stop and remove containers
docker-compose down

# Remove volumes (WARNING: deletes all data!)
docker-compose down -v

# Remove images
docker rmi terraforge:latest

# Clean system
docker system prune -a
```

## Advanced

### Using Redis for Queue Management

Redis is included in the docker-compose for batch processing:

```python
# In your application
import redis
r = redis.Redis(host='redis', port=6379)
```

### External Ollama

If running Ollama outside Docker:

```yaml
# docker-compose.yml
services:
  terraforge:
    extra_hosts:
      - "host.docker.internal:host-gateway"
    environment:
      - OLLAMA_HOST=http://host.docker.internal:11434
```

### Database Integration

Add PostgreSQL for persistent storage:

```yaml
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: terraforge
      POSTGRES_USER: terraforge
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## Security Best Practices

1. **Use secrets for sensitive data**
   ```yaml
   secrets:
     api_key:
       file: ./secrets/api_key.txt
   ```

2. **Run as non-root user** (already configured)

3. **Limit network exposure**
   ```yaml
   ports:
     - "127.0.0.1:8000:8000"  # Only localhost
   ```

4. **Regular updates**
   ```bash
   docker-compose pull
   docker-compose up -d
   ```

5. **Use environment-specific configs**
   - `docker-compose.yml` - base config
   - `docker-compose.prod.yml` - production overrides
   
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

## Support

For issues or questions:
- GitHub Issues: https://github.com/yourusername/TerraForge-Studio/issues
- Documentation: https://github.com/yourusername/TerraForge-Studio/docs

