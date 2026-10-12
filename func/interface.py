
import ctypes
import subprocess
import time


def is_admin() -> bool:
    """Check whether the current process has administrator privileges."""
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except (AttributeError, OSError):
        return False


def control_interface(
    action: str,
    interface: str,
    timeout: int = 15,
    interval: float = 1,
) -> str:
    """
    Control a Windows network adapter and wait for its expected state.

    Args:
        action: "enable", "disable", or "status".
        interface: Network adapter name, e.g. "Ethernet" or "Wi-Fi".
        timeout: Maximum time to wait for the expected state, in seconds.
        interval: Interval between status checks, in seconds.

    Returns:
        The final adapter status.
        "Up", "Disconnected", "Disabled"

    Raises:
        ValueError: If arguments are invalid.
        PermissionError: If administrator privileges are missing.
        RuntimeError: If the PowerShell operation fails.
        TimeoutError: If the expected status is not reached.
    """
    if not isinstance(interface, str) or not interface.strip():
        raise ValueError("interface must not be empty")

    if not isinstance(action, str):
        raise ValueError("action must be a string")

    action = action.lower().strip()
    interface = interface.strip()

    if action not in {"enable", "disable", "status"}:
        raise ValueError(
            "action must be enable, disable, or status"
        )

    if timeout <= 0:
        raise ValueError("timeout must be greater than 0")

    if interval <= 0:
        raise ValueError("interval must be greater than 0")

    if action in {"enable", "disable"} and not is_admin():
        raise PermissionError(
            "Administrator privileges are required. "
            "Run pytest from an elevated PowerShell."
        )

    safe_name = interface.replace("'", "''")

    if action == "status":
        expected_status = None
        operation = ""
    elif action == "enable":
        expected_status = "Up"
        operation = (
            f"Enable-NetAdapter -Name '{safe_name}' "
            "-Confirm:$false -ErrorAction Stop"
        )
    else:
        expected_status = "Disabled"
        operation = (
            f"Disable-NetAdapter -Name '{safe_name}' "
            "-Confirm:$false -ErrorAction Stop"
        )

    if operation:
        script = f"""
$ErrorActionPreference = 'Stop'
{operation}
if ($?) {{
    exit 0
}}
exit 1
"""
        result = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-NonInteractive",
                "-Command",
                script,
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            check=False,
        )

        if result.returncode != 0:
            message = result.stderr.strip() or result.stdout.strip()
            raise RuntimeError(
                f"Interface operation failed: {message}"
            )

    if expected_status is None:
        return _get_interface_status(interface)

    return wait_for_interface_status(
        interface=interface,
        expected_status=expected_status,
        timeout=timeout,
        interval=interval,
    )


def _get_interface_status(interface: str) -> str:
    """Get the current Windows network adapter status."""
    safe_name = interface.replace("'", "''")

    script = f"""
$ErrorActionPreference = 'Stop'
Get-NetAdapter -Name '{safe_name}' -ErrorAction Stop |
    Select-Object -ExpandProperty Status
"""

    result = subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-NonInteractive",
            "-Command",
            script,
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
        check=False,
    )

    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(
            f"Failed to get interface status: {message}"
        )

    status = result.stdout.strip()

    if not status:
        raise RuntimeError(
            f"No status returned for interface '{interface}'"
        )

    return status


def wait_for_interface_status(
    interface: str,
    expected_status: str,
    timeout: int = 15,
    interval: float = 1,
) -> str:
    """Poll the interface until its status matches the expected state."""
    deadline = time.monotonic() + timeout
    last_status = ""

    while True:
        last_status = _get_interface_status(interface)

        if last_status == expected_status:
            return last_status

        if time.monotonic() >= deadline:
            raise TimeoutError(
                f"Interface '{interface}' did not reach "
                f"'{expected_status}' within {timeout}s. "
                f"Last status: '{last_status}'"
            )

        time.sleep(interval)
