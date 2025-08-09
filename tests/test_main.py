"""Tests for the main module."""

import argparse
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from updatedirdates.main import (
    create_parser,
    main,
    print_colored,
    print_error,
    print_success,
    print_warning,
    setup_colorama,
    validate_directories,
)


class TestParser:
    """Test the argument parser."""

    def test_create_parser_basic(self):
        """Test parser creation with basic functionality."""
        parser = create_parser()
        assert isinstance(parser, argparse.ArgumentParser)

    def test_parser_help(self):
        """Test parser help output."""
        parser = create_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["--help"])

    def test_parser_version(self):
        """Test parser version output."""
        parser = create_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["--version"])

    def test_parser_required_directory(self):
        """Test parser requires at least one directory."""
        parser = create_parser()
        with pytest.raises(SystemExit):
            parser.parse_args([])

    def test_parser_single_directory(self, tmp_path):
        """Test parser with single directory."""
        parser = create_parser()
        args = parser.parse_args([str(tmp_path)])
        
        assert len(args.directories) == 1
        assert args.directories[0] == tmp_path
        assert not args.execute
        assert args.verbosity == 0

    def test_parser_multiple_directories(self, tmp_path):
        """Test parser with multiple directories."""
        dir1 = tmp_path / "dir1"
        dir2 = tmp_path / "dir2"
        dir1.mkdir()
        dir2.mkdir()
        
        parser = create_parser()
        args = parser.parse_args([str(dir1), str(dir2)])
        
        assert len(args.directories) == 2
        assert args.directories[0] == dir1
        assert args.directories[1] == dir2

    def test_parser_execute_flag(self, tmp_path):
        """Test parser execute flag."""
        parser = create_parser()
        args = parser.parse_args(["-x", str(tmp_path)])
        assert args.execute

    def test_parser_verbosity_levels(self, tmp_path):
        """Test parser verbosity levels."""
        parser = create_parser()
        
        # Test all valid verbosity levels
        for level in [0, 1, 2]:
            args = parser.parse_args(["-v", str(level), str(tmp_path)])
            assert args.verbosity == level

    def test_parser_invalid_verbosity(self, tmp_path):
        """Test parser rejects invalid verbosity levels."""
        parser = create_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["-v", "3", str(tmp_path)])

    def test_parser_combined_flags(self, tmp_path):
        """Test parser with multiple flags combined."""
        parser = create_parser()
        args = parser.parse_args(["-x", "-v", "2", str(tmp_path)])
        
        assert args.execute
        assert args.verbosity == 2
        assert len(args.directories) == 1


class TestColoredOutput:
    """Test colored output functions."""

    @patch('updatedirdates.main.print')
    def test_print_colored_no_color(self, mock_print):
        """Test print_colored without color."""
        print_colored("test message")
        mock_print.assert_called_once()

    @patch('updatedirdates.main.print')
    def test_print_colored_with_color(self, mock_print):
        """Test print_colored with color."""
        print_colored("test message", "RED")
        mock_print.assert_called_once()

    @patch('updatedirdates.main.print_colored')
    def test_print_error(self, mock_print_colored):
        """Test print_error function."""
        print_error("error message")
        mock_print_colored.assert_called_once_with("ERROR: error message", "\033[31m")

    @patch('updatedirdates.main.print_colored')
    def test_print_warning(self, mock_print_colored):
        """Test print_warning function."""
        print_warning("warning message")
        mock_print_colored.assert_called_once_with("WARNING: warning message", "\033[33m")

    @patch('updatedirdates.main.print_colored')
    def test_print_success(self, mock_print_colored):
        """Test print_success function."""
        print_success("success message")
        mock_print_colored.assert_called_once_with("success message", "\033[32m")


class TestDirectoryValidation:
    """Test directory validation."""

    def test_validate_existing_directory(self, tmp_path):
        """Test validation of existing directory."""
        test_dir = tmp_path / "test"
        test_dir.mkdir()
        
        result = validate_directories([test_dir])
        assert len(result) == 1
        assert result[0].resolve() == test_dir.resolve()

    def test_validate_multiple_directories(self, tmp_path):
        """Test validation of multiple directories."""
        dir1 = tmp_path / "dir1"
        dir2 = tmp_path / "dir2"
        dir1.mkdir()
        dir2.mkdir()
        
        result = validate_directories([dir1, dir2])
        assert len(result) == 2

    def test_validate_nonexistent_directory(self, tmp_path):
        """Test validation rejects non-existent directory."""
        nonexistent = tmp_path / "nonexistent"
        
        with patch('updatedirdates.main.print_error') as mock_error:
            result = validate_directories([nonexistent])
            assert len(result) == 0
            mock_error.assert_called_once()

    def test_validate_file_not_directory(self, tmp_path):
        """Test validation rejects file as directory."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")
        
        with patch('updatedirdates.main.print_error') as mock_error:
            result = validate_directories([test_file])
            assert len(result) == 0
            mock_error.assert_called_once()

    def test_validate_mixed_valid_invalid(self, tmp_path):
        """Test validation with mix of valid and invalid paths."""
        valid_dir = tmp_path / "valid"
        invalid_file = tmp_path / "invalid.txt"
        nonexistent = tmp_path / "nonexistent"
        
        valid_dir.mkdir()
        invalid_file.write_text("test")
        
        with patch('updatedirdates.main.print_error'):
            result = validate_directories([valid_dir, invalid_file, nonexistent])
            assert len(result) == 1
            assert result[0].resolve() == valid_dir.resolve()


class TestMainFunction:
    """Test the main function."""

    @patch('updatedirdates.main.setup_colorama')
    @patch('updatedirdates.main.DirectoryUpdater')
    def test_main_success(self, mock_updater_class, mock_setup, tmp_path):
        """Test main function success case."""
        test_dir = tmp_path / "test"
        test_dir.mkdir()
        
        # Mock the updater instance
        mock_updater = Mock()
        mock_updater.process_directory.return_value = 2
        mock_updater_class.return_value = mock_updater
        
        # Mock sys.argv
        with patch.object(sys, 'argv', ['updatedirdates', str(test_dir)]):
            result = main()
        
        assert result == 0
        mock_setup.assert_called_once()
        mock_updater.process_directory.assert_called_once()
        mock_updater.print_statistics.assert_called_once()

    @patch('updatedirdates.main.validate_directories')
    def test_main_no_valid_directories(self, mock_validate):
        """Test main function with no valid directories."""
        mock_validate.return_value = []
        
        with patch.object(sys, 'argv', ['updatedirdates', 'nonexistent']):
            result = main()
        
        assert result == 1

    @patch('updatedirdates.main.setup_colorama')
    @patch('updatedirdates.main.DirectoryUpdater')
    def test_main_keyboard_interrupt(self, mock_updater_class, mock_setup, tmp_path):
        """Test main function with keyboard interrupt."""
        test_dir = tmp_path / "test"
        test_dir.mkdir()
        
        # Mock the updater to raise KeyboardInterrupt
        mock_updater = Mock()
        mock_updater.process_directory.side_effect = KeyboardInterrupt()
        mock_updater_class.return_value = mock_updater
        
        with patch.object(sys, 'argv', ['updatedirdates', str(test_dir)]):
            result = main()
        
        assert result == 130

    @patch('updatedirdates.main.setup_colorama')
    @patch('updatedirdates.main.DirectoryUpdater')
    def test_main_unexpected_error(self, mock_updater_class, mock_setup, tmp_path):
        """Test main function with unexpected error."""
        test_dir = tmp_path / "test"
        test_dir.mkdir()
        
        # Mock the updater to raise an exception
        mock_updater = Mock()
        mock_updater.process_directory.side_effect = Exception("Test error")
        mock_updater_class.return_value = mock_updater
        
        with patch.object(sys, 'argv', ['updatedirdates', str(test_dir)]):
            result = main()
        
        assert result == 1

    @patch('updatedirdates.main.setup_colorama')
    @patch('updatedirdates.main.DirectoryUpdater')
    def test_main_with_execute_flag(self, mock_updater_class, mock_setup, tmp_path):
        """Test main function with execute flag."""
        test_dir = tmp_path / "test"
        test_dir.mkdir()
        
        mock_updater = Mock()
        mock_updater.process_directory.return_value = 1
        mock_updater_class.return_value = mock_updater
        
        with patch.object(sys, 'argv', ['updatedirdates', '-x', str(test_dir)]):
            result = main()
        
        assert result == 0
        # Verify updater was created with dry_run=False
        mock_updater_class.assert_called_once()
        args, kwargs = mock_updater_class.call_args
        assert kwargs['dry_run'] is False

    @patch('updatedirdates.main.setup_colorama')
    @patch('updatedirdates.main.DirectoryUpdater')
    def test_main_with_verbosity(self, mock_updater_class, mock_setup, tmp_path):
        """Test main function with verbosity setting."""
        test_dir = tmp_path / "test"
        test_dir.mkdir()
        
        mock_updater = Mock()
        mock_updater.process_directory.return_value = 0
        mock_updater_class.return_value = mock_updater
        
        with patch.object(sys, 'argv', ['updatedirdates', '-v', '2', str(test_dir)]):
            result = main()
        
        assert result == 0
        # Verify updater was created with verbosity=2
        mock_updater_class.assert_called_once()
        args, kwargs = mock_updater_class.call_args
        assert kwargs['verbosity'] == 2


class TestColoramaSetup:
    """Test colorama setup."""

    @patch('colorama.init')
    def test_setup_colorama(self, mock_init):
        """Test colorama initialization."""
        setup_colorama()
        mock_init.assert_called_once_with(autoreset=True)