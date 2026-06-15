import pytest
from unittest.mock import patch, mock_open
from automation.python.checks import (
    check_os_version,
    check_ram_and_disk,
    check_selinux,
    check_ports,
    CheckResult,
    CheckItem,
)
from automation.python.config import KscConfig


def test_checkresult_add_and_has_critical():
    result = CheckResult(items=[])
    assert len(result.items) == 0
    assert not result.has_critical

    item1 = CheckItem(name="test_ok", status="ok", message="All good")
    result.add(item1)
    assert len(result.items) == 1
    assert result.items[0] == item1
    assert not result.has_critical

    item2 = CheckItem(name="test_warn", status="warning", message="Watch out")
    result.add(item2)
    assert len(result.items) == 2
    assert not result.has_critical

    item3 = CheckItem(name="test_crit", status="critical", message="Failure")
    result.add(item3)
    assert len(result.items) == 3
    assert result.items[2] == item3
    assert result.has_critical


@pytest.fixture
def dummy_config():
    return KscConfig(
        db_host="127.0.0.1",
        db_port=5432,
        db_name="ksciam",
        db_user="kluser",
        db_password="123",
        db_sslmode="prefer",
        ksc_admin_password="123",
        ksc_license_path=None,
        web_port=443,
        selinux_expected_mode="enforcing",
    )


@patch(
    "builtins.open", new_callable=mock_open, read_data='ID="rocky"\nVERSION_ID="9.2"\n'
)
def test_check_os_version_supported(mock_file):
    result = check_os_version()
    assert not result.has_critical
    assert result.items[0].status == "ok"


@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data='ID="ubuntu"\nVERSION_ID="22.04"\n',
)
def test_check_os_version_unsupported(mock_file):
    result = check_os_version()
    assert result.has_critical
    assert "não suportado" in result.items[0].message.lower()


@patch("automation.python.checks._get_total_ram_mb", return_value=16384)
@patch("automation.python.checks._get_disk_gb", return_value=150)
def test_check_ram_and_disk_ok(mock_disk, mock_ram, dummy_config):
    result = check_ram_and_disk(dummy_config)
    assert not result.has_critical
    for item in result.items:
        assert item.status == "ok"


@patch("automation.python.checks.os.getenv", return_value="false")
@patch("automation.python.checks._get_total_ram_mb", return_value=4096)
@patch("automation.python.checks._get_disk_gb", return_value=50)
def test_check_ram_and_disk_critical(mock_disk, mock_ram, mock_getenv, dummy_config):
    result = check_ram_and_disk(dummy_config)
    assert result.has_critical
    assert (
        len([i for i in result.items if i.status == "critical"]) == 3
    )  # ram, opt, varopt


@patch("automation.python.checks.os.getenv", return_value="true")
@patch("automation.python.checks._get_total_ram_mb", return_value=4096)
@patch("automation.python.checks._get_disk_gb", return_value=50)
def test_check_ram_and_disk_ci_warning(mock_disk, mock_ram, mock_getenv, dummy_config):
    result = check_ram_and_disk(dummy_config)
    assert not result.has_critical
    assert (
        len([i for i in result.items if i.status == "warning"]) == 3
    )  # ram, opt, varopt



@patch("automation.python.checks._get_selinux_mode", return_value="enforcing")
def test_check_selinux_ok(mock_selinux, dummy_config):
    result = check_selinux(dummy_config)
    assert not result.has_critical
    assert result.items[0].status == "ok"


@patch("automation.python.checks._get_selinux_mode", return_value="permissive")
def test_check_selinux_warning(mock_selinux, dummy_config):
    result = check_selinux(dummy_config)
    assert not result.has_critical
    assert result.items[0].status == "warning"


@patch("automation.python.checks._get_selinux_mode", return_value="unknown")
def test_check_selinux_unknown(mock_selinux, dummy_config):
    result = check_selinux(dummy_config)
    assert not result.has_critical
    assert result.items[0].status == "warning"
    assert "Não foi possível determinar o modo" in result.items[0].message


@patch("automation.python.checks._get_listening_ports", return_value=[])
def test_check_ports_ok(mock_ports, dummy_config):
    result = check_ports(dummy_config)
    assert not result.has_critical
    for item in result.items:
        assert item.status == "ok"


@patch("automation.python.checks._get_listening_ports", return_value=[13000, 443])
def test_check_ports_critical(mock_ports, dummy_config):
    result = check_ports(dummy_config)
    assert result.has_critical
    # 13000 and 443 should be critical, 14000 should be ok
    critical_ports = [i.name for i in result.items if i.status == "critical"]
    assert "port_13000" in critical_ports
    assert "port_443" in critical_ports
