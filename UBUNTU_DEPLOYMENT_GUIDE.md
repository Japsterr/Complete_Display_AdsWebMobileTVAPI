# Ubuntu Production Deployment Guide with Portainer

This guide covers deploying the Display Ads API system on Ubuntu with Portainer management via SSH/PuTTY.

## Table of Contents
1. [Server Requirements](#server-requirements)
2. [Initial Server Setup](#initial-server-setup)
3. [Docker & Portainer Installation](#docker--portainer-installation)
4. [Application Deployment](#application-deployment)
5. [Production Configuration](#production-configuration)
6. [SSL Setup with Let's Encrypt](#ssl-setup-with-lets-encrypt)
7. [Monitoring & Maintenance](#monitoring--maintenance)
8. [Backup Strategy](#backup-strategy)
9. [Troubleshooting](#troubleshooting)

## Server Requirements

### Minimum Specifications
- **CPU**: 2 vCPU cores
- **RAM**: 4GB (8GB recommended)
- **Storage**: 50GB SSD
- **OS**: Ubuntu 20.04 LTS or 22.04 LTS
- **Network**: Public IP with ports 80, 443, 22 accessible

### Recommended Specifications
- **CPU**: 4 vCPU cores
- **RAM**: 8GB
- **Storage**: 100GB SSD
- **OS**: Ubuntu 22.04 LTS

## Initial Server Setup

### 1. Connect via PuTTY/SSH

```bash
# Connect to your server
ssh root@YOUR_SERVER_IP

# Or if using a non-root user
ssh your_username@YOUR_SERVER_IP
```

### 2. Update System

```bash
# Update package lists
sudo apt update && sudo apt upgrade -y

# Install essential packages
sudo apt install -y curl wget git htop unzip software-properties-common apt-transport-https ca-certificates gnupg lsb-release

# Set timezone (optional)
sudo timedatectl set-timezone UTC
```

### 3. Create Application User

```bash
# Create a dedicated user for the application
sudo adduser displayads
sudo usermod -aG sudo displayads
sudo usermod -aG docker displayads  # We'll create docker group later

# Switch to the new user
sudo su - displayads
```

### 4. Setup SSH Key Authentication (Recommended)

```bash
# On your local machine, generate SSH key if you haven't
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"

# Copy public key to server
ssh-copy-id displayads@YOUR_SERVER_IP

# Or manually add to authorized_keys
mkdir -p ~/.ssh
echo "your_public_key_here" >> ~/.ssh/authorized_keys
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

## Docker & Portainer Installation

### 1. Install Docker

```bash
# Remove old Docker versions
sudo apt remove docker docker-engine docker.io containerd runc

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Test Docker installation
docker --version
docker run hello-world
```

### 2. Install Docker Compose

```bash
# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker-compose --version
```

### 3. Install Portainer

```bash
# Create Portainer volume
docker volume create portainer_data

# Deploy Portainer
docker run -d \
  -p 8000:8000 \
  -p 9443:9443 \
  --name portainer \
  --restart=always \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v portainer_data:/data \
  portainer/portainer-ce:latest

# Check Portainer status
docker ps | grep portainer
```

### 4. Access Portainer

1. Open browser: `https://YOUR_SERVER_IP:9443`
2. Create admin account
3. Select "Docker" environment
4. Connect to local Docker environment

## Application Deployment

### 1. Clone Repository

```bash
# Navigate to home directory
cd ~

# Clone the repository
git clone https://github.com/Japsterr/Complete_Display_AdsWebMobileTVAPI.git
cd Complete_Display_AdsWebMobileTVAPI

# Switch to latest branch
git checkout latest-code
```

### 2. Create Production Environment Files

```bash
# Create production environment file
cp .env.example .env.production

# Edit production environment
nano .env.production
```

**Production .env.production content:**

```bash
# Django Settings
DEBUG=False
SECRET_KEY=your_super_secret_key_here_minimum_50_characters_long
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,YOUR_SERVER_IP

# Database Configuration
DB_ENGINE=django.db.backends.postgresql
DB_NAME=displayads_prod
DB_USER=displayads_user
DB_PASSWORD=your_secure_database_password
DB_HOST=postgres
DB_PORT=5432

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_email_password

# Stripe Configuration (if using payments)
STRIPE_PUBLISHABLE_KEY=pk_live_your_stripe_key
STRIPE_SECRET_KEY=sk_live_your_stripe_secret

# Media Storage
MEDIA_ROOT=/app/media
STATIC_ROOT=/app/static

# Security
SECURE_SSL_REDIRECT=True
SECURE_PROXY_SSL_HEADER=('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Logging
LOG_LEVEL=INFO
```

### 3. Create Production Docker Compose

```bash
# Create production docker-compose file
nano docker-compose.prod.yml
```

**docker-compose.prod.yml content:**

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    container_name: displayads_postgres_prod
    environment:
      POSTGRES_DB: displayads_prod
      POSTGRES_USER: displayads_user
      POSTGRES_PASSWORD: your_secure_database_password
    volumes:
      - postgres_prod_data:/var/lib/postgresql/data
      - ./backups:/backups
    restart: unless-stopped
    networks:
      - displayads_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U displayads_user -d displayads_prod"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    container_name: displayads_redis_prod
    restart: unless-stopped
    volumes:
      - redis_prod_data:/data
    networks:
      - displayads_network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  api:
    build: .
    container_name: displayads_api_prod
    env_file: .env.production
    volumes:
      - ./media:/app/media
      - ./static:/app/static
      - ./logs:/app/logs
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    networks:
      - displayads_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    container_name: displayads_nginx_prod
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/conf.d:/etc/nginx/conf.d
      - ./static:/var/www/static
      - ./media:/var/www/media
      - ./certbot/conf:/etc/letsencrypt
      - ./certbot/www:/var/www/certbot
    depends_on:
      - api
    restart: unless-stopped
    networks:
      - displayads_network

  certbot:
    image: certbot/certbot
    container_name: displayads_certbot
    volumes:
      - ./certbot/conf:/etc/letsencrypt
      - ./certbot/www:/var/www/certbot
    command: certonly --webroot -w /var/www/certbot --force-renewal --email your_email@example.com -d yourdomain.com -d www.yourdomain.com --agree-tos

volumes:
  postgres_prod_data:
  redis_prod_data:

networks:
  displayads_network:
    driver: bridge
```

### 4. Create Nginx Configuration

```bash
# Create nginx directory
mkdir -p nginx/conf.d

# Create main nginx config
nano nginx/nginx.conf
```

**nginx/nginx.conf:**

```nginx
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    access_log /var/log/nginx/access.log main;

    # Basic settings
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 100M;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/xml+rss
        application/json;

    # Include conf.d files
    include /etc/nginx/conf.d/*.conf;
}
```

**nginx/conf.d/default.conf:**

```nginx
# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS Server
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_session_tickets off;

    # SSL Security
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # HSTS
    add_header Strict-Transport-Security "max-age=63072000" always;

    # API Backend
    location /api/ {
        proxy_pass http://api:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # Admin Panel
    location /admin/ {
        proxy_pass http://api:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static Files
    location /static/ {
        alias /var/www/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Media Files
    location /media/ {
        alias /var/www/media/;
        expires 1y;
        add_header Cache-Control "public";
    }

    # Health Check
    location /health/ {
        proxy_pass http://api:8000;
        access_log off;
    }

    # Frontend (if serving from same domain)
    location / {
        root /var/www/frontend;
        try_files $uri $uri/ /index.html;
        expires 1h;
    }
}
```

## Production Configuration

### 1. Security Setup

```bash
# Create logs directory
mkdir -p logs

# Set proper permissions
sudo chown -R displayads:displayads ~/Complete_Display_AdsWebMobileTVAPI
chmod -R 755 ~/Complete_Display_AdsWebMobileTVAPI

# Create secure directories
mkdir -p backups
mkdir -p certbot/{conf,www}
chmod 700 backups
```

### 2. Firewall Configuration

```bash
# Install and configure UFW
sudo ufw --force reset
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 9443/tcp  # Portainer HTTPS
sudo ufw --force enable
sudo ufw status
```

### 3. Deploy with Portainer

#### Option A: Using Portainer Web UI

1. Access Portainer: `https://YOUR_SERVER_IP:9443`
2. Go to **Stacks** → **Add Stack**
3. Name: `displayads-production`
4. Upload `docker-compose.prod.yml`
5. Set environment variables
6. Deploy stack

#### Option B: Using Command Line

```bash
# Navigate to project directory
cd ~/Complete_Display_AdsWebMobileTVAPI

# Deploy production stack
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps
```

### 4. Initial Database Setup

```bash
# Run database migrations
docker-compose -f docker-compose.prod.yml exec api python manage.py migrate

# Create superuser
docker-compose -f docker-compose.prod.yml exec api python manage.py createsuperuser

# Collect static files
docker-compose -f docker-compose.prod.yml exec api python manage.py collectstatic --noinput

# Create initial data (optional)
docker-compose -f docker-compose.prod.yml exec api python manage.py shell -c "
from api.models import User, Plan
# Create default plans
plans_data = [
    {'plan_name': 'Free', 'price': 0, 'max_campaigns': 3, 'max_displays': 5},
    {'plan_name': 'Pro', 'price': 29.99, 'max_campaigns': 50, 'max_displays': 25},
    {'plan_name': 'Enterprise', 'price': 99.99, 'max_campaigns': -1, 'max_displays': -1}
]
for plan_data in plans_data:
    Plan.objects.get_or_create(plan_name=plan_data['plan_name'], defaults=plan_data)
print('Default plans created!')
"
```

## SSL Setup with Let's Encrypt

### 1. Initial Certificate Generation

```bash
# First, run without SSL to get initial certificates
# Edit nginx config to remove SSL sections temporarily
nano nginx/conf.d/default.conf

# Start nginx without SSL
docker-compose -f docker-compose.prod.yml up -d nginx

# Generate certificates
docker-compose -f docker-compose.prod.yml run --rm certbot certonly --webroot -w /var/www/certbot --force-renewal --email your_email@example.com -d yourdomain.com -d www.yourdomain.com --agree-tos

# Restore full nginx config with SSL
# Restart nginx
docker-compose -f docker-compose.prod.yml restart nginx
```

### 2. Auto-renewal Setup

```bash
# Create renewal script
cat > ~/ssl-renewal.sh << 'EOF'
#!/bin/bash
cd ~/Complete_Display_AdsWebMobileTVAPI
docker-compose -f docker-compose.prod.yml run --rm certbot renew
docker-compose -f docker-compose.prod.yml restart nginx
EOF

chmod +x ~/ssl-renewal.sh

# Add to crontab for auto-renewal
(crontab -l 2>/dev/null; echo "0 12 * * * ~/ssl-renewal.sh") | crontab -
```

## Monitoring & Maintenance

### 1. System Monitoring Scripts

```bash
# Create monitoring script
cat > ~/monitor.sh << 'EOF'
#!/bin/bash

echo "=== Display Ads API System Status ==="
echo "Date: $(date)"
echo

echo "=== Docker Containers ==="
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo

echo "=== System Resources ==="
echo "CPU Usage:"
top -bn1 | grep "Cpu(s)" | awk '{print $2}' | awk -F'%' '{print $1"%"}'
echo

echo "Memory Usage:"
free -h | grep -E "^Mem|^Swap"
echo

echo "Disk Usage:"
df -h | grep -vE '^Filesystem|tmpfs|cdrom'
echo

echo "=== API Health Check ==="
curl -s -o /dev/null -w "API Status: %{http_code}\n" http://localhost/health/
echo

echo "=== Database Status ==="
docker-compose -f docker-compose.prod.yml exec -T postgres pg_isready -U displayads_user -d displayads_prod
echo

echo "=== Recent Logs (Last 20 lines) ==="
docker-compose -f docker-compose.prod.yml logs --tail=20 api
EOF

chmod +x ~/monitor.sh
```

### 2. Backup Scripts

```bash
# Create backup script
cat > ~/backup.sh << 'EOF'
#!/bin/bash

BACKUP_DIR=~/backups
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Database backup
echo "Backing up database..."
docker-compose -f docker-compose.prod.yml exec -T postgres pg_dump -U displayads_user displayads_prod > $BACKUP_DIR/db_backup_$DATE.sql

# Media files backup
echo "Backing up media files..."
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz media/

# Configuration backup
echo "Backing up configuration..."
tar -czf $BACKUP_DIR/config_backup_$DATE.tar.gz .env.production nginx/ docker-compose.prod.yml

# Remove old backups (keep last 7 days)
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
ls -la $BACKUP_DIR/
EOF

chmod +x ~/backup.sh

# Schedule daily backups
(crontab -l 2>/dev/null; echo "0 2 * * * ~/backup.sh") | crontab -
```

### 3. Log Rotation

```bash
# Create logrotate configuration
sudo tee /etc/logrotate.d/displayads << 'EOF'
/home/displayads/Complete_Display_AdsWebMobileTVAPI/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    notifempty
    create 644 displayads displayads
    postrotate
        docker-compose -f /home/displayads/Complete_Display_AdsWebMobileTVAPI/docker-compose.prod.yml restart api
    endscript
}
EOF
```

## Backup Strategy

### 1. Automated Daily Backups

The backup script above will run daily at 2 AM and includes:
- Database dump
- Media files
- Configuration files
- Automatic cleanup of old backups

### 2. Manual Backup

```bash
# Manual backup when needed
~/backup.sh

# Restore from backup
# Database restore
docker-compose -f docker-compose.prod.yml exec -T postgres psql -U displayads_user displayads_prod < backups/db_backup_YYYYMMDD_HHMMSS.sql

# Media restore
tar -xzf backups/media_backup_YYYYMMDD_HHMMSS.tar.gz
```

### 3. Remote Backup (Recommended)

```bash
# Install rclone for cloud backups
curl https://rclone.org/install.sh | sudo bash

# Configure cloud storage (follow prompts)
rclone config

# Add to backup script for cloud sync
echo "rclone sync ~/backups remote:displayads-backups" >> ~/backup.sh
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Container Won't Start

```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs service_name

# Check system resources
free -h
df -h

# Restart specific service
docker-compose -f docker-compose.prod.yml restart service_name
```

#### 2. Database Connection Issues

```bash
# Check database container
docker-compose -f docker-compose.prod.yml exec postgres pg_isready

# Check database logs
docker-compose -f docker-compose.prod.yml logs postgres

# Reset database (CAUTION: Data loss!)
docker-compose -f docker-compose.prod.yml down
docker volume rm complete_display_adswebmobiletvapi_postgres_prod_data
docker-compose -f docker-compose.prod.yml up -d
```

#### 3. SSL Certificate Issues

```bash
# Check certificate status
docker-compose -f docker-compose.prod.yml run --rm certbot certificates

# Force renewal
docker-compose -f docker-compose.prod.yml run --rm certbot renew --force-renewal

# Check nginx configuration
docker-compose -f docker-compose.prod.yml exec nginx nginx -t
```

#### 4. Performance Issues

```bash
# Monitor system resources
htop
iotop
docker stats

# Check application logs
docker-compose -f docker-compose.prod.yml logs api | tail -100

# Optimize database
docker-compose -f docker-compose.prod.yml exec postgres psql -U displayads_user displayads_prod -c "VACUUM ANALYZE;"
```

### Emergency Procedures

#### 1. Complete System Recovery

```bash
# Stop all services
docker-compose -f docker-compose.prod.yml down

# Clean up containers and volumes
docker system prune -af
docker volume prune -f

# Restore from backup
# ... restore steps ...

# Redeploy
docker-compose -f docker-compose.prod.yml up -d
```

#### 2. Quick Health Check

```bash
# Run comprehensive health check
~/monitor.sh

# Test API endpoints
curl -I https://yourdomain.com/health/
curl -I https://yourdomain.com/api/v1/health/
```

## Security Best Practices

1. **Regular Updates**: Keep system and Docker images updated
2. **Strong Passwords**: Use complex passwords for all accounts
3. **SSH Keys**: Disable password authentication, use SSH keys only
4. **Firewall**: Keep UFW enabled with minimal open ports
5. **SSL**: Always use HTTPS in production
6. **Backups**: Maintain regular, tested backups
7. **Monitoring**: Set up alerts for system issues
8. **Access Control**: Limit server access to necessary personnel only

## Performance Optimization

1. **Database Tuning**: Optimize PostgreSQL settings for your server size
2. **Caching**: Ensure Redis is properly configured
3. **Static Files**: Use CDN for static file delivery
4. **Resource Limits**: Set appropriate Docker resource limits
5. **Monitoring**: Use tools like Prometheus/Grafana for detailed monitoring

---

## Quick Reference Commands

```bash
# Check system status
~/monitor.sh

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Restart services
docker-compose -f docker-compose.prod.yml restart

# Update application
git pull origin latest-code
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

# Backup now
~/backup.sh

# SSL renewal
~/ssl-renewal.sh
```

This guide provides a comprehensive production deployment setup for Ubuntu with Portainer management. Adjust domain names, passwords, and configurations according to your specific requirements.