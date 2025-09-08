import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
import os
import sys
from datetime import datetime, timedelta
import numpy as np

# Add current directory to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Now import custom modules
try:
    import data_loading
    import marketing_analysis
    import email_utils
    import utils
    
    from data_loading import DataLoader
    from marketing_analysis import MarketingAnalyzer
    from email_utils import EmailManager
    from utils import UIHelper, CampaignOptimizer
except ImportError as e:
    st.error(f"""
    **Import Error**: {e}
    
    Please ensure all required files are present:
    - data_loading.py
    - marketing_analysis.py 
    - email_utils.py
    - utils.py
    """)
    st.stop()

# Page config
st.set_page_config(
    page_title="GAIBA Marketing Analytics",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load API keys from Streamlit secrets
@st.cache_data
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
    except Exception:
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
        defaults = {
            'chat_history': [],
            'campaign_data': None,
            'analysis_complete': False
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
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
            <h2 style="color: #667eea; text-align: center;">🎯 Navigation</h2>
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
            
            # Quick stats
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
        if st.session_state.campaign_data is not None:
            # Render metrics
            data = st.session_state.campaign_data
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="color: #667eea; margin: 0;">📊 Total Campaigns</h3>
                    <p style="font-size: 2rem; font-weight: bold; margin: 10px 0; color: #e2e8f0;">{len(data)}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                total_spend = data['spend'].sum() if 'spend' in data.columns else 0
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="color: #667eea; margin: 0;">💰 Total Spend</h3>
                    <p style="font-size: 2rem; font-weight: bold; margin: 10px 0; color: #e2e8f0;">${total_spend:,.0f}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                avg_roi = data['roi'].mean() if 'roi' in data.columns else 0
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="color: #667eea; margin: 0;">📈 Average ROI</h3>
                    <p style="font-size: 2rem; font-weight: bold; margin: 10px 0; color: #10b981;">{avg_roi:.1f}%</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                total_impressions = data['impressions'].sum() if 'impressions' in data.columns else 0
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="color: #667eea; margin: 0;">👁️ Impressions</h3>
                    <p style="font-size: 2rem; font-weight: bold; margin: 10px 0; color: #e2e8f0;">{total_impressions:,.0f}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Charts
            st.markdown("## 📈 Campaign Performance")
            col1, col2 = st.columns(2)
            
            with col1:
                if 'roi' in data.columns:
                    fig = px.line(data, y='roi', title='ROI Trend', color_discrete_sequence=['#667eea'])
                    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white')
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                if 'channel' in data.columns:
                    channel_counts = data['channel'].value_counts()
                    fig = px.bar(x=channel_counts.index, y=channel_counts.values, 
                               title='Campaigns by Channel', color_discrete_sequence=['#764ba2'])
                    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white')
                    st.plotly_chart(fig, use_container_width=True)
            
            # Data table
            st.markdown("## 🗂️ Recent Campaigns")
            st.dataframe(data.head(10), use_container_width=True)
        else:
            st.markdown("""
            <div class="upload-area">
                <h2 style="color: #667eea;">Welcome to GAIBA Analytics!</h2>
                <p style="color: #a0aec0; font-size: 1.1rem;">
                    Upload your marketing campaign data to unlock powerful analytics and AI insights.
                </p>
                <p style="color: #667eea;">👈 Start with <strong>Data Upload</strong> in the sidebar</p>
            </div>
            """, unsafe_allow_html=True)
    
    def render_data_upload(self):
        """Render data upload interface"""
        st.markdown("## 📤 Upload Campaign Data")
        
        uploaded_file = st.file_uploader(
            "Choose a CSV file", 
            type=['csv'],
            help="Upload your marketing campaign dataset in CSV format"
        )
        
        if uploaded_file is not None:
            try:
                data = self.data_loader.load_csv(uploaded_file)
                st.session_state.campaign_data = data
                st.success(f"✅ Successfully uploaded {len(data)} campaign records!")
                
                # Data preview
                st.markdown("### 👀 Data Preview")
                st.dataframe(data.head(), use_container_width=True)
                
                # Data info
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Rows", len(data))
                with col2:
                    st.metric("Total Columns", len(data.columns))
                with col3:
                    st.metric("Memory Usage", f"{data.memory_usage(deep=True).sum() / 1024:.1f} KB")
                    
            except Exception as e:
                st.error(f"❌ Error uploading file: {str(e)}")
        
        # Sample data option
        st.markdown("---")
        st.markdown("### 🎲 Try Sample Data")
        if st.button("Load Sample Dataset", type="primary"):
            sample_data = self.data_loader.generate_sample_data()
            st.session_state.campaign_data = sample_data
            st.success("✅ Sample dataset loaded successfully!")
            st.rerun()
    
    def render_analytics(self):
        """Render analytics dashboard"""
        if st.session_state.campaign_data is None:
            st.warning("⚠️ Please upload campaign data first in the Data Upload section.")
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
                    try:
                        clusters = self.analyzer.perform_clustering(data)
                        if clusters is not None:
                            st.success("✅ Clustering completed!")
                            st.info(f"📊 Found {len(set(clusters))} clusters in your campaign data")
                        else:
                            st.warning("⚠️ Could not perform clustering - insufficient numeric data")
                    except Exception as e:
                        st.error(f"Error in clustering: {str(e)}")
        
        with tab3:
            if 'roi' in data.columns:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("#### 📊 ROI Distribution")
                    fig = px.histogram(data, x='roi', title='ROI Distribution', 
                                     color_discrete_sequence=['#667eea'])
                    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', 
                                    paper_bgcolor='rgba(0,0,0,0)', font_color='white')
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.markdown("#### 🏆 Top Performing Campaigns")
                    top_campaigns = data.nlargest(5, 'roi')[['campaign_name', 'roi', 'spend']] if 'campaign_name' in data.columns else data.nlargest(5, 'roi')
                    st.dataframe(top_campaigns, use_container_width=True)
            else:
                st.info("📈 ROI column not found in your data. Please ensure your dataset includes ROI metrics.")
    
    def render_ai_chat(self):
        """Render AI chat interface"""
        st.markdown("## 🤖 AI Campaign Assistant")
        
        if not self.api_keys.get('groq_api_key'):
            st.warning("⚠️ Groq API key not configured. Add GROQ_API_KEY to Streamlit secrets for AI features.")
        
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
            if st.button("📊 Performance Analysis"):
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
            st.info("ℹ️ Configure email credentials in Streamlit secrets for full functionality.")
        
        tab1, tab2 = st.tabs(["✉️ Send Campaign", "📋 Campaign History"])
        
        with tab1:
            with st.form("email_campaign_form"):
                st.markdown("### Create Email Campaign")
                
                col1, col2 = st.columns(2)
                with col1:
                    campaign_name = st.text_input("Campaign Name*")
                    subject_line = st.text_input("Subject Line*")
                
                with col2:
                    campaign_type = st.selectbox("Campaign Type", ["Newsletter", "Promotional", "Transactional"])
                    send_time = st.selectbox("Send Time", ["Send Now", "Schedule Later"])
                
                recipient_list = st.text_area("Recipients (one email per line)*", height=100)
                email_content = st.text_area("Email Content*", height=200, 
                                           placeholder="Enter your email content here...")
                
                submitted = st.form_submit_button("📤 Send Campaign", type="primary")
                
                if submitted:
                    if campaign_name and subject_line and email_content and recipient_list:
                        recipients = [email.strip() for email in recipient_list.split('\n') if email.strip()]
                        if recipients:
                            success = self.email_manager.send_campaign(
                                campaign_name, subject_line, email_content, recipients
                            )
                            if success:
                                st.success("✅ Email campaign sent successfully!")
                                st.balloons()
                            else:
                                st.error("❌ Failed to send email campaign")
                        else:
                            st.error("❌ Please provide at least one recipient email")
                    else:
                        st.error("❌ Please fill in all required fields marked with *")
        
        with tab2:
            st.markdown("### 📋 Campaign History")
            history = self.email_manager.get_campaign_history()
            if not history.empty:
                st.dataframe(history, use_container_width=True)
            else:
                st.info("📭 No email campaigns sent yet. Create your first campaign!")
    
    def run(self):
        """Main application runner"""
        try:
            self.render_header()
            selected = self.render_sidebar()
            
            # Route to selected page
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
                
        except Exception as e:
            st.error(f"Application error: {str(e)}")
            st.info("Please refresh the page or check your data.")

# Run the application
if __name__ == "__main__":
    app = GAIBAApp()
    app.run()
