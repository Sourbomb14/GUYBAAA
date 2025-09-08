import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
import os
import sys
from datetime import datetime, timedelta
import numpy as np
import json

# Add the app directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import custom modules with proper error handling
try:
    from data_loading import DataLoader
    from marketing_analysis import MarketingAnalyzer
    from email_utils import EmailManager
    from utils import UIHelper, CampaignOptimizer
except ImportError as e:
    st.error(f"Import error: {e}")
    st.stop()

# Page config
st.set_page_config(
    page_title="GAIBA Marketing Analytics",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load API keys from Streamlit secrets
def load_api_keys():
    """Load API keys from Streamlit secrets"""
    try:
        return {
            'groq_api_key': st.secrets.get("GROQ_API_KEY", ""),
            'email': st.secrets.get("EMAIL", ""),
            'email_password': st.secrets.get("EMAIL_PASSWORD", ""),
            'smtp_server': st.secrets.get("SMTP_SERVER", "smtp.gmail.com"),
            'smtp_port': st.secrets.get("SMTP_PORT", 587)
        }
    except Exception as e:
        st.warning(f"Could not load secrets: {e}")
        return {}

# Custom CSS for dark theme
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .stApp { background: linear-gradient(135deg, #0e1117 0%, #1a1a2e 100%); }
    
    .metric-card {
        background: linear-gradient(135deg, #16213e 0%, #0f3460 100%);
        padding: 1.5rem; border-radius: 15px; border: 1px solid #2d3748;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3); margin: 1rem 0;
    }
    
    .chat-container {
        background: rgba(22, 33, 62, 0.8); border-radius: 15px;
        padding: 1.5rem; border: 1px solid #2d3748; backdrop-filter: blur(10px);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none; border-radius: 10px; color: white; font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    h1, h2, h3 { color: #e2e8f0; font-family: 'Arial', sans-serif; }
    
    .upload-area {
        background: rgba(22, 33, 62, 0.6); border: 2px dashed #667eea;
        border-radius: 15px; padding: 2rem; text-align: center; margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

class GAIBAApp:
    def __init__(self):
        self.api_keys = load_api_keys()
        self.data_loader = DataLoader()
        self.analyzer = MarketingAnalyzer()
        self.email_manager = EmailManager(self.api_keys)
        self.ui_helper = UIHelper()
        self.optimizer = CampaignOptimizer(self.api_keys.get('groq_api_key', ''))
        self.init_session_state()
    
    def init_session_state(self):
        """Initialize session state variables"""
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        if 'campaign_data' not in st.session_state:
            st.session_state.campaign_data = None
        if 'analysis_complete' not in st.session_state:
            st.session_state.analysis_complete = False
    
    def render_header(self):
        """Render the main header"""
        st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <h1 style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                       -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
                       font-size: 3rem; margin: 0;">🚀 GAIBA Analytics</h1>
            <p style="color: #a0aec0; font-size: 1.2rem; margin-top: 0.5rem;">
                AI-Powered Marketing Campaign Intelligence
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_sidebar(self):
        """Render the sidebar navigation"""
        with st.sidebar:
            st.markdown("""
            <div style="text-align: center; padding: 1rem 0;">
                <h2 style="color: #667eea;">🎯 Navigation</h2>
            </div>
            """, unsafe_allow_html=True)
            
            selected = option_menu(
                menu_title=None,
                options=["Dashboard", "Data Upload", "Analytics", "AI Chat", "Email Campaigns"],
                icons=["speedometer2", "cloud-upload", "graph-up", "robot", "envelope"],
                menu_icon="cast",
                default_index=0,
                styles={
                    "container": {"padding": "0!important", "background-color": "transparent"},
                    "icon": {"color": "#667eea", "font-size": "18px"}, 
                    "nav-link": {
                        "font-size": "16px", "text-align": "left", "margin": "0px",
                        "color": "#e2e8f0", "background-color": "transparent",
                        "--hover-color": "rgba(102, 126, 234, 0.2)"
                    },
                    "nav-link-selected": {
                        "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                        "color": "white"
                    },
                }
            )
            
            # Quick stats in sidebar
            if st.session_state.campaign_data is not None:
                st.markdown("---")
                st.markdown("### 📊 Quick Stats")
                data = st.session_state.campaign_data
                st.metric("Total Campaigns", len(data))
                if 'roi' in data.columns:
                    st.metric("Average ROI", f"{data['roi'].mean():.2f}%")
        
        return selected
    
    def render_dashboard(self):
        """Render the main dashboard"""
        self.ui_helper.render_metric_cards()
        
        if st.session_state.campaign_data is not None:
            st.markdown("## 📈 Campaign Performance Overview")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if 'roi' in st.session_state.campaign_data.columns:
                    fig = px.line(st.session_state.campaign_data, y='roi', 
                                title='ROI Trend', color_discrete_sequence=['#667eea'])
                    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', 
                                    paper_bgcolor='rgba(0,0,0,0)', font_color='white')
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                if 'engagement_rate' in st.session_state.campaign_data.columns:
                    fig = px.bar(st.session_state.campaign_data.head(10), 
                               y='engagement_rate', title='Top 10 Engagement Rates',
                               color_discrete_sequence=['#764ba2'])
                    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', 
                                    paper_bgcolor='rgba(0,0,0,0)', font_color='white')
                    st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("## 🗂️ Recent Campaigns")
            st.dataframe(st.session_state.campaign_data.head(10), use_container_width=True)
        else:
            self.render_welcome_message()
    
    def render_welcome_message(self):
        """Render welcome message"""
        st.markdown("""
        <div class="upload-area">
            <h2 style="color: #667eea;">Welcome to GAIBA Analytics!</h2>
            <p style="color: #a0aec0; font-size: 1.1rem;">
                Upload your marketing campaign data to unlock powerful analytics and AI insights.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_data_upload(self):
        """Render data upload interface"""
        st.markdown("## 📤 Upload Campaign Data")
        
        uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])
        
        if uploaded_file is not None:
            try:
                data = self.data_loader.load_csv(uploaded_file)
                st.session_state.campaign_data = data
                st.success(f"✅ Successfully uploaded {len(data)} campaign records!")
                st.dataframe(data.head(), use_container_width=True)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Rows", len(data))
                with col2:
                    st.metric("Total Columns", len(data.columns))
                with col3:
                    st.metric("Memory Usage", f"{data.memory_usage(deep=True).sum() / 1024:.1f} KB")
                    
            except Exception as e:
                st.error(f"❌ Error uploading file: {str(e)}")
        
        st.markdown("---")
        st.markdown("### 🎲 Or Try Sample Data")
        if st.button("Load Sample Dataset", type="primary"):
            sample_data = self.data_loader.generate_sample_data()
            st.session_state.campaign_data = sample_data
            st.success("✅ Sample dataset loaded successfully!")
            st.rerun()
    
    def render_analytics(self):
        """Render analytics dashboard"""
        if st.session_state.campaign_data is None:
            st.warning("⚠️ Please upload campaign data first.")
            return
        
        data = st.session_state.campaign_data
        st.markdown("## 📊 Advanced Analytics")
        
        tab1, tab2, tab3 = st.tabs(["📈 Performance", "🎯 Segmentation", "💰 ROI Analysis"])
        
        with tab1:
            metrics = self.analyzer.calculate_performance_metrics(data)
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Revenue", f"${metrics.get('total_revenue', 0):,.2f}")
            with col2:
                st.metric("Average ROI", f"{metrics.get('avg_roi', 0):.2f}%")
            with col3:
                st.metric("Total Impressions", f"{metrics.get('total_impressions', 0):,}")
            with col4:
                st.metric("Avg Engagement", f"{metrics.get('avg_engagement', 0):.2f}%")
        
        with tab2:
            if st.button("🔄 Run K-Means Clustering", type="primary"):
                with st.spinner("Running clustering analysis..."):
                    clusters = self.analyzer.perform_clustering(data)
                    if clusters is not None:
                        cluster_chart = self.analyzer.create_cluster_chart(data, clusters)
                        st.plotly_chart(cluster_chart, use_container_width=True)
        
        with tab3:
            if 'roi' in data.columns:
                col1, col2 = st.columns(2)
                with col1:
                    roi_chart = self.analyzer.create_roi_distribution_chart(data)
                    st.plotly_chart(roi_chart, use_container_width=True)
                with col2:
                    st.markdown("#### 🏆 Top Performing Campaigns")
                    top_campaigns = self.analyzer.get_top_campaigns(data, 'roi')
                    st.dataframe(top_campaigns, use_container_width=True)
    
    def render_ai_chat(self):
        """Render AI chat interface"""
        st.markdown("## 🤖 AI Campaign Assistant")
        
        if not self.api_keys.get('groq_api_key'):
            st.warning("⚠️ Groq API key not configured. Please add GROQ_API_KEY to Streamlit secrets.")
            return
        
        # Display chat history
        for i, (role, content) in enumerate(st.session_state.chat_history):
            if role == "user":
                st.chat_message("user").write(content)
            else:
                st.chat_message("assistant").write(content)
        
        # Chat input
        if prompt := st.chat_input("Ask me about your marketing campaigns..."):
            st.session_state.chat_history.append(("user", prompt))
            st.chat_message("user").write(prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("🤖 Thinking..."):
                    response = self.optimizer.get_ai_response(prompt, st.session_state.campaign_data)
                    st.write(response)
                    st.session_state.chat_history.append(("assistant", response))
        
        # Quick action buttons
        st.markdown("#### 🚀 Quick Actions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💡 Campaign Suggestions"):
                response = self.optimizer.generate_campaign_suggestions(st.session_state.campaign_data)
                st.session_state.chat_history.append(("assistant", response))
                st.rerun()
        
        with col2:
            if st.button("📊 Analyze Performance"):
                response = self.optimizer.analyze_campaign_performance(st.session_state.campaign_data)
                st.session_state.chat_history.append(("assistant", response))
                st.rerun()
        
        with col3:
            if st.button("🎯 Optimization Tips"):
                response = self.optimizer.get_optimization_tips(st.session_state.campaign_data)
                st.session_state.chat_history.append(("assistant", response))
                st.rerun()
    
    def render_email_campaigns(self):
        """Render email campaigns interface"""
        st.markdown("## 📧 Email Campaign Management")
        
        if not self.api_keys.get('email'):
            st.warning("⚠️ Email credentials not configured. Add EMAIL and EMAIL_PASSWORD to secrets.")
            return
        
        tab1, tab2 = st.tabs(["✉️ Send Campaign", "📋 Campaign History"])
        
        with tab1:
            with st.form("email_campaign_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    campaign_name = st.text_input("Campaign Name")
                    subject_line = st.text_input("Subject Line")
                
                with col2:
                    recipient_list = st.text_area("Recipients (one email per line)")
                    campaign_type = st.selectbox("Campaign Type", ["Newsletter", "Promotional", "Transactional"])
                
                email_content = st.text_area("Email Content", height=200)
                submitted = st.form_submit_button("📤 Send Campaign", type="primary")
                
                if submitted and campaign_name and subject_line and email_content:
                    success = self.email_manager.send_campaign(
                        campaign_name, subject_line, email_content, recipient_list.split('\n')
                    )
                    if success:
                        st.success("✅ Email campaign sent successfully!")
                        st.balloons()
        
        with tab2:
            history = self.email_manager.get_campaign_history()
            if not history.empty:
                st.dataframe(history, use_container_width=True)
            else:
                st.info("📭 No email campaigns sent yet.")
    
    def run(self):
        """Main application runner"""
        self.render_header()
        selected = self.render_sidebar()
        
        if selected == "Dashboard":
            self.render_dashboard()
        elif selected == "Data Upload":
            self.render_data_upload()
        elif selected == "Analytics":
            self.render_analytics()
        elif selected == "AI Chat":
            self.render_ai_chat()
        elif selected == "Email Campaigns":
            self.render_email_campaigns()

# Run the application
if __name__ == "__main__":
    app = GAIBAApp()
    app.run()
