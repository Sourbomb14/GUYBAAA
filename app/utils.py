import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import logging
import json
import random

class UIHelper:
    """UI helper functions for consistent styling and components"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def render_metric_cards(self):
        """Render metric cards for the dashboard"""
        if st.session_state.campaign_data is not None:
            data = st.session_state.campaign_data
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown("""
                <div class="metric-card">
                    <h3 style="color: #667eea; margin: 0;">📊 Total Campaigns</h3>
                    <p style="font-size: 2rem; font-weight: bold; margin: 10px 0; color: #e2e8f0;">{}</p>
                    <p style="color: #a0aec0; margin: 0;">Active campaigns</p>
                </div>
                """.format(len(data)), unsafe_allow_html=True)
            
            with col2:
                total_spend = data['spend'].sum() if 'spend' in data.columns else 0
                st.markdown("""
                <div class="metric-card">
                    <h3 style="color: #667eea; margin: 0;">💰 Total Spend</h3>
                    <p style="font-size: 2rem; font-weight: bold; margin: 10px 0; color: #e2e8f0;">${:,.0f}</p>
                    <p style="color: #a0aec0; margin: 0;">Campaign investment</p>
                </div>
                """.format(total_spend), unsafe_allow_html=True)
            
            with col3:
                avg_roi = data['roi'].mean() if 'roi' in data.columns else 0
                roi_color = "#10b981" if avg_roi > 0 else "#ef4444"
                st.markdown("""
                <div class="metric-card">
                    <h3 style="color: #667eea; margin: 0;">📈 Average ROI</h3>
                    <p style="font-size: 2rem; font-weight: bold; margin: 10px 0; color: {};">{:.1f}%</p>
                    <p style="color: #a0aec0; margin: 0;">Return on investment</p>
                </div>
                """.format(roi_color, avg_roi), unsafe_allow_html=True)
            
            with col4:
                total_impressions = data['impressions'].sum() if 'impressions' in data.columns else 0
                st.markdown("""
                <div class="metric-card">
                    <h3 style="color: #667eea; margin: 0;">👁️ Total Impressions</h3>
                    <p style="font-size: 2rem; font-weight: bold; margin: 10px 0; color: #e2e8f0;">{:,.0f}</p>
                    <p style="color: #a0aec0; margin: 0;">Total reach</p>
                </div>
                """.format(total_impressions), unsafe_allow_html=True)
    
    def create_status_badge(self, status: str) -> str:
        """Create colored status badge"""
        status_colors = {
            'active': '#10b981',
            'paused': '#f59e0b',
            'completed': '#6b7280',
            'draft': '#3b82f6'
        }
        
        color = status_colors.get(status.lower(), '#6b7280')
        return f"""
        <span style="background-color: {color}; color: white; padding: 2px 8px; 
                     border-radius: 12px; font-size: 0.75rem; font-weight: bold;">
            {status.upper()}
        </span>
        """
    
    def create_progress_bar(self, value: float, max_value: float, color: str = "#667eea") -> str:
        """Create custom progress bar"""
        percentage = min((value / max_value) * 100, 100)
        return f"""
        <div style="background-color: rgba(102, 126, 234, 0.2); border-radius: 10px; height: 8px; margin: 5px 0;">
            <div style="background-color: {color}; height: 100%; border-radius: 10px; width: {percentage}%;"></div>
        </div>
        """
    
    def format_currency(self, value: float) -> str:
        """Format currency values"""
        if abs(value) >= 1_000_000:
            return f"${value/1_000_000:.1f}M"
        elif abs(value) >= 1_000:
            return f"${value/1_000:.1f}K"
        else:
            return f"${value:.2f}"
    
    def format_large_number(self, value: float) -> str:
        """Format large numbers"""
        if abs(value) >= 1_000_000:
            return f"{value/1_000_000:.1f}M"
        elif abs(value) >= 1_000:
            return f"{value/1_000:.1f}K"
        else:
            return f"{value:.0f}"

class CampaignOptimizer:
    """AI-powered campaign optimization and suggestions"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_ai_response(self, user_input: str, campaign_data: Optional[pd.DataFrame] = None) -> str:
        """Generate AI response based on user input and campaign data"""
        # This is a simplified AI response system
        # In production, you would integrate with OpenAI GPT or similar
        
        user_input_lower = user_input.lower()
        
        # Analyze user intent
        if any(word in user_input_lower for word in ['roi', 'return', 'profit']):
            return self.analyze_roi_query(campaign_data)
        
        elif any(word in user_input_lower for word in ['budget', 'spend', 'cost']):
            return self.analyze_budget_query(campaign_data)
        
        elif any(word in user_input_lower for word in ['channel', 'platform']):
            return self.analyze_channel_query(campaign_data)
        
        elif any(word in user_input_lower for word in ['optimize', 'improve', 'better']):
            return self.provide_optimization_suggestions(campaign_data)
        
        elif any(word in user_input_lower for word in ['trend', 'performance', 'analytics']):
            return self.analyze_performance_trends(campaign_data)
        
        else:
            return self.provide_general_insights(campaign_data)
    
    def analyze_roi_query(self, data: Optional[pd.DataFrame]) -> str:
        """Analyze ROI-related queries"""
        if data is None or 'roi' not in data.columns:
            return """
            🔍 **ROI Analysis**
            
            I'd love to help you analyze ROI, but I need campaign data first. Please upload your campaign dataset in the Data Upload section.
            
            Once you have data uploaded, I can provide insights on:
            • Best performing campaigns by ROI
            • ROI trends over time
            • Channel-specific ROI analysis
            • Optimization recommendations
            """
        
        avg_roi = data['roi'].mean()
        best_roi = data['roi'].max()
        worst_roi = data['roi'].min()
        positive_campaigns = (data['roi'] > 0).sum()
        total_campaigns = len(data)
        
        # Find best performing channel
        if 'channel' in data.columns:
            channel_roi = data.groupby('channel')['roi'].mean().sort_values(ascending=False)
            best_channel = channel_roi.index[0]
            best_channel_roi = channel_roi.iloc[0]
        else:
            best_channel = "N/A"
            best_channel_roi = 0
        
        return f"""
        📊 **ROI Analysis Results**
        
        **Overall Performance:**
        • Average ROI: {avg_roi:.2f}%
        • Best Campaign ROI: {best_roi:.2f}%
        • Worst Campaign ROI: {worst_roi:.2f}%
        • Profitable Campaigns: {positive_campaigns}/{total_campaigns} ({(positive_campaigns/total_campaigns)*100:.1f}%)
        
        **Top Performing Channel:**
        • {best_channel}: {best_channel_roi:.2f}% average ROI
        
        **Recommendations:**
        {'✅ Great job! Your average ROI is positive.' if avg_roi > 0 else '⚠️ Consider optimizing campaigns - negative average ROI detected.'}
        {'🎯 Focus more budget on ' + best_channel + ' campaigns.' if best_channel != 'N/A' else ''}
        💡 Consider A/B testing top performers to scale success.
        """
    
    def analyze_budget_query(self, data: Optional[pd.DataFrame]) -> str:
        """Analyze budget-related queries"""
        if data is None:
            return """
            💰 **Budget Analysis**
            
            Upload your campaign data to get detailed budget insights including:
            • Spend efficiency analysis
            • Budget allocation recommendations
            • Cost per acquisition optimization
            • Channel-wise budget performance
            """
        
        total_budget = data['budget'].sum() if 'budget' in data.columns else 0
        total_spend = data['spend'].sum() if 'spend' in data.columns else 0
        budget_utilization = (total_spend / total_budget * 100) if total_budget > 0 else 0
        
        avg_budget = data['budget'].mean() if 'budget' in data.columns else 0
        avg_spend = data['spend'].mean() if 'spend' in data.columns else 0
        
        return f"""
        💰 **Budget Analysis**
        
        **Budget Overview:**
        • Total Budget Allocated: ${total_budget:,.2f}
        • Total Amount Spent: ${total_spend:,.2f}
        • Budget Utilization: {budget_utilization:.1f}%
        • Average Campaign Budget: ${avg_budget:,.2f}
        • Average Campaign Spend: ${avg_spend:,.2f}
        
        **Budget Efficiency:**
        {'🟢 Good budget management - spending within limits' if budget_utilization <= 100 else '🔴 Budget exceeded - review spend controls'}
        
        **Recommendations:**
        • {'Increase budget for high-ROI campaigns' if 'roi' in data.columns and data['roi'].mean() > 15 else 'Focus on cost optimization'}
        • Consider reallocating budget from underperforming campaigns
        • Set up automated budget alerts for better control
        """
    
    def analyze_channel_query(self, data: Optional[pd.DataFrame]) -> str:
        """Analyze channel-related queries"""
        if data is None or 'channel' not in data.columns:
            return """
            📺 **Channel Analysis**
            
            Upload campaign data with channel information to get insights on:
            • Best performing marketing channels
            • Channel-specific ROI and engagement
            • Budget allocation by channel
            • Cross-channel optimization opportunities
            """
        
        channel_performance = data.groupby('channel').agg({
            'roi': 'mean',
            'spend': 'sum',
            'budget': 'sum'
        }).round(2)
        
        # Sort by ROI
        channel_performance = channel_performance.sort_values('roi', ascending=False)
        
        best_channel = channel_performance.index[0]
        worst_channel = channel_performance.index[-1]
        
        return f"""
        📺 **Channel Performance Analysis**
        
        **Channel Rankings (by ROI):**
        {self._format_channel_rankings(channel_performance)}
        
        **Key Insights:**
        🥇 **Best Performer:** {best_channel} ({channel_performance.loc[best_channel, 'roi']:.2f}% ROI)
        📉 **Needs Attention:** {worst_channel} ({channel_performance.loc[worst_channel, 'roi']:.2f}% ROI)
        
        **Recommendations:**
        • Increase budget allocation to {best_channel}
        • Investigate why {worst_channel} is underperforming
        • Consider cross-channel attribution analysis
        • Test new creative formats on top channels
        """
    
    def _format_channel_rankings(self, channel_performance: pd.DataFrame) -> str:
        """Format channel rankings for display"""
        rankings = []
        for i, (channel, row) in enumerate(channel_performance.iterrows()):
            emoji = ["🥇", "🥈", "🥉", "🏅", "📊"][min(i, 4)]
            rankings.append(f"{emoji} {channel}: {row['roi']:.2f}% ROI, ${row['spend']:,.0f} spend")
        
        return '\n'.join(rankings[:5])  # Show top 5
    
    def provide_optimization_suggestions(self, data: Optional[pd.DataFrame]) -> str:
        """Provide campaign optimization suggestions"""
        if data is None:
            return """
            🚀 **Optimization Suggestions**
            
            Upload your campaign data to get personalized optimization recommendations:
            • Performance improvement opportunities
            • Budget reallocation suggestions
            • Channel optimization strategies
            • Creative and targeting recommendations
            """
        
        suggestions = []
        
        # ROI-based suggestions
        if 'roi' in data.columns:
            avg_roi = data['roi'].mean()
            if avg_roi < 10:
                suggestions.append("🎯 **Target Optimization:** Review audience targeting - low ROI suggests poor fit")
            elif avg_roi > 50:
                suggestions.append("📈 **Scale Success:** Consider increasing budget for high-ROI campaigns")
        
        # Budget efficiency
        if 'budget' in data.columns and 'spend' in data.columns:
            underutilized = data[data['spend'] < data['budget'] * 0.8]
            if len(underutilized) > 0:
                suggestions.append(f"💰 **Budget Reallocation:** {len(underutilized)} campaigns are under-utilizing budget")
        
        # Channel diversity
        if 'channel' in data.columns:
            channel_count = data['channel'].nunique()
            if channel_count < 3:
                suggestions.append("📺 **Channel Diversification:** Consider expanding to more marketing channels")
        
        # Engagement optimization
        if 'engagement_rate' in data.columns:
            low_engagement = data[data['engagement_rate'] < 2]
            if len(low_engagement) > 0:
                suggestions.append("🎨 **Creative Refresh:** Low engagement rates suggest need for new creatives")
        
        if not suggestions:
            suggestions = [
                "✅ **Overall Performance:** Your campaigns are performing well!",
                "📊 **Continuous Testing:** Consider A/B testing to further optimize",
                "🔍 **Deep Dive Analytics:** Look into user journey analysis"
            ]
        
        return f"""
        🚀 **Campaign Optimization Recommendations**
        
        Based on your campaign data analysis:
        
        {chr(10).join(suggestions)}
        
        **Next Steps:**
        1. Prioritize high-impact optimizations first
        2. Set up proper tracking and measurement
        3. Test changes on small budget allocations initially
        4. Monitor performance changes closely
        """
    
    def analyze_performance_trends(self, data: Optional[pd.DataFrame]) -> str:
        """Analyze performance trends"""
        if data is None:
            return """
            📈 **Performance Trends Analysis**
            
            Upload your campaign data to see:
            • Performance trends over time
            • Seasonal patterns and insights
            • Growth opportunities
            • Predictive recommendations
            """
        
        # Calculate basic trend metrics
        numeric_cols = ['roi', 'engagement_rate', 'spend', 'revenue']
        available_metrics = [col for col in numeric_cols if col in data.columns]
        
        trends = {}
        for metric in available_metrics:
            values = data[metric].dropna()
            if len(values) > 1:
                # Simple trend calculation (slope)
                x = np.arange(len(values))
                slope = np.polyfit(x, values, 1)[0]
                trends[metric] = slope
        
        return f"""
        📈 **Performance Trends Analysis**
        
        **Trend Summary:**
        {self._format_trends(trends)}
        
        **Key Insights:**
        • Campaign count: {len(data)} total campaigns
        • Performance stability: {'Consistent' if len(trends) > 0 else 'Variable'}
        • Optimization opportunity: {'High' if any(v < 0 for v in trends.values()) else 'Moderate'}
        
        **Recommendations:**
        • Monitor declining trends closely
        • Capitalize on improving metrics
        • Set up automated trend alerts
        • Consider seasonal adjustments
        """
    
    def _format_trends(self, trends: Dict[str, float]) -> str:
        """Format trends for display"""
        if not trends:
            return "• Insufficient data for trend analysis"
        
        formatted = []
        for metric, slope in trends.items():
            direction = "📈 Improving" if slope > 0 else "📉 Declining" if slope < 0 else "➡️ Stable"
            formatted.append(f"• {metric.replace('_', ' ').title()}: {direction}")
        
        return '\n'.join(formatted)
    
    def provide_general_insights(self, data: Optional[pd.DataFrame]) -> str:
        """Provide general insights about the campaign data"""
        if data is None:
            return """
            🤖 **GAIBA AI Assistant**
            
            Hello! I'm your AI-powered marketing assistant. I can help you with:
            
            📊 **Campaign Analytics:**
            • Performance analysis and insights
            • ROI and budget optimization
            • Channel effectiveness review
            
            🎯 **Optimization:**
            • Targeting recommendations
            • Budget reallocation advice
            • Creative performance insights
            
            💡 **Strategy:**
            • Growth opportunities
            • Competitive analysis
            • Market trends
            
            To get started, upload your campaign data or ask me specific questions about marketing analytics!
            """
        
        # Generate insights based on available data
        insights = []
        
        total_campaigns = len(data)
        insights.append(f"📊 You have {total_campaigns} campaigns in your dataset")
        
        if 'channel' in data.columns:
            unique_channels = data['channel'].nunique()
            insights.append(f"📺 Running across {unique_channels} different channels")
        
        if 'roi' in data.columns:
            avg_roi = data['roi'].mean()
            insights.append(f"💰 Average ROI is {avg_roi:.2f}%")
        
        if 'spend' in data.columns:
            total_spend = data['spend'].sum()
            insights.append(f"💸 Total spend: ${total_spend:,.2f}")
        
        return f"""
        🤖 **Campaign Overview**
        
        {chr(10).join(insights)}
        
        **What would you like to explore?**
        • Ask about ROI performance: "How is my ROI looking?"
        • Budget questions: "How efficient is my budget allocation?"
        • Channel analysis: "Which channels perform best?"
        • Optimization tips: "How can I improve my campaigns?"
        
        I'm here to help you make data-driven marketing decisions! 🚀
        """
    
    def generate_campaign_suggestions(self, data: Optional[pd.DataFrame]) -> str:
        """Generate campaign suggestions based on data"""
        if data is None:
            return """
            💡 **Campaign Suggestions**
            
            Upload your data first, then I can provide:
            • New campaign ideas based on your best performers
            • Budget allocation recommendations
            • Channel expansion opportunities
            • Audience targeting suggestions
            """
        
        suggestions = []
        
        # Budget suggestions
        if 'budget' in data.columns and 'roi' in data.columns:
            high_roi_campaigns = data[data['roi'] > data['roi'].quantile(0.75)]
            if len(high_roi_campaigns) > 0:
                avg_budget = high_roi_campaigns['budget'].mean()
                suggestions.append(f"💰 Consider campaigns with ${avg_budget:,.0f} budget (based on high-ROI patterns)")
        
        # Channel suggestions
        if 'channel' in data.columns and 'roi' in data.columns:
            best_channel = data.groupby('channel')['roi'].mean().idxmax()
            suggestions.append(f"📺 Focus on {best_channel} campaigns (your best performing channel)")
        
        # Timing suggestions
        if any(col in data.columns for col in ['date', 'start_date', 'campaign_date']):
            suggestions.append("📅 Consider seasonal timing based on your historical data")
        
        return f"""
        💡 **New Campaign Suggestions**
        
        Based on your performance data:
        
        {chr(10).join(suggestions) if suggestions else '• Upload more data for personalized suggestions'}
        
        **Campaign Ideas:**
        🎯 **Lookalike Campaign:** Target similar audiences to your best performers
        🔄 **Retargeting Campaign:** Re-engage previous campaign audiences
        📱 **Cross-Channel Campaign:** Expand successful campaigns to new channels
        🆕 **Product Launch Campaign:** Use proven formats for new offerings
        
        **Success Tips:**
        • Start with small test budgets
        • Use proven creative formats
        • Monitor performance daily
        • Scale gradually based on results
        """
    
    def get_optimization_tips(self, data: Optional[pd.DataFrame]) -> str:
        """Get specific optimization tips"""
        return """
        🔧 **Campaign Optimization Tips**
        
        **📊 Data & Analytics:**
        • Set up proper conversion tracking
        • Use UTM parameters for attribution
        • Monitor key metrics daily
        • Set up automated alerts
        
        **🎯 Targeting Optimization:**
        • Test different audience segments
        • Use lookalike audiences from converters
        • Exclude poor-performing segments
        • Adjust geographic targeting
        
        **💰 Budget Optimization:**
        • Shift budget to high-ROI campaigns
        • Use automated bidding strategies
        • Set appropriate daily budgets
        • Monitor cost-per-acquisition
        
        **🎨 Creative Optimization:**
        • A/B test ad creatives regularly
        • Use dynamic creative optimization
        • Test different call-to-actions
        • Refresh creatives every 2-3 weeks
        
        **📱 Technical Optimization:**
        • Optimize landing page speed
        • Ensure mobile responsiveness
        • Test different landing pages
        • Implement proper tracking pixels
        
        **🚀 Advanced Tips:**
        • Use machine learning for bidding
        • Implement cross-device tracking
        • Test different attribution models
        • Consider customer lifetime value
        """

class DataProcessor:
    """Data processing utilities"""
    
    @staticmethod
    def clean_numeric_columns(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """Clean numeric columns by removing non-numeric characters"""
        df_clean = df.copy()
        
        for col in columns:
            if col in df_clean.columns:
                # Remove currency symbols and commas
                df_clean[col] = df_clean[col].astype(str).str.replace(r'[$,]', '', regex=True)
                # Convert to numeric
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
        
        return df_clean
    
    @staticmethod
    def calculate_derived_metrics(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate derived marketing metrics"""
        df_derived = df.copy()
        
        # ROI calculation
        if 'revenue' in df.columns and 'spend' in df.columns:
            df_derived['roi'] = ((df_derived['revenue'] - df_derived['spend']) / df_derived['spend'] * 100).round(2)
        
        # CTR calculation
        if 'clicks' in df.columns and 'impressions' in df.columns:
            df_derived['ctr'] = (df_derived['clicks'] / df_derived['impressions'] * 100).round(4)
        
        # CPA calculation
        if 'spend' in df.columns and 'conversions' in df.columns:
            df_derived['cpa'] = (df_derived['spend'] / df_derived['conversions']).round(2)
            df_derived['cpa'] = df_derived['cpa'].replace([np.inf, -np.inf], np.nan)
        
        # ROAS calculation
        if 'revenue' in df.columns and 'spend' in df.columns:
            df_derived['roas'] = (df_derived['revenue'] / df_derived['spend']).round(2)
        
        return df_derived
