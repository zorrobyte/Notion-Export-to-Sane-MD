# Notion Export to Sane MD

![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![License](https://img.shields.io/badge/License-GPT-blue.svg)

**Notion Export to Sane MD** is a suite of Python scripts designed to clean and validate your Notion markdown exports. These tools ensure your markdown files are organized, free of broken links, and adhere to consistent naming conventions. Additionally, the suite includes a link checker to identify and report broken or unreferenced links within your documentation.

## Features

- **Link Validation:** Detects broken links within your markdown files and suggests possible fixes.
- **File Sanitization:** Cleans filenames and paths by removing invalid characters and GUIDs.
- **Unreferenced File Detection:** Identifies image and media files that are not referenced in any markdown files.
- **Markdown Link Updates:** Automatically updates links in markdown files to reflect sanitized filenames and paths.
- **Comprehensive Reporting:** Generates detailed reports on the validation and conversion processes.
- Basically, gets rid of the GUID and other garbage notion exports

## Usage

### Link Checker (`checker.py`)

The `checker.py` script scans your Notion markdown export directory, identifies broken links, and reports unreferenced files.

The `converter.py` script removes the GUID garbage, dedupliates, and updates all links in the MD files

If your files have `()` in them, it may skip and you may need to manually rename/update links (accepting PRs)

**Usage:**

Slap your paths in the scripts and run. Export from notion is MD with all desired space content.

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

## License

This project is licensed under the [GPT License](LICENSE).

---

*Made with ❤️ by [zorrobyte](https://github.com/zorrobyte)*
