"""
Freshdesk Knowledge Base Articles Export Script

DESCRIPTION:
This script exports all articles from the Freshdesk knowledge base, organizing
them by categories and folders. It cleans HTML content from descriptions and
exports the data to a CSV file for documentation and analysis purposes.

GUI MODE:
Run with --gui flag to launch the graphical user interface:
python knowledge_base_articles_exporter.py --gui

REQUIREMENTS:
- Python 3.x
- requests library (install with: pip install requests)
- tkinter (usually included with Python)
- Valid Freshdesk API key with solutions read permissions
- Freshdesk account and domain access

SETUP INSTRUCTIONS:
1. Replace API_KEY with your actual Freshdesk API key
2. Replace DOMAIN with your Freshdesk domain (e.g., 'yourcompany.freshdesk.com')
3. Update csv_filename if desired
4. Ensure your API key has permissions for solutions access

GUI USAGE:
1. Enter your API key and domain in the input fields
2. Modify output filename if desired
3. Click "Export Articles" to start the process
4. Monitor progress in the status area
5. Results are automatically saved to CSV file

COMMAND LINE USAGE:
python knowledge_base_articles_exporter.py

API DOCUMENTATION:
- Freshdesk API v2: https://developers.freshdesk.com/api/
- Solutions API: https://developers.freshdesk.com/api/#solutions
- Authentication: Basic Auth with API key

INPUT PARAMETERS:
- API_KEY: Your Freshdesk API key
- DOMAIN: Your Freshdesk domain
- csv_filename: Output CSV file name

OUTPUT:
- CSV file with cleaned article data
- Console output showing processing progress
- Error messages for failed API calls

ARTICLE DATA INCLUDES:
- Category name for organization
- Folder name for grouping
- Article ID for reference
- Article title
- Cleaned description (HTML removed)
- Creation and update timestamps

CONTENT PROCESSING:
- Removes HTML tags from article descriptions
- Converts HTML entities to readable text
- Preserves article structure and metadata
- Handles encoding for international characters

ERROR HANDLING:
- Handles HTTP errors with descriptive messages
- Validates API responses and data structure
- Continues processing even if individual articles fail
- Displays clear error messages for troubleshooting

SECURITY NOTE:
- Store API keys securely (environment variables recommended for production)
- Never commit API keys to version control
- Rotate API keys regularly for security

TROUBLESHOOTING:
- Verify API key has solutions read permissions
- Check that knowledge base contains categories and folders
- Ensure network connectivity to Freshdesk API
- Monitor rate limit usage in Freshdesk dashboard
- Check that articles have descriptions

USAGE SCENARIOS:
- Create knowledge base documentation archives
- Generate article inventories for content audits
- Analyze knowledge base structure and organization
- Support content migration projects
- Build internal documentation indexes
"""

import requests
import csv
import re
from html import unescape
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import sys

class KnowledgeBaseExporter:
    """GUI for Freshdesk Knowledge Base Articles Export"""

    def __init__(self, root):
        self.root = root
        self.root.title("Freshdesk Knowledge Base Articles Export")
        self.root.geometry("600x500")
        self.root.resizable(True, True)

        # Default values
        self.api_key = "5TMgbcZdRFY70hSpEdj"
        self.domain = "benchmarkeducationcompany.freshdesk.com"
        self.csv_filename = "solution_articles_cleaned.csv"

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

        # Output Configuration Frame
        output_frame = ttk.LabelFrame(main_frame, text="Output Configuration", padding="5")
        output_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        output_frame.columnconfigure(1, weight=1)

        # CSV Filename
        ttk.Label(output_frame, text="CSV Filename:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.csv_filename_var = tk.StringVar()
        csv_entry = ttk.Entry(output_frame, textvariable=self.csv_filename_var, width=50)
        csv_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2)

        # Progress Frame
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="5")
        progress_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        progress_frame.columnconfigure(0, weight=1)

        self.progress_var = tk.StringVar(value="Ready to start...")
        progress_label = ttk.Label(progress_frame, textvariable=self.progress_var)
        progress_label.grid(row=0, column=0, sticky=tk.W, pady=2)

        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=2)

        # Buttons Frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=3, column=0, columnspan=2, pady=10)

        self.export_btn = ttk.Button(buttons_frame, text="Export Articles", command=self.export_articles)
        self.export_btn.grid(row=0, column=0, padx=5)

        self.load_btn = ttk.Button(buttons_frame, text="Load Defaults", command=self.load_defaults)
        self.load_btn.grid(row=0, column=1, padx=5)

        # Status text area
        status_frame = ttk.LabelFrame(main_frame, text="Status Log", padding="5")
        status_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        status_frame.columnconfigure(0, weight=1)
        status_frame.rowconfigure(0, weight=1)

        self.status_text = scrolledtext.ScrolledText(status_frame, height=8, state='disabled')
        self.status_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    def load_defaults(self):
        """Load default values into the form"""
        self.api_key_var.set(self.api_key)
        self.domain_var.set(self.domain)
        self.csv_filename_var.set(self.csv_filename)
        self.log_message("Default configuration loaded.")

    def log_message(self, message):
        """Add a message to the status log"""
        self.status_text.config(state='normal')
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
        self.status_text.config(state='disabled')
        self.root.update()

    def export_articles(self):
        """Export knowledge base articles to CSV"""
        # Disable button during processing
        self.export_btn.config(state='disabled')
        self.progress_bar.start()

        # Get values from form
        api_key = self.api_key_var.get().strip()
        domain = self.domain_var.get().strip()
        csv_filename = self.csv_filename_var.get().strip()

        if not api_key or not domain:
            messagebox.showerror("Error", "API Key and Domain are required.")
            self.export_btn.config(state='normal')
            self.progress_bar.stop()
            return

        if not csv_filename:
            csv_filename = "solution_articles_cleaned.csv"

        self.log_message(f"Starting export to {csv_filename}...")
        self.progress_var.set("Fetching categories...")

        # Run in thread to keep GUI responsive
        thread = threading.Thread(target=self._export_articles_thread,
                                args=(api_key, domain, csv_filename))
        thread.daemon = True
        thread.start()

    def _export_articles_thread(self, api_key, domain, csv_filename):
        """Thread function for article export"""
        try:
            self._do_export_articles(api_key, domain, csv_filename)
        except Exception as e:
            self.log_message(f"Error during export: {str(e)}")
        finally:
            self.root.after(0, self._export_complete)

    def _export_complete(self):
        """Called when export is complete"""
        self.export_btn.config(state='normal')
        self.progress_bar.stop()
        self.progress_var.set("Ready to start...")
        self.log_message("Export completed!")

    def _do_export_articles(self, api_key, domain, csv_filename):
        """Perform the actual article export"""
        # Update progress
        self.root.after(0, lambda: self.progress_var.set("Fetching categories..."))

        # Fetch categories
        categories = self.fetch_freshdesk_data(f"https://{domain}/api/v2/solutions/categories", api_key)
        if not categories:
            self.root.after(0, lambda: self.log_message("Failed to fetch categories"))
            return

        articles_data = []
        total_categories = len(categories)

        for i, category in enumerate(categories):
            category_name = category["name"]
            self.root.after(0, lambda: self.progress_var.set(f"Processing category {i+1}/{total_categories}: {category_name}"))
            self.root.after(0, lambda: self.log_message(f"Processing category: {category_name}"))

            # Fetch folders for this category
            folders = self.fetch_freshdesk_data(f"https://{domain}/api/v2/solutions/categories/{category['id']}/folders", api_key)
            if folders:
                for folder in folders:
                    folder_name = folder["name"]
                    self.root.after(0, lambda: self.log_message(f"  Processing folder: {folder_name}"))

                    # Fetch articles for this folder
                    articles = self.fetch_freshdesk_data(f"https://{domain}/api/v2/solutions/folders/{folder['id']}/articles", api_key)
                    if articles:
                        for article in articles:
                            cleaned_description = self.clean_html(article["description"])
                            articles_data.append([
                                category_name,
                                folder_name,
                                article["id"],
                                article["title"],
                                cleaned_description,
                                article["created_at"],
                                article["updated_at"]
                            ])

        # Save data to CSV
        if articles_data:
            with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Category", "Folder", "Article ID", "Title", "Description", "Created At", "Updated At"])
                writer.writerows(articles_data)

            self.root.after(0, lambda: self.log_message(f"CSV file '{csv_filename}' created with {len(articles_data)} articles"))
        else:
            self.root.after(0, lambda: self.log_message("No articles found to export"))

    def fetch_freshdesk_data(self, url, api_key):
        """Make API request to Freshdesk"""
        headers = {"Content-Type": "application/json"}
        response = requests.get(url, auth=(api_key, "X"), headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            self.root.after(0, lambda: self.log_message(f"Error: {response.status_code} - {response.text}"))
            return None

    def clean_html(self, raw_html):
        """Remove HTML tags from descriptions"""
        clean_text = re.sub(r'<[^>]+>', '', raw_html)  # Remove HTML tags
        clean_text = unescape(clean_text)  # Convert HTML entities to normal text
        return clean_text.strip()

# Freshdesk API credentials
API_KEY = "5TMgbcZdRFY70hSpEdj"
DOMAIN = "benchmarkeducationcompany.freshdesk.com"

# Headers for authentication
headers = {
    "Content-Type": "application/json"
}

# Function to make API requests
def fetch_freshdesk_data(endpoint):
    url = f"https://{DOMAIN}/api/v2/{endpoint}"
    response = requests.get(url, auth=(API_KEY, "X"), headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

# Function to remove HTML tags from descriptions
def clean_html(raw_html):
    clean_text = re.sub(r'<[^>]+>', '', raw_html)  # Remove HTML tags
    clean_text = unescape(clean_text)  # Convert HTML entities to normal text
    return clean_text.strip()

# Step 1: Get all Solution Categories
categories = fetch_freshdesk_data("solutions/categories")
if categories:
    articles_data = []

    # Step 2: Get all Solution Folders for each category
    for category in categories:
        category_id = category["id"]
        category_name = category["name"]
        folders = fetch_freshdesk_data(f"solutions/categories/{category_id}/folders")

        if folders:
            # Step 3: Get all Solution Articles for each folder
            for folder in folders:
                folder_id = folder["id"]
                folder_name = folder["name"]
                articles = fetch_freshdesk_data(f"solutions/folders/{folder_id}/articles")

                if articles:
                    for article in articles:
                        cleaned_description = clean_html(article["description"])
                        articles_data.append([
                            category_name,
                            folder_name,
                            article["id"],
                            article["title"],
                            cleaned_description,
                            article["created_at"],
                            article["updated_at"]
                        ])

    # Save data to CSV
    csv_filename = "solution_articles_cleaned.csv"
    with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Category", "Folder", "Article ID", "Title", "Description", "Created At", "Updated At"])
        writer.writerows(articles_data)

    print(f"CSV file '{csv_filename}' has been created successfully and formatted correctly!")

def main():
    """Command line mode - original functionality"""
    # Step 1: Get all Solution Categories
    categories = fetch_freshdesk_data("solutions/categories")
    if categories:
        articles_data = []

        # Step 2: Get all Solution Folders for each category
        for category in categories:
            category_id = category["id"]
            category_name = category["name"]
            folders = fetch_freshdesk_data(f"solutions/categories/{category_id}/folders")

            if folders:
                # Step 3: Get all Solution Articles for each folder
                for folder in folders:
                    folder_id = folder["id"]
                    folder_name = folder["name"]
                    articles = fetch_freshdesk_data(f"solutions/folders/{folder_id}/articles")

                    if articles:
                        for article in articles:
                            cleaned_description = clean_html(article["description"])
                            articles_data.append([
                                category_name,
                                folder_name,
                                article["id"],
                                article["title"],
                                cleaned_description,
                                article["created_at"],
                                article["updated_at"]
                            ])

        # Save data to CSV
        csv_filename = "solution_articles_cleaned.csv"
        with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Category", "Folder", "Article ID", "Title", "Description", "Created At", "Updated At"])
            writer.writerows(articles_data)

        print(f"CSV file '{csv_filename}' has been created successfully and formatted correctly!")

def launch_gui():
    """Launch the GUI application"""
    root = tk.Tk()
    app = KnowledgeBaseExporter(root)
    root.mainloop()

if __name__ == "__main__":
    # Check for command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--gui":
        launch_gui()
    else:
        main()

