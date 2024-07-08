# File Sorter

File Sorter is a Python application designed to organize files into categorized directories based on their metadata. The application uses a Tkinter-based GUI for user interaction and leverages TMDb for media metadata retrieval.

## Features

- **File Organization**: Automatically organizes files into directories based on their metadata (e.g., year, quarter, title).
- **Directory Management**: Creates necessary directories and handles file duplication.
- **User Interface**: Provides a user-friendly interface to select directories and view progress.
- **Configuration Handling**: Loads and saves configuration settings, including the last sorted directory.

## Installation

1. **Clone the repository**:
    ```sh
    git clone https://github.com/tigers2020/AnimeFileSorter.git
    cd AnimeFileSorter
    ```

2. **Install the required packages**:
    ```sh
    pip install -r requirements.txt
    ```

3. **Configure TMDb API key**:
    - Create a `config.json` file in the `src` directory with the following structure:
      ```json
      {
          "api_key": "YOUR_TMDB_API_KEY"
      }
      ```

## Usage

1. **Run the application**:
    ```sh
    python FileSorterUI.py
    ```

2. **User Interface**:
    - **Directory to Sort**: Click "Browse" to select the directory containing the files to be sorted.
    - **Output Directory**: This will be automatically set relative to the selected directory.
    - **Process Files**: Click to start organizing files. Progress and logs will be displayed in the UI.

## Code Structure

- **FileSorter.py**: Contains the core functionality for file handling and organization.
- **FileSorterUI.py**: Implements the Tkinter-based user interface for interacting with the application.
- **src/log.py**: Logging configuration.
- **src/title_cleaner.py**: Utility functions for cleaning and extracting information from file titles.
- **src/tmdb_handler.py**: Handles interactions with the TMDb API.

## Example Configuration File (`config.json`)

```json
{
    "api_key": "YOUR_TMDB_API_KEY",
}
