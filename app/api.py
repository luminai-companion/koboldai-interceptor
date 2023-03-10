from typing import Union

import httpx
from fastapi import FastAPI, Request
from starlette.responses import JSONResponse, RedirectResponse

app = FastAPI(
    title="KoboldAI Interceptor",
    version="1.0",
    description="Request/response interception proof-of-concept",
)

api_url = "http://127.0.0.1:5000/api/v1"


@app.get("/", include_in_schema=False)
def docs_redirect() -> RedirectResponse:
    return RedirectResponse("/docs")


@app.get("/api/v1/{path:path}")
def handle_get(path: str, q: Union[str, None] = None) -> JSONResponse:
    url = f"{api_url}/{path}"
    response = httpx.get(url, params=q)

    return JSONResponse(response.json(), status_code=response.status_code)


def process_generate_request_hooks(request: dict) -> dict:
    request["prompt"] = "Once upon a time, "  # example request interception
    return request


def process_generate_response_hooks(response: dict) -> dict:
    response["results"][0]["text"] += " /gen /pos"  # example response interception
    return response


@app.post("/api/v1/generate")
async def handle_generate(request: Request) -> JSONResponse:
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    payload_json = process_generate_request_hooks(await request.json())

    # TODO could make this async with httpx
    post_response = httpx.post(
        f"{api_url}/generate", headers=headers, json=payload_json
    )

    response_json = process_generate_response_hooks(post_response.json())

    return JSONResponse(response_json, status_code=post_response.status_code)
