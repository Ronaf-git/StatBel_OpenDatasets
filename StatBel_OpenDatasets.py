# ----------------------------------------------------
# -- Projet : StatBel_OpenDatasets
# -- Author : Ronaf - https://github.com/Ronaf-git
# -- Created : 06/12/2024
# -- Usage : Get All Datasets existing in StatBel
#            https://statbel.fgov.be/en/statistics/bestat/faq
#            https://statbel.fgov.be/en/open-data/consumer-price-index-and-health-index
# -- Update : 
# --  
# ----------------------------------------------------
# --- Install/Create Exe
#pyinstaller --onefile --noconsole StatBel_OpenDatasets.py

# ===============================================================
# INIT Variables
# ===============================================================
API_URL = "https://bestat.statbel.fgov.be/bestat/api"  
VALID_EXPORTERS = ['XML','JSON','CSV','XLS','HTML','PDF']
VALID_LANGUAGES = ['fr','en','nl','de']

# ===============================================================
# Imports
# ===============================================================
from datetime import datetime
import requests
import logging
import urllib.request
import logging
import sys
import os
import time
from requests.exceptions import ConnectionError, Timeout
from tkinter import  ttk,messagebox
import tkinter as tk
# ===============================================================
# Functions
# ===============================================================
def sanitize_filename(filename):
    """
    Sanitizes a filename by replacing invalid characters with underscores.

    This function ensures the filename is safe for use on a Windows file system 
    by replacing characters that are not allowed in Windows filenames with underscores.
    The invalid characters include: 
    '<', '>', ':', '"', '/', '\\', '|', '?', and '*'.

    Args:
        filename (str): The original filename to be sanitized.

    Returns:
        str: The sanitized filename with invalid characters replaced by underscores.
    
    Example:
        >>> sanitize_filename("my:file|name?.txt")
        "my_file_name_.txt"
    """
    # Define a list of characters to be replaced
    invalid_chars = r'<>:"/\\|?*'  # These are illegal characters in Windows filenames
    sanitized_filename = filename

    # Replace invalid characters
    for char in invalid_chars:
        sanitized_filename = sanitized_filename.replace(char, '_')    
    return sanitized_filename

def fetch_data_with_retry(url, retries=5, delay=3):
    attempt = 0
    while attempt < retries:
        try:
            response = requests.get(url, timeout=10)  
            response.raise_for_status() 
            return response.json()  # Assuming JSON response
        except ConnectionError as e:
            logging.error(f"ConnectionError: {e}. Retrying in {delay} seconds...")
        except Timeout as e:
            logging.error(f"TimeoutError: {e}. Retrying in {delay} seconds...")
        except requests.exceptions.HTTPError as e:
            logging.error(f"HTTPError: {e}. Response code: {e.response.status_code}")
            break
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            break
        
        time.sleep(delay)  
        attempt += 1

    logging.error("Max retries reached. Could not fetch the data.")
    return None

# Function to get the file path (works for both Python script and compiled executable)
def get_file_path(file_name):
    """
    Fetch data from a given URL with retry logic in case of network-related errors.

    This function attempts to retrieve data from the specified URL using the `requests.get` method.
    If the request fails due to a connection error, timeout, or any other exception, it will retry 
    the request up to the specified number of retries, with a delay between each attempt.

    Parameters:
    - url (str): The URL from which to fetch data.
    - retries (int, optional): The maximum number of retry attempts (default is 5).
    - delay (int, optional): The delay in seconds between each retry attempt (default is 3).

    Returns:
    - dict: The parsed JSON response from the server if the request is successful.
    - None: If the request fails after the maximum number of retries or if an HTTP error occurs.

    Raises:
    - None: All exceptions are handled internally, and None is returned in case of failure.

    Logs:
    - Logs error messages for each failed attempt and when the retry limit is reached.
    """
    # If running from a bundled exe, the file will be in same folder as the exe
    if getattr(sys, 'frozen', False):
        # Running as a bundled exe, get the path to the directory of the exe
        exe_dir = os.path.dirname(sys.executable)
        return os.path.join(exe_dir, file_name)
    else:
        # Running as a Python script
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), file_name)    


def write_json_to_txt(txtfile, json,header):
    """
    Writes the contents of a JSON-like structure to a text file with a specified format.

    Args:
        json_data (list of dict): A list of dictionaries containing the data to be written.
        txtfile (file-like object): The text file object where the data will be written.
        header (str): A header string to display at the beginning of each section.

    The function processes each dictionary in the input `json_data` list and writes its keys and values 
    into the provided `txtfile`. If a value is itself a dictionary (nested dictionary), its keys and 
    values are indented and written accordingly. A separator line (`"-" * 50`) is written after each dictionary 
    to clearly separate entries. The header is written at the beginning of each entry.

    Example:
        json_data = [
            {'name': 'Alice', 'age': 30, 'address': {'city': 'New York', 'zipcode': '10001'}},
            {'name': 'Bob', 'age': 25, 'address': {'city': 'Los Angeles', 'zipcode': '90001'}}
        ]
        with open('output.txt', 'w') as file:
            write_json_to_txt(json_data, file, 'User Information')
    """
    # Based on json datas
    for data in json:
        txtfile.write(f"--- {header} ---\n")
        for key, value in data.items():
            if isinstance(value, dict):  # If the value is a nested dictionary
                txtfile.write(f"{key}:\n")
                for subkey, subvalue in value.items():
                    txtfile.write(f"    {subkey}: {subvalue}\n")
            else:
                txtfile.write(f"{key}: {value}\n")
        txtfile.write("-" * 50 + "\n")

def create_metadata() :
    # --- Create medatata.txt to inform users
    Metadata_path = os.path.join(outputFolder,'metadata.txt')
    with open(Metadata_path, 'w') as file:
        write_json_to_txt(file, datasources,'Datasource')
        write_json_to_txt(file, views,'View')
    metadata_lb.config(text=f"Export done ! See {Metadata_path}")

def create_linked_views_metadata() :
    Metadata_path = os.path.join(outputFolder,'linked_views.txt')
    with open(Metadata_path, 'w') as file:
        # Link views to the corresponding data sources and write to the file
        for data_source in datasources:
            # Find all views that are linked to the current data source
            linked_views = [view for view in views if view["dataSourceId"] == data_source["id"]]
            
            # Write the data source and its linked views to the file
            file.write(f"Data Source ID: {data_source['id']}\n")
            file.write(f"Data Source Name: {data_source['name']}\n")
            file.write("Linked Views:\n")
            
            if linked_views:
                for view in linked_views:
                    file.write(f"  - View ID: {view['id']}, View Name: {view['name']}\n")
            else:
                file.write("  No linked views.\n")
            
            file.write("===================================\n")
    metadatalk_lb.config(text=f"Results have been written to {Metadata_path}")


def export_views() :
    # Function to print selected exporters and languages
    # Get selected values
    selected_exporters = [VALID_EXPORTERS[i] for i, var in enumerate(exporter_vars) if var.get()]
    selected_languages = [VALID_LANGUAGES[i] for i, var in enumerate(lang_vars) if var.get()]
    selected_view =  [views_listbox.get(i) for i in views_listbox.curselection()]

    # check if a format is selected
    if not selected_exporters :
        export_progress_bar_lb.config(text=f"Please select format")
        return

    # If selected_view is not empty, filter filtered_views by the selected_view values
    if selected_view:
        filtered_views = [view for view in views if view['name'] in selected_view]
    else :
        # Filter views by the selected languages
        filtered_views = [view for view in views if view['locale'] in selected_languages]
    # Calculate the total number of views to process
    total_items = len(filtered_views) * len(selected_exporters)
    processed_items = 0
    start_time = datetime.now()

    # Init progressBar
    expected_duration = total_items * 1
    export_progress_bar_lb.config(text=f"Exporting {total_items} files. Expected duration : {expected_duration//3600} hour(s), {(expected_duration%3600)//60} min, {expected_duration%60} sec") 
    export_progress_bar['value'] = 0  # Reset the progress bar
    root.update_idletasks()  # Update the window

    error_occurred = False  # Flag to check if any error occurred
    # --- Iterate through each dataset and export it
    for exporter in selected_exporters :
        # Create a folder for each exporter if it doesn't exist
        exporter_folder = os.path.join(outputFolder,exporter)
        os.makedirs(exporter_folder, exist_ok=True)
        for view in filtered_views:
            # - Export Dataset in multiple formats
            id = view['id']
            name = sanitize_filename(view['name'])
            url = f"{API_URL}/views/{id}/result/{exporter}"
            local_filename = os.path.join(exporter_folder, f"{name}.{exporter}")
            # Download and save the file
            # Try to download and save the file, continue on error
            try:
                urllib.request.urlretrieve(url, local_filename)
                #print(f"File successfully saved to {local_filename}")
            except Exception as e:
                # Log the error
                logging.error(f"Error downloading {url}: {e}")
                error_occurred = True
                continue  # Continue with the next exporter

            
            # Update Progressbar
            processed_items += 1
            progress_percentage = (processed_items / total_items) * 100
            export_progress_bar['value'] = progress_percentage
            root.update_idletasks()  # Update the window to reflect the changes

    duration = datetime.now() - start_time
    # Ensure progress bar reaches 100% at the end. When errors, it doesn't reach 100%, it's why we force it
    export_progress_bar['value'] = 100
    root.update_idletasks()  # Make sure the GUI reflects the final update

    # Update progress label based on whether an error occurred
    if error_occurred:
        export_progress_bar_lb.config(text=f"Export Done with errors! Duration: {duration.days*24 + duration.seconds//3600} hour(s), {(duration.seconds//60)%60} min, {duration.seconds%60} sec. Check 'export_errors.log' for details.")
    else:
        export_progress_bar_lb.config(text=f"Export Done! Duration: {duration.days*24 + duration.seconds//3600} hour(s), {(duration.seconds//60)%60} min, {duration.seconds%60} sec")

def export_all_views() :
    # --- Iterate through each dataset and export it
    for exporter in VALID_EXPORTERS :
        # Create a folder for each exporter if it doesn't exist
        exporter_folder = os.path.join(outputFolder,exporter)
        os.makedirs(exporter_folder, exist_ok=True)
        for view in views:
            # - Export Dataset in multiple formats
            id = view['id']
            name = sanitize_filename(view['name'])
            url = f"{API_URL}/views/{id}/result/{exporter}"
            local_filename = os.path.join(exporter_folder, f"{name}.{exporter}")
            # Download and save the file
            # Try to download and save the file, continue on error
            try:
                urllib.request.urlretrieve(url, local_filename)
                #print(f"File successfully saved to {local_filename}")
            except Exception as e:
                # Log the error
                logging.error(f"Error downloading {url}: {e}")
                continue  # Continue with the next exporter

def update_views_listbox():
    # Clear the current items in the Listbox
    views_listbox.delete(0, tk.END)
    # Get selected values
    selected_languages = [VALID_LANGUAGES[i] for i, var in enumerate(lang_vars) if var.get()]
    # Filter views by the selected languages
    filtered_views = [view for view in views if view['locale'] in selected_languages]
    # Sort the filtered views alphabetically by 'name'
    sorted_filtered_views = sorted(filtered_views, key=lambda view: view['name'].lower())
    for item in sorted_filtered_views:
        views_listbox.insert(tk.END, item['name'])

# Function to show the popup and stop the script
def show_error_and_exit(message):
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    messagebox.showerror("Error", message)
    sys.exit(1)  # Stop the script
        
# ===============================================================
# Init script : Create Output and get api json
# ===============================================================
# -- Create Output folder
outputFolder = get_file_path("Output")
os.makedirs(outputFolder, exist_ok=True)
# -- Setup logging configuration
log_file = os.path.join(outputFolder, 'export_errors.log')
logging.basicConfig(filename=log_file, level=logging.ERROR, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
# --- Send a GET request to fetch the raw JSON data with all views (to get ids)
# Datasource are not exportable. Views are. Each views is linked, via ID, to a datasource
datasources = fetch_data_with_retry(f"{API_URL}/datasources")
views = fetch_data_with_retry(f"{API_URL}/views")
# if cannont get data : stop script
if datasources is None or views is None:
    show_error_and_exit(f"Datasources or Views data is missing. Please check the logfile ({outputFolder})")

# ===============================================================
# Init Window
# ===============================================================
root = tk.Tk()
root.title("StatBel_OpenDatasets")
root.state('zoomed')  # This will maximize the window
# Set the window to fullscreen
#root.attributes('-fullscreen', True)
#root.bind("<Escape>", lambda event: root.attributes('-fullscreen', False))
# Create a Notebook widget
notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True)
style = ttk.Style()
style.configure(
    'TNotebook.Tab',
    font=('Arial', 16, 'bold'),
    padding=(20, 10),
    borderwidth=21,
    relief='solid',
    background='lightblue',
    foreground='black',
    highlightthickness=10,
    highlightcolor='red',
    highlightbackground='gray'
)

# ===============================================================
# Tab 0 : ReadMe/About
# ===============================================================
# Create my tab
tab0 = ttk.Frame(notebook)
notebook.add(tab0, text='About' )

# Adding a Text widget to ReadMe_frame
text_widget_tab0 = tk.Text(tab0, wrap='word' , bg=style.lookup("TFrame", "background"), fg='Black', bd=0)
# Text
Text_tab0 = """
    StatBel Open Datasets Tool

    This tool allows you to retrieve and export datasets from the Belgian Statistical Office's StatBel API in various formats.

    Key Features:
    - Export Metadata: Retrieve information about available datasets.
    - Export All Views: Download all datasets (all languages) in selected formats (XML, JSON, CSV, XLS, HTML, PDF).
    - Export Specific Views: 
        Filtered by Language: French, English, Dutch, or German.
        Individually selected.
        In selected format.

    Usage:
    1. Export Metadata: Click "Export Metadata" to generate a text file with dataset information.
    2. Export Views: In the "Export Views" tab, select formats and languages, then click "Export Views" to download your data.

    Author: Ronaf-Git
    For more information, visit: https://github.com/Ronaf-git/StatBel_OpenDatasets
"""
text_widget_tab0.insert(tk.END,Text_tab0) 
# Set the Text widget to "disabled" to make it unwritable
text_widget_tab0.config(state=tk.DISABLED)
text_widget_tab0.bind("<FocusIn>", lambda e: text_widget_tab0.config(state=tk.DISABLED))
# pack it
text_widget_tab0.pack(fill="both", expand=True)


# ==============================================================================================================================
# Tab 1 : Get Metadatas
# ==============================================================================================================================
# Create Tab
tab1 = ttk.Frame(notebook)
notebook.add(tab1, text='Metadata' )
# --- metadata : button and label
# Create Button 
metadata_bt = tk.Button(tab1, text="Export metadata", command=create_metadata)
metadata_bt.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
# Create Label 
metadata_lb = tk.Label(tab1, text="Export metadata (Datasources and views) in a texte file", font=("Helvetica", 14, "bold"))
metadata_lb.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)

# --- relationnal link between datasources and views : button and label
# Create Button 
metadatalk_bt = tk.Button(tab1, text="Export relationnal metadata", command=create_linked_views_metadata)
metadatalk_bt.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)
# Create Label 
metadatalk_lb = tk.Label(tab1, text="Show relations between datasources and views", font=("Helvetica", 14, "bold"))
metadatalk_lb.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)

# ===============================================================================================================
# Tab 2 : All datas
# ===============================================================================================================
tab2 = ttk.Frame(notebook)
notebook.add(tab2, text='Export All Views')

# --- export ALL views : button and label
# Create Button 
export_all_bt = tk.Button(tab2, text="Export ALL views", command=create_metadata)
export_all_bt.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)
# Create Label 
export_all_lb = tk.Label(tab2, text="Export all views (all languages/format). Will be long.", font=("Helvetica", 14, "bold"))
export_all_lb.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)

# ===============================================================================================================
# Tab 3 : dédicated Views
# ===============================================================================================================
# --- Create Tab
tab3 = ttk.Frame(notebook)
notebook.add(tab3, text='Export selected views')

# Configure the grid to allow widgets to expand properly
for i in range(20):
    tab3.grid_rowconfigure(i, weight=1)
for i in range(0):
    tab3.grid_columnconfigure(i, weight=1)

# --- Exporters : Checkbuttons and label
# Create Label
exporters_lb = tk.Label(tab3, text="Format selector", font=("Helvetica", 14, "bold"))
exporters_lb.grid(row=0, column=2, sticky="nsew", padx=10, pady=5)
# Frame to contain all Exporter Checkbuttons (for horizontal layout)
exporters_frame = tk.Frame(tab3)
exporters_frame.grid(row=1, column=2, sticky="nsew", padx=10, pady=5)
# Variables to track selected exporters
exporter_vars = []
for item in VALID_EXPORTERS:
    exporter_vars.append(tk.BooleanVar(value=False))  # Each variable tracks if it's selected
# Create Checkbuttons for each exporter inside the exporters_frame (horizontal layout)
for idx, (item, var) in enumerate(zip(VALID_EXPORTERS, exporter_vars)):
    cb = tk.Checkbutton(exporters_frame, text=item, variable=var, font=("Helvetica", 12))
    cb.grid(row=0, column=idx, sticky="w", padx=10, pady=5)  # All checkbuttons in row 0, columns 0,1,2...

# --- Lang : Checkbuttons and label
# Create Label
Lang_lb = tk.Label(tab3, text="Language selector", font=("Helvetica", 14, "bold"))
Lang_lb.grid(row=2, column=2, sticky="nsew", padx=10, pady=5)
# Frame to contain all Language Checkbuttons (for horizontal layout)
lang_frame = tk.Frame(tab3)
lang_frame.grid(row=3, column=2, sticky="nsew", padx=10, pady=5)
# Variables to track selected languages
lang_vars = []
for item in VALID_LANGUAGES:
    lang_vars.append(tk.BooleanVar(value=False))  # Each variable tracks if it's selected
# Create Checkbuttons for each language inside the lang_frame (horizontal layout)
for idx, (item, var) in enumerate(zip(VALID_LANGUAGES, lang_vars)):
    cb = tk.Checkbutton(lang_frame, text=item, variable=var, font=("Helvetica", 12), command=update_views_listbox)
    cb.grid(row=0, column=idx, sticky="w", padx=10, pady=5)  # All checkbuttons in row 0, columns 0,1,2...


# --- dedicated views : listbow and label
# Create Label
views_lb = tk.Label(tab3, text="Views selector - Will restrain the export to these views", font=("Helvetica", 14, "bold"))
views_lb.grid(row=4, column=2, sticky="nsew", padx=10, pady=5)
# Create a Frame to contain both the Listbox and Scrollbar
views_frame = tk.Frame(tab3)
views_frame.grid(row=5, column=2, padx=10, pady=10)  # Grid row 5, col 2
# Create the Listbox widget with MULTIPLE selection mode
views_listbox = tk.Listbox(views_frame, selectmode=tk.MULTIPLE, height=10, width=150)  # Set height to show only 10 items at once
# Get selected values
selected_languages = [VALID_LANGUAGES[i] for i, var in enumerate(lang_vars) if var.get()]
# Filter views by the selected languages
if selected_languages:
    filtered_views = [view for view in views if view['locale'] in selected_languages]
else :
    filtered_views = views
# Sort the filtered views alphabetically by 'name'
sorted_filtered_views = sorted(filtered_views, key=lambda view: view['name'].lower())
for item in sorted_filtered_views:
    views_listbox.insert(tk.END, item['name'])
# Create the Scrollbar widget
views_scrollbar = tk.Scrollbar(views_frame, orient=tk.VERTICAL, command=views_listbox.yview)
views_scrollbar.grid(row=0, column=1, sticky="ns")  # Place the scrollbar in column 1 of the frame
# Attach the scrollbar to the Listbox
views_listbox.config(yscrollcommand=views_scrollbar.set)
# Pack the Listbox inside the frame
views_listbox.grid(row=0, column=0, sticky="nsew")  # Make the listbox fill the frame
# Configure the frame to expand and fill the space
views_frame.grid_rowconfigure(0, weight=1)
views_frame.grid_columnconfigure(0, weight=1)

# --- export : button, label and progressbarr
# Create Button 
export_bt = tk.Button(tab3, text="Export views", command=export_views)
export_bt.grid(row=10, column=2, sticky="nsew", padx=10, pady=10)
# Create Label 
export_lb = tk.Label(tab3, text="Export all available views in selected language and format. If specific views are selected, only those will be exported.", font=("Helvetica", 14, "bold"))
export_lb.grid(row=9, column=2, sticky="nsew", padx=10, pady=5)
# ---  Progressbar
# Create the progress bar
export_progress_bar = ttk.Progressbar(tab3, length=300, mode='determinate')
export_progress_bar.grid(row=11, column=2, sticky="nsew", padx=10, pady=10)
# Create Label 
export_progress_bar_lb = tk.Label(tab3, text="ProgressBar Statut...")
export_progress_bar_lb.grid(row=12, column=2, sticky="nsew", padx=10, pady=5)


root.mainloop()