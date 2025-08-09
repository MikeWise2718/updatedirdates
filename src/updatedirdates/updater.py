"""Directory date updater implementation."""

import os
import stat
from pathlib import Path
from typing import Callable, Optional

from colorama import Fore


class DirectoryUpdater:
    """Handles updating directory modification dates to reflect latest files."""
    
    def __init__(
        self,
        verbosity: int = 0,
        dry_run: bool = True,
        print_colored: Optional[Callable[[str, str], None]] = None,
        print_error: Optional[Callable[[str], None]] = None,
        print_warning: Optional[Callable[[str], None]] = None,
        print_success: Optional[Callable[[str], None]] = None,
    ):
        """Initialize the DirectoryUpdater.
        
        Args:
            verbosity: Output verbosity level (0=quiet, 1=first level, 2=all)
            dry_run: If True, don't actually modify dates
            print_colored: Function to print colored messages
            print_error: Function to print error messages
            print_warning: Function to print warning messages
            print_success: Function to print success messages
        """
        self.verbosity = verbosity
        self.dry_run = dry_run
        self.print_colored = print_colored or self._default_print
        self.print_error = print_error or self._default_print
        self.print_warning = print_warning or self._default_print
        self.print_success = print_success or self._default_print
        
    def _default_print(self, message: str, color: str = "") -> None:
        """Default print function."""
        print(message)
        
    def get_latest_modification_time(self, directory: Path) -> tuple[float, int, int]:
        """Get the latest modification time from files directly in directory.
        If no files present, use latest modification time from subdirectories.
        
        Args:
            directory: Directory to scan
            
        Returns:
            Tuple of (latest_modification_time, dir_count, file_count)
        """
        latest_time = 0.0
        dir_count = 0
        file_count = 0
        subdirs = []
        
        try:
            # Only examine direct children of this directory, not recursive
            for item in directory.iterdir():
                if item.is_file():
                    try:
                        file_stat = item.stat()
                        latest_time = max(latest_time, file_stat.st_mtime)
                        file_count += 1
                    except (OSError, IOError) as e:
                        if self.verbosity >= 2:
                            self.print_warning(f"Could not stat file {item}: {e}")
                elif item.is_dir():
                    subdirs.append(item)
                    dir_count += 1
            
            # If no files found, use latest modification time from subdirectories
            if file_count == 0 and subdirs:
                for subdir in subdirs:
                    try:
                        subdir_stat = subdir.stat()
                        latest_time = max(latest_time, subdir_stat.st_mtime)
                    except (OSError, IOError) as e:
                        if self.verbosity >= 2:
                            self.print_warning(f"Could not stat directory {subdir}: {e}")
                            
        except (OSError, IOError) as e:
            self.print_error(f"Error reading directory {directory}: {e}")
            return directory.stat().st_mtime, 0, 0
            
        return latest_time, dir_count, file_count
        
    def should_update_directory(self, directory: Path) -> tuple[bool, float, float, int, int]:
        """Check if directory needs updating and return relevant times and counts.
        
        Args:
            directory: Directory to check
            
        Returns:
            Tuple of (needs_update, current_time, latest_time, dir_count, file_count)
        """
        try:
            current_stat = directory.stat()
            current_time = current_stat.st_mtime
            latest_time, dir_count, file_count = self.get_latest_modification_time(directory)
            
            # Consider updating if the latest file time differs from directory time
            # Add a small tolerance (1 second) to avoid floating point precision issues
            needs_update = abs(latest_time - current_time) > 1.0
            
            return needs_update, current_time, latest_time, dir_count, file_count
            
        except (OSError, IOError) as e:
            self.print_error(f"Error checking directory {directory}: {e}")
            return False, 0.0, 0.0, 0, 0
            
    def update_directory_date(self, directory: Path, new_time: float) -> bool:
        """Update directory modification time.
        
        Args:
            directory: Directory to update
            new_time: New modification time
            
        Returns:
            True if update was successful
        """
        if self.dry_run:
            return True
            
        try:
            # Update both access time and modification time
            os.utime(directory, (new_time, new_time))
            return True
        except (OSError, IOError) as e:
            self.print_error(f"Failed to update directory {directory}: {e}")
            return False
            
    def process_directory(self, root_directory: Path, depth: int = 0) -> int:
        """Process a directory and all its subdirectories.
        
        Args:
            root_directory: Root directory to process
            depth: Current depth for verbosity control
            
        Returns:
            Number of directories that were changed (or would be changed)
        """
        changes_made = 0
        
        # Process all subdirectories first (bottom-up approach)
        try:
            subdirs = [d for d in root_directory.iterdir() if d.is_dir()]
            for subdir in subdirs:
                changes_made += self.process_directory(subdir, depth + 1)
        except (OSError, IOError) as e:
            self.print_error(f"Error listing subdirectories in {root_directory}: {e}")
            return 0
            
        # Now process the current directory
        needs_update, current_time, latest_time, dir_count, file_count = self.should_update_directory(root_directory)
        
        # Print directory status based on verbosity level
        if self.verbosity >= 2 or (self.verbosity >= 1 and depth <= 1):
            count_info = f" (dirs:{dir_count} files:{file_count})"
            if needs_update:
                action = "Would update" if self.dry_run else "Updating"
                self.print_colored(
                    f"{action} {root_directory}: "
                    f"{self._format_timestamp(current_time)} -> "
                    f"{self._format_timestamp(latest_time)}{count_info}",
                    Fore.CYAN
                )
            else:
                if self.verbosity >= 2 or (self.verbosity >= 1 and depth <= 1):
                    self.print_colored(
                        f"Directory OK: {root_directory} "
                        f"({self._format_timestamp(current_time)}){count_info}",
                        ""
                    )
                    
        # Update directory if needed
        if needs_update:
            if self.update_directory_date(root_directory, latest_time):
                changes_made += 1
                if not self.dry_run and self.verbosity >= 1:
                    self.print_success(f"Updated {root_directory}")
            else:
                self.print_error(f"Failed to update {root_directory}")
                
        return changes_made
        
    def _format_timestamp(self, timestamp: float) -> str:
        """Format timestamp for display.
        
        Args:
            timestamp: Unix timestamp
            
        Returns:
            Formatted timestamp string
        """
        import datetime
        dt = datetime.datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
        
    def print_statistics(self, total_changes: int, execution_time: float) -> None:
        """Print final statistics.
        
        Args:
            total_changes: Number of directories changed
            execution_time: Total execution time in seconds
        """
        if self.dry_run:
            if total_changes == 0:
                self.print_success("No directory dates need updating.")
            elif total_changes == 1:
                self.print_colored(
                    f"1 directory date would be updated.",
                    Fore.CYAN
                )
            else:
                self.print_colored(
                    f"{total_changes} directory dates would be updated.",
                    Fore.CYAN
                )
        else:
            if total_changes == 0:
                self.print_success("No directory dates needed updating.")
            elif total_changes == 1:
                self.print_success("1 directory date was updated.")
            else:
                self.print_success(f"{total_changes} directory dates were updated.")
                
        if self.verbosity >= 1 or total_changes > 0:
            self.print_colored(f"Execution time: {execution_time:.2f} seconds", "")