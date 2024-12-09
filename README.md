# StatBel Open Datasets

**Author:** Ronaf (Ronaf-Git)  
**Project:** [StatBel Open Datasets](https://github.com/Ronaf-git/StatBel_OpenDatasets)

## Overview

This tool allows users to interact with the [StatBel](https://statbel.fgov.be/en/statistics/bestat/faq) API to retrieve and export open datasets (referred to as "views") provided by the Belgian Statistical Office. You can export the data in multiple formats (CSV, XML, JSON, HTML, PDF, XLS) and choose specific views based on language and format preferences.

The application also allows you to export metadata about datasets and view relationships between datasources and views.

## Features

- **Retrieve Metadata**: Export metadata about datasets (datasources and views) as text files.
- **Export All Views**: Export all available datasets in multiple formats. Will take a long time. Not recommended.
- **Filter by Language**: Export datasets in different languages (French, English, Dutch, German) - if available.
- **Export Specific Views**: Select specific views to export based on chosen languages and formats.
- **Progress Tracking**: View export progress in real-time with a progress bar.

## How to Use

### Prerequisites

- **Windows OS**: The application is packaged as an executable (`.exe`), so no additional setup is required.
- **Internet connection**: The application needs internet connection to get datas.
- **No Installation Required**: Just run the `.exe` file on your system.

### Running the Application

1. **Download the Executable**: Download the executable file from the releases section of this repository.
2. **Launch the Application**: Double-click the `.exe` file to launch the tool.

### Main Features in the GUI

- **Tab 1: About**  
  Displays general information about the tool and instructions for usage.

- **Tab 2: Metadata**  
  - Export metadata about datasets (datasources and views).
  - Show relationships between datasources and views.

- **Tab 3: Export all Views**  
  - Export all available views in all available format. Not recommended.

- **Tab 4: Export specific Views**  
  - Allows users to select specific views and export them in the desired format and language.
  - Export progress is displayed in a progress bar.

### Available Formats

- **XML**
- **JSON**
- **CSV**
- **XLS**
- **HTML**
- **PDF**

### Supported Languages

- **French (fr)**
- **English (en)**
- **Dutch (nl)**
- **German (de)**

### Folder Structure

When launched, the tool will create an `Output` folder in the directory where it's located. Inside the `Output` folder, separate folders for each selected export format will be created, with the exported files saved in the respective formats.
Metadata text files and log will also be located in this folder.

## Example Usage

1. Launch the application.
2. Go to **Tab 2: Metadata** and click **Export metadata** to retrieve information about the datasets and views.
3. Switch to **Tab 3: All Views** to export **all views** available in the selected formats and languages. Not recommended.
4. In **Tab 4: Export selected views**, choose specific views, select formats and languages, and then click **Export views**.

The progress of the export will be displayed in real-time.

## Troubleshooting

- **No progress or export failure**: If the application fails to fetch data from the StatBel API, it will retry up to 5 times with a 3-second delay between each attempt.
- **File name issues**: The tool automatically sanitizes file names to remove invalid characters that may cause issues on Windows file systems.
- **Not responding**: The tool may looks like it isn't responding during exporting files.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
