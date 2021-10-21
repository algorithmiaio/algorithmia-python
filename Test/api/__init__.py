import importlib
from fastapi import FastAPI, Response, Request
import json
import base64
app = FastAPI()

@app.post("/v1/algo/{username}/{algoname}")
async def process_algo_req(request: Request, username, algoname):
    if algoname == "500":
        return Response("Internal Server Error", status_code=500)
    elif algoname == "raise_exception":
        return {"error": {"message":"This is an exception"}}
    else:
        content_type = request.headers['Content-Type']
        metadata = {"request_id": "req-55c0480d-6af3-4a21-990a-5c51d29f5725", "duration": 0.000306774}
        request = await request.body()
        if content_type != "application/octet-stream":
            request = request.decode('utf-8')
        if content_type == "text/plain":
            metadata['content_type'] = "text"
        elif content_type == "application/json":
            request = json.loads(request)
            metadata['content_type'] = "json"
        else:
            metadata['content_type'] = "binary"
            request = base64.b64encode(request)
        output = {"result": request, "metadata": metadata}
        return output

@app.get("/v1/algorithms/{username}/{algoname}/builds/{buildid}")
async def get_build_id(username, algoname, buildid):
    return {"status": "succeeded", "build_id": buildid, "commit_sha": "bcdadj",
            "started_at": "2021-09-27T22:54:20.786Z", "finished_at": "2021-09-27T22:54:40.898Z", "version_info": {"semantic_version":"0.1.1"}}

@app.get("/v1/algorithms/{username}/{algoname}/builds/{buildid}/logs")
async def get_build_log(username, algoname, buildid):
    return {"logs": "This is a log"}

@app.get("/v1/algorithms/{username}/{algoname}/scm/status")
async def get_scm_status(username, algoname):
    return {"scm_connection_status": "active"}



def create_endpoint(algoname):
    module = importlib.import_module(algoname)
    @app.get("/invocations")
    def invocations(data):
         return module.apply(data)

