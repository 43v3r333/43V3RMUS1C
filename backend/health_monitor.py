#!/usr/bin/env python3
"""
43V3R CORE Automated Health Monitor
Monitors PostgreSQL, Redis, Web Frontend, and API Backend health.
Outputs status to console and can send alerts via email/Slack/webhook.

Usage:
  ./health_monitor.py --interval 60 --webhook https://hooks.slack.com/...
  ./health_monitor.py --no-alerts  # Just print status
"""

import argparse
import json
import logging
import os
import socket
import subprocess
import sys
import time
import urllib.request
from datetime import datetime
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Service definitions
SERVICES = {
    "postgres": {
        "name": "PostgreSQL",
        "type": "docker_health",
        "container": "verse-postgres",
        "health_endpoint": "tcp:5432",
        "critical_on_down": True
    },
    "redis": {
        "name": "Redis",
        "type": "docker_health",
        "container": "verse-redis",
        "health_endpoint": "tcp:6379",
        "critical_on_down": True
    },
    "web": {
        "name": "Web Frontend",
        "type": "http_status",
        "url": "http://localhost:3000",
        "critical_on_down": False,
        "expected_status": 200
    },
    "api": {
        "name": "API Backend",
        "type": "http_status",
        "url": "http://localhost:8000/api/v1/health",
        "critical_on_down": False,
        "expected_status": 200
    }
}

class HealthMonitor:
    def __init__(self, interval: int = 60, webhook_url: Optional[str] = None, 
                 alert_email: Optional[str] = None, no_alerts: bool = False):
        self.interval = interval
        self.webhook_url = webhook_url
        self.alert_email = alert_email
        self.no_alerts = no_alerts
        self.last_state = {}
        self.alert_cooldown = {}  # To prevent alert spam
        self.cooldown_period = 300  # 5 minutes between same alerts
        
    def check_docker_health(self, container: str) -> tuple[bool, str]:
        """Check Docker container health status"""
        try:
            result = subprocess.run(
                ["docker", "inspect", "--format", "{{.State.Health.Status}}", container],
                capture_output=True, text=True, timeout=10
            )
            status = result.stdout.strip()
            
            if status == "healthy":
                return True, "healthy"
            elif status == "unhealthy":
                return False, "unhealthy"
            else:
                # Check if container is running
                result = subprocess.run(
                    ["docker", "ps", "--filter", f"name={container}", "--format", "{{.Status}}"],
                    capture_output=True, text=True, timeout=10
                )
                status_text = result.stdout.strip()
                if status_text:
                    return True, f"running ({status_text})"
                return False, "not found"
                
        except subprocess.TimeoutExpired:
            return False, "timeout"
        except Exception as e:
            return False, f"error: {str(e)}"
            
    def check_http_status(self, url: str, expected_status: int = 200) -> tuple[bool, str]:
        """Check HTTP endpoint status"""
        try:
            req = urllib.request.Request(url, method='GET')
            req.add_header('User-Agent', '43V3R-HealthMonitor/1.0')
            
            with urllib.request.urlopen(req, timeout=10) as response:
                status_code = response.getcode()
                if status_code == expected_status:
                    return True, f"OK ({status_code})"
                return False, f"unexpected status: {status_code}"
                
        except urllib.error.HTTPError as e:
            return False, f"HTTP {e.code}"
        except urllib.error.URLError as e:
            return False, f"connection failed: {str(e.reason)}"
        except subprocess.TimeoutExpired:
            return False, "timeout"
        except Exception as e:
            return False, f"error: {str(e)}"
            
    def check_all_services(self) -> Dict[str, Dict]:
        """Check health of all services"""
        results = {}
        
        for service_id, config in SERVICES.items():
            if config["type"] == "docker_health":
                healthy, message = self.check_docker_health(config["container"])
            elif config["type"] == "http_status":
                healthy, message = self.check_http_status(
                    config["url"], 
                    config.get("expected_status", 200)
                )
            else:
                healthy, message = False, f"unknown type: {config['type']}"
            
            results[service_id] = {
                "name": config["name"],
                "healthy": healthy,
                "message": message,
                "critical": config.get("critical_on_down", False),
                "timestamp": datetime.now().isoformat()
            }
            
        return results
        
    def send_alert(self, subject: str, message: str) -> bool:
        """Send alert via configured channels"""
        if self.no_alerts:
            return False
            
        success = True
        
        # Slack Webhook
        if self.webhook_url:
            try:
                payload = {
                    "text": f"⚠️ 43V3R CORE Alert\n\n{subject}\n{message}",
                    "username": "43V3R Monitor",
                    "icon_emoji": ":rotating_light:"
                }
                
                data = json.dumps(payload).encode('utf-8')
                req = urllib.request.Request(
                    self.webhook_url, 
                    data=data, 
                    headers={'Content-Type': 'application/json'}
                )
                
                with urllib.request.urlopen(req, timeout=10) as response:
                    if response.status != 200:
                        logger.warning(f"Slack webhook failed: {response.status}")
                        success = False
                        
            except Exception as e:
                logger.error(f"Failed to send Slack alert: {e}")
                success = False
                
        # Email (basic implementation)
        if self.alert_email:
            try:
                # This would require SMTP setup
                logger.info(f"Email alert would be sent to: {self.alert_email}")
                logger.info(f"Subject: {subject}")
                # Actual email sending would go here
            except Exception as e:
                logger.error(f"Failed to send email alert: {e}")
                success = False
                
        return success
        
    def should_alert(self, service_id: str, current_state: str) -> bool:
        """Check if we should alert (respecting cooldown)"""
        last_state_key = f"{service_id}:{current_state}"
        now = time.time()
        
        if last_state_key in self.alert_cooldown:
            if now - self.alert_cooldown[last_state_key] < self.cooldown_period:
                return False
                
        self.alert_cooldown[last_state_key] = now
        return True
        
    def print_status(self, results: Dict[str, Dict]):
        """Print formatted status table"""
        print("\n" + "="*70)
        print(f"43V3R CORE Health Status - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        print(f"{'Service':<20} {'Status':<15} {'Message':<35}")
        print("-"*70)
        
        for service_id, data in results.items():
            status_icon = "✅" if data["healthy"] else "❌"
            status_text = f"{status_icon} {data['name']:<15}"
            message = data["message"][:34] + "..." if len(data["message"]) > 35 else data["message"]
            
            # Highlight critical failures
            if not data["healthy"] and data["critical"]:
                status_text = f"! {status_icon} {data['name']:<14}"
                message = f"[CRITICAL] {message}"
                
            print(f"{status_text:<20} {message:<35}")
            
        # Summary
        total = len(results)
        healthy = sum(1 for r in results.values() if r["healthy"])
        critical_failures = sum(1 for r in results.values() if not r["healthy"] and r["critical"])
        
        print("-"*70)
        print(f"Summary: {healthy}/{total} services healthy")
        if critical_failures > 0:
            print(f"⚠️  CRITICAL: {critical_failures} critical service(s) down!")
        elif healthy == total:
            print("🟢 All systems operational")
        print("="*70 + "\n")
        
    def detect_state_changes(self, new_results: Dict[str, Dict]) -> List[Dict]:
        """Detect which services changed state since last check"""
        changes = []
        
        for service_id, new_data in new_results.items():
            if service_id not in self.last_state:
                # First check - no previous state
                if not new_data["healthy"]:
                    changes.append({
                        "service_id": service_id,
                        "old_state": "unknown",
                        "new_state": "down" if not new_data["healthy"] else "up"
                    })
            else:
                old_data = self.last_state[service_id]
                if old_data["healthy"] != new_data["healthy"]:
                    changes.append({
                        "service_id": service_id,
                        "old_state": "up" if old_data["healthy"] else "down",
                        "new_state": "up" if new_data["healthy"] else "down"
                    })
                    
        self.last_state = new_results
        return changes
        
    def process_changes(self, changes: List[Dict]):
        """Process state changes and send alerts if needed"""
        for change in changes:
            service_id = change["service_id"]
            config = SERVICES[service_id]
            
            if change["new_state"] == "down" and change["old_state"] != "down":
                # Service just went down
                if self.should_alert(service_id, "down"):
                    subject = f"🔴 {config['name']} is DOWN"
                    message = (
                        f"Service: {config['name']}\n"
                        f"Status: {SERVICES[service_id]['type']}\n"
                        f"Critical: {'Yes' if config['critical_on_down'] else 'No'}\n"
                        f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    )
                    
                    if self.send_alert(subject, message):
                        logger.info(f"Alert sent for {config['name']} down")
                        
            elif change["new_state"] == "up" and change["old_state"] != "up":
                # Service just came back up
                if self.should_alert(service_id, "up"):
                    subject = f"🟢 {config['name']} is BACK UP"
                    message = (
                        f"Service: {config['name']}\n"
                        f"Recovery time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"Status returned to healthy"
                    )
                    
                    if self.send_alert(subject, message):
                        logger.info(f"Alert sent for {config['name']} recovery")

    def run(self):
        """Main monitoring loop"""
        logger.info("Starting 43V3R CORE Health Monitor")
        logger.info(f"Check interval: {self.interval} seconds")
        if self.no_alerts:
            logger.info("Alerts disabled")
        elif self.webhook_url or self.alert_email:
            logger.info("Alerts enabled")
        else:
            logger.warning("No alert channels configured - only logging")
            
        logger.info(f"Monitoring: {', '.join([s['name'] for s in SERVICES.values()])}")
        
        try:
            while True:
                # Check all services
                results = self.check_all_services()
                
                # Print status
                self.print_status(results)
                
                # Detect and handle changes
                changes = self.detect_state_changes(results)
                if changes:
                    logger.info(f"Detected {len(changes)} state change(s)")
                    self.process_changes(changes)
                else:
                    logger.debug("No state changes detected")
                    
                # Wait for next interval
                time.sleep(self.interval)
                
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Monitor error: {e}")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description='43V3R CORE Health Monitor',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ./health_monitor.py --interval 60
  ./health_monitor.py --interval 120 --webhook https://hooks.slack.com/...
  ./health_monitor.py --no-alerts           # Just print status, no alerts
        """
    )
    
    parser.add_argument(
        '--interval', '-i',
        type=int,
        default=60,
        help='Check interval in seconds (default: 60)'
    )
    
    parser.add_argument(
        '--webhook', '-w',
        type=str,
        help='Slack webhook URL for alerts'
    )
    
    parser.add_argument(
        '--email', '-e',
        type=str,
        help='Email address for alerts (basic implementation)'
    )
    
    parser.add_argument(
        '--no-alerts', '-n',
        action='store_true',
        help='Disable all alerts (print status only)'
    )
    
    args = parser.parse_args()
    
    monitor = HealthMonitor(
        interval=args.interval,
        webhook_url=args.webhook,
        alert_email=args.email,
        no_alerts=args.no_alerts
    )
    
    monitor.run()

if __name__ == '__main__':
    main()