from Test.api import start_webserver
import pytest


@pytest.fixture(scope='package', autouse=True)
def fastapi_start():
    p = start_webserver()
    yield p
    p.terminate()
