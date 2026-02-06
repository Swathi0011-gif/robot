# Robot CLI Tool

The **Robot CLI** is a powerful command-line agent that translates your natural language instructions into system actions using the Google Gemini model (via OpenRouter).

## Installation

1.  Clone this repository.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Build the executable (Windows):
    ```bash
    build.bat
    ```
    Output: `dist/robot_global.exe`

## Usage

Use the `do` command to tell the robot what to do.

### Example 1: Find Files
```powershell
python main.py do "Find all PDF files in C:/User/Downloads and list them"
```

### Example 2: Organize Files
```powershell
python main.py do "Create a folder named 'Invoices' and move all PDF files from current directory into it"
```

## Setup

1.  Run the setup command:
    ```powershell
    python main.py setup
    ```
2.  Paste your API key when prompted. It will be saved globally to `%USERPROFILE%/.robot_env`.

