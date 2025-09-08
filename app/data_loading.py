import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime, timedelta
import io
from typing import Optional, Dict, Any
import logging

class DataLoader:
    """Handles data loading and preprocessing for marketing campaigns"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def load_csv(self, uploaded_file) -> pd.DataFrame:
        """Load and preprocess CSV data"""
        try:
            # Read CSV file
            df = pd.read_csv(uploaded_file)
            
            # Basic preprocessing
            df = self.preprocess_data(df)
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error loading CSV: {str(e)}")
            raise Exception(f"Failed to load CSV file: {str(e)}")
    
    def preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess the marketing campaign data"""
        try:
            # Convert date columns
            date_columns = ['date', 'campaign_date', 'start_date', 'end_date']
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            
            # Clean numeric columns
            numeric_columns = ['budget', 'spend', 'revenue', 'impressions', 'clicks', 'roi', 'engagement_rate']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Fill missing values
            df = self.handle_missing_values(df)
            
            # Add derived columns
            df = self.add_derived_columns(df)
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error preprocessing data: {str(e)}")
            return df
    
    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values in the dataset"""
        # Fill numeric columns with median
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            df[col].fillna(df[col].median(), inplace=True)
        
        # Fill categorical columns with mode
        categorical_columns = df.select_dtypes(include=['object']).columns
        for col in categorical_columns:
            if not df[col].empty:
                df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else 'Unknown', inplace=True)
        
        return df
    
    def add_derived_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add derived columns for analysis"""
        try:
            # Calculate ROI if not present
            if 'roi' not in df.columns and 'revenue' in df.columns and 'spend' in df.columns:
                df['roi'] = ((df['revenue'] - df['spend']) / df['spend'] * 100).round(2)
            
            # Calculate CTR if not present
            if 'ctr' not in df.columns and 'clicks' in df.columns and 'impressions' in df.columns:
                df['ctr'] = (df['clicks'] / df['impressions'] * 100).round(4)
            
            # Calculate engagement rate if not present
            if 'engagement_rate' not in df.columns and 'clicks' in df.columns and 'impressions' in df.columns:
                df['engagement_rate'] = df['ctr']
            
            # Add campaign duration
            if 'start_date' in df.columns and 'end_date' in df.columns:
                df['campaign_duration'] = (df['end_date'] - df['start_date']).dt.days
            
            # Add cost per acquisition
            if 'cpa' not in df.columns and 'spend' in df.columns and 'conversions' in df.columns:
                df['cpa'] = (df['spend'] / df['conversions']).round(2)
                df['cpa'] = df['cpa'].replace([np.inf, -np.inf], np.nan)
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error adding derived columns: {str(e)}")
            return df
    
    def generate_sample_data(self, num_records: int = 1000) -> pd.DataFrame:
        """Generate sample marketing campaign data for demo purposes"""
        np.random.seed(42)
        
        # Campaign channels
        channels = ['Email', 'Social Media', 'Google Ads', 'Display', 'Video', 'Native']
        
        # Generate data
        data = {
            'campaign_id': [f'CAMP_{i+1:04d}' for i in range(num_records)],
            'campaign_name': [f'Campaign {i+1}' for i in range(num_records)],
            'channel': np.random.choice(channels, num_records),
            'start_date': pd.date_range(start='2023-01-01', periods=num_records, freq='D')[:num_records],
            'budget': np.random.uniform(1000, 50000, num_records).round(2),
            'spend': np.random.uniform(800, 45000, num_records).round(2),
            'impressions': np.random.randint(10000, 1000000, num_records),
            'clicks': np.random.randint(100, 50000, num_records),
            'conversions': np.random.randint(10, 1000, num_records),
            'revenue': np.random.uniform(1500, 75000, num_records).round(2),
        }
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Calculate end dates
        df['end_date'] = df['start_date'] + pd.Timedelta(days=np.random.randint(1, 30))
        
        # Preprocess the sample data
        df = self.preprocess_data(df)
        
        return df
    
    def validate_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate the loaded data and return validation results"""
        validation_results = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'info': {}
        }
        
        # Check required columns
        required_columns = ['campaign_id', 'budget', 'spend']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            validation_results['errors'].append(f"Missing required columns: {missing_columns}")
            validation_results['is_valid'] = False
        
        # Check data types
        if 'budget' in df.columns and not pd.api.types.is_numeric_dtype(df['budget']):
            validation_results['warnings'].append("Budget column should be numeric")
        
        if 'spend' in df.columns and not pd.api.types.is_numeric_dtype(df['spend']):
            validation_results['warnings'].append("Spend column should be numeric")
        
        # Check for negative values in financial columns
        financial_columns = ['budget', 'spend', 'revenue']
        for col in financial_columns:
            if col in df.columns and (df[col] < 0).any():
                validation_results['warnings'].append(f"Negative values found in {col} column")
        
        # Data quality metrics
        validation_results['info'] = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'missing_values': df.isnull().sum().sum(),
            'duplicate_rows': df.duplicated().sum(),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / (1024 * 1024)
        }
        
        return validation_results
    
    def export_data(self, df: pd.DataFrame, format: str = 'csv') -> bytes:
        """Export data in specified format"""
        if format.lower() == 'csv':
            return df.to_csv(index=False).encode('utf-8')
        elif format.lower() == 'excel':
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Campaign Data', index=False)
            return output.getvalue()
        else:
            raise ValueError(f"Unsupported export format: {format}")
