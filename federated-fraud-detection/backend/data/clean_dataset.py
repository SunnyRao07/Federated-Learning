"""
Simple script to clean the dataset - removes missing values and duplicates
"""
import pandas as pd
import numpy as np
from pathlib import Path

def clean_dataset(input_file='creditcard.csv', output_file='creditcard_cleaned.csv'):
    """
    Clean dataset: remove missing values, duplicates, and invalid entries
    """
    data_dir = Path(__file__).parent
    
    input_path = data_dir / input_file
    output_path = data_dir / output_file
    
    print(f"Loading dataset from {input_path}...")
    df = pd.read_csv(input_path)
    
    original_size = len(df)
    print(f"Original dataset size: {original_size:,} rows")
    
    # Step 1: Remove duplicates
    df = df.drop_duplicates()
    duplicates_removed = original_size - len(df)
    if duplicates_removed > 0:
        print(f"✓ Removed {duplicates_removed:,} duplicate rows")
    
    # Step 2: Remove rows with any missing values
    missing_before = df.isnull().sum().sum()
    if missing_before > 0:
        print(f"Found {missing_before:,} missing values")
        df = df.dropna()
        print(f"✓ Removed rows with missing values")
    
    # Step 3: Remove rows with infinite values
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    inf_mask = np.isinf(df[numeric_cols]).any(axis=1)
    if inf_mask.sum() > 0:
        print(f"✓ Removed {inf_mask.sum():,} rows with infinite values")
        df = df[~inf_mask]
    
    # Step 4: Validate Class column (should be 0 or 1)
    if 'Class' in df.columns:
        invalid_class = ~df['Class'].isin([0, 1])
        if invalid_class.sum() > 0:
            print(f"✓ Removed {invalid_class.sum():,} rows with invalid Class values")
            df = df[~invalid_class]
    
    # Step 5: Remove negative amounts (if any)
    if 'Amount' in df.columns:
        negative_amounts = df['Amount'] < 0
        if negative_amounts.sum() > 0:
            print(f"✓ Removed {negative_amounts.sum():,} rows with negative amounts")
            df = df[df['Amount'] >= 0]
    
    final_size = len(df)
    removed = original_size - final_size
    
    print(f"\n✓ Cleaning complete!")
    print(f"  Final dataset size: {final_size:,} rows")
    print(f"  Total removed: {removed:,} rows ({100*removed/original_size:.2f}%)")
    
    if 'Class' in df.columns:
        fraud_count = df['Class'].sum()
        fraud_ratio = 100 * fraud_count / final_size
        print(f"  Fraud cases: {fraud_count:,} ({fraud_ratio:.3f}%)")
    
    # Save cleaned dataset
    df.to_csv(output_path, index=False)
    print(f"\n✓ Cleaned dataset saved to {output_path}")
    
    return df

if __name__ == "__main__":
    clean_dataset()

