import sys
from unittest.mock import patch
from core import config


def test_default_config():
    """Test default values of configuration variables."""
    assert config.get_readonly_mode() is False
    assert config.get_transport() == 'stdio'


def test_parse_arguments_readonly():
    """Test parse_arguments with --readonly flag."""
    test_args = ["k8s_pilot.py", "--readonly"]
    with patch.object(sys, 'argv', test_args):
        config.parse_arguments()
        assert config.is_readonly_mode() is True
        assert config.get_readonly_mode() is True
        assert config.get_transport() == 'stdio'
        
    # Reset state for other tests
    config._readonly_mode = False
    config._transport = 'stdio'


def test_parse_arguments_transport():
    """Test parse_arguments with --transport flag."""
    test_args = ["k8s_pilot.py", "--transport", "streamable-http"]
    with patch.object(sys, 'argv', test_args):
        config.parse_arguments()
        assert config.is_readonly_mode() is False
        assert config.get_transport() == 'streamable-http'
        
    # Reset state for other tests
    config._readonly_mode = False
    config._transport = 'stdio'


def test_parse_arguments_both():
    """Test parse_arguments with both flags."""
    test_args = ["k8s_pilot.py", "--readonly", "--transport", "streamable-http"]
    with patch.object(sys, 'argv', test_args):
        config.parse_arguments()
        assert config.is_readonly_mode() is True
        assert config.get_transport() == 'streamable-http'
        
    # Reset state for other tests
    config._readonly_mode = False
    config._transport = 'stdio'
