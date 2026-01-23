import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import json
import logging
from datetime import datetime
from typing import Dict, List

class AlertManager:
    def __init__(self, config_path="config/alerts_config.json"):
        self.config = self.load_config(config_path)
        self.logger = self.setup_logger()
        self.alert_history = []
        
    def load_config(self, config_path):
        """Load alert configuration"""
        config = {
            "email": {
                "enabled": True,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "sender": "alerts@anomalens.com",
                "recipients": ["admin@example.com"],
                "username": None,
                "password": None
            },
            "slack": {
                "enabled": False,
                "webhook_url": None
            },
            "teams": {
                "enabled": False,
                "webhook_url": None
            },
            "thresholds": {
                "critical": 0.9,
                "warning": 0.7,
                "info": 0.5
            }
        }
        return config
    
    def send_alert(self, anomaly_data: Dict, severity: str = "warning"):
        """Send alert through all configured channels"""
        alert_id = f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        alert_message = {
            "alert_id": alert_id,
            "timestamp": datetime.now().isoformat(),
            "severity": severity,
            "data": anomaly_data,
            "status": "triggered"
        }
        
        # Store in history
        self.alert_history.append(alert_message)
        
        # Send via email
        if self.config["email"]["enabled"]:
            self.send_email_alert(alert_message)
        
        # Send via Slack
        if self.config["slack"]["enabled"]:
            self.send_slack_alert(alert_message)
        
        # Send via Teams
        if self.config["teams"]["enabled"]:
            self.send_teams_alert(alert_message)
        
        self.logger.info(f"Alert sent: {alert_id} - {severity}")
        return alert_id
    
    def send_email_alert(self, alert_message: Dict):
        """Send email alert"""
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"[{alert_message['severity'].upper()}] Anomaly Alert"
        msg['From'] = self.config['email']['sender']
        msg['To'] = ', '.join(self.config['email']['recipients'])
        
        # HTML email content
        html = f"""
        <html>
          <body>
            <h2>🚨 Anomaly Alert</h2>
            <p><strong>Alert ID:</strong> {alert_message['alert_id']}</p>
            <p><strong>Severity:</strong> <span style="color: red">{alert_message['severity'].upper()}</span></p>
            <p><strong>Time:</strong> {alert_message['timestamp']}</p>
            <hr>
            <h3>Sensor Data:</h3>
            <table border="1" cellpadding="5">
              <tr><th>Sensor ID</th><td>{alert_message['data'].get('sensor_id', 'N/A')}</td></tr>
              <tr><th>Temperature</th><td>{alert_message['data'].get('temperature', 'N/A')}°C</td></tr>
              <tr><th>Pressure</th><td>{alert_message['data'].get('pressure', 'N/A')} hPa</td></tr>
              <tr><th>Anomaly Score</th><td>{alert_message['data'].get('anomaly_score', 'N/A')}</td></tr>
            </table>
            <hr>
            <p><em>This is an automated alert from AnomaLens</em></p>
          </body>
        </html>
        """
        
        msg.attach(MIMEText(html, 'html'))
        
        try:
            server = smtplib.SMTP(self.config['email']['smtp_server'], 
                                 self.config['email']['smtp_port'])
            server.starttls()
            server.login(self.config['email']['username'], 
                        self.config['email']['password'])
            server.send_message(msg)
            server.quit()
        except Exception as e:
            self.logger.error(f"Failed to send email alert: {e}")