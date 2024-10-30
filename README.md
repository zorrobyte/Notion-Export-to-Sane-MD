# Notion Export to Sane MD

![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![License](https://img.shields.io/badge/License-GPT-blue.svg)

**Notion Export to Sane MD** is a suite of Python scripts designed to clean and validate your Notion markdown exports. These tools ensure your markdown files are organized, free of broken links, and adhere to consistent naming conventions. Additionally, the suite includes a link checker to identify and report broken or unreferenced links within your documentation.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [Link Checker (`checker.py`)](#link-checker-checkerpy)
  - [Markdown Converter (`converter.py`)](#markdown-converter-converterpy)
- [Requirements](#requirements)
- [Examples](#examples)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Link Validation:** Detects broken links within your markdown files and suggests possible fixes.
- **File Sanitization:** Cleans filenames and paths by removing invalid characters and GUIDs.
- **Unreferenced File Detection:** Identifies image and media files that are not referenced in any markdown files.
- **Markdown Link Updates:** Automatically updates links in markdown files to reflect sanitized filenames and paths.
- **Comprehensive Reporting:** Generates detailed reports on the validation and conversion processes.

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/zorrobyte/Notion-Export-to-Sane-MD.git
   cd Notion-Export-to-Sane-MD
   ```

2. **Create a Virtual Environment (Optional but Recommended):**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies:**

   The scripts use only standard Python libraries, so no additional installations are required. Ensure you are using Python 3.8 or higher.

## Usage

### Link Checker (`checker.py`)

The `checker.py` script scans your Notion markdown export directory, identifies broken links, and reports unreferenced files.

**Usage:**

```bash
python checker.py [base_directory]
```

- `base_directory` (optional): The path to the directory containing your Notion markdown export. If not provided, it defaults to `"Target Directory"`.

**Example:**

```bash
python checker.py ./notion_export
```

**Output:**

The script will output a validation report detailing broken links, unreferenced files, and files with no links, along with statistics.

### Markdown Converter (`converter.py`)

The `converter.py` script sanitizes filenames and paths in your markdown export, removes unwanted characters and GUIDs, and updates markdown links accordingly.

**Usage:**

```bash
python converter.py
```

**Configuration:**

By default, the script looks for `"Source Directory"` and outputs to `"Target Directory"`. Modify these variables within the script or update the script to accept command-line arguments for flexibility.

**Example:**

```bash
python converter.py
```

**Output:**

The script will process and copy files from the source to the target directory with sanitized filenames. It will also update markdown links to reflect the new filenames and paths.

## Requirements

- Python 3.8 or higher

Both scripts use standard Python libraries (`os`, `re`, `sys`, `pathlib`, `shutil`, `urllib.parse`), so no additional packages are required.

## Examples

### Link Checker Report

```
Validation Report
================================================================================

Broken Links Found:
--------------------------------------------------------------------------------

File: docs/Getting-Started.md
  - ./images/setup.png
  - ./docs/installation.md

Unreferenced Files:
--------------------------------------------------------------------------------
  - images/unused-image.png
  - media/old-video.mp4

Files with No Links:
--------------------------------------------------------------------------------
  - README.md

Statistics:
--------------------------------------------------------------------------------
Total files: 50
Files with broken links: 2
Unreferenced files: 2
Files with no links: 1
Total broken links: 2
Total valid links: 48
```

### Markdown Converter Summary

```
Processing Summary:
Total files processed: 45
Errors encountered: 1
Files mapped: 45

Errors encountered:
  - images/badimage?.png: Invalid character in filename

Skipped files:
  - tempfile.tmp: Unsupported file extension
```

## Contributing

Contributions are welcome! If you have suggestions, bug reports, or feature requests, please open an issue or submit a pull request.

1. **Fork the Repository**
2. **Create a Feature Branch**

   ```bash
   git checkout -b feature/YourFeature
   ```

3. **Commit Your Changes**

   ```bash
   git commit -m "Add Your Feature"
   ```

4. **Push to the Branch**

   ```bash
   git push origin feature/YourFeature
   ```

5. **Open a Pull Request**

## License

This project is licensed under the [GPT License](LICENSE).

---

*Made with ❤️ by [zorrobyte](https://github.com/zorrobyte)*
