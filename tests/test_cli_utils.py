import pytest
from unittest.mock import Mock, patch
import os
from hkopenai_common.cli_utils import cli_main

@pytest.fixture(autouse=True)
def cleanup_env_vars():
    # Store original environment variables
    original_transport_mode = os.environ.get('TRANSPORT_MODE')
    original_host = os.environ.get('HOST')
    original_port = os.environ.get('PORT')

    yield

    # Restore original environment variables
    if original_transport_mode is not None:
        os.environ['TRANSPORT_MODE'] = original_transport_mode
    else:
        os.environ.pop('TRANSPORT_MODE', None)

    if original_host is not None:
        os.environ['HOST'] = original_host
    else:
        os.environ.pop('HOST', None)

    if original_port is not None:
        os.environ['PORT'] = original_port
    else:
        os.environ.pop('PORT', None)


def test_cli_main_defaults():
    mock_server_main = Mock()
    cli_main(mock_server_main, "Test Server", args_list=[])
    mock_server_main.assert_called_once_with(host="127.0.0.1", port=8000, sse=False)

def test_cli_main_command_line_args_override_defaults():
    mock_server_main = Mock()
    cli_main(mock_server_main, "Test Server", args_list=["--host", "192.168.1.1", "-p", "9000", "-s"])
    mock_server_main.assert_called_once_with(host="192.168.1.1", port=9000, sse=True)

def test_cli_main_env_vars_override_defaults():
    mock_server_main = Mock()
    os.environ['TRANSPORT_MODE'] = 'sse'
    os.environ['HOST'] = '0.0.0.0'
    os.environ['PORT'] = '7000'
    cli_main(mock_server_main, "Test Server", args_list=[])
    mock_server_main.assert_called_once_with(host="0.0.0.0", port=7000, sse=True)

def test_cli_main_command_line_args_override_env_vars():
    mock_server_main = Mock()
    os.environ['TRANSPORT_MODE'] = 'sse'
    os.environ['HOST'] = '0.0.0.0'
    os.environ['PORT'] = '7000'
    cli_main(mock_server_main, "Test Server", args_list=["--host", "192.168.1.1", "-p", "9000"])
    mock_server_main.assert_called_once_with(host="192.168.1.1", port=9000, sse=True)

def test_cli_main_invalid_port_env_var():
    mock_server_main = Mock()
    os.environ['PORT'] = 'invalid'
    cli_main(mock_server_main, "Test Server", args_list=[])
    mock_server_main.assert_called_once_with(host="127.0.0.1", port=8000, sse=False)

def test_cli_main_sse_env_var_only():
    mock_server_main = Mock()
    os.environ['TRANSPORT_MODE'] = 'sse'
    cli_main(mock_server_main, "Test Server", args_list=[])
    mock_server_main.assert_called_once_with(host="127.0.0.1", port=8000, sse=True)

def test_cli_main_sse_command_line_only():
    mock_server_main = Mock()
    cli_main(mock_server_main, "Test Server", args_list=["-s"])
    mock_server_main.assert_called_once_with(host="127.0.0.1", port=8000, sse=True)
