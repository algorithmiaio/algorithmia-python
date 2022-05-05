from fastapi import FastAPI, Request
from typing import Optional
from fastapi.responses import Response
import json
import base64
from multiprocessing import Process
import uvicorn

self_signed_app = FastAPI()


def start_webserver_self_signed():
    def _start_webserver():
        uvicorn.run(self_signed_app, host="127.0.0.1", port=8090, log_level="debug",
                    ssl_certfile="Test/resources/cert.cert", ssl_keyfile="Test/resources/cert.key")

    p = Process(target=_start_webserver)
    p.start()
    return p

@self_signed_app.post("/v1/algo/{username}/{algoname}")
async def process_algo_req(request: Request, username, algoname, output: Optional[str] = None):
    metadata = {"request_id": "req-55c0480d-6af3-4a21-990a-5c51d29f5725", "duration": 0.000306774}
    content_type = request.headers['Content-Type']
    auth = request.headers.get('Authorization', None)
    if auth is None:
        return {"error": {"message": "authorization required"}}
    request = await request.body()
    if output and output == "void":
        return {"async": "abcd123", "request_id": "req-55c0480d-6af3-4a21-990a-5c51d29f5725"}
    elif output and output == "raw":
        return Response(request.decode(), status_code=200)
    elif algoname == "500":
        return Response("Internal Server Error", status_code=500)
    elif algoname == "raise_exception":
        return {"error": {"message": "This is an exception"}}
    else:
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


@self_signed_app.post("/v1/algo/{username}/{algoname}/{githash}")
async def process_hello_world(request: Request, username, algoname, githash):
    metadata = {"request_id": "req-55c0480d-6af3-4a21-990a-5c51d29f5725", "duration": 0.000306774,
                'content_type': "text"}
    request = await request.body()
    request = request.decode('utf-8')
    return {"result": f"hello {request}", "metadata": metadata}


### Algorithm Routes
@self_signed_app.get("/v1/algorithms/{username}/{algoname}/builds/{buildid}")
async def get_build_id(username, algoname, buildid):
    return {"status": "succeeded", "build_id": buildid, "commit_sha": "bcdadj",
            "started_at": "2021-09-27T22:54:20.786Z", "finished_at": "2021-09-27T22:54:40.898Z",
            "version_info": {"semantic_version": "0.1.1"}}


@self_signed_app.get("/v1/algorithms/{username}/{algoname}/builds/{buildid}/logs")
async def get_build_log(username, algoname, buildid):
    return {"logs": "This is a log"}

@self_signed_app.get("/v1/algorithms/{username}/{algoname}/scm/status")
async def get_scm_status(username, algoname):
    return {"scm_connection_status": "active"}


@self_signed_app.get("/v1/algorithms/{algo_id}/errors")
async def get_algo_errors(algo_id):
    return {"error": {"message": "not found"}}


@self_signed_app.post("/v1/algorithms/{username}")
async def create_algorithm(request: Request, username):
    payload = await request.json()
    return {"id": "2938ca9f-54c8-48cd-b0d0-0fb7f2255cdc", "name": payload["name"],
            "details": {"label": payload["details"]["label"]},
            "settings": {"algorithm_callability": "private", "source_visibility": "open",
                         "package_set": "tensorflow-gpu-2.3-python38", "license": "apl", "network_access": "isolated",
                         "pipeline_enabled": False, "insights_enabled": False,
                         "algorithm_environment": "fd980f4f-1f1c-4b2f-a128-d60b40c6567a"},
            "source": {"scm": {"id": "internal", "provider": "internal", "default": True, "enabled": True}},
            "resource_type": "algorithm"}


@self_signed_app.post("/v1/algorithms/{username}/{algoname}/compile")
async def compile_algorithm(username, algoname):
    return {
        "id": "2938ca9f-54c8-48cd-b0d0-0fb7f2255cdc",
        "name": algoname,
        "details": {
            "summary": "Example Summary",
            "label": "QA",
            "tagline": "Example Tagline"
        },
        "settings": {
            "algorithm_callability": "private",
            "source_visibility": "open",
            "package_set": "tensorflow-gpu-2.3-python38",
            "license": "apl",
            "network_access": "isolated",
            "pipeline_enabled": False,
            "insights_enabled": False,
            "algorithm_environment": "fd980f4f-1f1c-4b2f-a128-d60b40c6567a"
        },
        "version_info": {
            "git_hash": "e85db9bca2fad519f540b445f30d12523e4dec9c",
            "version_uuid": "1d9cb91d-11ca-49cb-a7f4-28f67f277654"
        },
        "source": {
            "scm": {
                "id": "internal",
                "provider": "internal",
                "default": True,
                "enabled": True
            }
        },
        "compilation": {
            "successful": True,
            "output": ""
        },
        "self_link": f"http://localhost:8080/v1/algorithms/{username}/{algoname}/versions/e85db9bca2fad519f540b445f30d12523e4dec9c",
        "resource_type": "algorithm"
    }


@self_signed_app.post("/v1/algorithms/{username}/{algoname}/versions")
async def publish_algorithm(request: Request, username, algoname):
    return {"id": "2938ca9f-54c8-48cd-b0d0-0fb7f2255cdc", "name": algoname,
            "details": {"summary": "Example Summary", "label": "QA", "tagline": "Example Tagline"},
            "settings": {"algorithm_callability": "private", "source_visibility": "open",
                         "package_set": "tensorflow-gpu-2.3-python38", "license": "apl", "network_access": "isolated",
                         "pipeline_enabled": False, "insights_enabled": False,
                         "algorithm_environment": "fd980f4f-1f1c-4b2f-a128-d60b40c6567a"},
            "version_info": {"semantic_version": "0.1.0", "git_hash": "e85db9bca2fad519f540b445f30d12523e4dec9c",
                             "release_notes": "created programmatically", "sample_input": "payload",
                             "version_uuid": "e85db9bca2fad519f540b445f30d12523e4dec9c"},
            "source": {"scm": {"id": "internal", "provider": "internal", "default": True, "enabled": True}},
            "compilation": {"successful": True},
            "self_link": f"http://localhost:8080/v1/algorithms/{username}/{algoname}/versions/e85db9bca2fad519f540b445f30d12523e4dec9c",
            "resource_type": "algorithm"}


@self_signed_app.get("/v1/algorithms/{username}/{algoname}/versions/{algohash}")
async def get_algorithm_info(username, algoname, algohash):
    return {
        "id": "2938ca9f-54c8-48cd-b0d0-0fb7f2255cdc",
        "name": algoname,
        "details": {
            "summary": "Example Summary",
            "label": "QA",
            "tagline": "Example Tagline"
        },
        "settings": {
            "algorithm_callability": "private",
            "source_visibility": "open",
            "language": "python3",
            "environment": "gpu",
            "package_set": "tensorflow-gpu-2.3-python38",
            "license": "apl",
            "network_access": "isolated",
            "pipeline_enabled": False,
            "insights_enabled": False,
            "algorithm_environment": "fd980f4f-1f1c-4b2f-a128-d60b40c6567a"
        },
        "version_info": {
            "semantic_version": "0.1.0",
            "git_hash": algohash,
            "release_notes": "created programmatically",
            "sample_input": "\"payload\"",
            "sample_output": "Exception encountered while running sample input",
            "version_uuid": "1d9cb91d-11ca-49cb-a7f4-28f67f277654"
        },
        "source": {
            "scm": {
                "id": "internal",
                "provider": "internal",
                "default": True,
                "enabled": True
            }
        },
        "compilation": {
            "successful": True,
            "output": ""
        },
        "resource_type": "algorithm"
    }


### Admin Routes
@self_signed_app.post("/v1/users")
async def create_user(request: Request):
    payload = await request.body()
    data = json.loads(payload)
    username = data['username']
    email = data['email']
    return {
        "id": "1e5c89ab-3d5c-4bad-b8a3-6c8a294d4418",
        "username": username,
        "email": email,
        "fullname": username,
        "self_link": f"http://localhost:8080/v1/users/{username}", "resource_type": "user"
    }


@self_signed_app.get("/v1/users/{user_id}/errors")
async def get_user_errors(user_id):
    return []


@self_signed_app.get("/v1/organization/types")
async def get_org_types():
    return [
        {"id": "d0c85ea6-ddfa-11ea-a0c8-12a811be4db3", "name": "basic"},
        {"id": "d0bff917-ddfa-11ea-a0c8-12a811be4db3", "name": "legacy"},
        {"id": "d0c9d825-ddfa-11ea-a0c8-12a811be4db3", "name": "pro"}
    ]


@self_signed_app.post("/v1/organizations")
async def create_org(request: Request):
    payload = await request.body()
    data = json.loads(payload)
    org_name = data["org_name"]
    org_email = data["org_email"]
    return {"id": "55073c92-5f8e-4d7e-a14d-568f94924fd9",
            "org_name": org_name,
            "org_label": "some label",
            "org_contact_name": "Some owner",
            "org_email": org_email,
            "org_created_at": "2021-10-22T16:41:32",
            "org_url": None,
            "type_id": "d0c85ea6-ddfa-11ea-a0c8-12a811be4db3",
            "stripe_customer_id": None,
            "external_admin_group": None,
            "external_member_group": None,
            "external_id": None,
            "owner_ids": None,
            "resource_type": "organization",
            "self_link": "http://localhost:8080/v1/organizations/a_myOrg1542"
            }


@self_signed_app.put("/v1/organizations/{orgname}/members/{username}")
async def add_user_to_org(orgname, username):
    return Response(status_code=200)


@self_signed_app.get("/v1/organizations/{orgname}/errors")
async def org_errors(orgname):
    return []


@self_signed_app.put("/v1/organizations/{org_name}")
async def edit_org(org_name):
    return Response(status_code=204)


@self_signed_app.get("/v1/organizations/{org_name}")
async def get_org_by_name(org_name):
    return {
        "id": "55073c92-5f8e-4d7e-a14d-568f94924fd9",
        "org_name": org_name,
        "org_label": "some label",
        "org_contact_name": "Some owner",
        "org_email": "a_myOrg1542@algo.com",
        "org_created_at": "2021-10-22T16:41:32",
        "org_url": None,
        "type_id": "d0c85ea6-ddfa-11ea-a0c8-12a811be4db3",
        "stripe_customer_id": None,
        "external_admin_group": None,
        "external_member_group": None,
        "external_id": None,
        "owner_ids": None,
        "resource_type": "organization",
        "self_link": "http://localhost:8080/v1/organizations/a_myOrg1542"
    }

@self_signed_app.get("/v1/algorithms/{username}/{algoname}/builds/{buildid}/logs")
async def get_build_log(username, algoname, buildid):
    return {"logs": "This is a log"}


@self_signed_app.get("/v1/algorithm-environments/edge/languages")
async def get_supported_langs():
    return [{"name": "anaconda3", "display_name": "Conda (Environments) - beta",
             "configuration": "{\n    \"display_name\": \"Conda (Environments) - beta\",\n    \"req_files\": [\n        \"environment.yml\"\n    ],\n    \"artifacts\": [\n        {\"source\":\"/home/algo/.cache\", \"destination\":\"/home/algo/.cache/\"},\n        {\"source\":\"/home/algo/anaconda_environment\", \"destination\": \"/home/algo/anaconda_environment/\"},\n        {\"source\":\"/opt/algorithm\", \"destination\":\"/opt/algorithm/\"}\n    ]\n}\n"},
            {"name": "csharp-dotnet-core2", "display_name": "C# .NET Core 2.x+ (Environments)",
             "configuration": "{\n    \"display_name\": \"C# .NET Core 2.x+ (Environments)\",\n    \"artifacts\": [\n        {\"source\":\"/opt/algorithm/bin/Release/*/*\", \"destination\":\"/opt/algorithm/\"},\n        {\"source\":\"/opt/algorithm/resources\", \"destination\":\"/opt/algorithm/resources/\"},\n        {\"source\":\"/home/algo/.nuget\", \"destination\":\"/home/algo/.nuget/\"}\n    ]\n}\n"},
            {"name": "java11", "display_name": "Java OpenJDK 11.0 (Environments)",
             "configuration": "{\n    \"display_name\": \"Java OpenJDK 11.0 (Environments)\",\n    \"artifacts\": [\n        {\"source\":\"/opt/algorithm/target/*.jar\", \"destination\":\"/opt/algorithm/target/algorithm.jar\"},\n        {\"source\":\"/opt/algorithm/target/lib\", \"destination\":\"/opt/algorithm/target/lib/\"}\n    ]\n}\n"},
            {"name": "python2", "display_name": "Python 2.x (Environments)",
             "configuration": "{\n    \"display_name\": \"Python 2.x (Environments)\",\n    \"req_files\": [\n        \"requirements.txt\"\n    ],\n    \"artifacts\": [\n        {\"source\":\"/home/algo/.local\", \"destination\":\"/home/algo/.local/\"},\n        {\"source\":\"/opt/algorithm\", \"destination\":\"/opt/algorithm/\"}\n    ]\n}\n"},
            {"name": "python3", "display_name": "Python 3.x (Environments)",
             "configuration": "{\n    \"display_name\": \"Python 3.x (Environments)\",\n    \"req_files\": [\n        \"requirements.txt\"\n    ],\n    \"artifacts\": [\n        {\"source\":\"/home/algo/.local\", \"destination\":\"/home/algo/.local/\"},\n        {\"source\":\"/opt/algorithm\", \"destination\":\"/opt/algorithm/\"}\n    ]\n}\n"},
            {"name": "r36", "display_name": "R 3.6.x (Environments)",
             "configuration": "{\n    \"display_name\": \"R 3.6.x (Environments)\",\n      \"req_files\": [\n        \"packages.txt\"\n    ],\n    \"artifacts\": [\n      {\"source\":\"/opt/algorithm\", \"destination\":\"/opt/algorithm/\"},\n      {\"source\":\"/usr/local/lib/R/site-library\", \"destination\":\"/usr/local/lib/R/site-library/\"}\n    ]\n}\n\n"},
            {"name": "scala-2", "display_name": "Scala 2.x & sbt 1.3.x (Environments)",
             "configuration": "{\n    \"display_name\": \"Scala 2.x & sbt 1.3.x (Environments)\",\n    \"artifacts\": [\n      {\"source\":\"/opt/algorithm/target/universal/stage\", \"destination\":\"/opt/algorithm/stage/\"}\n    ]\n}\n\n"}]


@self_signed_app.get("/v1/algorithm-environments/edge/languages/{language}/environments")
async def get_environments_by_lang(language):
    return {
        "environments": [
            {
                "id": "717d36e0-222c-44a0-9aa8-06f4ebc1b82a",
                "environment_specification_id": "f626effa-e519-431e-9d7a-0d3a7563ae1e",
                "display_name": "Python 2.7",
                "description": "Generic Python 2.7 installation",
                "created_at": "2020-12-21T21:47:53.239",
                "language": {
                    "name": language,
                    "display_name": "Python 2.x (Environments)",
                    "configuration": "{\n    \"display_name\": \"Python 2.x (Environments)\",\n    \"req_files\": [\n "
                                     "       \"requirements.txt\"\n    ],\n    \"artifacts\": [\n        {"
                                     "\"source\":\"/home/algo/.local\", \"destination\":\"/home/algo/.local/\"},"
                                     "\n        {\"source\":\"/opt/algorithm\", "
                                     "\"destination\":\"/opt/algorithm/\"}\n    ]\n}\n "
                },
                "machine_type": "CPU"
            },
            {
                "id": "6f57e041-54e0-4e1a-8b2f-4589bb2c06f8",
                "environment_specification_id": "faf81400-eb15-4f64-81c0-3d4ed7181e77",
                "display_name": "Python 2.7 + GPU support",
                "description": "Python2.7 installation with CUDA 9.0 and CUDNN7",
                "created_at": "2020-08-14T07:22:32.955",
                "language": {
                    "name": language,
                    "display_name": "Python 2.x (Environments)",
                    "configuration": "{\n    \"display_name\": \"Python 2.x (Environments)\",\n    \"req_files\": [\n "
                                     "       \"requirements.txt\"\n    ],\n    \"artifacts\": [\n        {"
                                     "\"source\":\"/home/algo/.local\", \"destination\":\"/home/algo/.local/\"},"
                                     "\n        {\"source\":\"/opt/algorithm\", "
                                     "\"destination\":\"/opt/algorithm/\"}\n    ]\n}\n "
                },
                "machine_type": "GPU"
            }
        ]
    }
