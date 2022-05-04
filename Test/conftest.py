import sys
from time import sleep
import os, signal
if sys.version_info.major >= 3:
    from Test.api import start_webserver
    import pytest

    @pytest.fixture(scope='package', autouse=True)
    def fastapi_start():
        p1, p2 = start_webserver()
        sleep(2)
        yield p1, p2
        os.kill(p1.pid, signal.SIGKILL)
        os.kill(p2.pid, signal.SIGKILL)