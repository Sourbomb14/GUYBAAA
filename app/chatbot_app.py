import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
from streamlit_chat import message
import os
from datetime import datetime, timedelta
import numpy as np

# Import custom modules
from data_loading import DataLoader
from marketing_analysis import MarketingAnalyzer
from email_utils import EmailManager
from utils import UIHelper, CampaignOptimizer

# Page config
st.set_page_config(
    page_title="GAIBA Marketing Analytics",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0e1117 0%, #1a1a2e 100%);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #16213e 0%, #0f3460 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid #2d3748;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        margin: 1rem 0;
    }
    
    .chat-container {
        background: rgba(22, 33, 62, 0.8);
        border-radius: 15px;
        padding: 1.5rem;
        border: 1px solid #2d3748;
        backdrop-filter: blur(10px);
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        border-radius: 10px;
        color: white;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    h1, h2, h3 {
        color: #e2e8f0;
        font-family: 'Arial', sans-serif;
    }
    
    .upload-area {
        background: rgba(22, 33, 62, 0.6);
        border: 2px dashed #667eea;
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

class GAIBAApp:
    def __init__(self):
        self.data_loader = DataLoader()
        self.analyzer = MarketingAnalyzer()
        self.email_manager = EmailManager()
        self.ui_helper = UIHelper()
        self.optimizer = CampaignOptimizer()
        
        # Initialize session state
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
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("""
            <div style="text-align: center; padding: 2rem 0;">
                <h1 style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                           -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
                           font-size: 3rem; margin: 0;">
                    🚀 GAIBA Analytics
                </h1>
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
                options=["Dashboard", "Data Upload", "Analytics", "AI Chat", "Email Campaigns", "Settings"],
                icons=["speedometer2", "cloud-upload", "graph-up", "robot", "envelope", "gear"],
                menu_icon="cast",
                default_index=0,
                styles={
                    "container": {"padding": "0!important", "background-color": "transparent"},
                    "icon": {"color": "#667eea", "font-size": "18px"}, 
                    "nav-link": {
                        "font-size": "16px", 
                        "text-align": "left", 
                        "margin": "0px",
                        "color": "#e2e8f0",
                        "background-color": "transparent",
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
                    avg_roi = data['roi'].mean()
                    st.metric("Average ROI", f"{avg_roi:.2f}%")
                if 'engagement_rate' in data.columns:
                    avg_engagement = data['engagement_rate'].mean()
                    st.metric("Avg Engagement", f"{avg_engagement:.2f}%")
        
        return selected
    
    def render_dashboard(self):
        """Render the main dashboard"""
        self.ui_helper.render_metric_cards()
        
        if st.session_state.campaign_data is not None:
            st.markdown("## 📈 Campaign Performance Overview")
            
            # Performance charts
            col1, col2 = st.columns(2)
            
            with col1:
                self.render_roi_chart()
            
            with col2:
                self.render_engagement_chart()
            
            # Recent campaigns table
            st.markdown("## 🗂️ Recent Campaigns")
            self.render_campaigns_table()
        else:
            self.render_welcome_message()
    
    def render_welcome_message(self):
        """Render welcome message when no data is uploaded"""
        st.markdown("""
        <div class="upload-area">
            <h2 style="color: #667eea;">Welcome to GAIBA Analytics!</h2>
            <p style="color: #a0aec0; font-size: 1.1rem;">
                Get started by uploading your marketing campaign data in the 
                <strong>Data Upload</strong> section to unlock powerful analytics and AI insights.
            </p>
            <div style="margin-top: 2rem;">
                <p style="color: #e2e8f0;">✨ <strong>Features you'll unlock:</strong></p>
                <ul style="color: #a0aec0; text-align: left; max-width: 400px; margin: 0 auto;">
                    <li>Real-time campaign performance analytics</li>
                    <li>AI-powered optimization suggestions</li>
                    <li>ROI and engagement tracking</li>
                    <li>Conversational campaign assistant</li>
                    <li>Email campaign management</li>
                </ul>
            </div>
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
                # Load and process data
                data = self.data_loader.load_csv(uploaded_file)
                st.session_state.campaign_data = data
                st.session_state.analysis_complete = False
                
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
                
                # Column analysis
                st.markdown("### 🔍 Column Analysis")
                col_analysis = self.analyzer.analyze_columns(data)
                st.json(col_analysis)
                
            except Exception as e:
                st.error(f"❌ Error uploading file: {str(e)}")
        
        # Sample data option
        st.markdown("---")
        st.markdown("### 🎲 Or Try Sample Data")
        
        if st.button("Load Sample Dataset", type="primary"):
            sample_data = self.data_loader.generate_sample_data()
            st.session_state.campaign_data = sample_data
            st.success("✅ Sample dataset loaded successfully!")
            st.experimental_rerun()
    
    def render_analytics(self):
        """Render analytics dashboard"""
        if st.session_state.campaign_data is None:
            st.warning("⚠️ Please upload campaign data first in the Data Upload section.")
            return
        
        data = st.session_state.campaign_data
        
        st.markdown("## 📊 Advanced Analytics")
        
        # Analytics tabs
        tab1, tab2, tab3, tab4 = st.tabs(["📈 Performance", "🎯 Segmentation", "💰 ROI Analysis", "📧 Channel Analysis"])
        
        with tab1:
            self.render_performance_analytics(data)
        
        with tab2:
            self.render_segmentation_analytics(data)
        
        with tab3:
            self.render_roi_analytics(data)
        
        with tab4:
            self.render_channel_analytics(data)
    
    def render_performance_analytics(self, data):
        """Render performance analytics"""
        st.markdown("### 📈 Campaign Performance Metrics")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        metrics = self.analyzer.calculate_performance_metrics(data)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Total Revenue", f"${metrics.get('total_revenue', 0):,.2f}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Average ROI", f"{metrics.get('avg_roi', 0):.2f}%")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Total Impressions", f"{metrics.get('total_impressions', 0):,}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Avg Engagement", f"{metrics.get('avg_engagement', 0):.2f}%")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Performance over time
        if 'date' in data.columns or 'campaign_date' in data.columns:
            st.markdown("#### 📅 Performance Trends")
            time_series_chart = self.analyzer.create_time_series_chart(data)
            st.plotly_chart(time_series_chart, use_container_width=True)
    
    def render_segmentation_analytics(self, data):
        """Render segmentation analytics"""
        st.markdown("### 🎯 Audience Segmentation")
        
        # K-means clustering
        if st.button("🔄 Run K-Means Clustering", type="primary"):
            with st.spinner("Running clustering analysis..."):
                clusters = self.analyzer.perform_clustering(data)
                
                if clusters is not None:
                    # Cluster visualization
                    cluster_chart = self.analyzer.create_cluster_chart(data, clusters)
                    st.plotly_chart(cluster_chart, use_container_width=True)
                    
                    # Cluster summary
                    st.markdown("#### 📋 Cluster Summary")
                    cluster_summary = self.analyzer.analyze_clusters(data, clusters)
                    st.dataframe(cluster_summary, use_container_width=True)
    
    def render_roi_analytics(self, data):
        """Render ROI analytics"""
        st.markdown("### 💰 ROI Deep Dive")
        
        roi_analysis = self.analyzer.analyze_roi(data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # ROI distribution
            roi_dist_chart = self.analyzer.create_roi_distribution_chart(data)
            st.plotly_chart(roi_dist_chart, use_container_width=True)
        
        with col2:
            # Top performing campaigns
            st.markdown("#### 🏆 Top Performing Campaigns")
            top_campaigns = self.analyzer.get_top_campaigns(data, metric='roi')
            st.dataframe(top_campaigns, use_container_width=True)
    
    def render_channel_analytics(self, data):
        """Render channel analytics"""
        st.markdown("### 📧 Channel Performance")
        
        channel_metrics = self.analyzer.analyze_channels(data)
        
        # Channel performance chart
        if 'channel' in data.columns:
            channel_chart = self.analyzer.create_channel_performance_chart(data)
            st.plotly_chart(channel_chart, use_container_width=True)
            
            # Channel comparison table
            st.markdown("#### 📊 Channel Comparison")
            st.dataframe(channel_metrics, use_container_width=True)
    
    def render_ai_chat(self):
        """Render AI chat interface"""
        st.markdown("## 🤖 AI Campaign Assistant")
        
        st.markdown("""
        <div class="chat-container">
            <p style="color: #a0aec0; margin-bottom: 1.5rem;">
                Chat with our AI assistant to get insights about your campaigns, 
                optimization suggestions, and marketing strategy advice.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Chat interface
        chat_container = st.container()
        
        with chat_container:
            # Display chat history
            for i, (role, content) in enumerate(st.session_state.chat_history):
                if role == "user":
                    message(content, is_user=True, key=f"user_{i}")
                else:
                    message(content, key=f"assistant_{i}")
        
        # Chat input
        user_input = st.chat_input("Ask me anything about your marketing campaigns...")
        
        if user_input:
            # Add user message to history
            st.session_state.chat_history.append(("user", user_input))
            
            # Generate AI response
            with st.spinner("🤖 Thinking..."):
                response = self.optimizer.get_ai_response(user_input, st.session_state.campaign_data)
                st.session_state.chat_history.append(("assistant", response))
            
            st.experimental_rerun()
        
        # Quick action buttons
        st.markdown("#### 🚀 Quick Actions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💡 Get Campaign Suggestions"):
                suggestions = self.optimizer.generate_campaign_suggestions(st.session_state.campaign_data)
                st.session_state.chat_history.append(("assistant", suggestions))
                st.experimental_rerun()
        
        with col2:
            if st.button("📊 Analyze Performance"):
                analysis = self.optimizer.analyze_campaign_performance(st.session_state.campaign_data)
                st.session_state.chat_history.append(("assistant", analysis))
                st.experimental_rerun()
        
        with col3:
            if st.button("🎯 Optimization Tips"):
                tips = self.optimizer.get_optimization_tips(st.session_state.campaign_data)
                st.session_state.chat_history.append(("assistant", tips))
                st.experimental_rerun()
    
    def render_email_campaigns(self):
        """Render email campaigns interface"""
        st.markdown("## 📧 Email Campaign Management")
        
        tab1, tab2, tab3 = st.tabs(["✉️ Send Campaign", "📋 Campaign History", "⚙️ Email Settings"])
        
        with tab1:
            self.render_send_email_campaign()
        
        with tab2:
            self.render_campaign_history()
        
        with tab3:
            self.render_email_settings()
    
    def render_send_email_campaign(self):
        """Render send email campaign interface"""
        st.markdown("### ✉️ Create & Send Email Campaign")
        
        with st.form("email_campaign_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                campaign_name = st.text_input("Campaign Name")
                subject_line = st.text_input("Subject Line")
                sender_email = st.text_input("Sender Email", value="marketing@company.com")
            
            with col2:
                recipient_list = st.text_area("Recipients (one email per line)")
                send_time = st.selectbox("Send Time", ["Now", "Schedule for later"])
                campaign_type = st.selectbox("Campaign Type", ["Newsletter", "Promotional", "Transactional"])
            
            email_content = st.text_area("Email Content", height=200)
            
            submitted = st.form_submit_button("📤 Send Campaign", type="primary")
            
            if submitted:
                if campaign_name and subject_line and email_content:
                    # Process email sending (stubbed for demo)
                    success = self.email_manager.send_campaign(
                        campaign_name, subject_line, email_content, recipient_list.split('\n')
                    )
                    
                    if success:
                        st.success("✅ Email campaign sent successfully!")
                        st.balloons()
                    else:
                        st.error("❌ Failed to send email campaign")
                else:
                    st.error("❌ Please fill in all required fields")
    
    def render_campaign_history(self):
        """Render campaign history"""
        st.markdown("### 📋 Campaign History")
        
        # Sample campaign history
        history = self.email_manager.get_campaign_history()
        
        if history:
            st.dataframe(history, use_container_width=True)
        else:
            st.info("📭 No email campaigns sent yet.")
    
    def render_email_settings(self):
        """Render email settings"""
        st.markdown("### ⚙️ Email Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.text_input("SMTP Server", value="smtp.gmail.com")
            st.number_input("SMTP Port", value=587)
            st.text_input("Username", value="your-email@gmail.com")
        
        with col2:
            st.text_input("Password", type="password")
            st.selectbox("Security", ["TLS", "SSL", "None"])
            st.checkbox("Enable Email Tracking")
        
        if st.button("💾 Save Settings", type="primary"):
            st.success("✅ Email settings saved successfully!")
    
    def render_roi_chart(self):
        """Render ROI chart"""
        if st.session_state.campaign_data is not None and 'roi' in st.session_state.campaign_data.columns:
            data = st.session_state.campaign_data
            fig = px.line(data, y='roi', title='ROI Trend', 
                         color_discrete_sequence=['#667eea'])
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    def render_engagement_chart(self):
        """Render engagement chart"""
        if st.session_state.campaign_data is not None and 'engagement_rate' in st.session_state.campaign_data.columns:
            data = st.session_state.campaign_data
            fig = px.bar(data.head(10), y='engagement_rate', title='Top 10 Engagement Rates',
                        color_discrete_sequence=['#764ba2'])
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    def render_campaigns_table(self):
        """Render campaigns table"""
        if st.session_state.campaign_data is not None:
            data = st.session_state.campaign_data.head(10)
            st.dataframe(data, use_container_width=True)
    
    def render_settings(self):
        """Render settings page"""
        st.markdown("## ⚙️ Application Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🎨 UI Preferences")
            st.selectbox("Theme", ["Dark (Default)", "Light", "Auto"])
            st.slider("Chart Animation Speed", 0, 100, 50)
            st.checkbox("Enable Notifications", value=True)
            
        with col2:
            st.markdown("### 🔧 Analytics Settings")
            st.number_input("Default Clustering Groups", min_value=2, max_value=10, value=5)
            st.selectbox("Default Chart Type", ["Plotly", "Matplotlib", "Altair"])
            st.checkbox("Auto-refresh Data", value=False)
        
        st.markdown("### 🔐 API Settings")
        st.text_input("OpenAI API Key", type="password", help="Required for AI chat features")
        st.text_input("Email API Key", type="password", help="Required for email campaigns")
        
        if st.button("💾 Save All Settings", type="primary"):
            st.success("✅ Settings saved successfully!")
    
    def run(self):
        """Main application runner"""
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
        elif selected == "Settings":
            self.render_settings()

# Run the application
if __name__ == "__main__":
    app = GAIBAApp()
    app.run()
