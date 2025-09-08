import unittest
import pandas as pd
import numpy as np
from app.utils import UIHelper, CampaignOptimizer, DataProcessor

class TestUIHelper(unittest.TestCase):
    
    def setUp(self):
        self.ui_helper = UIHelper()
    
    def test_create_status_badge(self):
        """Test status badge creation"""
        badge = self.ui_helper.create_status_badge("active")
        self.assertIn("ACTIVE", badge)
        self.assertIn("background-color", badge)
    
    def test_create_progress_bar(self):
        """Test progress bar creation"""
        progress = self.ui_helper.create_progress_bar(75, 100)
        self.assertIn("75%", progress)
        self.assertIn("background-color", progress)
    
    def test_format_currency(self):
        """Test currency formatting"""
        self.assertEqual(self.ui_helper.format_currency(1500), "$1.5K")
        self.assertEqual(self.ui_helper.format_currency(1500000), "$1.5M")
        self.assertEqual(self.ui_helper.format_currency(150), "$150.00")
    
    def test_format_large_number(self):
        """Test large number formatting"""
        self.assertEqual(self.ui_helper.format_large_number(1500), "1.5K")
        self.assertEqual(self.ui_helper.format_large_number(1500000), "1.5M")
        self.assertEqual(self.ui_helper.format_large_number(150), "150")

class TestCampaignOptimizer(unittest.TestCase):
    
    def setUp(self):
        self.optimizer = CampaignOptimizer()
        self.test_data = pd.DataFrame({
            'campaign_id': ['C001', 'C002'],
            'roi': [25.5, 15.2],
            'spend': [1000, 1500],
            'channel': ['Email', 'Social']
        })
    
    def test_get_ai_response_roi_query(self):
        """Test AI response for ROI queries"""
        response = self.optimizer.get_ai_response("What's my ROI?", self.test_data)
        self.assertIn("ROI", response)
        self.assertIn("25.5", response)  # Should include actual ROI values
    
    def test_get_ai_response_budget_query(self):
        """Test AI response for budget queries"""
        response = self.optimizer.get_ai_response("How's my budget?", self.test_data)
        self.assertIn("Budget", response)
        self.assertIn("spend", response.lower())
    
    def test_get_ai_response_general(self):
        """Test general AI response"""
        response = self.optimizer.get_ai_response("Hello", self.test_data)
        self.assertIn("campaigns", response.lower())
    
    def test_generate_campaign_suggestions(self):
        """Test campaign suggestions"""
        suggestions = self.optimizer.generate_campaign_suggestions(self.test_data)
        self.assertIn("Campaign", suggestions)
        self.assertIn("suggestions", suggestions.lower())

class TestDataProcessor(unittest.TestCase):
    
    def test_clean_numeric_columns(self):
        """Test numeric column cleaning"""
        df = pd.DataFrame({
            'budget': ['$1,000', '$2,500', '3000'],
            'other': ['a', 'b', 'c']
        })
        
        cleaned = DataProcessor.clean_numeric_columns(df, ['budget'])
        
        self.assertEqual(cleaned['budget'].iloc[0], 1000)
        self.assertEqual(cleaned['budget'].iloc[1], 2500)
        self.assertEqual(cleaned['other'].iloc[0], 'a')  # Should be unchanged
    
    def test_calculate_derived_metrics(self):
        """Test derived metrics calculation"""
        df = pd.DataFrame({
            'revenue': [1200, 1800],
            'spend': [1000, 1500],
            'clicks': [100, 150],
            'impressions': [10000, 15000],
            'conversions': [10, 15]
        })
        
        derived = DataProcessor.calculate_derived_metrics(df)
        
        self.assertIn('roi', derived.columns)
        self.assertIn('ctr', derived.columns)
        self.assertIn('cpa', derived.columns)
        
        # Check ROI calculation
        expected_roi = ((1200 - 1000) / 1000 * 100)
        self.assertAlmostEqual(derived['roi'].iloc[0], expected_roi, places=2)

if __name__ == '__main__':
    unittest.main()
