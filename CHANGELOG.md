# Changelog

## [0.2.0] - 2024-02-11 (Nov 2nd 2024)

### Moved all hard coded options to the default_config.yaml file

### Added
- New `exclude_extensions` configuration option to exclude file types globally
- New `exclude_extensions` configuration option to exclude patterns like .min.js
- New `include_dirs` configuration option to explicitly include specific directories
- Enhanced priority system for file inclusion/exclusion rules
- Better support for user configuration overrides
- Updated and added some more exclusions that came up later when it would add unnecessary files

### Changed
- Improved file processing logic with clearer priority rules:
  1. Explicitly included files (highest priority)
  2. Explicitly excluded files
  3. Excluded extensions
  4. Code extensions (lowest priority)
- Enhanced directory processing logic:
  1. Explicitly included directories (highest priority)
  2. Explicitly excluded directories
  3. Normal directory processing

### Coming soon, GUI menu so you can right click right in a folder and run it from there and also add/remove files/folders which will be automatically pre-checked and displayed for speed
