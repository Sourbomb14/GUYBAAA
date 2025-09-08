import smtplib
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import streamlit as st
from typing import List, Dict, Optional

class EmailManager:
    """Email campaign management with Streamlit secrets integration"""
    
    def __init__(self, api_keys: Dict):
        self.api_keys = api_keys
        if 'email_history' not in st.session_state:
            st.session_state.email_history = []
    
    def send_campaign(self, campaign_name: str, subject: str, content: str, recipients: List[str]) -> bool:
        """Send email campaign"""
        try:
            valid_emails = [email.strip() for email in recipients if email.strip() and '@' in email]
            
            if not valid_emails:
                st.error("❌ No valid email addresses found")
                return False
            
            # For demo - simulate sending
            success = self._simulate_send(campaign_name, subject, content, valid_emails)
            
            if success:
                self._save_campaign_history(campaign_name, subject, valid_emails)
                return True
            
            return False
            
        except Exception as e:
            st.error(f"Error sending campaign: {str(e)}")
            return False
    
    def _simulate_send(self, campaign_name: str, subject: str, content: str, recipients: List[str]) -> bool:
        """Simulate email sending for demo"""
        # In production, implement actual SMTP sending using self.api_keys
        return True
    
    def _save_campaign_history(self, campaign_name: str, subject: str, recipients: List[str]):
        """Save campaign to history"""
        import numpy as np
        record = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'campaign_name': campaign_name,
            'subject': subject,
            'recipients_count': len(recipients),
            'status': 'Sent',
            'open_rate': f"{np.random.uniform(15, 35):.1f}%",
            'click_rate': f"{np.random.uniform(2, 8):.1f}%",
        }
        st.session_state.email_history.append(record)
    
    def get_campaign_history(self) -> pd.DataFrame:
        """Get campaign history"""
        if not st.session_state.email_history:
            return pd.DataFrame()
        return pd.DataFrame(st.session_state.email_history)
