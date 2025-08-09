#!/usr/bin/env python3
"""Main module for UpdateDirDates application."""

import argparse
import os
import sys
import time
from pathlib import Path
from typing import List

import colorama
from colorama import Fore, Style

from .updater import DirectoryUpdater


def setup_colorama() -> None:
    """Initialize colorama for cross-platform colored output."""
    colorama.init(autoreset=True)


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="Update directory modification dates to reflect latest files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  updatedirdates /path/to/directory        # Dry run on directory
  updatedirdates -x /path/to/directory     # Actually update dates
  updatedirdates -v 2 -x /path/to/dir      # Verbose output with updates
  updatedirdates -v 0 -x /path/to/dir      # Quiet mode with updates
        """,
    )
    
    parser.add_argument(
        "directories",
        nargs="+",
        type=Path,
        help="Directories to process",
    )
    
    parser.add_argument(
        "-x", "--execute",
        action="store_true",
        help="Actually update directory dates (default: dry run only)",
    )
    
    parser.add_argument(
        "-v", "--verbosity",
        type=int,
        choices=[0, 1, 2],
        default=0,
        help="Verbosity level: 0=quiet, 1=first level dirs, 2=all dirs (default: 0)",
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0",
    )
    
    return parser


def print_colored(message: str, color: str = "") -> None:
    """Print a message with optional color."""
    print(f"{color}{message}{Style.RESET_ALL}")


def print_error(message: str) -> None:
    """Print an error message in red."""
    print_colored(f"ERROR: {message}", Fore.RED)


def print_warning(message: str) -> None:
    """Print a warning message in yellow."""
    print_colored(f"WARNING: {message}", Fore.YELLOW)


def print_success(message: str) -> None:
    """Print a success message in green."""
    print_colored(message, Fore.GREEN)


def validate_directories(directories: List[Path]) -> List[Path]:
    """Validate that all provided directories exist and are accessible."""
    valid_dirs = []
    
    for directory in directories:
        if not directory.exists():
            print_error(f"Directory does not exist: {directory}")
            continue
            
        if not directory.is_dir():
            print_error(f"Path is not a directory: {directory}")
            continue
            
        if not os.access(directory, os.R_OK):
            print_error(f"Directory is not readable: {directory}")
            continue
            
        valid_dirs.append(directory.resolve())
    
    return valid_dirs


def main() -> int:
    """Main entry point for the application."""
    setup_colorama()
    
    parser = create_parser()
    args = parser.parse_args()
    
    # Validate directories
    valid_directories = validate_directories(args.directories)
    if not valid_directories:
        print_error("No valid directories to process")
        return 1
    
    # Initialize the updater
    updater = DirectoryUpdater(
        verbosity=args.verbosity,
        dry_run=not args.execute,
        print_colored=print_colored,
        print_error=print_error,
        print_warning=print_warning,
        print_success=print_success,
    )
    
    # Process directories
    start_time = time.time()
    total_changes = 0
    
    try:
        for directory in valid_directories:
            changes = updater.process_directory(directory)
            total_changes += changes
            
    except KeyboardInterrupt:
        print_error("Operation interrupted by user")
        return 130
        
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return 1
    
    # Print final statistics
    execution_time = time.time() - start_time
    updater.print_statistics(total_changes, execution_time)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())