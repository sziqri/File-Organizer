# Smart File Organizer
A powerful, GUI-based Python utility designed to effortlessly filter, sort, copy, and move files between directories. Whether you are preparing datasets for machine learning, organizing forensic evidence, or just cleaning up a messy downloads folder, this tool provides granular control over how your files are processed.

## Features
**Dynamic Extension Detection:** Automatically scans the source directory and lists all available file extensions for precise selection.

**Smart Categories:** Pre-defined categories (Images, Videos, Audio, Documents, Archives) for quick, one-click bulk selection.

**Auto-Sorting:** Automatically creates subfolders in your target directory based on file extensions (e.g., /JPG_Files, /PDF_Files) to keep your destination clean.

**Precision Control:** Choose to process All files, a specific Percentage (%), or an Exact Number.

**Selection Priority:** Grab files alphabetically (A-Z), reverse alphabetically (Z-A), or randomly (perfect for splitting train/test machine learning datasets).

**Safe Operations:** Choose between Copying (preserves originals) and Moving. The tool automatically handles naming collisions to prevent accidental overwrites.

**Real-time Metrics:** Displays dynamic counters for total source files and total files ready to be processed based on your current filters.

## Prerequisites
Python 3.7 or higher

Standard Python libraries (Tkinter, os, shutil, random). No external pip installations are required to run the source code.

## Installation & Setup
**Clone the repository:**

```
Bash
git clone https://github.com/yourusername/smart-file-organizer.git
cd smart-file-organizer
```

**Run the script:**

```
Bash
python file_organizer.py
```

## How to Use
The user interface is divided into three simple steps:

**Step 1:** Select Directories
Click Browse to select your Source folder (where your messy files are) and your Target folder (where you want them to go).

You can also manually type or paste directory paths into the text boxes.

**Step 2:** Select Formats
Left Panel (Pre-defined): Quickly tick main categories like "Images" or "Documents".

Right Panel (Specific): The app automatically detects every file format in your source folder. Tick specific formats (e.g., .csv, .heic) to narrow down your selection.

Note: The two panels sync automatically. Checking a category will check all associated extensions on the right.

**Step 3:** Operation Settings & Execution
Amount: Process everything, or limit it to a percentage (e.g., 20%) or an exact number (e.g., 50 files).

Priority: Determine which files get picked first if you set an amount limit (Top A-Z, Bottom Z-A, or Random).

Action: Choose Copy or Move.

Auto-sort into subfolders: Tick this box if you want the tool to automatically create neatly organized folders for each extension in your target directory.

Click EXECUTE OPERATION to start.

## Building a Standalone Executable (.exe)
If you want to run this tool on a computer without installing Python, you can compile it into a standalone executable using pyinstaller.

Install PyInstaller:

```
Bash
pip install pyinstaller
```
Build the .exe file (this hides the background console and bundles it into one file):

```
Bash
pyinstaller --noconsole --onefile file_organizer.py
```
Navigate to the newly created dist/ folder in your project directory to find your file_organizer.exe.
