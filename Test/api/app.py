from fastapi import FastAPI, Request, status
from typing import Optional
from fastapi.responses import Response, JSONResponse
import json
import base64
from multiprocessing import Process
import uvicorn

regular_app = FastAPI()


def start_webserver_reg():
    def _start_webserver():
        uvicorn.run(regular_app, host="127.0.0.1", port=8080, log_level="debug")

    p = Process(target=_start_webserver)
    p.start()
    return p


@regular_app.post("/v1/algo/{username}/{algoname}")
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


@regular_app.post("/v1/algo/{username}/{algoname}/{githash}", status_code=status.HTTP_200_OK)
async def process_hello_world(request: Request, username, algoname, githash):
    metadata = {"request_id": "req-55c0480d-6af3-4a21-990a-5c51d29f5725", "duration": 0.000306774,
                'content_type': "text"}
    request = await request.body()
    request = request.decode('utf-8')
    return {"result": f"hello {request}", "metadata": metadata}


### Algorithm Routes
@regular_app.get('/v1/algorithms/{username}/{algoname}')
async def process_get_algo(username, algoname):
    if algoname == "echo" and username == 'quality':
        return {"id": "21df7a38-eab8-4ac8-954c-41a285535e69", "name": "echo",
                "details": {"summary": "", "label": "echo", "tagline": ""},
                "settings": {"algorithm_callability": "public", "source_visibility": "closed",
                             "package_set": "python36", "license": "apl", "royalty_microcredits": 0,
                             "network_access": "full", "pipeline_enabled": True, "insights_enabled": False,
                             "algorithm_environment": "067110e7-8969-4441-b3d6-5333f18a3db3"},
                "version_info": {"semantic_version": "0.1.0", "git_hash": "0cfd7a6600f1fa05f9fe93016e661a9332c4ded2",
                                 "version_uuid": "e06d2808-bb5e-46ae-b7bc-f3d9968e3c6b"},
                "build": {"build_id": "a9ae2c93-6f4e-42c0-ac54-baa4a66e53d3", "status": "succeeded",
                          "commit_sha": "0cfd7a6600f1fa05f9fe93016e661a9332c4ded2",
                          "started_at": "2022-05-08T22:43:09.050Z", "finished_at": "2022-05-08T22:43:28.646Z",
                          "version_info": {"semantic_version": "0.1.0"}, "resource_type": "algorithm_build"},
                "source": {"scm": {"id": "internal", "provider": "internal", "default": True, "enabled": True}},
                "compilation": {"successful": True, "output": ""},
                "self_link": "https://api.algorithmia.com/v1/algorithms/quality/echo/versions/0cfd7a6600f1fa05f9fe93016e661a9332c4ded2",
                "resource_type": "algorithm"}
    elif algoname == "echo":
        return JSONResponse(content={"error": {"id": "1cfb98c5-532e-4cbf-9192-fdd45b86969c", "code": 2001,
                                               "message": "Caller is not authorized to perform the operation"}},
                            status_code=403)
    else:
        return JSONResponse(content={"error": "No such algorithm"}, status_code=404)


@regular_app.get("/v1/algorithms/{username}/{algoname}/builds/{buildid}")
async def get_build_id(username, algoname, buildid):
    return {"status": "succeeded", "build_id": buildid, "commit_sha": "bcdadj",
            "started_at": "2021-09-27T22:54:20.786Z", "finished_at": "2021-09-27T22:54:40.898Z",
            "version_info": {"semantic_version": "0.1.1"}}


@regular_app.get("/v1/algorithms/{username}/{algoname}/builds/{buildid}/logs")
async def get_build_log(username, algoname, buildid):
    return {"logs": "This is a log"}


@regular_app.get("/v1/algorithms/{username}/{algoname}/scm/status")
async def get_scm_status(username, algoname):
    return {"scm_connection_status": "active"}


@regular_app.get("/v1/scms")
async def get_scms():
    return {'results': [{'default': True, 'enabled': True, 'id': 'internal', 'name': '', 'provider': 'internal'},
                        {'default': False, 'enabled': True, 'id': 'github', 'name': 'https://github.com',
                         'provider': 'github', 'scm': {'client_id': '0ff25ba21ec67dbed6e2'},
                         'oauth': {'client_id': '0ff25ba21ec67dbed6e2'},
                         'urls': {'web': 'https://github.com', 'api': 'https://api.github.com',
                                  'ssh': 'ssh://git@github.com'}},
                        {'default': False, 'enabled': True, 'id': 'aadebe70-007f-48ff-ba38-49007c6e0377',
                         'name': 'https://gitlab.com', 'provider': 'gitlab',
                         'scm': {'client_id': 'ca459576279bd99ed480236a267cc969f8322caad292fa5147cc7fdf7b530a7e'},
                         'oauth': {'client_id': 'ca459576279bd99ed480236a267cc969f8322caad292fa5147cc7fdf7b530a7e'},
                         'urls': {'web': 'https://gitlab.com', 'api': 'https://gitlab.com',
                                  'ssh': 'ssh://git@gitlab.com'}},
                        {'default': False, 'enabled': True, 'id': '24ad1496-5a1d-43e2-9d96-42fce8e5484f',
                         'name': 'IQIVA Public GitLab', 'provider': 'gitlab',
                         'scm': {'client_id': '3341c989f9d28043d2597388aa4f43ce60a74830b981c4b7d79becf641959376'},
                         'oauth': {'client_id': '3341c989f9d28043d2597388aa4f43ce60a74830b981c4b7d79becf641959376'},
                         'urls': {'web': 'https://gitlab.com', 'api': 'https://gitlab.com',
                                  'ssh': 'ssh://git@gitlab.com'}},
                        {'default': False, 'enabled': False, 'id': '83cd96ae-b1f4-4bd9-b9ca-6f7f25c37708',
                         'name': 'GitlabTest', 'provider': 'gitlab',
                         'scm': {'client_id': '5e257d6e168d579d439b7d38cdfa647e16573ae1dace6d93a30c5c60b4e5dd32'},
                         'oauth': {'client_id': '5e257d6e168d579d439b7d38cdfa647e16573ae1dace6d93a30c5c60b4e5dd32'},
                         'urls': {'web': 'https://gitlab.com', 'api': 'https://gitlab.com',
                                  'ssh': 'ssh://git@gitlab.com'}}]}


@regular_app.get("/v1/algorithms/{algo_id}/errors")
async def get_algo_errors(algo_id):
    return JSONResponse(content={"error": {"message": "not found"}}, status_code=404)


@regular_app.post("/v1/algorithms/{username}")
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


@regular_app.put('/v1/algorithms/{username}/{algoname}')
async def update_algorithm(request: Request, username, algoname):
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


@regular_app.post("/v1/algorithms/{username}/{algoname}/compile")
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

fail_cnt = 0

@regular_app.post("/v1/algorithms/{username}/{algoname}/versions")
async def publish_algorithm(request: Request, username, algoname):
    global fail_cnt
    if "failonce" == algoname and fail_cnt == 0:
        fail_cnt +=1
        return JSONResponse(content="This is an expected failure mode, try again", status_code=400)
    elif "failalways" == algoname:
        return JSONResponse(status_code=500)
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


@regular_app.get("/v1/algorithms/{username}/{algoname}/versions")
async def versions_of_algorithm(request: Request, username, algoname):
    return {"marker": None, "next_link": None, "results": [
        {"id": "21df7a38-eab8-4ac8-954c-41a285535e69", "name": algoname,
         "details": {"summary": "", "label": algoname, "tagline": ""},
         "settings": {"algorithm_callability": "public", "source_visibility": "closed", "package_set": "python36",
                      "license": "apl", "royalty_microcredits": 0, "network_access": "full", "pipeline_enabled": True,
                      "insights_enabled": False, "algorithm_environment": "067110e7-8969-4441-b3d6-5333f18a3db3"},
         "version_info": {"semantic_version": "0.1.0", "git_hash": "0cfd7a6600f1fa05f9fe93016e661a9332c4ded2",
                          "version_uuid": "e06d2808-bb5e-46ae-b7bc-f3d9968e3c6b"},
         "build": {"build_id": "a9ae2c93-6f4e-42c0-ac54-baa4a66e53d3", "status": "succeeded",
                   "commit_sha": "0cfd7a6600f1fa05f9fe93016e661a9332c4ded2", "started_at": "2022-05-08T22:43:09.050Z",
                   "finished_at": "2022-05-08T22:43:28.646Z", "version_info": {"semantic_version": "0.1.0"},
                   "resource_type": "algorithm_build"},
         "source": {"scm": {"id": "internal", "provider": "internal", "default": True, "enabled": True}},
         "compilation": {"successful": True},
         "self_link": f"https://api.algorithmia.com/v1/algorithms/{username}/{algoname}/versions"
                      "/0cfd7a6600f1fa05f9fe93016e661a9332c4ded2",
         "resource_type": "algorithm"}]}


@regular_app.get("/v1/algorithms/{username}/{algoname}/versions/{algohash}")
async def get_algorithm_info(username, algoname, algohash):
    if algohash == "e85db9bca2fad519f540b445f30d12523e4dec9c":
        return {"id": "21df7a38-eab8-4ac8-954c-41a285535e69", "name": algoname,
                "details": {"summary": "", "label": algoname, "tagline": ""},
                "settings": {"algorithm_callability": "public", "source_visibility": "closed", "language": "python3",
                             "environment": "cpu", "package_set": "python36", "license": "apl",
                             "royalty_microcredits": 0, "network_access": "full", "pipeline_enabled": True,
                             "insights_enabled": False,
                             "algorithm_environment": "067110e7-8969-4441-b3d6-5333f18a3db3"},
                "version_info": {"semantic_version": "0.1.0", "git_hash": "0cfd7a6600f1fa05f9fe93016e661a9332c4ded2",
                                 "version_uuid": "e06d2808-bb5e-46ae-b7bc-f3d9968e3c6b"},
                "build": {"build_id": "a9ae2c93-6f4e-42c0-ac54-baa4a66e53d3", "status": "succeeded",
                          "commit_sha": "0cfd7a6600f1fa05f9fe93016e661a9332c4ded2",
                          "started_at": "2022-05-08T22:43:09.050Z", "finished_at": "2022-05-08T22:43:28.646Z",
                          "version_info": {"semantic_version": "0.1.0"}, "resource_type": "algorithm_build"},
                "source": {"scm": {"id": "internal", "provider": "internal", "default": True, "enabled": True}},
                "compilation": {"successful": True, "output": ""}, "resource_type": "algorithm"}
    else:
        return JSONResponse(content={"error": {"message": "not found"}}, status_code=404)


### Admin Routes
@regular_app.post("/v1/users")
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


@regular_app.get("/v1/users/{user_id}/errors")
async def get_user_errors(user_id):
    return []


@regular_app.get("/v1/organization/types")
async def get_org_types():
    return [
        {"id": "d0c85ea6-ddfa-11ea-a0c8-12a811be4db3", "name": "basic"},
        {"id": "d0bff917-ddfa-11ea-a0c8-12a811be4db3", "name": "legacy"},
        {"id": "d0c9d825-ddfa-11ea-a0c8-12a811be4db3", "name": "pro"}
    ]


@regular_app.post("/v1/organizations")
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


@regular_app.put("/v1/organizations/{orgname}/members/{username}")
async def add_user_to_org(orgname, username):
    return Response(status_code=200)


@regular_app.get("/v1/organizations/{orgname}/errors")
async def org_errors(orgname):
    return []


@regular_app.put("/v1/organizations/{org_name}")
async def edit_org(org_name):
    return Response(status_code=204)


@regular_app.get("/v1/organizations/{org_name}")
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


@regular_app.get("/v1/algorithms/{username}/{algoname}/builds/{buildid}/logs")
async def get_build_log(username, algoname, buildid):
    return {"logs": "This is a log"}


@regular_app.get("/v1/algorithm-environments/edge/languages")
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


@regular_app.get("/v1/algorithm-environments/edge/languages/{language}/environments")
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


@regular_app.get("/v1/secret-provider")
async def get_service_providers():
    return [
        {
            "id": "dee00b6c-05c4-4de7-98d8-e4a3816ed75f",
            "name": "algorithmia_internal_secret_provider",
            "description": "Internal Secret Provider",
            "moduleName": "module",
            "factoryClassName": "com.algorithmia.plugin.sqlsecretprovider.InternalSecretProviderFactory",
            "interfaceVersion": "1.0",
            "isEnabled": True,
            "isDefault": True,
            "created": "2021-03-11T20:42:23Z",
            "modified": "2021-03-11T20:42:23Z"
        }
    ]


@regular_app.get("/v1/algorithms/{algorithm_id}/secrets")
async def get_secrets_for_algorithm(algorithm_id):
    return {
        "secrets": [
            {
                "id": "45e97c47-3ae6-46be-87ee-8ab23746706b",
                "short_name": "MLOPS_SERVICE_URL",
                "description": "",
                "secret_key": "MLOPS_SERVICE_URL",
                "owner_type": "algorithm",
                "owner_id": "fa2cd80b-d22a-4548-b16a-45dbad2d3499",
                "provider_id": "dee00b6c-05c4-4de7-98d8-e4a3816ed75f",
                "created": "2022-07-22T14:36:01Z",
                "modified": "2022-07-22T14:36:01Z"
            },
            {
                "id": "50dca60e-317f-4582-8854-5b83b4d182d0",
                "short_name": "deploy_id",
                "description": "",
                "secret_key": "DEPLOYMENT_ID",
                "owner_type": "algorithm",
                "owner_id": "fa2cd80b-d22a-4548-b16a-45dbad2d3499",
                "provider_id": "dee00b6c-05c4-4de7-98d8-e4a3816ed75f",
                "created": "2022-07-21T19:04:31Z",
                "modified": "2022-07-21T19:04:31Z"
            },
            {
                "id": "5a75cdc8-ecc8-4715-8c4b-8038991f1608",
                "short_name": "model_path",
                "description": "",
                "secret_key": "MODEL_PATH",
                "owner_type": "algorithm",
                "owner_id": "fa2cd80b-d22a-4548-b16a-45dbad2d3499",
                "provider_id": "dee00b6c-05c4-4de7-98d8-e4a3816ed75f",
                "created": "2022-07-21T19:04:31Z",
                "modified": "2022-07-21T19:04:31Z"
            },
            {
                "id": "80e51ed3-f6db-419d-9349-f59f4bbfdcbb",
                "short_name": "model_id",
                "description": "",
                "secret_key": "MODEL_ID",
                "owner_type": "algorithm",
                "owner_id": "fa2cd80b-d22a-4548-b16a-45dbad2d3499",
                "provider_id": "dee00b6c-05c4-4de7-98d8-e4a3816ed75f",
                "created": "2022-07-21T19:04:30Z",
                "modified": "2022-07-21T19:04:30Z"
            },
            {
                "id": "8773c654-ea2f-4ac5-9ade-55dfc47fec9d",
                "short_name": "datarobot_api_token",
                "description": "",
                "secret_key": "DATAROBOT_MLOPS_API_TOKEN",
                "owner_type": "algorithm",
                "owner_id": "fa2cd80b-d22a-4548-b16a-45dbad2d3499",
                "provider_id": "dee00b6c-05c4-4de7-98d8-e4a3816ed75f",
                "created": "2022-07-21T19:04:31Z",
                "modified": "2022-07-21T19:04:31Z"
            }
        ]
    }


@regular_app.post("/v1/algorithms/{algorithm_id}/secrets")
async def set_algorithm_secret(algorithm_id):
    return {
   "id":"959af771-7cd8-4981-91c4-70def15bbcdc",
   "short_name":"tst",
   "description":"",
   "secret_key":"test",
   "owner_type":"algorithm",
   "owner_id":"fa2cd80b-d22a-4548-b16a-45dbad2d3499",
   "provider_id":"dee00b6c-05c4-4de7-98d8-e4a3816ed75f",
   "created":"2022-07-22T18:28:42Z",
   "modified":"2022-07-22T18:28:42Z"
}