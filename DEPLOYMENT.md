# Deployment Guide

This guide covers deploying the Insurance Recommender System to production.

## Deployment Options

### Option 1: Docker Compose (Recommended for Quick Deploy)

**Best for**: Small to medium deployments, single server

```bash
# Production docker-compose
docker-compose -f docker-compose.prod.yml up -d
```

### Option 2: Cloud Platform (AWS, Azure, GCP)

**Best for**: Scalable production deployments

### Option 3: Platform as a Service (Heroku, Railway, Render)

**Best for**: Quick deployment without infrastructure management

## Pre-Deployment Checklist

- [ ] Update `.env` with production values
- [ ] Set `DEBUG=False` in Django settings
- [ ] Configure production database (MongoDB Atlas)
- [ ] Set secure SECRET_KEY values
- [ ] Configure ALLOWED_HOSTS
- [ ] Set up SSL certificates
- [ ] Enable HTTPS
- [ ] Configure CORS properly
- [ ] Set up monitoring and logging
- [ ] Backup strategy for database

## Production Environment Variables

Create `.env.production`:

```bash
# MongoDB (Atlas recommended)
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/insurance?retryWrites=true&w=majority
MONGODB_DB_NAME=insurance_recommender

# Flask
FLASK_SECRET_KEY=<strong-random-key>
FLASK_ENV=production
FLASK_PORT=5000

# Django
DJANGO_SECRET_KEY=<strong-random-key>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
FLASK_SERVICE_URL=https://api.yourdomain.com

# LLM APIs (Optional)
HUGGINGFACE_API_KEY=your_key
TOGETHER_AI_API_KEY=your_key

# Redis (Optional)
REDIS_URL=redis://redis:6379/0
```

## MongoDB Atlas Setup

1. **Create Account**: [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)

2. **Create Cluster**:
   - Choose free tier (M0) for development
   - Select region closest to your server
   - Name: `insurance-recommender`

3. **Security**:
   - Create database user with password
   - Whitelist IP addresses (or 0.0.0.0/0 for testing)

4. **Get Connection String**:
   ```
   mongodb+srv://<username>:<password>@cluster.mongodb.net/insurance
   ```

5. **Load Data**:
   ```bash
   # Update .env with Atlas URI
   python3 scripts/load_data.py
   ```

## Heroku Deployment

### Flask Service

```bash
cd flask_service

# Login to Heroku
heroku login

# Create app
heroku create insurance-recommender-api

# Add MongoDB addon
heroku addons:create mongolab:sandbox

# Set environment variables
heroku config:set FLASK_ENV=production
heroku config:set FLASK_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')

# Deploy
git init
heroku git:remote -a insurance-recommender-api
git add .
git commit -m "Deploy Flask service"
git push heroku master
```

### Django App

```bash
cd django_app

# Create app
heroku create insurance-recommender-web

# Set environment variables
heroku config:set DJANGO_DEBUG=False
heroku config:set DJANGO_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
heroku config:set FLASK_SERVICE_URL=https://insurance-recommender-api.herokuapp.com

# Deploy
git init
heroku git:remote -a insurance-recommender-web
git add .
git commit -m "Deploy Django app"
git push heroku master

# Run migrations
heroku run python manage.py migrate
```

## AWS Deployment

### Architecture

```
┌─────────────────┐
│   CloudFront    │ (CDN)
└────────┬────────┘
         │
┌────────▼────────┐
│   ALB (HTTPS)   │ (Load Balancer)
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼──┐  ┌──▼───┐
│ ECS  │  │ ECS  │ (Containers)
│Flask │  │Django│
└───┬──┘  └──┬───┘
    │        │
    └────┬───┘
         │
┌────────▼────────┐
│  DocumentDB     │ (MongoDB-compatible)
│  (or Atlas)     │
└─────────────────┘
```

### Setup Steps

1. **Create ECS Cluster**
2. **Build Docker images**
3. **Push to ECR**
4. **Create Task Definitions**
5. **Create Services**
6. **Configure Load Balancer**
7. **Set up Route53 for DNS**

## Docker Production Configuration

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  mongodb:
    image: mongo:7.0
    restart: always
    volumes:
      - mongodb_data:/data/db
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_PASSWORD}

  flask_service:
    build:
      context: ./flask_service
    restart: always
    ports:
      - "5000:5000"
    environment:
      - MONGODB_URI=mongodb://admin:${MONGO_PASSWORD}@mongodb:27017/
      - FLASK_ENV=production
    depends_on:
      - mongodb

  django_app:
    build:
      context: ./django_app
    restart: always
    ports:
      - "8000:8000"
    environment:
      - DJANGO_DEBUG=False
      - FLASK_SERVICE_URL=http://flask_service:5000
    depends_on:
      - flask_service

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - django_app

volumes:
  mongodb_data:
```

## Nginx Configuration

Create `nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream django {
        server django_app:8000;
    }

    upstream flask {
        server flask_service:5000;
    }

    server {
        listen 80;
        server_name yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl;
        server_name yourdomain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        location / {
            proxy_pass http://django;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        location /api/ {
            proxy_pass http://flask;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
```

## SSL Certificates

### Using Let's Encrypt (Free)

```bash
# Install certbot
sudo apt install certbot

# Get certificate
sudo certbot certonly --standalone -d yourdomain.com

# Certificates will be in:
# /etc/letsencrypt/live/yourdomain.com/fullchain.pem
# /etc/letsencrypt/live/yourdomain.com/privkey.pem
```

## Monitoring

### Application Monitoring

**Sentry** (Error tracking):

```python
# In flask_service/app.py
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0
)
```

### Infrastructure Monitoring

- **CloudWatch** (AWS)
- **Datadog**
- **New Relic**

### Logging

Centralized logging with ELK stack or CloudWatch Logs.

## Backup Strategy

### MongoDB Backups

```bash
# Automated daily backups
mongodump --uri="mongodb+srv://..." --out=/backups/$(date +%Y%m%d)

# Restore
mongorestore --uri="mongodb+srv://..." /backups/20241115
```

### Application Data

- Version control (Git)
- Docker images (registry)
- Configuration files (encrypted)

## Security Best Practices

1. **Environment Variables**: Never commit secrets
2. **HTTPS Only**: Force SSL
3. **Authentication**: Implement JWT or OAuth
4. **Rate Limiting**: Prevent abuse
5. **Input Validation**: Use Pydantic schemas
6. **CORS**: Configure properly
7. **Database**: Use authentication
8. **Firewall**: Restrict ports
9. **Updates**: Keep dependencies current

## Performance Optimization

1. **Caching**: Redis for API responses
2. **CDN**: CloudFront for static files
3. **Database**: Indexes on frequent queries
4. **Compression**: Gzip responses
5. **Minification**: JS/CSS assets

## Health Checks

```python
# Flask health endpoint
@app.route('/health')
def health():
    return {
        'status': 'healthy',
        'database': 'connected' if db else 'disconnected',
        'timestamp': datetime.now().isoformat()
    }
```

Monitor this endpoint with:
- AWS ELB health checks
- Uptime monitors (Pingdom, UptimeRobot)

## Rollback Strategy

```bash
# Docker rollback
docker-compose down
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d --force-recreate

# Heroku rollback
heroku releases  # List releases
heroku rollback v123  # Rollback to specific version
```

## Cost Estimation

### Small Scale (Development/Testing)

- MongoDB Atlas Free (M0): $0
- Heroku Hobby: $14/month (Flask + Django)
- Total: ~$14/month

### Medium Scale (Production)

- MongoDB Atlas Shared (M10): $57/month
- AWS ECS: ~$30/month (2 tasks)
- ALB: $16/month
- Total: ~$103/month

### Large Scale

- MongoDB Atlas Dedicated: $250+/month
- AWS ECS with auto-scaling: $200+/month
- CloudFront CDN: Variable
- Total: $450+/month

## Post-Deployment

1. **Test All Endpoints**: Run `scripts/test_api.py`
2. **Monitor Logs**: Check for errors
3. **Performance Test**: Load testing with Apache Bench
4. **User Testing**: Beta users feedback
5. **Analytics**: Google Analytics integration

## Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose logs flask_service
docker-compose logs django_app

# Heroku logs
heroku logs --tail -a insurance-recommender-api
```

### Database Connection Issues

1. Check connection string
2. Verify IP whitelist
3. Test with mongosh
4. Check firewall rules

### High Latency

1. Enable caching
2. Optimize database queries
3. Use CDN for static files
4. Scale horizontally

## Support

For deployment issues:
- Check service logs
- Verify environment variables
- Test database connection
- Review security group rules

