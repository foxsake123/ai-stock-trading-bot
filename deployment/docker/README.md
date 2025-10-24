# Docker Deployment Guide

Complete guide for deploying AI Trading Bot using Docker and Docker Compose.

## Quick Start

```bash
# 1. Navigate to project root
cd /path/to/ai-stock-trading-bot

# 2. Create .env file
cp .env.example configs/.env
nano configs/.env  # Add your API keys

# 3. Build and start all services
docker-compose -f deployment/docker/docker-compose.yml up -d

# 4. Check status
docker-compose -f deployment/docker/docker-compose.yml ps

# 5. View logs
docker-compose -f deployment/docker/docker-compose.yml logs -f trading-bot
```

## Files

### Dockerfile (219 lines)

**Multi-stage build for optimized image:**

**Builder Stage:**
- Installs build dependencies (gcc, make, etc.)
- Creates virtual environment
- Installs Python packages
- Size: ~300MB (discarded in final image)

**Runtime Stage:**
- Based on python:3.11-slim
- Copies only venv from builder
- Minimal runtime dependencies
- Final size: ~500MB

**Key Features:**
- Non-root user (trader:1000)
- America/New_York timezone
- Proper permissions on directories
- Health check included
- Security hardening

### docker-compose.yml (476 lines)

**Services:**

1. **trading-bot** (Main service)
   - Runs daily pipeline
   - 2GB memory limit
   - 1 CPU core limit
   - Mounts: data, logs, reports, configs

2. **redis** (Caching)
   - Redis 7 Alpine
   - 512MB memory limit
   - Persistent storage
   - Internal network only

3. **postgres** (Database)
   - PostgreSQL 15 Alpine
   - 1GB memory limit
   - Persistent storage
   - Auto-creates schema

4. **monitor** (Health checks)
   - Runs monitoring scripts
   - 256MB memory limit
   - Read-only data mount

5. **dashboard** (Optional)
   - Web interface
   - Port 5000 exposed
   - Read-only mounts

### .dockerignore (294 lines)

**Excludes from build context:**
- venv/, __pycache__/
- logs/, data/cache/
- .git/, .github/
- IDE files (.vscode/, .idea/)
- Test files, coverage reports
- Secrets (.env, *.key)

### Supporting Files

- **redis.conf** - Redis configuration
- **init-db.sql** - PostgreSQL schema
- **README.md** - This file

## Installation

### Prerequisites

```bash
# Check Docker version (requires >= 20.10)
docker --version

# Check Docker Compose version (requires >= 1.29)
docker-compose --version

# Verify Docker daemon is running
docker ps
```

### Build Images

```bash
# Build trading bot image
docker build -t ai-trading-bot:latest -f deployment/docker/Dockerfile .

# Or use docker-compose to build all
docker-compose -f deployment/docker/docker-compose.yml build

# Build without cache (fresh build)
docker-compose -f deployment/docker/docker-compose.yml build --no-cache
```

### Configure Environment

```bash
# 1. Copy environment template
cp .env.example configs/.env

# 2. Edit with your API keys
nano configs/.env

# Required variables:
# - ALPACA_API_KEY
# - ALPACA_SECRET_KEY
# - ANTHROPIC_API_KEY
# - TELEGRAM_BOT_TOKEN
# - TELEGRAM_CHAT_ID
```

### Start Services

```bash
# Start all services in detached mode
docker-compose -f deployment/docker/docker-compose.yml up -d

# Start specific service
docker-compose -f deployment/docker/docker-compose.yml up -d trading-bot

# Start with rebuild
docker-compose -f deployment/docker/docker-compose.yml up -d --build
```

## Usage

### Service Management

```bash
# View running services
docker-compose -f deployment/docker/docker-compose.yml ps

# View logs
docker-compose -f deployment/docker/docker-compose.yml logs -f

# View logs for specific service
docker-compose -f deployment/docker/docker-compose.yml logs -f trading-bot

# Restart service
docker-compose -f deployment/docker/docker-compose.yml restart trading-bot

# Stop all services
docker-compose -f deployment/docker/docker-compose.yml stop

# Stop and remove containers
docker-compose -f deployment/docker/docker-compose.yml down

# Stop and remove volumes (WARNING: deletes data!)
docker-compose -f deployment/docker/docker-compose.yml down -v
```

### Execute Commands

```bash
# Run health check
docker-compose -f deployment/docker/docker-compose.yml exec trading-bot \
  python scripts/monitoring/health_check.py

# Interactive shell
docker-compose -f deployment/docker/docker-compose.yml exec trading-bot bash

# Run pipeline manually
docker-compose -f deployment/docker/docker-compose.yml exec trading-bot \
  python scripts/daily_pipeline.py

# View portfolio status
docker-compose -f deployment/docker/docker-compose.yml exec trading-bot \
  python scripts/portfolio/get_portfolio_status.py
```

### Database Operations

```bash
# Connect to PostgreSQL
docker-compose -f deployment/docker/docker-compose.yml exec postgres \
  psql -U trader -d trading_bot

# Backup database
docker-compose -f deployment/docker/docker-compose.yml exec postgres \
  pg_dump -U trader trading_bot > backup_$(date +%Y%m%d).sql

# Restore database
cat backup_20251023.sql | \
  docker-compose -f deployment/docker/docker-compose.yml exec -T postgres \
  psql -U trader trading_bot

# View tables
docker-compose -f deployment/docker/docker-compose.yml exec postgres \
  psql -U trader -d trading_bot -c "\dt trading.*"
```

### Redis Operations

```bash
# Connect to Redis CLI
docker-compose -f deployment/docker/docker-compose.yml exec redis redis-cli

# Check Redis status
docker-compose -f deployment/docker/docker-compose.yml exec redis redis-cli ping

# View all keys
docker-compose -f deployment/docker/docker-compose.yml exec redis redis-cli KEYS '*'

# Save Redis snapshot
docker-compose -f deployment/docker/docker-compose.yml exec redis redis-cli SAVE

# Backup Redis
docker cp ai-trading-bot-redis:/data/dump.rdb ./redis-backup.rdb
```

## Monitoring

### Health Checks

```bash
# Check container health
docker-compose -f deployment/docker/docker-compose.yml ps

# View health check logs
docker inspect ai-trading-bot | grep -A 10 Health

# Manual health check
docker-compose -f deployment/docker/docker-compose.yml exec trading-bot \
  python scripts/monitoring/health_check.py --verbose
```

### Resource Usage

```bash
# Real-time stats for all containers
docker stats

# Stats for specific container
docker stats ai-trading-bot

# Container resource limits
docker inspect ai-trading-bot | grep -A 20 Resources
```

### Logs

```bash
# Application logs (from container)
docker-compose -f deployment/docker/docker-compose.yml logs -f trading-bot

# System logs (from host volume)
tail -f logs/app/daily_pipeline_*.log

# Error logs
tail -f logs/errors/*.log

# Trade logs
tail -f logs/trades/*.log

# All logs
docker-compose -f deployment/docker/docker-compose.yml logs -f
```

## Scheduled Execution

### Option 1: Cron on Host

```bash
# Edit crontab
crontab -e

# Add line (6 AM weekdays):
0 6 * * 1-5 cd /path/to/repo && docker-compose -f deployment/docker/docker-compose.yml up trading-bot >> /var/log/trading-bot-cron.log 2>&1
```

### Option 2: Docker Restart Policy

The `restart: unless-stopped` policy ensures services restart after failure or reboot.

### Option 3: Kubernetes CronJob

For production deployments, use Kubernetes CronJob (see deployment/kubernetes/).

## Networking

### Internal Communication

Services communicate via internal network (172.28.0.0/16):

```
trading-bot → redis:6379
trading-bot → postgres:5432
monitor → trading-bot (health checks)
```

### External Access

To expose services externally, uncomment ports in docker-compose.yml:

```yaml
ports:
  - "6379:6379"  # Redis
  - "5432:5432"  # PostgreSQL
  - "5000:5000"  # Dashboard
```

**Security Warning:** Only expose ports in development, not production.

## Volumes

### Persistent Data

```bash
# List volumes
docker volume ls | grep trading

# Inspect volume
docker volume inspect deployment_docker_postgres-data

# Backup volume
docker run --rm \
  -v deployment_docker_postgres-data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/postgres-data-backup.tar.gz /data

# Restore volume
docker run --rm \
  -v deployment_docker_postgres-data:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/postgres-data-backup.tar.gz -C /
```

### Host Mounts

These directories are mounted from host:

```
./data → /app/data
./logs → /app/logs
./reports → /app/reports
./configs → /app/configs (read-only)
```

## Troubleshooting

### Container Won't Start

```bash
# 1. Check logs
docker-compose -f deployment/docker/docker-compose.yml logs trading-bot

# 2. Inspect container
docker inspect ai-trading-bot

# 3. Try interactive mode
docker-compose -f deployment/docker/docker-compose.yml run --rm trading-bot bash

# 4. Check dependencies
docker-compose -f deployment/docker/docker-compose.yml ps
```

### Database Connection Errors

```bash
# 1. Verify postgres is running
docker-compose -f deployment/docker/docker-compose.yml ps postgres

# 2. Check postgres logs
docker-compose -f deployment/docker/docker-compose.yml logs postgres

# 3. Test connection
docker-compose -f deployment/docker/docker-compose.yml exec postgres \
  pg_isready -U trader

# 4. Verify DATABASE_URL
docker-compose -f deployment/docker/docker-compose.yml exec trading-bot \
  env | grep DATABASE_URL
```

### Redis Connection Errors

```bash
# 1. Check redis is running
docker-compose -f deployment/docker/docker-compose.yml ps redis

# 2. Test connection
docker-compose -f deployment/docker/docker-compose.yml exec redis \
  redis-cli ping

# 3. Check logs
docker-compose -f deployment/docker/docker-compose.yml logs redis
```

### Permission Errors

```bash
# 1. Check directory ownership on host
ls -la data/ logs/ reports/

# 2. Fix ownership (UID 1000 = trader user in container)
sudo chown -R 1000:1000 data/ logs/ reports/

# 3. Verify in container
docker-compose -f deployment/docker/docker-compose.yml exec trading-bot \
  ls -la /app/data
```

### Out of Memory

```bash
# 1. Check current usage
docker stats ai-trading-bot

# 2. Increase memory limit in docker-compose.yml
# Edit deploy.resources.limits.memory

# 3. Restart container
docker-compose -f deployment/docker/docker-compose.yml restart trading-bot
```

### Build Fails

```bash
# 1. Clear Docker cache
docker builder prune -a

# 2. Remove old images
docker image prune -a

# 3. Rebuild without cache
docker-compose -f deployment/docker/docker-compose.yml build --no-cache

# 4. Check disk space
df -h
```

## Maintenance

### Updates

```bash
# 1. Pull latest code
git pull

# 2. Rebuild images
docker-compose -f deployment/docker/docker-compose.yml build

# 3. Recreate containers
docker-compose -f deployment/docker/docker-compose.yml up -d --force-recreate
```

### Cleanup

```bash
# Remove stopped containers
docker container prune

# Remove unused images
docker image prune -a

# Remove unused volumes (WARNING: data loss!)
docker volume prune

# Remove all unused resources
docker system prune -a --volumes
```

### Backups

```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="backups/docker-$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

# Backup database
docker-compose -f deployment/docker/docker-compose.yml exec -T postgres \
  pg_dump -U trader trading_bot > $BACKUP_DIR/database.sql

# Backup Redis
docker-compose -f deployment/docker/docker-compose.yml exec redis redis-cli SAVE
docker cp ai-trading-bot-redis:/data/dump.rdb $BACKUP_DIR/redis.rdb

# Backup volumes
cp -r data/ $BACKUP_DIR/
cp -r logs/ $BACKUP_DIR/
cp -r reports/ $BACKUP_DIR/

# Create archive
tar czf $BACKUP_DIR.tar.gz $BACKUP_DIR
rm -rf $BACKUP_DIR

echo "Backup created: $BACKUP_DIR.tar.gz"
EOF

chmod +x backup.sh
./backup.sh
```

## Production Deployment

### Checklist

- [ ] Update PostgreSQL password in docker-compose.yml
- [ ] Set strong Redis password in redis.conf
- [ ] Configure .env with production API keys
- [ ] Remove or secure exposed ports
- [ ] Set up automated backups
- [ ] Configure monitoring/alerting
- [ ] Set up log rotation
- [ ] Use Docker secrets for sensitive data
- [ ] Enable Docker Content Trust
- [ ] Configure firewall rules
- [ ] Set up SSL/TLS for exposed services
- [ ] Document recovery procedures

### Security Hardening

```bash
# 1. Use Docker secrets instead of env vars
echo "my_secret_password" | docker secret create db_password -

# 2. Run containers with read-only filesystem
docker run --read-only --tmpfs /tmp ai-trading-bot:latest

# 3. Limit capabilities
docker run --cap-drop=ALL --cap-add=NET_BIND_SERVICE ai-trading-bot:latest

# 4. Use private registry
docker tag ai-trading-bot:latest registry.example.com/ai-trading-bot:latest
docker push registry.example.com/ai-trading-bot:latest
```

## Support

For issues:

1. Check logs: `docker-compose logs`
2. Verify health: `docker-compose ps`
3. Test manually: `docker-compose exec trading-bot python scripts/monitoring/health_check.py`
4. Check GitHub issues
5. Review Docker documentation

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [PostgreSQL Docker](https://hub.docker.com/_/postgres)
- [Redis Docker](https://hub.docker.com/_/redis)
