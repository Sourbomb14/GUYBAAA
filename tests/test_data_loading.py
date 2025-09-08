import unittest
import pandas as pd
import numpy as np
from app.data_loading import DataLoader
import io

class TestDataLoader(unittest.TestCase):
    
    def setUp(self):
        self.loader = DataLoader()
    
    def test_generate_sample_data(self):
        """Test sample data generation"""
        data = self.loader.generate_sample_data(100)
        
        self.assertEqual(len(data), 100)
        self.assertIn('campaign_id', data.columns)
        self.assertIn('roi', data.columns)
        self.assertTrue(all(data['roi'].notna()))
    
    def test_preprocess_data(self):
        """Test data preprocessing"""
        # Create sample data with missing values
        raw_data = pd.DataFrame({
            'campaign_id': ['C001', 'C002', 'C003'],
            'budget': [1000, None, 1500],
            'spend': [800, 1200, None],
            'channel': ['Email', None, 'Social']
        })
        
        processed = self.loader.preprocess_data(raw_data)
        
        # Check that missing values are handled
        self.assertTrue(all(processed['budget'].notna()))
        self.assertTrue(all(processed['spend'].notna()))
        self.assertTrue(all(processed['channel'].notna()))
    
    def test_validate_data(self):
        """Test data validation"""
        valid_data = pd.DataFrame({
            'campaign_id': ['C001', 'C002'],
            'budget': [1000, 1500],
            'spend': [800, 1200]
        })
        
        validation = self.loader.validate_data(valid_data)
        self.assertTrue(validation['is_valid'])
        self.assertEqual(len(validation['errors']), 0)
    
    def test_export_data(self):
        """Test data export"""
        data = self.loader.generate_sample_data(10)
        
        # Test CSV export
        csv_data = self.loader.export_data(data, 'csv')
        self.assertIsInstance(csv_data, bytes)
        
        # Test Excel export
        excel_data = self.loader.export_data(data, 'excel')
        self.assertIsInstance(excel_data, bytes)

if __name__ == '__main__':
    unittest.main()
