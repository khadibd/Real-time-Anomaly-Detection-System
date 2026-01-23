import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import json

class AlertSystem:
    def __init__(self, config):
        self.config = config
        
    def send_email_alert(self, anomaly_data):
        msg = MIMEMultipart()
        msg['From'] = self.config['email']['sender']
        msg['To'] = self.config['email']['recipient']
        msg['Subject'] = f"🚨 Anomaly Alert: {anomaly_data['sensor_id']}"
        
        body = f"""
        Anomaly Detected!
        
        Sensor: {anomaly_data['sensor_id']}
        Time: {anomaly_data['timestamp']}
        Type: {anomaly_data.get('anomaly_type', 'Unknown')}
        Values: {anomaly_data}
        
        Please investigate immediately.
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP(self.config['email']['smtp_server'], 
                         self.config['email']['smtp_port']) as server:
            server.starttls()
            server.login(self.config['email']['username'], 
                        self.config['email']['password'])
            server.send_message(msg)
    
    def send_slack_alert(self, anomaly_data):
        webhook_url = self.config['slack']['webhook_url']
        
        message = {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🚨 Anomaly Detected!"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Sensor:*\n{anomaly_data['sensor_id']}"},
                        {"type": "mrkdwn", "text": f"*Time:*\n{anomaly_data['timestamp']}"}
                    ]
                }
            ]
        }
        
        requests.post(webhook_url, json=message)