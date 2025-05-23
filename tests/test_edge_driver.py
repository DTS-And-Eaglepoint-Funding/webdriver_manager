import os
import re
import browsers
import pytest
from selenium import webdriver
from selenium.webdriver.edge.service import Service

from webdriver_manager.core.driver_cache import DriverCacheManager
from webdriver_manager.core.os_manager import PATTERN, ChromeType, OperationSystemManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager


def test_edge_manager_with_selenium():
    options = webdriver.EdgeOptions()
    options.binary_location = browsers.get("msedge")["path"]
    driver_path = EdgeChromiumDriverManager().install()
    driver = webdriver.Edge(service=Service(driver_path), options=options)
    driver.get("http://automation-remarks.com")
    driver.quit()


@pytest.mark.filterwarnings("ignore:Unverified HTTPS request:urllib3.exceptions.InsecureRequestWarning")
def test_driver_with_ssl_verify_disabled_can_be_downloaded(ssl_verify_enable):
    os.environ['WDM_SSL_VERIFY'] = '0'
    custom_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "ssl_disabled",
    )
    driver_path = EdgeChromiumDriverManager(cache_manager=DriverCacheManager(custom_path)).install()
    os.environ['WDM_SSL_VERIFY'] = '1'
    assert os.path.exists(driver_path)


def test_edge_manager_with_wrong_version():
    with pytest.raises(ValueError) as ex:
        EdgeChromiumDriverManager(
            version="0.2",
            os_system_manager=OperationSystemManager("win64")
        ).install()

    assert (
               "There is no such driver by url "
               "https://msedgedriver.azureedge.net/0.2/edgedriver_win64.zip"
           ) in ex.value.args[0]


@pytest.mark.parametrize('os_type', ['win32', 'win64', 'mac64', 'linux64'])
@pytest.mark.parametrize('specific_version', ['101.0.1210.53'])
def test_edge_with_specific_version(os_type, specific_version):
    bin_path = EdgeChromiumDriverManager(
        version=specific_version,
        os_system_manager=OperationSystemManager(os_type),
    ).install()
    assert os.path.exists(bin_path)


@pytest.mark.parametrize('os_type', ['win32', 'win64', 'mac64', 'linux64'])
@pytest.mark.parametrize('specific_version', ['101.0.1210.53'])
def test_can_get_edge_driver_from_cache(os_type, specific_version):
    EdgeChromiumDriverManager(
        version=specific_version,
        os_system_manager=OperationSystemManager(os_type),
    ).install()
    driver_path = EdgeChromiumDriverManager(
        version=specific_version,
        os_system_manager=OperationSystemManager(os_type)
    ).install()
    assert os.path.exists(driver_path)


def test_get_stable_release_version():
    pattern = PATTERN[ChromeType.MSEDGE]
    edge_driver = EdgeChromiumDriverManager(
    ).driver

    version = edge_driver.get_stable_release_version()
    version = re.search(pattern, version).group(0)

    assert len(version.split('.')) == 3, (
        f"version '{version}' doesn't match version's count parts"
    )
