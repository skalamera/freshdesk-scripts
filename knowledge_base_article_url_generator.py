"""
Freshdesk Knowledge Base Article URL Generator

DESCRIPTION:
This script retrieves all articles from specified folders in the Freshdesk
knowledge base and generates direct URLs for each article. The results are
exported to an Excel file for easy access and reference purposes.

GUI MODE:
Run with --gui flag to launch the graphical user interface:
python knowledge_base_article_url_generator.py --gui

REQUIREMENTS:
- Python 3.x
- requests library (install with: pip install requests)
- pandas library (install with: pip install pandas)
- tkinter (usually included with Python)
- Valid Freshdesk API key with solutions read permissions
- Freshdesk account and domain access

SETUP INSTRUCTIONS:
1. Replace API_KEY with your actual Freshdesk API key
2. Replace DOMAIN with your Freshdesk domain (e.g., 'yourcompany.freshdesk.com')
3. Update folder_ids list with your folder IDs
4. Update OUTPUT_URL_PREFIX if your URL structure is different
5. Ensure your API key has permissions for solutions access

GUI USAGE:
1. Enter your API key and domain in the input fields
2. Enter folder IDs (one per line) in the text area
3. Modify output URL prefix if needed
4. Click "Generate URLs" to start the process
5. Monitor progress in the status area
6. Results are automatically saved to Article_Details.xlsx

COMMAND LINE USAGE:
python knowledge_base_article_url_generator.py

API DOCUMENTATION:
- Freshdesk API v2: https://developers.freshdesk.com/api/
- Solutions API: https://developers.freshdesk.com/api/#solutions
- Authentication: Basic Auth with API key

INPUT PARAMETERS:
- API_KEY: Your Freshdesk API key
- DOMAIN: Your Freshdesk domain
- folder_ids: List of folder IDs to process
- OUTPUT_URL_PREFIX: Base URL for article links

OUTPUT:
- Excel file with article names and direct URLs
- Console output showing processing progress
- Error messages for failed folder processing

ARTICLE DATA INCLUDES:
- Article ID from Freshdesk
- Article title/name
- Direct URL for easy access
- Processing status for each folder

ERROR HANDLING:
- Handles HTTP 404 (folder not found) errors
- Handles HTTP 429 (rate limit) errors with automatic retry
- Handles network and parsing errors
- Continues processing even if individual folders fail

RATE LIMIT HANDLING:
- Automatically detects rate limit responses (HTTP 429)
- Waits for the specified retry-after period
- Continues processing remaining folders after rate limit delay

SECURITY NOTE:
- Store API keys securely (environment variables recommended for production)
- Never commit API keys to version control
- Rotate API keys regularly for security

TROUBLESHOOTING:
- Verify API key has solutions read permissions
- Check that folder IDs are valid
- Ensure network connectivity to Freshdesk API
- Monitor rate limit usage in Freshdesk dashboard
- Check that folders contain articles

USAGE SCENARIOS:
- Generate quick reference lists for knowledge base articles
- Create documentation indexes with direct links
- Share article collections with team members
- Build internal knowledge base navigation aids
- Support content management and organization
"""

import requests
import time
import pandas as pd
import base64
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import sys
import argparse

class KnowledgeBaseURLGenerator:
    """GUI for Freshdesk Knowledge Base Article URL Generator"""

    def __init__(self, root):
        self.root = root
        self.root.title("Freshdesk Knowledge Base URL Generator")
        self.root.geometry("700x600")
        self.root.resizable(True, True)

        # Default values
        self.api_key = "5TMgbcZdRFY70hSpEdj"
        self.domain = "benchmarkeducationcompany.freshdesk.com"
        self.output_url_prefix = "https://techsupport.benchmarkeducation.com/support/solutions/articles/"
        self.default_folder_ids = """67000581069
67000578178
67000568834
67000577978
67000577979
67000577980
67000577981
67000577982
67000578171
67000578031
67000581156
67000578068
67000578069
67000578101
67000578273
67000580319
67000580615
67000581752
67000581070
67000581490
67000576038"""

        self.setup_gui()
        self.load_defaults()

    def setup_gui(self):
        """Setup the GUI components"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # API Configuration Frame
        config_frame = ttk.LabelFrame(main_frame, text="API Configuration", padding="5")
        config_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        config_frame.columnconfigure(1, weight=1)

        # API Key
        ttk.Label(config_frame, text="API Key:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.api_key_var = tk.StringVar()
        api_key_entry = ttk.Entry(config_frame, textvariable=self.api_key_var, width=50)
        api_key_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2)

        # Domain
        ttk.Label(config_frame, text="Domain:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.domain_var = tk.StringVar()
        domain_entry = ttk.Entry(config_frame, textvariable=self.domain_var, width=50)
        domain_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)

        # URL Configuration Frame
        url_frame = ttk.LabelFrame(main_frame, text="URL Configuration", padding="5")
        url_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        url_frame.columnconfigure(1, weight=1)

        # Output URL Prefix
        ttk.Label(url_frame, text="URL Prefix:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.url_prefix_var = tk.StringVar()
        url_prefix_entry = ttk.Entry(url_frame, textvariable=self.url_prefix_var, width=50)
        url_prefix_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2)

        # Folder IDs Frame
        folders_frame = ttk.LabelFrame(main_frame, text="Folder IDs (one per line)", padding="5")
        folders_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        folders_frame.columnconfigure(0, weight=1)
        folders_frame.rowconfigure(0, weight=1)

        self.folder_ids_text = scrolledtext.ScrolledText(folders_frame, height=10, width=60)
        self.folder_ids_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Progress Frame
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="5")
        progress_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        progress_frame.columnconfigure(0, weight=1)

        self.progress_var = tk.StringVar(value="Ready to start...")
        progress_label = ttk.Label(progress_frame, textvariable=self.progress_var)
        progress_label.grid(row=0, column=0, sticky=tk.W, pady=2)

        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=2)

        # Buttons Frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=4, column=0, columnspan=2, pady=10)

        self.generate_btn = ttk.Button(buttons_frame, text="Generate URLs", command=self.generate_urls)
        self.generate_btn.grid(row=0, column=0, padx=5)

        self.save_btn = ttk.Button(buttons_frame, text="Save Configuration", command=self.save_config)
        self.save_btn.grid(row=0, column=1, padx=5)

        self.load_btn = ttk.Button(buttons_frame, text="Load Defaults", command=self.load_defaults)
        self.load_btn.grid(row=0, column=2, padx=5)

        # Status text area
        status_frame = ttk.LabelFrame(main_frame, text="Status Log", padding="5")
        status_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        status_frame.columnconfigure(0, weight=1)
        status_frame.rowconfigure(0, weight=1)

        self.status_text = scrolledtext.ScrolledText(status_frame, height=8, state='disabled')
        self.status_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    def load_defaults(self):
        """Load default values into the form"""
        self.api_key_var.set(self.api_key)
        self.domain_var.set(self.domain)
        self.url_prefix_var.set(self.output_url_prefix)
        self.folder_ids_text.delete(1.0, tk.END)
        self.folder_ids_text.insert(1.0, self.default_folder_ids)
        self.log_message("Default configuration loaded.")

    def save_config(self):
        """Save current configuration (placeholder for future implementation)"""
        self.log_message("Configuration saved (feature not yet implemented).")

    def log_message(self, message):
        """Add a message to the status log"""
        self.status_text.config(state='normal')
        self.status_text.insert(tk.END, f"{time.strftime('%H:%M:%S')}: {message}\n")
        self.status_text.see(tk.END)
        self.status_text.config(state='disabled')
        self.root.update()

    def generate_urls(self):
        """Generate URLs for knowledge base articles"""
        # Disable button during processing
        self.generate_btn.config(state='disabled')
        self.progress_bar.start()

        # Get values from form
        api_key = self.api_key_var.get().strip()
        domain = self.domain_var.get().strip()
        url_prefix = self.url_prefix_var.get().strip()

        if not api_key or not domain:
            messagebox.showerror("Error", "API Key and Domain are required.")
            self.generate_btn.config(state='normal')
            self.progress_bar.stop()
            return

        # Parse folder IDs
        folder_ids_text = self.folder_ids_text.get(1.0, tk.END).strip()
        if not folder_ids_text:
            messagebox.showerror("Error", "Folder IDs are required.")
            self.generate_btn.config(state='normal')
            self.progress_bar.stop()
            return

        try:
            folder_ids = [int(fid.strip()) for fid in folder_ids_text.split('\n') if fid.strip()]
        except ValueError:
            messagebox.showerror("Error", "All folder IDs must be valid numbers.")
            self.generate_btn.config(state='normal')
            self.progress_bar.stop()
            return

        self.log_message(f"Starting URL generation for {len(folder_ids)} folders...")
        self.progress_var.set(f"Processing {len(folder_ids)} folders...")

        # Run in thread to keep GUI responsive
        thread = threading.Thread(target=self._generate_urls_thread,
                                args=(api_key, domain, url_prefix, folder_ids))
        thread.daemon = True
        thread.start()

    def _generate_urls_thread(self, api_key, domain, url_prefix, folder_ids):
        """Thread function for URL generation"""
        try:
            self._do_generate_urls(api_key, domain, url_prefix, folder_ids)
        except Exception as e:
            self.log_message(f"Error during processing: {str(e)}")
        finally:
            self.root.after(0, self._generation_complete)

    def _generation_complete(self):
        """Called when generation is complete"""
        self.generate_btn.config(state='normal')
        self.progress_bar.stop()
        self.progress_var.set("Ready to start...")
        self.log_message("URL generation completed!")

    def _do_generate_urls(self, api_key, domain, url_prefix, folder_ids):
        """Perform the actual URL generation"""
        # Encode API Key for Authentication
        encoded_api_key = base64.b64encode(f"{api_key}:X".encode("utf-8")).decode("utf-8")
        base_url = f"https://{domain}/api/v2/solutions/folders"

        article_data = []
        total_folders = len(folder_ids)

        for i, folder_id in enumerate(folder_ids):
            self.root.after(0, lambda: self.progress_var.set(f"Processing folder {i+1}/{total_folders}: {folder_id}"))
            self.root.after(0, lambda: self.log_message(f"Fetching articles for folder ID: {folder_id}"))

            articles = self.get_articles_from_folder(base_url, encoded_api_key, folder_id)

            for article in articles:
                article_id = article.get("id")
                article_name = article.get("title")
                if article_id and article_name:
                    article_url = f"{url_prefix}{article_id}"
                    article_data.append({"Article Name": article_name, "URL": article_url})

        # Save results to Excel
        if article_data:
            df = pd.DataFrame(article_data)
            output_path = "Article_Details.xlsx"
            df.to_excel(output_path, index=False)
            self.root.after(0, lambda: self.log_message(f"Data saved to {output_path}"))
            self.root.after(0, lambda: self.log_message(f"Generated {len(article_data)} article URLs"))
        else:
            self.root.after(0, lambda: self.log_message("No articles found."))

    def get_articles_from_folder(self, base_url, encoded_api_key, folder_id):
        """Retrieve all articles from a given folder ID with rate limit handling."""
        headers = {
            "Authorization": f"Basic {encoded_api_key}",
            "Content-Type": "application/json"
        }
        articles = []
        page = 1

        while True:
            try:
                response = requests.get(f"{base_url}/{folder_id}/articles", headers=headers, params={"page": page}, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    if not data:
                        break  # No more articles
                    articles.extend(data)
                    page += 1
                elif response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 1))
                    self.root.after(0, lambda: self.log_message(f"Rate limit exceeded. Retrying after {retry_after} seconds..."))
                    time.sleep(retry_after)
                elif response.status_code == 401:
                    self.root.after(0, lambda: self.log_message(f"Unauthorized access. Check API key or permissions for folder {folder_id}."))
                    break
                else:
                    self.root.after(0, lambda: self.log_message(f"Error fetching articles for folder {folder_id}: {response.status_code}"))
                    break
            except Exception as e:
                self.root.after(0, lambda: self.log_message(f"An error occurred: {e}"))
                break

        return articles

# Freshdesk API credentials and endpoint (for command line mode)
API_KEY = "5TMgbcZdRFY70hSpEdj"
DOMAIN = "benchmarkeducationcompany.freshdesk.com"
BASE_URL = f"https://{DOMAIN}/api/v2/solutions/folders"
OUTPUT_URL_PREFIX = "https://techsupport.benchmarkeducation.com/support/solutions/articles/"

# Encode API Key for Authentication
encoded_api_key = base64.b64encode(f"{API_KEY}:X".encode("utf-8")).decode("utf-8")

# Folder IDs to process
folder_ids = [
    67000581069, 67000578178, 67000568834, 67000577978, 67000577979,
    67000577980, 67000577981, 67000577982, 67000578171, 67000578031,
    67000581156, 67000578068, 67000578069, 67000578101, 67000578273,
    67000580319, 67000580615, 67000581752, 67000581070, 67000581490,
    67000576038
]

def get_articles_from_folder(folder_id):
    """Retrieve all articles from a given folder ID with rate limit handling."""
    headers = {
        "Authorization": f"Basic {encoded_api_key}",
        "Content-Type": "application/json"
    }
    articles = []
    page = 1

    while True:
        try:
            response = requests.get(f"{BASE_URL}/{folder_id}/articles", headers=headers, params={"page": page}, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if not data:
                    break  # No more articles
                articles.extend(data)
                page += 1
            elif response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 1))
                print(f"Rate limit exceeded. Retrying after {retry_after} seconds...")
                time.sleep(retry_after)
            elif response.status_code == 401:
                print(f"Unauthorized access. Check API key or permissions for folder {folder_id}.")
                break
            else:
                print(f"Error fetching articles for folder {folder_id}: {response.status_code}")
                break
        except Exception as e:
            print(f"An error occurred: {e}")
            break

    return articles

def main():
    """Command line mode - original functionality"""
    article_data = []
    for folder_id in folder_ids:
        print(f"Fetching articles for folder ID: {folder_id}")
        articles = get_articles_from_folder(folder_id)
        for article in articles:
            article_id = article.get("id")
            article_name = article.get("title")
            if article_id and article_name:
                article_url = f"{OUTPUT_URL_PREFIX}{article_id}"
                article_data.append({"Article Name": article_name, "URL": article_url})

    # Save results to Excel
    df = pd.DataFrame(article_data)
    output_path = "Article_Details.xlsx"
    df.to_excel(output_path, index=False)
    print(f"Data saved to {output_path}")

def launch_gui():
    """Launch the GUI application"""
    root = tk.Tk()
    app = KnowledgeBaseURLGenerator(root)
    root.mainloop()

if __name__ == "__main__":
    # Check for command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--gui":
        launch_gui()
    else:
        main()

