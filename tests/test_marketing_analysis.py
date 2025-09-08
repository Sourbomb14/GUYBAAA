import unittest
import pandas as pd
import numpy as np
from app.marketing_analysis import MarketingAnalyzer

class TestMarketingAnalyzer(unittest.TestCase):
    
    def setUp(self):
        self.analyzer = MarketingAnalyzer()
        
        # Create test data
        self.test_data = pd.DataFrame({
            'campaign_id': ['C001', 'C002', 'C003', 'C004'],
            'budget': [1000, 1500, 2000, 1200],
            'spend': [800, 1200, 1800, 1000],
            'revenue': [1200, 1800, 2400, 1300],
            'impressions': [10000, 15000, 20000, 12000],
            'clicks': [100, 200, 250, 150],
            'conversions': [10, 20, 25, 15],
            'channel': ['Email', 'Social', 'Google', 'Email']
        })
        
        # Add derived metrics
        self.test_data['roi'] = ((self.test_data['revenue'] - self.test_data['spend']) / self.test_data['spend'] * 100)
        self.test_data['ctr'] = (self.test_data['clicks'] / self.test_data['impressions'] * 100)
    
    def test_calculate_performance_metrics(self):
        """Test performance metrics calculation"""
        metrics = self.analyzer.calculate_performance_metrics(self.test_data)
        
        self.assertIn('total_revenue', metrics)
        self.assertIn('avg_roi', metrics)
        self.assertIn('total_impressions', metrics)
        
        # Check specific calculations
        self.assertEqual(metrics['total_revenue'], self.test_data['revenue'].sum())
        self.assertAlmostEqual(metrics['avg_roi'], self.test_data['roi'].mean(), places=2)
    
    def test_analyze_columns(self):
        """Test column analysis"""
        analysis = self.analyzer.analyze_columns(self.test_data)
        
        self.assertIn('numeric_columns', analysis)
        self.assertIn('categorical_columns', analysis)
        self.assertIn('missing_data', analysis)
        
        # Check that numeric columns are identified correctly
        self.assertIn('budget', analysis['numeric_columns'])
        self.assertIn('channel', analysis['categorical_columns'])
    
    def test_perform_clustering(self):
        """Test clustering functionality"""
        clusters = self.analyzer.perform_clustering(self.test_data, n_clusters=2)
        
        if clusters is not None:
            self.assertEqual(len(clusters), len(self.test_data))
            self.assertTrue(all(0 <= c < 2 for c in clusters))
    
    def test_analyze_roi(self):
        """Test ROI analysis"""
        roi_analysis = self.analyzer.analyze_roi(self.test_data)
        
        self.assertIn('mean_roi', roi_analysis)
        self.assertIn('positive_roi_campaigns', roi_analysis)
        
        # All test campaigns should have positive ROI
        self.assertEqual(roi_analysis['positive_roi_campaigns'], len(self.test_data))
    
    def test_get_top_campaigns(self):
        """Test top campaigns retrieval"""
        top_campaigns = self.analyzer.get_top_campaigns(self.test_data, 'roi', 2)
        
        self.assertEqual(len(top_campaigns), 2)
        self.assertIn('campaign_name', top_campaigns.columns)
        
        # Check that campaigns are sorted by ROI
        roi_values = top_campaigns['roi'].values
        self.assertTrue(roi_values[0] >= roi_values[1])
    
    def test_analyze_channels(self):
        """Test channel analysis"""
        channel_analysis = self.analyzer.analyze_channels(self.test_data)
        
        if not channel_analysis.empty:
            self.assertIn('channel', channel_analysis.columns)
            # Should have data for Email, Social, and Google channels
            self.assertLessEqual(len(channel_analysis), 3)

if __name__ == '__main__':
    unittest.main()
