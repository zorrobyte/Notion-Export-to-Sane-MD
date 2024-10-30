import os
import re
import sys
from pathlib import Path
from collections import defaultdict
from urllib.parse import unquote, quote


class LinkChecker:
    def __init__(self, base_dir):
        self.base_dir = Path(base_dir).resolve()
        self.all_files = set()
        self.broken_links = defaultdict(list)
        self.valid_links = defaultdict(list)
        self.files_with_no_links = []
        self.unreferenced_files = set()
        self.all_links = defaultdict(set)

    def normalize_path(self, path):
        """Normalize a path for consistent comparison."""
        try:
            # Decode URL-encoded characters
            decoded = unquote(str(path))
            # Convert to Path object and resolve
            return str(Path(decoded))
        except Exception as e:
            print(f"Error normalizing path {path}: {str(e)}")
            return str(path)

    def collect_all_files(self):
        """Build a set of all files in the directory."""
        print("\nCollecting all files...")
        for root, _, files in os.walk(self.base_dir):
            for file in files:
                try:
                    rel_path = os.path.relpath(os.path.join(root, file), self.base_dir)
                    self.all_files.add(self.normalize_path(rel_path))
                except Exception as e:
                    print(f"Error processing file {file}: {str(e)}")
        print(f"Found {len(self.all_files)} files")

    def resolve_relative_link(self, source_file, link):
        """Resolve a relative link from a source file."""
        try:
            # Get the directory of the source file
            source_dir = os.path.dirname(source_file)
            # Join with the link path
            full_path = os.path.normpath(os.path.join(source_dir, link))
            # Make it relative to base_dir
            return os.path.relpath(full_path, '.')
        except Exception as e:
            print(f"Error resolving link {link} from {source_file}: {str(e)}")
            return link

    def extract_links(self, content):
        """Extract all links from markdown content."""
        links = set()

        # Standard markdown links
        std_links = re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', content)
        for match in std_links:
            _, target = match.groups()
            if not target.startswith(('http://', 'https://', '#', '/', 'mailto:')):
                links.add(unquote(target))

        # Image links
        img_links = re.finditer(r'!\[([^\]]*)\]\(([^)]+)\)', content)
        for match in img_links:
            _, target = match.groups()
            if not target.startswith(('http://', 'https://', '/', 'data:')):
                links.add(unquote(target))

        return links

    def check_file(self, md_file):
        """Check a single markdown file for broken links."""
        try:
            with open(self.base_dir / md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            links = self.extract_links(content)

            if not links:
                self.files_with_no_links.append(md_file)
                return

            for link in links:
                self.all_links[md_file].add(link)
                resolved_link = self.resolve_relative_link(md_file, link)
                normalized_link = self.normalize_path(resolved_link)

                if normalized_link in self.all_files:
                    self.valid_links[md_file].append(link)
                else:
                    self.broken_links[md_file].append(link)

        except Exception as e:
            self.broken_links[md_file].append(f"Error processing file: {str(e)}")

    def find_unreferenced_files(self):
        """Find files that aren't linked from any markdown file."""
        referenced_files = set()
        for source_file, links in self.all_links.items():
            for link in links:
                try:
                    resolved_link = self.resolve_relative_link(source_file, link)
                    normalized_link = self.normalize_path(resolved_link)
                    referenced_files.add(normalized_link)
                except Exception as e:
                    print(f"Error processing link {link} from {source_file}: {str(e)}")

        self.unreferenced_files = {
            f for f in self.all_files
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg'))
               and self.normalize_path(f) not in referenced_files
        }

    def validate_all(self):
        """Validate all markdown files."""
        print("\nValidating markdown files...")
        md_files = [f for f in self.all_files if f.lower().endswith('.md')]

        for md_file in md_files:
            self.check_file(md_file)

        self.find_unreferenced_files()

    def generate_report(self):
        """Generate a detailed validation report."""
        print("\nValidation Report")
        print("=" * 80)

        if self.broken_links:
            print("\nBroken Links Found:")
            print("-" * 80)
            for file, links in sorted(self.broken_links.items()):
                print(f"\nFile: {file}")
                for link in links:
                    print(f"  - {link}")
                    # Try to suggest fixes
                    suggestions = self.suggest_fix(file, link)
                    if suggestions:
                        print("    Possible matches:")
                        for suggestion in suggestions:
                            print(f"    → {suggestion}")

        if self.unreferenced_files:
            print("\nUnreferenced Files:")
            print("-" * 80)
            for file in sorted(self.unreferenced_files):
                print(f"  - {file}")

        if self.files_with_no_links:
            print("\nFiles with No Links:")
            print("-" * 80)
            for file in sorted(self.files_with_no_links):
                print(f"  - {file}")

        print("\nStatistics:")
        print("-" * 80)
        print(f"Total files: {len(self.all_files)}")
        print(f"Files with broken links: {len(self.broken_links)}")
        print(f"Unreferenced files: {len(self.unreferenced_files)}")
        print(f"Files with no links: {len(self.files_with_no_links)}")

        total_broken = sum(len(links) for links in self.broken_links.values())
        total_valid = sum(len(links) for links in self.valid_links.values())
        print(f"Total broken links: {total_broken}")
        print(f"Total valid links: {total_valid}")

    def suggest_fix(self, source_file, broken_link):
        """Suggest possible fixes for a broken link."""
        suggestions = []
        normalized_link = self.normalize_path(broken_link).lower()

        for existing_file in self.all_files:
            normalized_existing = self.normalize_path(existing_file).lower()
            # Check if the filename part matches
            if os.path.basename(normalized_link) in normalized_existing:
                suggestions.append(existing_file)
            # Check if it's just missing an extension
            elif normalized_link + '.md' == normalized_existing:
                suggestions.append(existing_file)

        return suggestions[:3]  # Limit to top 3 suggestions


def main():
    if len(sys.argv) > 1:
        base_dir = sys.argv[1]
    else:
        base_dir = "Target Directory"

    base_dir = Path(base_dir).resolve()
    if not base_dir.exists():
        print(f"Error: Directory not found: {base_dir}")
        return

    print(f"Checking documentation in: {base_dir}")

    validator = LinkChecker(base_dir)
    validator.collect_all_files()
    validator.validate_all()
    validator.generate_report()


if __name__ == "__main__":
    main()
