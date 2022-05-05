import sys
from time import sleep
import os, signal
if sys.version_info.major >= 3:
    from Test.api import start_webserver_reg, start_webserver_self_signed
    import pytest

    @pytest.fixture(scope='package', autouse=True)
    def fastapi_start():
        p_reg = start_webserver_reg()
        p_self_signed = start_webserver_self_signed()
        sleep(2)
        yield p_reg, p_self_signed
        os.kill(p_reg.pid, signal.SIGKILL)
        os.kill(p_self_signed.pid, signal.SIGKILL)