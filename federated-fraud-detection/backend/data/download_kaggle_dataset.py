"""
Download Kaggle Credit Card Fraud Detection dataset
"""
import os
import sys
import subprocess
from pathlib import Path
import shutil

def download_kaggle_dataset():
    """
    Download the Credit Card Fraud Detection dataset from Kaggle.
    Dataset: https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud
    """
    # Dataset identifier
    dataset_name = "mlg-ulb/creditcardfraud"
    
    # Output directory
    data_dir = Path(__file__).parent
    output_file = data_dir / "creditcard.csv"
    
    # Check if file already exists
    if output_file.exists():
        print(f"Dataset already exists at {output_file}")
        print(f"File size: {output_file.stat().st_size / (1024*1024):.2f} MB")
        return str(output_file)
    
    print("Downloading Kaggle Credit Card Fraud Detection dataset...")
    print(f"This may take a few minutes depending on your internet connection.")
    print(f"Dataset: {dataset_name}")
    
    # Try kagglehub first (newer, simpler method)
    try:
        import kagglehub
        
        print("Using kagglehub to download dataset...")
        # Download latest version
        path = kagglehub.dataset_download("mlg-ulb/creditcardfraud")
        print(f"Path to dataset files: {path}")
        
        # Find creditcard.csv in the downloaded path
        downloaded_file = Path(path) / "creditcard.csv"
        if downloaded_file.exists():
            # Copy to our data directory
            shutil.copy2(str(downloaded_file), str(output_file))
            print(f"✓ Successfully downloaded dataset to {output_file}")
            print(f"File size: {output_file.stat().st_size / (1024*1024):.2f} MB")
            return str(output_file)
        else:
            # Search for csv files in the path
            csv_files = list(Path(path).glob("*.csv"))
            if csv_files:
                shutil.copy2(str(csv_files[0]), str(output_file))
                print(f"✓ Successfully downloaded dataset to {output_file}")
                return str(output_file)
            else:
                raise FileNotFoundError("creditcard.csv not found in downloaded files")
                
    except ImportError:
        print("kagglehub not available, trying kaggle API...")
    except Exception as e:
        print(f"kagglehub download failed: {e}")
        print("Trying kaggle API as fallback...")
    
    # Fallback to kaggle API
    try:
        import kaggle
        from kaggle.api.kaggle_api_extended import KaggleApi
        
        # Initialize Kaggle API
        api = KaggleApi()
        api.authenticate()
        
        # Download dataset
        print(f"Downloading to {data_dir}...")
        api.dataset_download_files(dataset_name, path=str(data_dir), unzip=True)
        
        # Check if download was successful
        if output_file.exists():
            print(f"✓ Successfully downloaded dataset to {output_file}")
            print(f"File size: {output_file.stat().st_size / (1024*1024):.2f} MB")
            return str(output_file)
        else:
            # Sometimes the file is in a subdirectory
            possible_paths = [
                data_dir / "creditcard.csv",
                data_dir / "creditcardfraud" / "creditcard.csv",
                data_dir / dataset_name.split('/')[1] / "creditcard.csv"
            ]
            
            for path in possible_paths:
                if path.exists():
                    # Move to data directory
                    shutil.move(str(path), str(output_file))
                    print(f"✓ Successfully downloaded and moved dataset to {output_file}")
                    return str(output_file)
            
            raise FileNotFoundError("Downloaded file not found in expected locations")
            
    except ImportError:
        print("ERROR: Neither kagglehub nor kaggle package installed.")
        print("Please install one of them:")
        print("  pip install kagglehub  # Recommended (simpler)")
        print("  OR")
        print("  pip install kaggle")
        print("\nFor kaggle API, you also need to set up credentials:")
        print("1. Go to https://www.kaggle.com/account")
        print("2. Scroll to 'API' section and click 'Create New API Token'")
        print("3. Place kaggle.json in ~/.kaggle/")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to download dataset: {e}")
        print("\nAlternative: Manual download")
        print("1. Visit: https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud")
        print("2. Download creditcard.csv")
        print(f"3. Place it in: {data_dir}")
        sys.exit(1)


def download_alternative():
    """
    Alternative method: Download using direct URL (if available)
    Note: This may not work if Kaggle requires authentication
    """
    import urllib.request
    import urllib.error
    
    data_dir = Path(__file__).parent
    output_file = data_dir / "creditcard.csv"
    
    # Note: Direct download URLs for Kaggle datasets typically require authentication
    # This is a placeholder - users should use the kaggle API method above
    print("Direct download not available - Kaggle requires authentication.")
    print("Please use the kaggle API method or download manually from:")
    print("https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud")


if __name__ == "__main__":
    print("=" * 60)
    print("Kaggle Credit Card Fraud Detection Dataset Downloader")
    print("=" * 60)
    print()
    
    filepath = download_kaggle_dataset()
    
    if filepath and os.path.exists(filepath):
        print()
        print("=" * 60)
        print("✓ Download complete!")
        print(f"Dataset location: {filepath}")
        print("=" * 60)
        
        # Quick validation
        try:
            import pandas as pd
            df = pd.read_csv(filepath, nrows=5)
            print(f"\nDataset preview:")
            print(f"Columns: {list(df.columns)}")
            print(f"Shape preview: {len(df)} rows (showing first 5)")
            print(f"\nExpected format: Time, Amount, V1-V28, Class")
        except Exception as e:
            print(f"Note: Could not preview dataset: {e}")

