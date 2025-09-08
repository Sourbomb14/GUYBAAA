import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
import requests
import json
from datetime import datetime

class UIHelper:
    """UI helper functions for consistent styling and components"""
    
    def render_metric_cards(self):
        """Render metric cards for the dashboard"""
        if st.session_state.campaign_data is not None:
            data = st.session_state.campaign_data
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="color: #667eea; margin: 0;">📊 Total Campaigns</h3>
                    <p style="font-size: 2rem; font-weight: bold; margin: 10px 0; color: #e2e8f0;">{len(data)}</p>
                    <p style="color: #a0aec0; margin: 0;">Active campaigns</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                total_spend = data['spend'].sum() if 'spend' in data.columns else 0
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="color: #667eea; margin: 0;">💰 Total Spend</h3>
                    <p style="font-size: 2rem; font-weight: bold; margin: 10px 0; color: #e2e8f0;">${total_spend:,.0f}</p>
                    <p style="color: #a0aec0; margin: 0;">Campaign investment</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                avg_roi = data['roi'].mean() if 'roi' in data.columns else 0
                roi_color = "#10b981" if avg_roi > 0 else "#ef4444"
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="color: #667eea; margin: 0;">📈 Average ROI</h3>
                    <p style="font-size: 2rem; font-weight: bold; margin: 10px 0; color: {roi_color};">{avg_roi:.1f}%</p>
                    <p style="color: #a0aec0; margin: 0;">Return on investment</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                total_impressions = data['impressions'].sum() if 'impressions' in data.columns else 0
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="color: #667eea; margin: 0;">👁️ Total Impressions</h3>
                    <p style="font-size: 2rem; font-weight: bold; margin: 10px 0; color: #e2e8f0;">{total_impressions:,.0f}</p>
                    <p style="color: #a0aec0; margin: 0;">Total reach</p>
                </div>
                """, unsafe_allow_html=True)

class CampaignOptimizer:
    """AI-powered campaign optimization using Groq"""
    
    def __init__(self, groq_api_key: str):
        self.groq_api_key = groq_api_key
        self.base_url = "https://api.groq.com/openai/v1"
    
    def get_ai_response(self, user_input: str, campaign_data: Optional[pd.DataFrame] = None) -> str:
        """Generate AI response using Groq API"""
        if not self.groq_api_key:
            return self._get_fallback_response(user_input, campaign_data)
        
        try:
            # Prepare context from campaign data
            context = self._prepare_context(campaign_data)
            
            # Create prompt
            prompt = f"""
            You are a marketing analytics expert. Based on the following campaign data context and user question, provide helpful insights and recommendations.

            Campaign Data Context:
            {context}

            User Question: {user_input}

            Please provide a comprehensive, actionable response with specific insights and recommendations.
            """
            
            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "llama3-8b-8192",
                "messages": [
                    {"role": "system", "content": "You are an expert marketing analytics consultant."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 1024,
                "temperature": 0.7
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                return f"API Error: {response.status_code} - {response.text}"
                
        except Exception as e:
            return f"Error generating AI response: {str(e)}"
    
    def _prepare_context(self, data: Optional[pd.DataFrame]) -> str:
        """Prepare campaign data context for AI"""
        if data is None:
            return "No campaign data available."
        
        context_parts = []
        
        # Basic stats
        context_parts.append(f"Total Campaigns: {len(data)}")
        
        if 'spend' in data.columns:
            context_parts.append(f"Total Spend: ${data['spend'].sum():,.2f}")
            context_parts.append(f"Average Spend: ${data['spend'].mean():,.2f}")
        
        if 'roi' in data.columns:
            context_parts.append(f"Average ROI: {data['roi'].mean():.2f}%")
            context_parts.append(f"Best ROI: {data['roi'].max():.2f}%")
            context_parts.append(f"Worst ROI: {data['roi'].min():.2f}%")
        
        if 'channel' in data.columns:
            channels = data['channel'].value_counts().head(3)
            context_parts.append(f"Top Channels: {', '.join(channels.index.tolist())}")
        
        return "; ".join(context_parts)
    
    def _get_fallback_response(self, user_input: str, data: Optional[pd.DataFrame]) -> str:
        """Fallback response when API is not available"""
        if data is None:
            return """
            🤖 **AI Assistant** (Demo Mode)
            
            I'd love to help analyze your campaigns! Please upload your campaign data first, then I can provide insights on:
            • Performance analysis and optimization suggestions
            • ROI and budget recommendations  
            • Channel effectiveness insights
            • Campaign strategy advice
            
            *Note: Full AI features require API configuration in secrets.*
            """
        
        # Simple analysis based on user input
        user_lower = user_input.lower()
        
        if 'roi' in user_lower:
            avg_roi = data['roi'].mean() if 'roi' in data.columns else 0
            return f"""
            📊 **ROI Analysis** (Demo Mode)
            
            Based on your {len(data)} campaigns:
            • Average ROI: {avg_roi:.2f}%
            • {'✅ Great performance!' if avg_roi > 20 else '⚠️ Room for improvement'}
            
            *Configure Groq API for detailed AI insights.*
            """
        
        return f"""
        🤖 **Campaign Insights** (Demo Mode)
        
        I see you have {len(data)} campaigns to analyze. For detailed AI-powered insights and recommendations, please configure the Groq API key in Streamlit secrets.
        
        Current data overview:
        • Total campaigns: {len(data)}
        • Columns available: {', '.join(data.columns[:5])}{'...' if len(data.columns) > 5 else ''}
        """
    
    def generate_campaign_suggestions(self, data: Optional[pd.DataFrame]) -> str:
        """Generate campaign suggestions"""
        if not self.groq_api_key:
            return self._get_basic_suggestions(data)
        
        context = self._prepare_context(data)
        prompt = f"""
        Based on this campaign data: {context}
        
        Please suggest 3-5 new campaign ideas with specific recommendations for:
        - Budget allocation
        - Target channels
        - Expected outcomes
        """
        
        return self.get_ai_response(prompt, data)
    
    def analyze_campaign_performance(self, data: Optional[pd.DataFrame]) -> str:
        """Analyze campaign performance"""
        if not self.groq_api_key:
            return self._get_basic_analysis(data)
        
        context = self._prepare_context(data)
        prompt = f"""
        Analyze the performance of these marketing campaigns: {context}
        
        Provide insights on:
        - Top performing campaigns and why
        - Areas needing improvement
        - Optimization opportunities
        """
        
        return self.get_ai_response(prompt, data)
    
    def get_optimization_tips(self, data: Optional[pd.DataFrame]) -> str:
        """Get optimization tips"""
        return """
        🔧 **Campaign Optimization Tips**
        
        **📊 Data & Analytics:**
        • Set up proper conversion tracking
        • Monitor key metrics daily
        • Use UTM parameters for attribution
        
        **🎯 Targeting:**
        • Test different audience segments
        • Use lookalike audiences
        • Optimize geographic targeting
        
        **💰 Budget:**
        • Shift budget to high-ROI campaigns
        • Use automated bidding
        • Monitor cost-per-acquisition
        
        **🎨 Creative:**
        • A/B test ad creatives regularly
        • Refresh creatives every 2-3 weeks
        • Test different call-to-actions
        """
    
    def _get_basic_suggestions(self, data: Optional[pd.DataFrame]) -> str:
        """Basic suggestions without AI"""
        if data is None:
            return "Upload campaign data to get personalized suggestions."
        
        suggestions = []
        if 'channel' in data.columns and 'roi' in data.columns:
            best_channel = data.groupby('channel')['roi'].mean().idxmax()
            suggestions.append(f"• Focus more budget on {best_channel} (your best performing channel)")
        
        if 'roi' in data.columns:
            high_roi_count = (data['roi'] > data['roi'].mean()).sum()
            suggestions.append(f"• Scale up {high_roi_count} campaigns performing above average")
        
        return f"""
        💡 **Campaign Suggestions**
        
        {chr(10).join(suggestions) if suggestions else '• Upload more detailed data for specific recommendations'}
        
        **General Recommendations:**
        • Test new audience segments
        • Optimize landing pages
        • Consider seasonal timing
        • Implement A/B testing
        """
    
    def _get_basic_analysis(self, data: Optional[pd.DataFrame]) -> str:
        """Basic analysis without AI"""
        if data is None:
            return "Upload campaign data for performance analysis."
        
        analysis = []
        if 'roi' in data.columns:
            avg_roi = data['roi'].mean()
            analysis.append(f"• Average ROI: {avg_roi:.2f}%")
            analysis.append(f"• {'Strong performance' if avg_roi > 15 else 'Needs optimization'}")
        
        if 'spend' in data.columns:
            total_spend = data['spend'].sum()
            analysis.append(f"• Total investment: ${total_spend:,.2f}")
        
        return f"""
        📊 **Performance Analysis**
        
        {chr(10).join(analysis)}
        
        **Key Insights:**
        • {len(data)} total campaigns analyzed
        • Performance varies across channels
        • Optimization opportunities available
        """
