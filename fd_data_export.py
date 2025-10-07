"""
Freshdesk Data Export Download Script

DESCRIPTION:
This script downloads Freshdesk data export files that have been scheduled
and generated through the Freshdesk reporting system. It retrieves the export
metadata from the Freshdesk API and then downloads the actual data file
from the provided S3 URL to a local directory.

REQUIREMENTS:
- Python 3.x
- requests library (install with: pip install requests)
- Valid Freshdesk API key with reports access permissions
- Freshdesk account and domain access
- Write permissions to the target download directory

SETUP INSTRUCTIONS:
1. Replace API_KEY with your actual Freshdesk API key
2. Replace DOMAIN with your Freshdesk domain (e.g., 'yourcompany.freshdesk.com')
3. Update EXPORT_UUID with the UUID of your scheduled export
4. Update DOWNLOAD_PATH to your desired download location
5. Ensure your API key has permissions for report access
6. Run the script: python fd_data_export.py

API DOCUMENTATION:
- Freshdesk API v2: https://developers.freshdesk.com/api/
- Reports API: https://developers.freshdesk.com/api/#reports
- Authentication: Basic Auth with API key

INPUT PARAMETERS:
- API_KEY: Your Freshdesk API key
- DOMAIN: Your Freshdesk domain
- EXPORT_UUID: UUID of the scheduled export job
- DOWNLOAD_PATH: Local directory path for file downloads

OUTPUT:
- Downloaded CSV/Excel file in the specified directory
- Console output showing progress and results
- Detailed logging for troubleshooting

SUPPORTED EXPORT TYPES:
- Ticket exports (CSV format)
- Contact exports (CSV format)
- Company exports (CSV format)
- Time entry exports (CSV format)
- Survey response exports (CSV format)

ERROR HANDLING:
- Validates API responses and export metadata
- Handles network errors and timeouts
- Validates file download integrity
- Provides detailed error messages for troubleshooting
- Continues processing with graceful failure handling

SECURITY NOTE:
- Store API keys securely (environment variables recommended for production)
- Never commit API keys to version control
- Rotate API keys regularly for security
- Ensure download directory permissions are properly configured

TROUBLESHOOTING:
- Verify API key has reports access permissions
- Check that EXPORT_UUID is valid and export is completed
- Ensure network connectivity to Freshdesk and S3
- Verify write permissions to download directory
- Check that export job has finished processing

PERFORMANCE CONSIDERATIONS:
- Downloads files sequentially (one export at a time)
- Handles large files efficiently with streaming
- Configurable timeout for long-running downloads
- Minimal memory usage for file operations

USAGE SCENARIOS:
- Automated daily/weekly data exports
- Backup of Freshdesk data
- Integration with other business systems
- Data analysis and reporting workflows
"""

import requests
import base64
import os
import json
import time
import logging
import sys
from pathlib import Path

# Configure logging to both file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fd_data_export.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Freshdesk API Configuration
# TODO: Move these to environment variables for security
API_KEY = "5TMgbcZdRFY70hSpEdj"  # Replace with your actual API key
DOMAIN = "benchmarkeducationcompany.freshdesk.com"  # Replace with your domain

# Export Configuration
EXPORT_UUID = "89c6af78-f312-4cdc-81c1-39d92a436dcf"  # Replace with your export UUID
DOWNLOAD_PATH = r"C:\Users\skala\OneDrive - Benchmark Education"  # Replace with your download path

# Script Configuration
DEFAULT_FILENAME = "freshdesk_export.csv"
LOG_FILENAME = "fd_data_export.log"
REQUEST_TIMEOUT = 300  # 5 minutes timeout for large files

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILENAME, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

def validate_configuration():
    """
    Validate that all required configuration is present and valid.

    Returns:
        bool: True if configuration is valid, False otherwise
    """
    errors = []

    if not API_KEY or API_KEY == "5TMgbcZdRFY70hSpEdj":
        errors.append("API_KEY not configured. Please set your actual Freshdesk API key.")

    if not DOMAIN or DOMAIN == "benchmarkeducationcompany.freshdesk.com":
        errors.append("DOMAIN not configured. Please set your actual Freshdesk domain.")

    if not EXPORT_UUID or EXPORT_UUID == "89c6af78-f312-4cdc-81c1-39d92a436dcf":
        errors.append("EXPORT_UUID not configured. Please set your actual export UUID.")

    if not DOWNLOAD_PATH:
        errors.append("DOWNLOAD_PATH not configured. Please set your download directory.")

    if errors:
        for error in errors:
            logging.error(error)
            print(f"❌ {error}")
        return False

    return True

def ensure_download_directory():
    """
    Ensure the download directory exists and is writable.

    Returns:
        bool: True if directory is ready, False otherwise
    """
    try:
        # Create Path object for better cross-platform compatibility
        download_dir = Path(DOWNLOAD_PATH)

        # Create directory if it doesn't exist
        download_dir.mkdir(parents=True, exist_ok=True)

        # Test write permissions by creating a temporary file
        test_file = download_dir / ".write_test"
        test_file.write_text("test")
        test_file.unlink()  # Delete the test file

        logging.info(f"Download directory ready: {download_dir}")
        print(f"✓ Download directory ready: {download_dir}")
        return True

    except PermissionError:
        error_msg = f"Permission denied: Cannot write to {DOWNLOAD_PATH}"
        logging.error(error_msg)
        print(f"❌ {error_msg}")
        return False
    except Exception as e:
        error_msg = f"Error creating download directory: {e}"
        logging.error(error_msg)
        print(f"❌ {error_msg}")
        return False

def get_export_metadata():
    """
    Retrieve export metadata from Freshdesk API.

    Returns:
        dict or None: Export metadata if successful, None if failed

    Note:
        - Retrieves information about the scheduled export
        - Includes file URL, status, and other metadata
    """
    # Construct the API URL for the specific export
    api_url = f"https://{DOMAIN}/reports/omni_schedule/download_file.json?uuid={EXPORT_UUID}"

    # Prepare authentication headers
    auth_string = f"{API_KEY}:X"
    auth_header = base64.b64encode(auth_string.encode()).decode()
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/json"
    }

    try:
        logging.info(f"Fetching export metadata for UUID: {EXPORT_UUID}")
        print("Fetching export metadata..."
        response = requests.get(api_url, headers=headers, timeout=REQUEST_TIMEOUT)

        if response.status_code == 200:
            metadata = response.json()
            logging.info("Successfully retrieved export metadata")
            print("✓ Export metadata retrieved successfully")

            # Log metadata for debugging (without sensitive data)
            if "export" in metadata:
                export_info = metadata["export"]
                file_url = export_info.get("url", "N/A")
                file_size = export_info.get("file_size", "Unknown")
                logging.info(f"Export file URL: {file_url[:50]}...")
                logging.info(f"Export file size: {file_size}")

            return metadata

        elif response.status_code == 404:
            error_msg = f"Export UUID {EXPORT_UUID} not found or expired"
            logging.error(error_msg)
            print(f"❌ {error_msg}")
            return None

        elif response.status_code == 403:
            error_msg = "Access denied. Check API key permissions for reports access."
            logging.error(error_msg)
            print(f"❌ {error_msg}")
            return None

        else:
            error_msg = f"Failed to fetch export metadata. Status: {response.status_code}"
            logging.error(f"{error_msg} - {response.text}")
            print(f"❌ {error_msg}")
            return None

    except requests.exceptions.Timeout:
        error_msg = f"Request timeout after {REQUEST_TIMEOUT} seconds"
        logging.error(error_msg)
        print(f"❌ {error_msg}")
        return None
    except requests.exceptions.RequestException as e:
        error_msg = f"Network error fetching export metadata: {e}"
        logging.error(error_msg)
        print(f"❌ {error_msg}")
        return None

def download_export_file(s3_url, filename=DEFAULT_FILENAME):
    """
    Download the export file from S3 URL.

    Args:
        s3_url (str): S3 URL of the export file
        filename (str): Local filename for the downloaded file

    Returns:
        bool: True if download successful, False otherwise

    Note:
        - Uses streaming download for large files
        - Validates download integrity
        - Handles network errors gracefully
    """
    if not s3_url:
        logging.error("No S3 URL provided for file download")
        print("❌ No S3 URL provided for file download")
        return False

    try:
        # Construct full file path
        file_path = Path(DOWNLOAD_PATH) / filename

        logging.info(f"Starting download from S3 URL: {s3_url[:50]}...")
        logging.info(f"Local file path: {file_path}")
        print(f"Downloading file to: {file_path}")

        # Use streaming download for large files
        with requests.get(s3_url, stream=True, timeout=REQUEST_TIMEOUT) as response:
            response.raise_for_status()  # Raise exception for HTTP errors

            # Get file size for progress tracking
            total_size = int(response.headers.get('content-length', 0))

            # Download with progress tracking
            downloaded_size = 0
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)

                        # Log progress for large files
                        if total_size > 0:
                            progress = (downloaded_size / total_size) * 100
                            if downloaded_size % (1024 * 1024) == 0:  # Every MB
                                logging.info(f"Download progress: {progress:.1f}% ({downloaded_size / (1024*1024):.1f} MB)")

            # Verify file was downloaded
            if file_path.exists():
                actual_size = file_path.stat().st_size
                logging.info(f"Download completed. File size: {actual_size:,} bytes")

                if total_size > 0 and actual_size != total_size:
                    logging.warning(f"File size mismatch. Expected: {total_size:,} bytes, Actual: {actual_size:,} bytes")
                    print(f"⚠ File size mismatch. Expected: {total_size:,} bytes, Actual: {actual_size:,} bytes")
                else:
                    print(f"✓ File downloaded successfully ({actual_size:,} bytes)")
                    return True
            else:
                logging.error("Downloaded file not found on disk")
                print("❌ Downloaded file not found on disk")
                return False

    except requests.exceptions.Timeout:
        error_msg = f"Download timeout after {REQUEST_TIMEOUT} seconds"
        logging.error(error_msg)
        print(f"❌ {error_msg}")
        return False
    except requests.exceptions.RequestException as e:
        error_msg = f"Network error during download: {e}"
        logging.error(error_msg)
        print(f"❌ {error_msg}")
        return False
    except Exception as e:
        error_msg = f"Error during file download: {e}"
        logging.error(error_msg)
        print(f"❌ {error_msg}")
        return False

def determine_file_extension(metadata):
    """
    Determine the appropriate file extension based on export metadata.

    Args:
        metadata (dict): Export metadata from Freshdesk API

    Returns:
        str: File extension (e.g., '.csv', '.xlsx')
    """
    if not metadata or "export" not in metadata:
        return ".csv"  # Default fallback

    export_info = metadata["export"]
    file_format = export_info.get("file_format", "").lower()

    # Map Freshdesk format names to file extensions
    format_mapping = {
        "csv": ".csv",
        "excel": ".xlsx",
        "json": ".json",
        "xml": ".xml"
    }

    return format_mapping.get(file_format, ".csv")

def generate_filename(metadata, base_name=DEFAULT_FILENAME):
    """
    Generate a descriptive filename based on export metadata.

    Args:
        metadata (dict): Export metadata from Freshdesk API
        base_name (str): Base filename if metadata doesn't provide one

    Returns:
        str: Generated filename with appropriate extension
    """
    if not metadata or "export" not in metadata:
        return base_name

    export_info = metadata["export"]

    # Try to get filename from metadata
    metadata_filename = export_info.get("filename")
    if metadata_filename:
        return metadata_filename

    # Generate filename based on export type and timestamp
    export_type = export_info.get("export_type", "data")
    timestamp = time.strftime("%Y%m%d_%H%M%S")

    # Get file extension
    extension = determine_file_extension(metadata)

    return f"freshdesk_{export_type}_export_{timestamp}{extension}"

def cleanup_failed_downloads():
    """
    Clean up any partially downloaded files from failed attempts.

    Note:
        - Removes files that may be incomplete or corrupted
        - Helps prevent confusion with partial downloads
    """
    try:
        download_dir = Path(DOWNLOAD_PATH)

        # Look for common temporary/partial file patterns
        cleanup_patterns = [
            "*.tmp",
            "*.part",
            "freshdesk_export_*_incomplete*"
        ]

        cleaned_count = 0
        for pattern in cleanup_patterns:
            for file_path in download_dir.glob(pattern):
                try:
                    file_path.unlink()
                    logging.info(f"Cleaned up partial file: {file_path}")
                    cleaned_count += 1
                except Exception as e:
                    logging.warning(f"Could not clean up {file_path}: {e}")

        if cleaned_count > 0:
            print(f"✓ Cleaned up {cleaned_count} partial download(s)")

    except Exception as e:
        logging.warning(f"Error during cleanup: {e}")

def main():
    """
    Main function to orchestrate the entire export download process.
    """
    print("Freshdesk Data Export Download Tool")
    print("=" * 60)

    logging.info("Starting Freshdesk Data Export Download Tool")
    logging.info(f"Export UUID: {EXPORT_UUID}")
    logging.info(f"Download path: {DOWNLOAD_PATH}")

    # Validate configuration
    if not validate_configuration():
        print("❌ Configuration validation failed. Please check your settings.")
        logging.error("Configuration validation failed.")
        return 1

    # Ensure download directory exists and is writable
    if not ensure_download_directory():
        print("❌ Download directory validation failed.")
        logging.error("Download directory validation failed.")
        return 1

    # Clean up any failed downloads from previous runs
    cleanup_failed_downloads()

    try:
        # Step 1: Get export metadata
        print("\nStep 1: Retrieving export metadata...")
        metadata = get_export_metadata()

        if not metadata:
            print("❌ Failed to retrieve export metadata.")
            return 1

        # Step 2: Extract S3 URL and generate filename
        if "export" not in metadata or "url" not in metadata["export"]:
            print("❌ Export metadata missing file URL.")
            logging.error("Export metadata missing file URL")
            return 1

        s3_url = metadata["export"]["url"]
        filename = generate_filename(metadata)

        # Step 3: Download the file
        print("
Step 2: Downloading export file...")
        success = download_export_file(s3_url, filename)

        if success:
            # Success summary
            file_path = Path(DOWNLOAD_PATH) / filename
            file_size = file_path.stat().st_size

            print("\n" + "=" * 60)
            print("DOWNLOAD SUMMARY")
            print("=" * 60)
            print(f"✓ Download completed successfully!")
            print(f"  Export UUID: {EXPORT_UUID}")
            print(f"  Downloaded file: {filename}")
            print(f"  File size: {file_size:,} bytes ({file_size / (1024*1024):.2f} MB)")
            print(f"  Download location: {file_path}")
            print(f"  Log file: {LOG_FILENAME}")

            logging.info("=" * 60)
            logging.info("DOWNLOAD COMPLETED SUCCESSFULLY")
            logging.info("=" * 60)
            logging.info(f"Downloaded file: {filename}")
            logging.info(f"File size: {file_size:,} bytes")
            logging.info(f"Download location: {file_path}")
            logging.info("=" * 60)

            return 0
        else:
            print("❌ Download failed. Check logs for details.")
            return 1

    except KeyboardInterrupt:
        print("\n⚠ Download interrupted by user")
        logging.info("Download interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error during download: {e}")
        logging.error(f"Unexpected error during download: {e}")
        return 1

# Run the script if executed directly
if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

