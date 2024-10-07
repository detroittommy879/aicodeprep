import os
import pathlib
import argparse
import pyperclip
import yaml
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def load_config(config_file: str = 'aicodeprep_config.yaml') -> dict:
    """Load configuration from YAML file."""
    try:
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logging.warning(f"Config file {config_file} not found. Using default settings.")
        return {}


config = load_config()
CODE_EXTENSIONS = set(config.get('code_extensions', [
    '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cpp', '.c', '.h',
    '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala',
    '.html', '.css', '.scss', '.sass', '.less', '.sql', '.sh',
    '.yaml', '.yml', '.json', '.xml', '.vue', '.r', '.m', '.f90',
    '.f95', '.f03', '.f08', '.gradle', '.groovy', '.ps1', '.psm1', '.ipynb'
]))
EXCLUDE_DIRS = set(config.get('exclude_dirs', [
    '.git', 'node_modules', 'venv', '__pycache__', 'build', 'dist', '.idea',
    'Lib', 'site-packages', '.venv'
]))
MAX_FILE_SIZE = config.get('max_file_size', 1000000)  # 1MB default


def is_code_file(file_path: str) -> bool:
    """Checks if a file is a code file based on its extension."""
    return pathlib.Path(file_path).suffix.lower() in CODE_EXTENSIONS


def process_directory(output_file: str = "fullcode.txt") -> int:
    """Processes the current directory and concatenates code files."""
    root_dir = os.getcwd()
    files_processed = 0

    try:
        with open(output_file, 'w', encoding='utf-8') as outfile:
            for root, dirs, files in os.walk(root_dir):
                dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith('.')]

                for file in files:
                    file_path = os.path.join(root, file)

                    if is_code_file(file_path) and not any(
                            part.startswith('.') for part in pathlib.Path(file_path).parts):
                        try:
                            if os.path.getsize(file_path) > MAX_FILE_SIZE:
                                logging.warning(f"Skipping {file_path}: File too large")
                                continue

                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as infile:
                                relative_path = os.path.relpath(file_path, root_dir)

                                outfile.write(f"{relative_path}:\n")
                                outfile.write("<code>\n")
                                outfile.write(infile.read())
                                outfile.write("\n</code>\n\n")

                                files_processed += 1
                                logging.info(f"Processed: {relative_path}")
                        except Exception as e:
                            logging.error(f"Error processing {file_path}: {str(e)}")
    except Exception as e:
        logging.error(f"Error writing to output file: {str(e)}")

    return files_processed


def main():
    parser = argparse.ArgumentParser(description="Concatenate code files into a single text file.")
    parser.add_argument("-n", "--no-copy", action="store_true",
                        help="Do NOT copy output to clipboard (default: copy to clipboard)")
    parser.add_argument("-o", "--output", default="fullcode.txt", help="Output file name (default: fullcode.txt)")

    args = parser.parse_args()

    logging.info("Starting code concatenation...")
    files_processed = process_directory(args.output)
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


if __name__ == "__main__":
    main()