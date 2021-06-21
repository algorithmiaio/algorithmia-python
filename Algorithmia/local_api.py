import importlib
from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/")
async def root():
    return HTMLResponse(
        """Algorithmia API Local Serve
        <br>Go to <a href="/docs">/docs</a> for swagger docs.
        """
    )

@app.post("/v1/{username}/{algoname}/{version}")
async def throw_error(username, algoname, version):
    return Response("Internal Server Error", status_code=500)


def create_endpoint(algoname):
    module = importlib.import_module(algoname)
    @app.get("/invocations")
    def invocations(data):
         return module.apply(data)

