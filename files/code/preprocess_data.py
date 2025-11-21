"""
Data Cleaning Script

This script contains functions for cleaning and preprocessing the research dataset.
"""

import pandas as pd
import numpy as np

def clean_data(df):
    """
    Clean and preprocess the input DataFrame.
    
    Args:
        df (pandas.DataFrame): Input DataFrame with raw data
        
    Returns:
        pandas.DataFrame: Cleaned DataFrame
    """
    # Remove duplicate rows
    df = df.drop_duplicates()
    
    # Handle missing values
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].fillna('Unknown')
        else:
            df[col] = df[col].fillna(df[col].median())
    
    # Clean string columns
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].str.strip()
    
    return df

if __name__ == "__main__":
    # Example usage
    print("Data cleaning module loaded successfully.")
    # Sample data for demonstration
    data = pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'value': [10, 20, None, 30, 40],
        'category': ['A', 'B', 'C', None, 'A']
    })
    
    print("Original data:")
    print(data)
    
    cleaned_data = clean_data(data)
    print("\nCleaned data:")
    print(cleaned_data)
