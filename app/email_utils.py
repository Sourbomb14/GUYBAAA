import smtplib
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
import logging
import streamlit as st

class EmailManager:
    """Handles email campaign management and validation"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.smtp_config = self.load_smtp_config()
        
        # Initialize session state for email history
        if 'email_history' not in st.session_state:
            st.session_state.email_history = []
    
    def load_smtp_config(self) -> Dict[str, Any]:
        """Load SMTP configuration from environment or defaults"""
        return {
            'server': 'smtp.gmail.com',
            'port': 587,
            'username': '',
            'password': '',
            'use_tls': True
        }
    
    def validate_email(self, email: str) -> bool:
        """Validate email address format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email.strip()) is not None
    
    def validate_email_list(self, email_list: List[str]) -> Tuple[List[str], List[str]]:
        """Validate a list of email addresses"""
        valid_emails = []
        invalid_emails = []
        
        for email in email_list:
            email = email.strip()
            if email and self.validate_email(email):
                valid_emails.append(email)
            elif email:  # Not empty but invalid
                invalid_emails.append(email)
        
        return valid_emails, invalid_emails
    
    def create_email_template(self, template_type: str = 'newsletter') -> Dict[str, str]:
        """Create email templates for different campaign types"""
        templates = {
            'newsletter': {
                'subject': '📧 Your Weekly Marketing Update',
                'body': """
                <html>
                <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px;">
                    <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 10px;">
                        <h2 style="color: #333; text-align: center;">Weekly Marketing Newsletter</h2>
                        <p>Dear Subscriber,</p>
                        <p>Here are your latest marketing insights and campaign updates...</p>
                        
                        <div style="background-color: #f8f9fa; padding: 15px; margin: 20px 0; border-radius: 5px;">
                            <h3 style="color: #667eea;">📊 This Week's Highlights</h3>
                            <ul>
                                <li>Campaign performance increased by 15%</li>
                                <li>New audience segment identified</li>
                                <li>ROI improvements across all channels</li>
                            </ul>
                        </div>
                        
                        <p>Best regards,<br>Your Marketing Team</p>
                        
                        <hr style="margin-top: 30px; border: none; border-top: 1px solid #eee;">
                        <p style="font-size: 12px; color: #666; text-align: center;">
                            You received this email because you're subscribed to our marketing updates.
                        </p>
                    </div>
                </body>
                </html>
                """
            },
            'promotional': {
                'subject': '🎯 Special Offer Just For You!',
                'body': """
                <html>
                <body style="font-family: Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); margin: 0; padding: 20px;">
                    <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 15px;">
                        <h1 style="color: #667eea; text-align: center;">🎉 Exclusive Offer!</h1>
                        <p style="font-size: 18px;">Hi there!</p>
                        <p>We have an amazing offer just for you...</p>
                        
                        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                   color: white; padding: 20px; margin: 20px 0; border-radius: 10px; text-align: center;">
                            <h2>50% OFF</h2>
                            <p>on all premium features</p>
                            <a href="#" style="background-color: white; color: #667eea; padding: 10px 20px; 
                                             text-decoration: none; border-radius: 5px; font-weight: bold;">
                                Claim Now
                            </a>
                        </div>
                        
                        <p>Don't miss out on this limited-time offer!</p>
                        <p>Cheers,<br>Marketing Team</p>
                    </div>
                </body>
                </html>
                """
            },
            'transactional': {
                'subject': '✅ Campaign Update - Action Required',
                'body': """
                <html>
                <body style="font-family: Arial, sans-serif; background-color: #f8f9fa; margin: 0; padding: 20px;">
                    <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 25px; border-radius: 8px; border: 1px solid #dee2e6;">
                        <h2 style="color: #333;">Campaign Status Update</h2>
                        <p>Hello,</p>
                        <p>This is an automated update regarding your marketing campaign:</p>
                        
                        <div style="background-color: #e7f3ff; padding: 15px; margin: 15px 0; border-left: 4px solid #667eea;">
                            <h4 style="margin: 0; color: #0c4a6e;">Campaign Details</h4>
                            <p style="margin: 5px 0;"><strong>Campaign:</strong> Summer Promotion 2024</p>
                            <p style="margin: 5px 0;"><strong>Status:</strong> Active</p>
                            <p style="margin: 5px 0;"><strong>Performance:</strong> Above target</p>
                        </div>
                        
                        <p>Please review and take any necessary actions.</p>
                        
                        <p>Best regards,<br>GAIBA Analytics System</p>
                    </div>
                </body>
                </html>
                """
            }
        }
        
        return templates.get(template_type, templates['newsletter'])
    
    def send_campaign(self, campaign_name: str, subject: str, content: str, recipients: List[str]) -> bool:
        """Send email campaign (stubbed for demo - replace with actual SMTP)"""
        try:
            # Validate recipients
            valid_emails, invalid_emails = self.validate_email_list(recipients)
            
            if not valid_emails:
                st.error("❌ No valid email addresses found")
                return False
            
            if invalid_emails:
                st.warning(f"⚠️ Invalid emails skipped: {', '.join(invalid_emails)}")
            
            # For demo purposes, we'll simulate sending
            # In production, replace this with actual SMTP sending
            success = self.simulate_email_send(campaign_name, subject, content, valid_emails)
            
            if success:
                # Save to campaign history
                self.save_campaign_history(campaign_name, subject, content, valid_emails)
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error sending campaign: {str(e)}")
            return False
    
    def simulate_email_send(self, campaign_name: str, subject: str, content: str, recipients: List[str]) -> bool:
        """Simulate email sending for demo purposes"""
        try:
            # Simulate API call delay
            import time
            time.sleep(1)
            
            # In a real implementation, this would be:
            # return self.send_via_smtp(campaign_name, subject, content, recipients)
            
            # For now, always return success
            return True
            
        except Exception as e:
            self.logger.error(f"Error in simulated send: {str(e)}")
            return False
    
    def send_via_smtp(self, campaign_name: str, subject: str, content: str, recipients: List[str]) -> bool:
        """Send emails via SMTP (production implementation)"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.smtp_config['username']
            msg['To'] = ', '.join(recipients)
            
            # Add HTML content
            html_part = MIMEText(content, 'html')
            msg.attach(html_part)
            
            # Connect to server and send
            server = smtplib.SMTP(self.smtp_config['server'], self.smtp_config['port'])
            
            if self.smtp_config['use_tls']:
                server.starttls()
            
            server.login(self.smtp_config['username'], self.smtp_config['password'])
            server.send_message(msg)
            server.quit()
            
            return True
            
        except Exception as e:
            self.logger.error(f"SMTP error: {str(e)}")
            return False
    
    def save_campaign_history(self, campaign_name: str, subject: str, content: str, recipients: List[str]):
        """Save campaign to history"""
        campaign_record = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'campaign_name': campaign_name,
            'subject': subject,
            'recipients_count': len(recipients),
            'status': 'Sent',
            'open_rate': f"{np.random.uniform(15, 35):.1f}%",  # Simulated
            'click_rate': f"{np.random.uniform(2, 8):.1f}%",   # Simulated
        }
        
        st.session_state.email_history.append(campaign_record)
    
    def get_campaign_history(self) -> pd.DataFrame:
        """Retrieve campaign history"""
        if not st.session_state.email_history:
            return pd.DataFrame()
        
        return pd.DataFrame(st.session_state.email_history)
    
    def create_campaign_report(self, campaign_data: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """Create campaign performance report"""
        report = {
            'total_campaigns': 0,
            'total_recipients': 0,
            'avg_open_rate': 0,
            'avg_click_rate': 0,
            'recent_campaigns': []
        }
        
        if st.session_state.email_history:
            history_df = pd.DataFrame(st.session_state.email_history)
            
            report['total_campaigns'] = len(history_df)
            report['total_recipients'] = history_df['recipients_count'].sum()
            
            # Extract numeric values from percentage strings for averages
            open_rates = [float(x.replace('%', '')) for x in history_df['open_rate']]
            click_rates = [float(x.replace('%', '')) for x in history_df['click_rate']]
            
            report['avg_open_rate'] = np.mean(open_rates)
            report['avg_click_rate'] = np.mean(click_rates)
            report['recent_campaigns'] = history_df.tail(5).to_dict('records')
        
        return report
    
    def generate_email_analytics(self) -> Dict[str, Any]:
        """Generate email campaign analytics"""
        analytics = {
            'performance_summary': {},
            'trends': {},
            'recommendations': []
        }
        
        if not st.session_state.email_history:
            return analytics
        
        history_df = pd.DataFrame(st.session_state.email_history)
        
        # Performance summary
        total_sent = history_df['recipients_count'].sum()
        avg_open_rate = np.mean([float(x.replace('%', '')) for x in history_df['open_rate']])
        avg_click_rate = np.mean([float(x.replace('%', '')) for x in history_df['click_rate']])
        
        analytics['performance_summary'] = {
            'total_emails_sent': total_sent,
            'average_open_rate': f"{avg_open_rate:.2f}%",
            'average_click_rate': f"{avg_click_rate:.2f}%",
            'campaign_count': len(history_df)
        }
        
        # Recommendations
        recommendations = []
        
        if avg_open_rate < 20:
            recommendations.append("📈 Consider improving subject lines to increase open rates")
        
        if avg_click_rate < 3:
            recommendations.append("🎯 Optimize email content and CTAs to improve click rates")
        
        if len(history_df) > 5:
            recommendations.append("📊 Consider A/B testing different email templates")
        
        analytics['recommendations'] = recommendations
        
        return analytics
    
    def export_email_report(self, format: str = 'csv') -> bytes:
        """Export email campaign report"""
        if not st.session_state.email_history:
            return b""
        
        history_df = pd.DataFrame(st.session_state.email_history)
        
        if format.lower() == 'csv':
            return history_df.to_csv(index=False).encode('utf-8')
        elif format.lower() == 'excel':
            import io
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                history_df.to_excel(writer, sheet_name='Email Campaigns', index=False)
            return output.getvalue()
        else:
            raise ValueError(f"Unsupported export format: {format}")
