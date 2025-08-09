# UpdateDirDates

A Python command-line application that updates directory modification dates to accurately reflect the latest modified dates of files within those directories and their subdirectories. This is useful when directories get out of synchronization after copying files or deleting content.

## Features

- **Recursive processing**: Traverses directory trees and updates timestamps bottom-up
- **Dry run by default**: Shows what would be changed without actually modifying anything
- **Colored output**: Uses green for success, yellow for warnings, red for errors
- **Multiple verbosity levels**: Control output detail from quiet to verbose
- **Directory and file counts**: Shows count of subdirectories and files in each directory `(dirs:NN files:NN)`
- **Cross-platform**: Works on Windows, macOS, and Linux
- **Robust error handling**: Gracefully handles permission issues and other errors

## Installation

### From Source

1. Clone or download this repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install the package:
   ```bash
   pip install -e .
   ```

### Requirements

- Python 3.13 or higher
- colorama (for colored output)

## Usage

### Basic Usage

```bash
# Dry run (default) - shows what would be changed
updatedirdates /path/to/directory

# Actually update directory dates
updatedirdates -x /path/to/directory

# Process multiple directories
updatedirdates -x /path/dir1 /path/dir2 /path/dir3
```

### Verbosity Levels

```bash
# Level 0 (default) - mostly quiet, only statistics
updatedirdates /path/to/directory

# Level 1 - show first-level directories being processed
updatedirdates -v 1 /path/to/directory

# Level 2 - show all directories with status messages
updatedirdates -v 2 /path/to/directory
```

### Complete Examples

```bash
# Quiet dry run
updatedirdates /home/user/photos

# Verbose dry run showing all directories
updatedirdates -v 2 /home/user/photos

# Actually update with moderate verbosity
updatedirdates -x -v 1 /home/user/photos

# Process multiple directories with updates
updatedirdates -x /var/log /home/backups /tmp/extracted

# Very verbose actual run
updatedirdates -x -v 2 /path/to/directory
```

## How It Works

UpdateDirDates processes directories using a bottom-up approach:

1. **Recursively traverses** the directory tree starting from the specified paths
2. **Processes subdirectories first** before their parent directories
3. **Finds the latest modification time** among all files and subdirectories
4. **Compares directory timestamp** with the latest content timestamp
5. **Updates directory timestamp** if content is newer (with 1-second tolerance)
6. **Reports statistics** including execution time and number of changes

### When Directories Are Updated

A directory's modification time is updated when:
- Any file within it (or its subdirectories) is newer than the directory
- The time difference exceeds 1 second (to avoid floating-point precision issues)

## Output Examples

### Dry Run (Default)
```
$ updatedirdates -v 2 /path/to/photos
Directory OK: /path/to/photos/2023 (2023-12-01 10:30:45) (dirs:0 files:12)
Would update /path/to/photos/2024: 2024-01-01 08:00:00 -> 2024-08-09 15:22:33 (dirs:2 files:24)
Directory OK: /path/to/photos (2024-08-09 15:22:35) (dirs:2 files:36)

1 directory date would be updated.
Execution time: 0.12 seconds
```

### Actual Update
```
$ updatedirdates -x -v 1 /path/to/photos
Updating /path/to/photos/2024: 2024-01-01 08:00:00 -> 2024-08-09 15:22:33 (dirs:2 files:24)
Updated /path/to/photos/2024

1 directory date was updated.
Execution time: 0.15 seconds
```

## Command Line Options

- `directories`: One or more directories to process (required)
- `-x, --execute`: Actually update directory dates (default: dry run only)
- `-v, --verbosity {0,1,2}`: Verbosity level (default: 0)
  - 0: Quiet mode - only statistics
  - 1: Show root and first-level subdirectories being processed  
  - 2: Show all directories with detailed status
- `--version`: Show version information
- `-h, --help`: Show help message

## Error Handling

UpdateDirDates handles various error conditions gracefully:

- **Non-existent paths**: Reports error and continues with other directories
- **Permission denied**: Reports warning and continues processing
- **Inaccessible files**: Reports warning but continues with accessible content
- **Invalid arguments**: Shows usage help and exits

## Exit Codes

- `0`: Success
- `1`: General error (invalid arguments, no valid directories, etc.)
- `130`: Interrupted by user (Ctrl+C)

## Use Cases

- **After copying directories**: Restore proper modification times
- **After deleting files**: Update parent directory timestamps
- **Archive maintenance**: Ensure directory timestamps reflect content
- **Build systems**: Maintain accurate timestamps for incremental builds
- **Backup verification**: Ensure backup timestamps are consistent

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please ensure tests pass and maintain code coverage above 80%.

## Author

Mike Wise - August 2025