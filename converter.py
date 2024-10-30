import os
import re
import shutil
from pathlib import Path
from urllib.parse import unquote


def sanitize_filename(name):
    """Clean filename/path of invalid characters and GUIDs."""
    # Handle the full path to preserve directory structure
    path_parts = Path(name).parts
    cleaned_parts = []

    for part in path_parts:
        # Remove GUID patterns
        cleaned = re.sub(r'\s*[a-f0-9]{32}\b', '', part)
        cleaned = re.sub(r'\s*[a-f0-9]{8}-?[a-f0-9]{4}-?[a-f0-9]{4}-?[a-f0-9]{4}-?[a-f0-9]{12}\b', '', cleaned)
        cleaned = re.sub(r'\s*[0-9a-f]{16}\b', '', cleaned)
        cleaned = re.sub(r'\s+\([0-9a-f]{3,}\)', '', cleaned)  # Remove parenthetical hex numbers

        # Handle special characters and clean up the name
        cleaned = cleaned.replace('…', '...')
        cleaned = cleaned.replace(' ', '-')  # Convert spaces to hyphens first
        cleaned = re.sub(r'[<>:"/\\|?*]', '-', cleaned)
        cleaned = re.sub(r'-+', '-', cleaned)  # Remove consecutive hyphens
        cleaned = cleaned.strip('-')

        # Remove non-ASCII characters
        cleaned = ''.join(c for c in cleaned if ord(c) < 128)

        # Handle empty or invalid results
        if not cleaned or cleaned == '.':
            cleaned = 'untitled'

        cleaned_parts.append(cleaned)

    return str(Path(*cleaned_parts))


def normalize_path(path):
    """Normalize path separators and handle special cases."""
    # Convert path to consistent format
    path = str(path).replace('\\', '/').strip()
    # Handle relative paths
    if path.startswith('./') or path.startswith('../'):
        return path
    return path.lstrip('/')


def is_supported_file(filename):
    """Check if file type is supported."""
    supported_extensions = {'.md', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.mp4', '.mov', '.csv'}
    return Path(filename).suffix.lower() in supported_extensions


def get_file_info(path):
    """Get basic file information."""
    try:
        stat = path.stat()
        return {
            'size': stat.st_size,
            'modified': stat.st_mtime,
            'exists': True
        }
    except:
        return {
            'size': 0,
            'modified': 0,
            'exists': False
        }


def update_markdown_links(content, current_file_original_rel_path, current_file_clean_rel_path, file_map):
    """
    Update markdown links with new filenames.

    Args:
        content (str): The original markdown content.
        current_file_original_rel_path (Path): The original relative path of the current markdown file.
        current_file_clean_rel_path (Path): The cleaned relative path of the current markdown file.
        file_map (dict): Mapping from original relative paths to cleaned relative paths.

    Returns:
        str: The updated markdown content with corrected links.
    """
    updated = content

    # Handle relative paths by getting the current file's directory in the target (cleaned) structure
    current_dir_clean = current_file_clean_rel_path.parent

    def replace_link(match):
        link_text = match.group(1)
        link_path = match.group(2).strip()

        # Skip external URLs and anchors
        if link_path.startswith(('http://', 'https://', '#')):
            return match.group(0)

        # Decode URL-encoded characters
        link_path = unquote(link_path)

        # Normalize the link path
        link_path_normalized = normalize_path(link_path)

        # Resolve the linked file's original relative path
        linked_original_path = (Path(current_file_original_rel_path).parent / link_path_normalized).resolve().relative_to(Path.cwd())

        # Ensure the linked_original_path is relative to the source directory
        try:
            linked_original_rel_path = Path(linked_original_path).relative_to(Path(current_file_original_rel_path).anchor)
        except ValueError:
            # If relative_to fails, it means linked_original_path is not under the source directory
            return match.group(0)

        # Convert to POSIX style for consistent mapping
        linked_original_rel_path_str = str(linked_original_rel_path.as_posix())

        # Find the cleaned path from the file_map
        linked_clean_rel_path = file_map.get(linked_original_rel_path_str)

        if not linked_clean_rel_path:
            # If not found, try case-insensitive match
            lower_map = {k.lower(): v for k, v in file_map.items()}
            linked_clean_rel_path = lower_map.get(linked_original_rel_path_str.lower())

        if linked_clean_rel_path:
            # Compute the relative path from the current file's cleaned directory to the linked file's cleaned path
            rel_path = os.path.relpath(linked_clean_rel_path, start=str(current_dir_clean))
            rel_path = normalize_path(rel_path)
            return f'[{link_text}]({rel_path})'

        # If no match found, keep the original link
        return match.group(0)

    # Update markdown links using regex
    updated = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', replace_link, updated)

    return updated


def copy_and_rename_files(source_dir, target_dir, file_map):
    """Copy files to new location with cleaned names."""
    source_dir = Path(source_dir).resolve()
    target_dir = Path(target_dir).resolve()
    processed = 0
    errors = []
    processed_files = {}

    # Create target directory
    target_dir.mkdir(parents=True, exist_ok=True)

    for old_rel_path_str, new_rel_path_str in file_map.items():
        try:
            old_rel_path = Path(old_rel_path_str)
            new_rel_path = Path(new_rel_path_str)

            source_path = source_dir / old_rel_path
            target_path = target_dir / new_rel_path

            if not source_path.exists():
                errors.append((old_rel_path_str, "Source file not found"))
                continue

            # Create necessary subdirectories
            target_path.parent.mkdir(parents=True, exist_ok=True)

            if old_rel_path.suffix.lower() == '.md':
                with source_path.open('r', encoding='utf-8') as f:
                    content = f.read()
                # Update markdown links
                updated_content = update_markdown_links(
                    content,
                    current_file_original_rel_path=old_rel_path,
                    current_file_clean_rel_path=new_rel_path,
                    file_map=file_map
                )
                with target_path.open('w', encoding='utf-8') as f:
                    f.write(updated_content)
            else:
                shutil.copy2(source_path, target_path)

            processed += 1
            processed_files[old_rel_path_str] = {
                'new_path': new_rel_path_str,
                'size': source_path.stat().st_size
            }

        except Exception as e:
            errors.append((old_rel_path_str, str(e)))

    return processed, errors, processed_files


def build_link_database(source_dir):
    """Build database of files and their cleaned names."""
    source_dir = Path(source_dir).resolve()
    file_map = {}
    skipped_files = []

    for root, _, files in os.walk(source_dir):
        for file in files:
            if is_supported_file(file):
                try:
                    full_path = Path(root) / file
                    rel_path = full_path.relative_to(source_dir)
                    clean_path = sanitize_filename(str(rel_path))
                    file_map[str(rel_path.as_posix())] = clean_path
                except Exception as e:
                    skipped_files.append((file, str(e)))

    return file_map, skipped_files


def main():
    source_dir = "Source Directory"
    target_dir = "Target Directory"

    # Convert to Path objects and resolve
    source_path = Path(source_dir).resolve()
    target_path = Path(target_dir).resolve()

    if not source_path.exists():
        print(f"Error: Source directory does not exist: {source_path}")
        return

    print(f"Source directory: {source_path}")
    print(f"Target directory: {target_path}")

    # Build file mapping
    print("\nBuilding file database...")
    file_map, skipped_files = build_link_database(source_path)

    if not file_map:
        print("No files to process!")
        return

    # Process files
    print("\nProcessing files...")
    processed, errors, processed_files = copy_and_rename_files(source_path, target_path, file_map)

    # Print summary
    print("\nProcessing Summary:")
    print(f"Total files processed: {processed}")
    print(f"Errors encountered: {len(errors)}")
    print(f"Files mapped: {len(file_map)}")

    if errors:
        print("\nErrors encountered:")
        for file_path, error in errors[:10]:
            print(f"  - {file_path}: {error}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more")

    if skipped_files:
        print("\nSkipped files:")
        for file, error in skipped_files[:10]:
            print(f"  - {file}: {error}")
        if len(skipped_files) > 10:
            print(f"  ... and {len(skipped_files) - 10} more")


if __name__ == "__main__":
    main()
