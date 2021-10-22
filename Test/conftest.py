import sys
if sys.version_info.major >= 3:
    from Test.api import start_webserver
    import pytest


    @pytest.fixture(scope='package', autouse=True)
    def fastapi_start():
        p = start_webserver()
        yield p
        p.terminate()
