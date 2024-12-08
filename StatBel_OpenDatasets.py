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
import json
import urllib.request
import ctypes
import logging
import sys
import os
import time
from requests.exceptions import ConnectionError, Timeout
from tkinter import  ttk,filedialog, messagebox
import tkinter as tk
# ===============================================================
# Functions
# ===============================================================
def sanitize_filename(filename):
    # Define a list of characters to be replaced or removed
    invalid_chars = r'<>:"/\\|?*'  # These are illegal characters in Windows filenames
    sanitized_filename = filename

    # Replace or remove invalid characters
    for char in invalid_chars:
        sanitized_filename = sanitized_filename.replace(char, '_')  # Replace with '_'    
    return sanitized_filename

def fetch_data_with_retry(url, retries=5, delay=3):
    attempt = 0
    while attempt < retries:
        try:
            response = requests.get(url, timeout=10)  # Timeout set to 10 seconds
            response.raise_for_status()  # Will raise HTTPError for bad responses (4xx or 5xx)
            return response.json()  # Assuming JSON response
        except ConnectionError as e:
            print(f"ConnectionError: {e}. Retrying in {delay} seconds...")
        except Timeout as e:
            print(f"TimeoutError: {e}. Retrying in {delay} seconds...")
        except requests.exceptions.HTTPError as e:
            print(f"HTTPError: {e}. Response code: {e.response.status_code}")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            break
        
        time.sleep(delay)  # Wait before retrying
        attempt += 1

    print("Max retries reached. Could not fetch the data.")
    return None
# Function to get the file path (works for both Python script and compiled executable)
def get_file_path(file_name):
    # If running from a bundled exe, the file will be in same folder as the exe
    if getattr(sys, 'frozen', False):
        # Running as a bundled exe, get the path to the directory of the exe
        exe_dir = os.path.dirname(sys.executable)
        return os.path.join(exe_dir, file_name)
    else:
        # Running as a Python script
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), file_name)    

# Function to update the label and refresh the window
def update_label(text):
    label.config(text=text)
    root.update()  
# Function to close the window
def close_window():
    root.quit()

# Based on json datas
def write_json_to_txt(txtfile, json,header):
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

# Function to print selected exporters and languages
def export_views() :
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
                # Print the error and continue to the next exporter
                print(f"Error downloading {url}: {e}")
                continue  # Continue with the next exporter
            
            # Update Progressbar
            processed_items += 1
            progress_percentage = (processed_items / total_items) * 100
            export_progress_bar['value'] = progress_percentage
            root.update_idletasks()  # Update the window to reflect the changes

    duration = datetime.now() - start_time
    export_progress_bar_lb.config(text=f"Export Done! Duration: {duration.days*24 + duration.seconds//3600} hour(s), {(duration.seconds//60)%60} min, {duration.seconds%60} sec")

# Function to print selected exporters and languages
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
                # Print the error and continue to the next exporter
                print(f"Error downloading {url}: {e}")
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

        
# ===============================================================
# Init script : Create Output and get api json
# ===============================================================
# -- Create Output folder
outputFolder = get_file_path("Output")
os.makedirs(outputFolder, exist_ok=True)
# --- Send a GET request to fetch the raw JSON data with all views (to get ids)
# Datasource are not exportable. Views are. Each views is linked, via ID, to a datasource
datasources = fetch_data_with_retry(f"{API_URL}/datasources")
views = fetch_data_with_retry(f"{API_URL}/views")


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
notebook.add(tab0, text='ReadMe' )

# Adding a Text widget to ReadMe_frame
text_widget_tab0 = tk.Text(tab0, wrap='word' , bg=style.lookup("TFrame", "background"), fg='Black', bd=0)
# Text
Text_tab0 = f"""
Author : Ronaf-Git

How-to :

See https://github.com/Ronaf-git/StatBel_OpenDatasets for more informations
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
notebook.add(tab1, text='Metadatas' )
# --- metadata : button and label
# Create Button 
metadata_bt = tk.Button(tab1, text="Export metadatas", command=create_metadata)
metadata_bt.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
# Create Label 
metadata_lb = tk.Label(tab1, text="Export all metadata (Datasource and views) in a texte file", font=("Helvetica", 14, "bold"))
metadata_lb.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)

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