# aicodeprep (AI Code Prep)

aicodeprep is a command-line tool designed to simplify the process of sharing your project's code with AI chatbots. It recursively scans your project directory, concatenates all code files into a single text file, and copies the content to your clipboard for easy pasting.

## Purpose

The primary purpose of aicodeprep is to save time when you need to ask AI chatbots questions about your development project. Instead of manually copying and pasting multiple files, aicodeprep automates the process of gathering all your project's code into a single, easily shareable format.

## Installation

You can install aicodeprep directly from PyPI:

pip install aicodeprep

## Usage

After installation, you can run aicodeprep from any directory containing your project files and folders:

aicodeprep

This will create a file named `fullcode.txt` in the current directory and copy its contents to your clipboard.

### Options

- `-n, --no-copy`: Do NOT copy output to clipboard (default behavior is to copy)
- `-o FILENAME, --output FILENAME`: Specify the output file name (default: fullcode.txt)

Example:

aicodeprep -n -o my_project_code.txt

This will create `my_project_code.txt` without copying to clipboard.

## Configuration

You can customize aicodeprep's behavior by creating a `aicodeprep_config.yaml` file in your project directory. Here's an example:

```yaml
code_extensions:
  - .py
  - .js
  - .html
exclude_dirs:
  - node_modules
  - venv
max_file_size: 500000  # in bytes

Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

License

This project is licensed under the MIT License.

