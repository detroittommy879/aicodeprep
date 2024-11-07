import os
import pathlib
import argparse
import pyperclip
import yaml
import logging
from typing import List, Tuple

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def load_default_config() -> dict:
    """Load default configuration from YAML file."""
    try:
        default_config_path = os.path.join(os.path.dirname(__file__), 'default_config.yaml')
        with open(default_config_path, 'r') as f:
            config = yaml.safe_load(f)
            if 'exclude_patterns' in config:
                config['exclude_patterns'] = [
                    pattern.lstrip('.') for pattern in config['exclude_patterns']
                ]
            return config
    except Exception as e:
        logging.error(f"Error loading default configuration: {str(e)}")
        return {}


def load_user_config() -> dict:
    """Load user configuration from current directory if it exists."""
    try:
        if os.path.exists('aicodeprep_config.yaml'):
            with open('aicodeprep_config.yaml', 'r') as f:
                config = yaml.safe_load(f)
                if config and 'exclude_patterns' in config:
                    config['exclude_patterns'] = [
                        pattern.lstrip('.') for pattern in config['exclude_patterns']
                    ]
                return config
    except Exception as e:
        logging.error(f"Error loading user configuration: {str(e)}")
    return {}


# Load configurations
default_config = load_default_config()
user_config = load_user_config()

# Merge configurations
config = {**default_config, **user_config}

# Set up global constants
CODE_EXTENSIONS = set(config.get('code_extensions', []))
EXCLUDE_EXTENSIONS = set(config.get('exclude_extensions', []))
EXCLUDE_PATTERNS = set(config.get('exclude_patterns', []))
EXCLUDE_DIRS = set(config.get('exclude_dirs', []))
INCLUDE_DIRS = set(config.get('include_dirs', []))
EXCLUDE_FILES = set(config.get('exclude_files', []))
INCLUDE_FILES = set(config.get('include_files', []))
MAX_FILE_SIZE = config.get('max_file_size', 1000000)


def matches_pattern(filename: str, pattern: str) -> bool:
    """Check if filename matches a pattern (case-insensitive)."""
    return pattern.lower() in filename.lower()


def is_excluded_directory(path: str) -> bool:
    """Check if any part of the path contains an excluded directory."""
    path_parts = pathlib.Path(path).parts
    return any(part in EXCLUDE_DIRS for part in path_parts)


def should_process_directory(dir_path: str) -> bool:
    """Determine if a directory should be processed."""
    # First check if any parent directory is excluded
    if is_excluded_directory(dir_path):
        return False

    dir_name = os.path.basename(dir_path)
    if dir_name in INCLUDE_DIRS:
        return True
    if dir_name in EXCLUDE_DIRS:
        return False
    return True


def collect_potential_files() -> List[Tuple[str, str]]:
    """First pass: Collect all potential files based on extensions."""
    potential_files = []
    root_dir = os.getcwd()

    for root, dirs, files in os.walk(root_dir):
        # Skip the entire directory if it should be excluded
        if is_excluded_directory(root):
            dirs[:] = []  # Clear the dirs list to prevent further recursion
            continue

        # Filter directories
        dirs[:] = [d for d in dirs if should_process_directory(os.path.join(root, d))
                   and not d.startswith('.')]

        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, root_dir)

            # Skip hidden files/paths
            if any(part.startswith('.') for part in pathlib.Path(file_path).parts):
                continue

            # Skip files in excluded directories
            if is_excluded_directory(file_path):
                continue

            # Check file size
            try:
                if os.path.getsize(file_path) > MAX_FILE_SIZE:
                    continue
            except (OSError, IOError):
                continue

            # Check if it's a potential code file
            extension = pathlib.Path(file_path).suffix.lower()
            if extension in CODE_EXTENSIONS or file in INCLUDE_FILES:
                potential_files.append((file_path, relative_path))
                logging.debug(f"Added potential file: {relative_path}")

    return potential_files


def filter_files(potential_files: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    """Second pass: Filter files based on exclusion rules."""
    filtered_files = []

    for file_path, relative_path in potential_files:
        file_name = os.path.basename(file_path)
        extension = pathlib.Path(file_path).suffix.lower()

        # Always include specifically included files
        if file_name in INCLUDE_FILES:
            filtered_files.append((file_path, relative_path))
            logging.debug(f"Including file (in INCLUDE_FILES): {relative_path}")
            continue

        # Check exclusion rules
        if file_name in EXCLUDE_FILES:
            logging.debug(f"Excluding file (in EXCLUDE_FILES): {relative_path}")
            continue

        if extension in EXCLUDE_EXTENSIONS:
            logging.debug(f"Excluding file (extension {extension}): {relative_path}")
            continue

        if any(matches_pattern(file_name, pattern) for pattern in EXCLUDE_PATTERNS):
            logging.debug(f"Excluding file (matches pattern): {relative_path}")
            continue

        filtered_files.append((file_path, relative_path))
        logging.debug(f"Including file (passed all filters): {relative_path}")

    return filtered_files


def process_files(filtered_files: List[Tuple[str, str]], output_file: str) -> int:
    """Process the filtered files and write to output."""
    try:
        with open(output_file, 'w', encoding='utf-8') as outfile:
            for file_path, relative_path in filtered_files:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as infile:
                        outfile.write(f"{relative_path}:\n<code>\n")
                        outfile.write(infile.read())
                        outfile.write("\n</code>\n\n")
                        logging.info(f"Processed: {relative_path}")
                except Exception as e:
                    logging.error(f"Error processing {file_path}: {str(e)}")

        return len(filtered_files)
    except Exception as e:
        logging.error(f"Error writing to output file: {str(e)}")
        return 0


def main():
    parser = argparse.ArgumentParser(description="Concatenate code files into a single text file.")
    parser.add_argument("-n", "--no-copy", action="store_true",
                        help="Do NOT copy output to clipboard (default: copy to clipboard)")
    parser.add_argument("-o", "--output", default="fullcode.txt",
                        help="Output file name (default: fullcode.txt)")
    parser.add_argument("-d", "--debug", action="store_true",
                        help="Enable debug logging")

    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    logging.info("Starting code concatenation...")

    # Two-pass processing
    potential_files = collect_potential_files()
    logging.info(f"Found {len(potential_files)} potential files")

    filtered_files = filter_files(potential_files)
    logging.info(f"After filtering: {len(filtered_files)} files")

    files_processed = process_files(filtered_files, args.output)

    logging.info(f"Concatenation complete! Processed {files_processed} code files.")
    logging.info(f"Output written to {args.output}")

    if not args.no_copy:
        try:
            with open(args.output, 'r', encoding='utf-8') as f:
                full_code = f.read()
            pyperclip.copy(full_code)
            logging.info("Code copied to clipboard!")
        except Exception as e:
            logging.error(f"Error copying to clipboard: {str(e)}")

    # Add final comments here
    logging.info("Buy my cat a treat, comments, ideas for improvement appreciated: ")
    logging.info("https://wuu73.org/hello.html")


if __name__ == "__main__":
    main()
