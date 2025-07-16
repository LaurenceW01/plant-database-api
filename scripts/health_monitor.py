#!/usr/bin/env python3
"""
Health Monitor for Plant Database API
Provides basic health checking and alerting for production deployment.
"""

import requests
import time
import logging
import os
from datetime import datetime
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('health_monitor.log'),
        logging.StreamHandler()
    ]
)

class APIHealthMonitor:
    """Simple health monitor for the Plant Database API"""
    
    def __init__(self, api_url, api_key=None, check_interval=300):
        """
        Initialize health monitor.
        
        Args:
            api_url (str): Base URL of the API
            api_key (str): API key for authenticated endpoints
            check_interval (int): Seconds between health checks (default: 5 minutes)
        """
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.check_interval = check_interval
        self.last_success = datetime.now()
        self.consecutive_failures = 0
        
    def check_health_endpoint(self):
        """Check the basic health endpoint"""
        try:
            response = requests.get(f"{self.api_url}/", timeout=10)
            return response.status_code == 200, response.status_code, response.text
        except requests.exceptions.RequestException as e:
            return False, 0, str(e)
    
    def check_plants_endpoint(self):
        """Check the plants listing endpoint"""
        try:
            response = requests.get(f"{self.api_url}/api/plants", timeout=15)
            if response.status_code == 200:
                data = response.json()
                return True, response.status_code, f"Returned {len(data.get('plants', []))} plants"
            else:
                return False, response.status_code, response.text
        except requests.exceptions.RequestException as e:
            return False, 0, str(e)
        except json.JSONDecodeError as e:
            return False, response.status_code, f"JSON decode error: {e}"
    
    def check_authenticated_endpoint(self):
        """Check an authenticated endpoint if API key is available"""
        if not self.api_key:
            return None, None, "No API key provided"
        
        try:
            headers = {"x-api-key": self.api_key, "Content-Type": "application/json"}
            test_data = {"Plant Name": f"HealthCheck-{int(time.time())}"}
            
            # Try to add a test plant
            response = requests.post(
                f"{self.api_url}/api/plants",
                headers=headers,
                json=test_data,
                timeout=15
            )
            
            return response.status_code == 201, response.status_code, response.text
        except requests.exceptions.RequestException as e:
            return False, 0, str(e)
    
    def run_health_check(self):
        """Run complete health check suite"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'checks': {}
        }
        
        # Check health endpoint
        success, status, message = self.check_health_endpoint()
        results['checks']['health_endpoint'] = {
            'status': 'pass' if success else 'fail',
            'response_code': status,
            'message': message
        }
        
        # Check plants endpoint
        success, status, message = self.check_plants_endpoint()
        results['checks']['plants_endpoint'] = {
            'status': 'pass' if success else 'fail',
            'response_code': status,
            'message': message
        }
        
        # Check authenticated endpoint if API key available
        if self.api_key:
            success, status, message = self.check_authenticated_endpoint()
            results['checks']['authenticated_endpoint'] = {
                'status': 'pass' if success else 'fail',
                'response_code': status,
                'message': message
            }
        
        # Determine overall status
        failed_checks = [check for check in results['checks'].values() if check['status'] == 'fail']
        if failed_checks:
            results['overall_status'] = 'unhealthy'
            self.consecutive_failures += 1
        else:
            results['overall_status'] = 'healthy'
            self.consecutive_failures = 0
            self.last_success = datetime.now()
        
        return results
    
    def log_results(self, results):
        """Log health check results"""
        status = results['overall_status']
        if status == 'healthy':
            logging.info(f"[PASS] Health check passed - All endpoints responding")
        else:
            failed_checks = [name for name, check in results['checks'].items() if check['status'] == 'fail']
            logging.error(f"[FAIL] Health check failed - Failed checks: {', '.join(failed_checks)}")
            logging.error(f"   Consecutive failures: {self.consecutive_failures}")
    
    def should_alert(self):
        """Determine if an alert should be sent"""
        # Alert after 3 consecutive failures (15 minutes of downtime at 5-minute intervals)
        return self.consecutive_failures >= 3
    
    def send_alert(self, results):
        """Send alert for health check failures"""
        # This is a basic implementation - replace with your preferred alerting method
        alert_message = f"""
[ALERT] Plant Database API Health Alert

Status: {results['overall_status'].upper()}
Time: {results['timestamp']}
Consecutive Failures: {self.consecutive_failures}
Last Success: {self.last_success}

Failed Checks:
"""
        
        for name, check in results['checks'].items():
            if check['status'] == 'fail':
                alert_message += f"- {name}: HTTP {check['response_code']} - {check['message']}\n"
        
        # Log the alert (replace with email, Slack, SMS, etc.)
        logging.critical(alert_message)
        
        # Example: Send to webhook (uncomment and configure as needed)
        # webhook_url = os.environ.get('ALERT_WEBHOOK_URL')
        # if webhook_url:
        #     try:
        #         requests.post(webhook_url, json={'text': alert_message})
        #     except Exception as e:
        #         logging.error(f"Failed to send webhook alert: {e}")
    
    def run_monitoring_loop(self):
        """Run continuous monitoring loop"""
        logging.info(f"[MONITOR] Starting health monitoring for {self.api_url}")
        logging.info(f"   Check interval: {self.check_interval} seconds")
        
        while True:
            try:
                results = self.run_health_check()
                self.log_results(results)
                
                # Send alert if needed
                if results['overall_status'] == 'unhealthy' and self.should_alert():
                    self.send_alert(results)
                
                # Save results to file for external monitoring
                with open('last_health_check.json', 'w') as f:
                    json.dump(results, f, indent=2)
                
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                logging.info("[STOP] Health monitoring stopped by user")
                break
            except Exception as e:
                logging.error(f"Error in monitoring loop: {e}")
                time.sleep(60)  # Wait 1 minute before retrying

def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Plant Database API Health Monitor')
    parser.add_argument('--url', required=True, help='API base URL (e.g., https://your-app.onrender.com)')
    parser.add_argument('--api-key', help='API key for authenticated endpoint tests')
    parser.add_argument('--interval', type=int, default=300, help='Check interval in seconds (default: 300)')
    parser.add_argument('--once', action='store_true', help='Run once instead of continuous monitoring')
    
    args = parser.parse_args()
    
    monitor = APIHealthMonitor(args.url, args.api_key, args.interval)
    
    if args.once:
        # Run single health check
        results = monitor.run_health_check()
        monitor.log_results(results)
        print(json.dumps(results, indent=2))
        exit(0 if results['overall_status'] == 'healthy' else 1)
    else:
        # Run continuous monitoring
        monitor.run_monitoring_loop()

if __name__ == "__main__":
    main() 