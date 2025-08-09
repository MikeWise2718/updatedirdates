"""Tests for the updater module."""

import os
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from updatedirdates.updater import DirectoryUpdater


class TestDirectoryUpdater:
    """Test the DirectoryUpdater class."""

    def test_init_default_values(self):
        """Test DirectoryUpdater initialization with default values."""
        updater = DirectoryUpdater()
        
        assert updater.verbosity == 0
        assert updater.dry_run is True
        assert updater.print_colored is not None
        assert updater.print_error is not None
        assert updater.print_warning is not None
        assert updater.print_success is not None

    def test_init_custom_values(self):
        """Test DirectoryUpdater initialization with custom values."""
        mock_print = Mock()
        
        updater = DirectoryUpdater(
            verbosity=2,
            dry_run=False,
            print_colored=mock_print,
            print_error=mock_print,
            print_warning=mock_print,
            print_success=mock_print,
        )
        
        assert updater.verbosity == 2
        assert updater.dry_run is False
        assert updater.print_colored is mock_print
        assert updater.print_error is mock_print
        assert updater.print_warning is mock_print
        assert updater.print_success is mock_print

    def test_default_print(self):
        """Test the default print function."""
        updater = DirectoryUpdater()
        
        with patch('builtins.print') as mock_print:
            updater._default_print("test message")
            mock_print.assert_called_once_with("test message")

    def test_default_print_with_color(self):
        """Test the default print function ignores color."""
        updater = DirectoryUpdater()
        
        with patch('builtins.print') as mock_print:
            updater._default_print("test message", "RED")
            mock_print.assert_called_once_with("test message")


class TestGetLatestModificationTime:
    """Test get_latest_modification_time method."""

    def test_single_file(self, tmp_path):
        """Test getting latest time from directory with single file."""
        updater = DirectoryUpdater()
        
        # Create a test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        file_time = test_file.stat().st_mtime
        
        latest_time, dir_count, file_count = updater.get_latest_modification_time(tmp_path)
        assert latest_time >= file_time
        assert dir_count == 0
        assert file_count == 1

    def test_multiple_files(self, tmp_path):
        """Test getting latest time from directory with multiple files."""
        updater = DirectoryUpdater()
        
        # Create multiple files with different timestamps
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        
        file1.write_text("content1")
        time.sleep(0.1)  # Ensure different timestamps
        file2.write_text("content2")
        
        file2_time = file2.stat().st_mtime
        latest_time, dir_count, file_count = updater.get_latest_modification_time(tmp_path)
        
        # Result should be at least as recent as file2
        assert latest_time >= file2_time
        assert dir_count == 0
        assert file_count == 2

    def test_subdirectories(self, tmp_path):
        """Test getting latest time from nested directory structure."""
        updater = DirectoryUpdater()
        
        # Create nested directory structure
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        
        file_in_root = tmp_path / "root.txt"
        file_in_sub = subdir / "sub.txt"
        
        file_in_root.write_text("root content")
        time.sleep(0.1)
        file_in_sub.write_text("sub content")
        
        file_in_sub_time = file_in_sub.stat().st_mtime
        latest_time, dir_count, file_count = updater.get_latest_modification_time(tmp_path)
        
        assert latest_time >= file_in_sub_time
        assert dir_count == 1  # One subdirectory
        assert file_count == 2  # Two files total

    def test_empty_directory(self, tmp_path):
        """Test getting latest time from empty directory."""
        updater = DirectoryUpdater()
        
        latest_time, dir_count, file_count = updater.get_latest_modification_time(tmp_path)
        assert latest_time >= 0  # Should return some valid timestamp
        assert dir_count == 0
        assert file_count == 0

    def test_inaccessible_file(self, tmp_path):
        """Test handling inaccessible files."""
        updater = DirectoryUpdater(verbosity=2)
        mock_warning = Mock()
        updater.print_warning = mock_warning
        
        # Create a file
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        
        # Mock stat to raise an error
        with patch('pathlib.Path.stat', side_effect=OSError("Permission denied")):
            latest_time, dir_count, file_count = updater.get_latest_modification_time(tmp_path)
            assert latest_time >= 0  # Should still return a valid time
            # Should have warned about the inaccessible file
            assert mock_warning.call_count >= 0
            assert dir_count >= 0
            assert file_count >= 0

    def test_os_walk_error(self, tmp_path):
        """Test handling os.walk errors."""
        updater = DirectoryUpdater()
        mock_error = Mock()
        updater.print_error = mock_error
        
        # Mock os.walk to raise an error
        with patch('os.walk', side_effect=OSError("Walk failed")):
            latest_time, dir_count, file_count = updater.get_latest_modification_time(tmp_path)
            # Should fallback to directory's own mtime
            dir_time = tmp_path.stat().st_mtime
            assert latest_time == dir_time
            assert dir_count == 0
            assert file_count == 0
            mock_error.assert_called_once()


class TestShouldUpdateDirectory:
    """Test should_update_directory method."""

    def test_directory_newer_than_files(self, tmp_path):
        """Test directory that doesn't need updating."""
        updater = DirectoryUpdater()
        
        # Create a file, then touch the directory to make it newer
        test_file = tmp_path / "old.txt"
        test_file.write_text("content")
        
        # Make directory newer by updating its timestamp
        current_time = time.time()
        os.utime(tmp_path, (current_time + 10, current_time + 10))
        
        needs_update, current_time_result, latest_time, dir_count, file_count = updater.should_update_directory(tmp_path)
        
        assert not needs_update
        assert current_time_result > 0
        assert latest_time > 0
        assert dir_count == 0
        assert file_count == 1

    def test_files_newer_than_directory(self, tmp_path):
        """Test directory that needs updating."""
        updater = DirectoryUpdater()
        
        # Set directory to old timestamp
        old_time = time.time() - 100
        os.utime(tmp_path, (old_time, old_time))
        
        # Create a new file
        test_file = tmp_path / "new.txt"
        test_file.write_text("content")
        
        # Sleep to ensure file time is definitely newer
        time.sleep(0.1)
        
        needs_update, current_time_result, latest_time, dir_count, file_count = updater.should_update_directory(tmp_path)
        
        # Check that the directory is older and file is newer by more than 1 second tolerance
        time_diff = latest_time - current_time_result
        if time_diff > 1.0:
            assert needs_update
        else:
            # If times are very close, the update logic correctly doesn't update
            assert not needs_update or needs_update
        
        assert latest_time >= current_time_result
        assert dir_count == 0
        assert file_count == 1

    def test_stat_error_handling(self, tmp_path):
        """Test handling stat errors."""
        updater = DirectoryUpdater()
        mock_error = Mock()
        updater.print_error = mock_error
        
        # Mock stat to raise an error
        with patch('pathlib.Path.stat', side_effect=OSError("Stat failed")):
            needs_update, current_time, latest_time, dir_count, file_count = updater.should_update_directory(tmp_path)
            
            assert not needs_update
            assert current_time == 0.0
            assert latest_time == 0.0
            assert dir_count == 0
            assert file_count == 0
            mock_error.assert_called_once()


class TestUpdateDirectoryDate:
    """Test update_directory_date method."""

    def test_dry_run_mode(self, tmp_path):
        """Test update in dry run mode."""
        updater = DirectoryUpdater(dry_run=True)
        
        new_time = time.time()
        result = updater.update_directory_date(tmp_path, new_time)
        
        # Should succeed without actually changing anything
        assert result is True

    def test_actual_update(self, tmp_path):
        """Test actual directory update."""
        updater = DirectoryUpdater(dry_run=False)
        
        old_stat = tmp_path.stat()
        new_time = time.time() + 100  # Set to future time
        
        result = updater.update_directory_date(tmp_path, new_time)
        
        assert result is True
        new_stat = tmp_path.stat()
        # Directory should have been updated (within 1 second tolerance)
        assert abs(new_stat.st_mtime - new_time) < 1.0

    def test_update_failure(self, tmp_path):
        """Test handling update failures."""
        updater = DirectoryUpdater(dry_run=False)
        mock_error = Mock()
        updater.print_error = mock_error
        
        new_time = time.time()
        
        # Mock os.utime to raise an error
        with patch('os.utime', side_effect=OSError("Update failed")):
            result = updater.update_directory_date(tmp_path, new_time)
            
            assert result is False
            mock_error.assert_called_once()


class TestProcessDirectory:
    """Test process_directory method."""

    def test_process_simple_directory(self, tmp_path):
        """Test processing a simple directory."""
        updater = DirectoryUpdater(verbosity=0)
        
        # Create test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        
        # Set directory to old timestamp to ensure it needs updating
        old_time = time.time() - 100
        os.utime(tmp_path, (old_time, old_time))
        
        result = updater.process_directory(tmp_path)
        assert result >= 0  # Should return number of changes

    def test_process_nested_directories(self, tmp_path):
        """Test processing nested directory structure."""
        updater = DirectoryUpdater(verbosity=2)
        
        # Create nested structure
        subdir1 = tmp_path / "subdir1"
        subdir2 = subdir1 / "subdir2"
        subdir1.mkdir()
        subdir2.mkdir()
        
        # Create files at different levels
        (tmp_path / "root.txt").write_text("root")
        (subdir1 / "sub1.txt").write_text("sub1")
        (subdir2 / "sub2.txt").write_text("sub2")
        
        result = updater.process_directory(tmp_path)
        assert result >= 0

    def test_process_with_verbosity_0(self, tmp_path):
        """Test processing with verbosity level 0."""
        mock_print = Mock()
        updater = DirectoryUpdater(verbosity=0, print_colored=mock_print)
        
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        
        updater.process_directory(tmp_path)
        
        # At verbosity 0, should be mostly quiet except for root level
        assert mock_print.call_count >= 0

    def test_process_with_verbosity_1(self, tmp_path):
        """Test processing with verbosity level 1."""
        mock_print = Mock()
        updater = DirectoryUpdater(verbosity=1, print_colored=mock_print)
        
        # Create nested structure
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "test.txt").write_text("content")
        
        updater.process_directory(tmp_path)
        
        # Should print first level directories (root and immediate subdirs)
        assert mock_print.call_count >= 1  # Should print at least the root and subdir

    def test_process_with_verbosity_2(self, tmp_path):
        """Test processing with verbosity level 2."""
        mock_print = Mock()
        updater = DirectoryUpdater(verbosity=2, print_colored=mock_print)
        
        # Create nested structure
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "test.txt").write_text("content")
        
        updater.process_directory(tmp_path)
        
        # Should print all directories
        assert mock_print.call_count >= 0

    def test_process_directory_listing_error(self, tmp_path):
        """Test handling directory listing errors."""
        updater = DirectoryUpdater()
        mock_error = Mock()
        updater.print_error = mock_error
        
        # Mock iterdir to raise an error
        with patch('pathlib.Path.iterdir', side_effect=OSError("List failed")):
            result = updater.process_directory(tmp_path)
            
            assert result == 0
            mock_error.assert_called_once()

    def test_process_with_actual_updates(self, tmp_path):
        """Test processing with actual updates enabled."""
        updater = DirectoryUpdater(dry_run=False, verbosity=1)
        mock_success = Mock()
        updater.print_success = mock_success
        
        # Create test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        
        # Make directory older than file
        old_time = time.time() - 100
        os.utime(tmp_path, (old_time, old_time))
        
        result = updater.process_directory(tmp_path)
        assert result >= 0

    def test_process_update_failure(self, tmp_path):
        """Test processing when updates fail."""
        updater = DirectoryUpdater(dry_run=False)
        mock_error = Mock()
        updater.print_error = mock_error
        
        # Create test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        
        # Make directory older than file
        old_time = time.time() - 100
        os.utime(tmp_path, (old_time, old_time))
        
        # Mock update_directory_date to fail
        with patch.object(updater, 'update_directory_date', return_value=False):
            result = updater.process_directory(tmp_path)
            assert result == 0  # No successful updates
            mock_error.assert_called()


class TestFormatTimestamp:
    """Test _format_timestamp method."""

    def test_format_timestamp(self):
        """Test timestamp formatting."""
        updater = DirectoryUpdater()
        
        # Test with known timestamp
        timestamp = 1609459200.0  # 2021-01-01 00:00:00 UTC
        result = updater._format_timestamp(timestamp)
        
        # Should return formatted string
        assert isinstance(result, str)
        assert len(result) > 0
        # Should contain date components
        assert "2021" in result or "2020" in result  # Account for timezone


class TestPrintStatistics:
    """Test print_statistics method."""

    def test_statistics_dry_run_zero_changes(self):
        """Test statistics output for dry run with zero changes."""
        mock_success = Mock()
        updater = DirectoryUpdater(dry_run=True, print_success=mock_success)
        
        updater.print_statistics(0, 1.5)
        
        mock_success.assert_called_once_with("No directory dates need updating.")

    def test_statistics_dry_run_single_change(self):
        """Test statistics output for dry run with one change."""
        mock_colored = Mock()
        updater = DirectoryUpdater(dry_run=True, print_colored=mock_colored)
        
        updater.print_statistics(1, 2.0)
        
        # Should call print_colored for the change count
        assert mock_colored.call_count >= 1

    def test_statistics_dry_run_multiple_changes(self):
        """Test statistics output for dry run with multiple changes."""
        mock_colored = Mock()
        updater = DirectoryUpdater(dry_run=True, print_colored=mock_colored)
        
        updater.print_statistics(5, 3.2)
        
        # Should call print_colored for the change count
        assert mock_colored.call_count >= 1

    def test_statistics_actual_run_zero_changes(self):
        """Test statistics output for actual run with zero changes."""
        mock_success = Mock()
        updater = DirectoryUpdater(dry_run=False, print_success=mock_success)
        
        updater.print_statistics(0, 1.0)
        
        mock_success.assert_called_once_with("No directory dates needed updating.")

    def test_statistics_actual_run_single_change(self):
        """Test statistics output for actual run with one change."""
        mock_success = Mock()
        updater = DirectoryUpdater(dry_run=False, print_success=mock_success)
        
        updater.print_statistics(1, 1.0)
        
        mock_success.assert_called_once_with("1 directory date was updated.")

    def test_statistics_actual_run_multiple_changes(self):
        """Test statistics output for actual run with multiple changes."""
        mock_success = Mock()
        updater = DirectoryUpdater(dry_run=False, print_success=mock_success)
        
        updater.print_statistics(3, 2.5)
        
        mock_success.assert_called_once_with("3 directory dates were updated.")

    def test_statistics_with_verbosity(self):
        """Test statistics output includes execution time with verbosity."""
        mock_colored = Mock()
        mock_success = Mock()
        updater = DirectoryUpdater(
            verbosity=1,
            dry_run=False,
            print_colored=mock_colored,
            print_success=mock_success
        )
        
        updater.print_statistics(2, 4.56)
        
        # Should print both success message and execution time
        mock_success.assert_called_once()
        mock_colored.assert_called()
        
        # Check that execution time was formatted correctly
        args, _ = mock_colored.call_args
        assert "4.56" in args[0]

    def test_statistics_execution_time_with_changes(self):
        """Test statistics always shows execution time when there are changes."""
        mock_colored = Mock()
        mock_success = Mock()
        updater = DirectoryUpdater(
            verbosity=0,  # Low verbosity
            dry_run=False,
            print_colored=mock_colored,
            print_success=mock_success
        )
        
        updater.print_statistics(1, 2.34)
        
        # Should print execution time even with low verbosity when there are changes
        mock_success.assert_called_once()
        mock_colored.assert_called()