from func.interface import control_interface


def test_interface_enable():
    status = control_interface(
        action="enable",
        interface="eth",
        timeout=15,
        interval=1,
    )

    assert status == "Up"


def test_interface_disable():
    status = control_interface(
        action="disable",
        interface="eth",
        timeout=15,
        interval=1,
    )

    assert status == "Disabled"


def test_interface_status():
    status = control_interface(
        action="status",
        interface="eth",
    )

    assert status in {"Up", "Disconnected", "Disabled"}