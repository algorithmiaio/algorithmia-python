import importlib
from fastapi import FastAPI, Response

app = FastAPI()

@app.post("/v1/{username}/{algoname}/{version}")
async def throw_error(username, algoname, version):
    return Response("Internal Server Error", status_code=500)


def create_endpoint(algoname):
    module = importlib.import_module(algoname)
    @app.get("/invocations")
    def invocations(data):
         return module.apply(data)