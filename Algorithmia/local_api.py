import importlib
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/")
async def root():
    return HTMLResponse(
        """Algorithmia API Local Serve
        <br>Go to <a href="/docs">/docs</a> for swagger docs.
        """
    )

def create_endpoint(algoname):
    module = importlib.import_module(algoname)
    @app.get("/invocations")
    def invocations(data):
         return module.apply(data)
