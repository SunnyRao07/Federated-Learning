"""
Enhanced data cleaning utilities for fraud detection dataset
"""
import pandas as pd
import numpy as np
from typing import Tuple, Optional

class DataCleaner:
    """Comprehensive data cleaning for fraud detection"""
    
    def __init__(self):
        self.cleaning_stats = {}
    
    def clean_dataset(self, data: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
        """
        Comprehensive data cleaning pipeline
        
        Steps:
        1. Remove duplicates
        2. Handle missing values
        3. Remove outliers (optional)
        4. Validate data types
        5. Check for invalid values
        """
        original_size = len(data)
        
        if verbose:
            print(f"Starting data cleaning...")
            print(f"Original dataset size: {original_size:,} rows")
        
        # Step 1: Remove duplicates
        data_clean = data.drop_duplicates()
        duplicates_removed = original_size - len(data_clean)
        if verbose and duplicates_removed > 0:
            print(f"✓ Removed {duplicates_removed:,} duplicate rows")
        
        # Step 2: Handle missing values
        missing_before = data_clean.isnull().sum().sum()
        if missing_before > 0:
            if verbose:
                print(f"✓ Found {missing_before:,} missing values")
            
            # Fill numeric columns with 0 (V features are PCA-transformed)
            numeric_cols = data_clean.select_dtypes(include=[np.number]).columns
            data_clean[numeric_cols] = data_clean[numeric_cols].fillna(0)
            
            missing_after = data_clean.isnull().sum().sum()
            if verbose:
                print(f"✓ Filled missing values: {missing_after:,} remaining")
        
        # Step 3: Validate Class column
        if 'Class' in data_clean.columns:
            invalid_class = ~data_clean['Class'].isin([0, 1])
            if invalid_class.sum() > 0:
                if verbose:
                    print(f"⚠ Found {invalid_class.sum():,} invalid Class values, removing...")
                data_clean = data_clean[~invalid_class]
        
        # Step 4: Check for infinite values
        numeric_cols = data_clean.select_dtypes(include=[np.number]).columns
        inf_mask = np.isinf(data_clean[numeric_cols]).any(axis=1)
        if inf_mask.sum() > 0:
            if verbose:
                print(f"⚠ Found {inf_mask.sum():,} rows with infinite values, removing...")
            data_clean = data_clean[~inf_mask]
        
        # Step 5: Validate Amount column (should be non-negative)
        if 'Amount' in data_clean.columns:
            negative_amounts = data_clean['Amount'] < 0
            if negative_amounts.sum() > 0:
                if verbose:
                    print(f"⚠ Found {negative_amounts.sum():,} negative amounts, setting to 0...")
                data_clean.loc[negative_amounts, 'Amount'] = 0
        
        # Step 6: Remove extreme outliers in Amount (optional - very conservative)
        if 'Amount' in data_clean.columns:
            # Use IQR method for extreme outliers (beyond 3*IQR)
            Q1 = data_clean['Amount'].quantile(0.25)
            Q3 = data_clean['Amount'].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 3 * IQR
            upper_bound = Q3 + 3 * IQR
            
            outliers = (data_clean['Amount'] < lower_bound) | (data_clean['Amount'] > upper_bound)
            if outliers.sum() > 0:
                if verbose:
                    print(f"⚠ Found {outliers.sum():,} extreme outliers in Amount (beyond 3*IQR)")
                    print(f"  Range: [{lower_bound:.2f}, {upper_bound:.2f}]")
                    print(f"  Keeping outliers (may be legitimate high-value transactions)")
        
        final_size = len(data_clean)
        removed = original_size - final_size
        
        self.cleaning_stats = {
            'original_size': original_size,
            'final_size': final_size,
            'removed': removed,
            'duplicates_removed': duplicates_removed,
            'missing_values_filled': missing_before
        }
        
        if verbose:
            print(f"\n✓ Cleaning complete!")
            print(f"  Final dataset size: {final_size:,} rows")
            print(f"  Total removed: {removed:,} rows ({100*removed/original_size:.2f}%)")
            
            if 'Class' in data_clean.columns:
                fraud_count = data_clean['Class'].sum()
                fraud_ratio = 100 * fraud_count / final_size
                print(f"  Fraud cases: {fraud_count:,} ({fraud_ratio:.3f}%)")
        
        return data_clean
    
    def validate_dataset(self, data: pd.DataFrame) -> Tuple[bool, list]:
        """
        Validate dataset structure and content
        Returns: (is_valid, list_of_issues)
        """
        issues = []
        
        # Check required columns
        required_cols = ['Time', 'Amount', 'Class']
        missing_cols = [col for col in required_cols if col not in data.columns]
        if missing_cols:
            issues.append(f"Missing required columns: {missing_cols}")
        
        # Check V features
        v_features = [f'V{i}' for i in range(1, 29)]
        missing_v = [v for v in v_features if v not in data.columns]
        if missing_v:
            issues.append(f"Missing V features: {len(missing_v)} (e.g., {missing_v[:3]})")
        
        # Check data types
        if 'Class' in data.columns:
            if not data['Class'].dtype in [np.int64, np.float64, np.int32, np.float32]:
                issues.append(f"Class column has wrong dtype: {data['Class'].dtype}")
        
        # Check for empty dataset
        if len(data) == 0:
            issues.append("Dataset is empty")
        
        # Check Class distribution
        if 'Class' in data.columns:
            unique_classes = data['Class'].unique()
            if not all(c in [0, 1] for c in unique_classes):
                issues.append(f"Class column contains invalid values: {unique_classes}")
        
        is_valid = len(issues) == 0
        return is_valid, issues
    
    def get_cleaning_stats(self) -> dict:
        """Get statistics from last cleaning operation"""
        return self.cleaning_stats.copy()


def clean_fraud_dataset(filepath: str, output_path: Optional[str] = None) -> pd.DataFrame:
    """
    Convenience function to clean a fraud detection dataset
    
    Args:
        filepath: Path to input CSV file
        output_path: Optional path to save cleaned dataset
    
    Returns:
        Cleaned DataFrame
    """
    # Load data
    print(f"Loading dataset from {filepath}...")
    data = pd.read_csv(filepath)
    
    # Clean
    cleaner = DataCleaner()
    data_clean = cleaner.clean_dataset(data, verbose=True)
    
    # Validate
    is_valid, issues = cleaner.validate_dataset(data_clean)
    if not is_valid:
        print("\n⚠ Validation Issues:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\n✓ Dataset validation passed!")
    
    # Save if output path provided
    if output_path:
        data_clean.to_csv(output_path, index=False)
        print(f"\n✓ Cleaned dataset saved to {output_path}")
    
    return data_clean


if __name__ == "__main__":
    # Example usage
    import sys
    from pathlib import Path
    
    data_dir = Path(__file__).parent
    
    # Try to clean existing dataset
    if (data_dir / "creditcard.csv").exists():
        clean_fraud_dataset(
            str(data_dir / "creditcard.csv"),
            str(data_dir / "creditcard_cleaned.csv")
        )
    elif (data_dir / "clean_dataset.csv").exists():
        clean_fraud_dataset(
            str(data_dir / "clean_dataset.csv"),
            str(data_dir / "clean_dataset_cleaned.csv")
        )
    else:
        print("No dataset found. Please download the Kaggle dataset first.")
        print("Run: python -m data.download_kaggle_dataset")

