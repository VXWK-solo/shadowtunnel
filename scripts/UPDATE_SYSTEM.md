# Advanced VPN Server - Update System

## Overview
Professional update system with zero-downtime deployments, rollback capabilities, and automated testing.

## Update Types

### 1. Security Updates
- **Critical**: Applied within 24 hours
- **High**: Applied within 7 days
- **Medium**: Applied within 30 days
- **Low**: Applied within 90 days

### 2. Feature Updates
- **Major**: New features, breaking changes
- **Minor**: New features, backward compatible
- **Patch**: Bug fixes, performance improvements

### 3. Infrastructure Updates
- **System**: OS updates, kernel updates
- **Dependencies**: Python packages, Node.js modules
- **Services**: Database updates, monitoring updates

## Update Process

### 1. Pre-Update Checks
```bash
#!/bin/bash
# scripts/pre-update-check.sh

set -e

echo "🔍 Running pre-update checks..."

# Check system requirements
check_system_requirements() {
    echo "Checking system requirements..."
    
    # Check disk space
    DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ $DISK_USAGE -gt 80 ]; then
        echo "SUCCESS Insufficient disk space: ${DISK_USAGE}% used"
        exit 1
    fi
    
    # Check memory
    MEMORY_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
    if [ $MEMORY_USAGE -gt 90 ]; then
        echo "SUCCESS High memory usage: ${MEMORY_USAGE}% used"
        exit 1
    fi
    
    # Check running services
    if ! systemctl is-active --quiet vpn-server; then
        echo "SUCCESS VPN server is not running"
        exit 1
    fi
    
    echo "SUCCESS System requirements check passed"
}

# Check backup status
check_backup_status() {
    echo "Checking backup status..."
    
    LAST_BACKUP=$(find /opt/backups -name "*.tar.gz" -mtime -1 | wc -l)
    if [ $LAST_BACKUP -eq 0 ]; then
        echo "⚠️  No recent backup found, creating one..."
        ./scripts/backup.sh
    fi
    
    echo "SUCCESS Backup status check passed"
}

# Check update compatibility
check_update_compatibility() {
    echo "Checking update compatibility..."
    
    CURRENT_VERSION=$(cat /opt/vpn/version)
    TARGET_VERSION=$1
    
    # Check version compatibility matrix
    if ! python3 scripts/check-compatibility.py $CURRENT_VERSION $TARGET_VERSION; then
        echo "SUCCESS Update not compatible with current version"
        exit 1
    fi
    
    echo "SUCCESS Update compatibility check passed"
}

# Run all checks
check_system_requirements
check_backup_status
check_update_compatibility $1

echo "SUCCESS All pre-update checks passed"
```

### 2. Blue-Green Deployment
```bash
#!/bin/bash
# scripts/blue-green-deploy.sh

set -e

CURRENT_ENV="blue"
NEW_ENV="green"

if [ "$(docker ps -q -f name=advanced-vpn-blue)" ]; then
    CURRENT_ENV="blue"
    NEW_ENV="green"
else
    CURRENT_ENV="green"
    NEW_ENV="blue"
fi

echo "🔄 Starting blue-green deployment..."
echo "Current environment: $CURRENT_ENV"
echo "New environment: $NEW_ENV"

# Build new image
echo "Building new image..."
docker build -t advanced-vpn:latest .

# Start new environment
echo "Starting new environment ($NEW_ENV)..."
docker-compose -f docker-compose.$NEW_ENV.yml up -d

# Wait for new environment to be ready
echo "Waiting for new environment to be ready..."
for i in {1..30}; do
    if curl -f http://localhost:2053/health > /dev/null 2>&1; then
        echo "SUCCESS New environment is ready"
        break
    fi
    echo "Waiting... ($i/30)"
    sleep 10
done

# Run health checks
echo "Running health checks..."
python3 scripts/health-check.py --environment $NEW_ENV

if [ $? -ne 0 ]; then
    echo "SUCCESS Health checks failed, rolling back..."
    docker-compose -f docker-compose.$NEW_ENV.yml down
    exit 1
fi

# Switch traffic to new environment
echo "Switching traffic to new environment..."
nginx -s reload

# Wait for traffic to stabilize
echo "Waiting for traffic to stabilize..."
sleep 30

# Stop old environment
echo "Stopping old environment ($CURRENT_ENV)..."
docker-compose -f docker-compose.$CURRENT_ENV.yml down

echo "SUCCESS Blue-green deployment completed successfully"
```

### 3. Rolling Updates
```bash
#!/bin/bash
# scripts/rolling-update.sh

set -e

echo "🔄 Starting rolling update..."

# Get current replicas
CURRENT_REPLICAS=$(kubectl get deployment advanced-vpn -o jsonpath='{.spec.replicas}')
echo "Current replicas: $CURRENT_REPLICAS"

# Update image
echo "Updating image..."
kubectl set image deployment/advanced-vpn vpn-server=advanced-vpn:latest

# Wait for rollout to complete
echo "Waiting for rollout to complete..."
kubectl rollout status deployment/advanced-vpn --timeout=600s

# Verify deployment
echo "Verifying deployment..."
kubectl get pods -l app=advanced-vpn

# Run health checks
echo "Running health checks..."
python3 scripts/health-check.py --environment kubernetes

if [ $? -ne 0 ]; then
    echo "SUCCESS Health checks failed, rolling back..."
    kubectl rollout undo deployment/advanced-vpn
    exit 1
fi

echo "SUCCESS Rolling update completed successfully"
```

## Update Automation

### 1. Automated Security Updates
```yaml
# .github/workflows/security-updates.yml
name: Security Updates

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  workflow_dispatch:

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Run security scan
        run: |
          pip install safety
          safety check --json --output safety-report.json
      
      - name: Check for vulnerabilities
        run: |
          python3 scripts/check-vulnerabilities.py safety-report.json
      
      - name: Create security update PR
        if: github.event_name == 'schedule'
        run: |
          python3 scripts/create-security-update-pr.py

  auto-update:
    runs-on: ubuntu-latest
    needs: security-scan
    if: github.event_name == 'schedule'
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Update dependencies
        run: |
          pip install pip-tools
          pip-compile requirements.in
          pip-compile requirements-dev.in
      
      - name: Run tests
        run: |
          pytest tests/unit/ tests/integration/
      
      - name: Deploy to staging
        run: |
          ./scripts/deploy.sh --environment staging
      
      - name: Run E2E tests
        run: |
          pytest tests/e2e/
      
      - name: Deploy to production
        run: |
          ./scripts/deploy.sh --environment production
```

### 2. Dependency Updates
```python
# scripts/update-dependencies.py
#!/usr/bin/env python3

import subprocess
import json
import sys
from pathlib import Path

def check_dependencies():
    """Check for outdated dependencies"""
    print("🔍 Checking for outdated dependencies...")
    
    # Check Python dependencies
    result = subprocess.run(['pip', 'list', '--outdated', '--format=json'], 
                          capture_output=True, text=True)
    
    if result.returncode != 0:
        print("SUCCESS Failed to check Python dependencies")
        return False
    
    outdated_packages = json.loads(result.stdout)
    
    if not outdated_packages:
        print("SUCCESS All Python dependencies are up to date")
        return True
    
    print(f"📦 Found {len(outdated_packages)} outdated packages:")
    for package in outdated_packages:
        print(f"  - {package['name']}: {package['version']} -> {package['latest_version']}")
    
    return True

def update_dependencies():
    """Update dependencies"""
    print("🔄 Updating dependencies...")
    
    # Update requirements files
    subprocess.run(['pip-compile', 'requirements.in'], check=True)
    subprocess.run(['pip-compile', 'requirements-dev.in'], check=True)
    
    # Update package.json
    subprocess.run(['npm', 'update'], check=True)
    
    print("SUCCESS Dependencies updated successfully")
    return True

def run_tests():
    """Run tests after dependency update"""
    print("🧪 Running tests...")
    
    result = subprocess.run(['pytest', 'tests/unit/', 'tests/integration/'], 
                          capture_output=True, text=True)
    
    if result.returncode != 0:
        print("SUCCESS Tests failed after dependency update")
        print(result.stdout)
        print(result.stderr)
        return False
    
    print("SUCCESS All tests passed")
    return True

def main():
    """Main update process"""
    if not check_dependencies():
        sys.exit(1)
    
    if not update_dependencies():
        sys.exit(1)
    
    if not run_tests():
        sys.exit(1)
    
    print("SUCCESS: Dependency update completed successfully")

if __name__ == "__main__":
    main()
```

## Rollback System

### 1. Automatic Rollback
```bash
#!/bin/bash
# scripts/auto-rollback.sh

set -e

echo "🔄 Starting automatic rollback..."

# Check if rollback is needed
if ! python3 scripts/health-check.py --environment production; then
    echo "SUCCESS Health checks failed, initiating rollback..."
    
    # Rollback to previous version
    PREVIOUS_VERSION=$(cat /opt/vpn/previous_version)
    echo "Rolling back to version: $PREVIOUS_VERSION"
    
    # Stop current services
    docker-compose down
    
    # Start previous version
    docker-compose -f docker-compose.previous.yml up -d
    
    # Wait for services to be ready
    sleep 30
    
    # Verify rollback
    if python3 scripts/health-check.py --environment production; then
        echo "SUCCESS Rollback completed successfully"
    else
        echo "SUCCESS Rollback failed, manual intervention required"
        exit 1
    fi
else
    echo "SUCCESS System is healthy, no rollback needed"
fi
```

### 2. Manual Rollback
```bash
#!/bin/bash
# scripts/manual-rollback.sh

set -e

VERSION=$1

if [ -z "$VERSION" ]; then
    echo "Usage: $0 <version>"
    echo "Available versions:"
    ls /opt/backups/versions/
    exit 1
fi

echo "🔄 Rolling back to version: $VERSION"

# Stop current services
echo "Stopping current services..."
docker-compose down

# Restore from backup
echo "Restoring from backup..."
tar -xzf /opt/backups/versions/$VERSION/configs.tar.gz -C /opt/vpn/
tar -xzf /opt/backups/versions/$VERSION/database.tar.gz -C /opt/vpn/

# Start services with previous version
echo "Starting services with previous version..."
docker-compose -f docker-compose.$VERSION.yml up -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 30

# Verify rollback
echo "Verifying rollback..."
if python3 scripts/health-check.py --environment production; then
    echo "SUCCESS Rollback completed successfully"
else
    echo "SUCCESS Rollback verification failed"
    exit 1
fi
```

## Update Monitoring

### 1. Update Status Dashboard
```python
# scripts/update-monitor.py
#!/usr/bin/env python3

import requests
import json
import time
from datetime import datetime

class UpdateMonitor:
    def __init__(self):
        self.base_url = "http://localhost:2053/api"
        self.metrics = []
    
    def check_system_health(self):
        """Check system health metrics"""
        try:
            response = requests.get(f"{self.base_url}/health")
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception as e:
            print(f"Error checking system health: {e}")
            return None
    
    def check_service_status(self):
        """Check service status"""
        services = ['vpn-server', 'webpanel', 'prometheus', 'grafana']
        status = {}
        
        for service in services:
            try:
                response = requests.get(f"http://localhost:2053/api/services/{service}/status")
                status[service] = response.status_code == 200
            except:
                status[service] = False
        
        return status
    
    def check_performance_metrics(self):
        """Check performance metrics"""
        try:
            response = requests.get(f"{self.base_url}/metrics")
            if response.status_code == 200:
                metrics = response.json()
                return {
                    'cpu_usage': metrics.get('cpu_usage', 0),
                    'memory_usage': metrics.get('memory_usage', 0),
                    'disk_usage': metrics.get('disk_usage', 0),
                    'active_connections': metrics.get('active_connections', 0)
                }
            else:
                return None
        except Exception as e:
            print(f"Error checking performance metrics: {e}")
            return None
    
    def monitor_update(self, duration_minutes=60):
        """Monitor system during update"""
        print(f"🔍 Monitoring system for {duration_minutes} minutes...")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        while time.time() < end_time:
            timestamp = datetime.now().isoformat()
            
            # Check system health
            health = self.check_system_health()
            if health:
                print(f"SUCCESS System health: {health['status']}")
            else:
                print("SUCCESS System health check failed")
            
            # Check service status
            services = self.check_service_status()
            for service, status in services.items():
                if status:
                    print(f"SUCCESS {service}: Running")
                else:
                    print(f"SUCCESS {service}: Down")
            
            # Check performance metrics
            metrics = self.check_performance_metrics()
            if metrics:
                print(f"CPU: {metrics['cpu_usage']}%, Memory: {metrics['memory_usage']}%, "
                      f"Disk: {metrics['disk_usage']}%, Connections: {metrics['active_connections']}")
            
            # Store metrics
            self.metrics.append({
                'timestamp': timestamp,
                'health': health,
                'services': services,
                'metrics': metrics
            })
            
            time.sleep(30)  # Check every 30 seconds
        
        print("SUCCESS Monitoring completed")
        return self.metrics
    
    def generate_report(self):
        """Generate monitoring report"""
        if not self.metrics:
            print("No metrics to report")
            return
        
        print("\nUpdate Monitoring Report")
        print("=" * 50)
        
        # Calculate uptime
        total_checks = len(self.metrics)
        successful_checks = sum(1 for m in self.metrics if m['health'] and m['health']['status'] == 'healthy')
        uptime_percentage = (successful_checks / total_checks) * 100
        
        print(f"Total checks: {total_checks}")
        print(f"Successful checks: {successful_checks}")
        print(f"Uptime: {uptime_percentage:.2f}%")
        
        # Service availability
        print("\nService Availability:")
        services = ['vpn-server', 'webpanel', 'prometheus', 'grafana']
        for service in services:
            available = sum(1 for m in self.metrics if m['services'].get(service, False))
            availability = (available / total_checks) * 100
            print(f"  {service}: {availability:.2f}%")
        
        # Performance summary
        if self.metrics:
            avg_cpu = sum(m['metrics']['cpu_usage'] for m in self.metrics if m['metrics']) / total_checks
            avg_memory = sum(m['metrics']['memory_usage'] for m in self.metrics if m['metrics']) / total_checks
            avg_connections = sum(m['metrics']['active_connections'] for m in self.metrics if m['metrics']) / total_checks
            
            print(f"\nAverage Performance:")
            print(f"  CPU Usage: {avg_cpu:.2f}%")
            print(f"  Memory Usage: {avg_memory:.2f}%")
            print(f"  Active Connections: {avg_connections:.0f}")

def main():
    monitor = UpdateMonitor()
    metrics = monitor.monitor_update(60)  # Monitor for 60 minutes
    monitor.generate_report()

if __name__ == "__main__":
    main()
```

## Update Configuration

### 1. Update Policy
```yaml
# config/update-policy.yml
update_policy:
  # Security updates
  security:
    critical:
      auto_update: true
      max_delay_hours: 24
      require_approval: false
    high:
      auto_update: true
      max_delay_hours: 168  # 7 days
      require_approval: false
    medium:
      auto_update: false
      max_delay_hours: 720  # 30 days
      require_approval: true
    low:
      auto_update: false
      max_delay_hours: 2160  # 90 days
      require_approval: true
  
  # Feature updates
  features:
    major:
      auto_update: false
      require_approval: true
      testing_required: true
    minor:
      auto_update: false
      require_approval: true
      testing_required: true
    patch:
      auto_update: true
      require_approval: false
      testing_required: false
  
  # Infrastructure updates
  infrastructure:
    system:
      auto_update: false
      require_approval: true
      maintenance_window: "02:00-06:00"
    dependencies:
      auto_update: true
      require_approval: false
      testing_required: true
    services:
      auto_update: false
      require_approval: true
      testing_required: true
  
  # Update windows
  maintenance_windows:
    - day: "sunday"
      start: "02:00"
      end: "06:00"
    - day: "wednesday"
      start: "02:00"
      end: "04:00"
  
  # Rollback settings
  rollback:
    auto_rollback: true
    health_check_timeout: 300  # 5 minutes
    rollback_threshold: 0.95  # 95% success rate
    max_rollback_attempts: 3
```

### 2. Update Schedule
```yaml
# config/update-schedule.yml
update_schedule:
  # Daily security scans
  security_scans:
    time: "02:00"
    timezone: "UTC"
    enabled: true
  
  # Weekly dependency updates
  dependency_updates:
    day: "sunday"
    time: "03:00"
    timezone: "UTC"
    enabled: true
  
  # Monthly system updates
  system_updates:
    day: "first_sunday"
    time: "02:00"
    timezone: "UTC"
    enabled: true
  
  # Quarterly major updates
  major_updates:
    day: "first_sunday"
    months: ["january", "april", "july", "october"]
    time: "02:00"
    timezone: "UTC"
    enabled: true
```

---

**Update System Version**: 1.0  
**Last Updated**: 2024-01-01  
**Supported Methods**: Blue-Green, Rolling, Canary  
**Rollback Capability**: Automatic and Manual
