import os

import pytest
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ["MOLECULE_INVENTORY_FILE"]
).get_hosts("all")


@pytest.mark.parametrize(
    "package_name,os_type,os_release",
    [
        ("fetch-crl", "redhat", "9"),
        ("voms-clients-cpp", "redhat", "9"),
        ("voms-clients-java", "redhat", "9"),
    ],
)
def test_packages(host, package_name, os_type, os_release):
    if host.system_info.release == os_release and host.system_info.distribution:
        assert host.package(package_name).is_installed


@pytest.mark.parametrize(
    "executable",
    [
        "/usr/bin/voms-proxy-info",
        "/usr/bin/voms-proxy-init",
        "/usr/bin/voms-proxy-destroy",
    ],
)
def test_voms_executables(host, executable):
    assert host.file(executable).exists
    # assert host.file(executable).mode == '511'


@pytest.mark.parametrize("directory", ["/etc/vomses", "/etc/grid-security/vomsdir"])
def test_voms_dir(host, directory):
    assert host.file(directory).exists
    assert host.file(directory).is_directory


# Check that sample VO data is correct
@pytest.mark.parametrize(
    "voname,voms_server,dn",
    [
        # XXX: 2025-01-29: dteam and ops info missing in the operations portal
        # Info was added manually to the files/data.yml via #33
        (
            "ops",
            "voms-ops-auth.app.cern.ch",
            "/DC=ch/DC=cern/OU=computers/CN=ops-auth.web.cern.ch",
        ),
        (
            "dteam",
            "voms-dteam-auth.app.cern.ch",
            "/DC=ch/DC=cern/OU=computers/CN=dteam-auth.web.cern.ch",
        ),
        (
            "demo.fedcloud.egi.eu",
            "voms1.grid.cesnet.cz",
            "/DC=cz/DC=cesnet-ca/O=CESNET/CN=voms1.grid.cesnet.cz",
        ),
        (
            "fedcloud.egi.eu",
            "voms1.grid.cesnet.cz",
            "/DC=cz/DC=cesnet-ca/O=CESNET/CN=voms1.grid.cesnet.cz",
        ),
    ],
)
def test_vo_configuration(host, voname, voms_server, dn):
    vomses_filename = "/etc/vomses/" + voname + "-" + voms_server
    vomses_file = host.file(vomses_filename)
    assert vomses_file.exists
    assert vomses_file.contains(voname)
    assert vomses_file.contains(dn)
    assert vomses_file.contains(voms_server)
