from app.contract import CONTRACT_VERSION
from app.main import create_app
from app.openapi_export import OPENAPI_PATH, main, render

CONTRACT_OPERATIONS = {
    ("post", "/v1/classes"),
    ("get", "/v1/jobs/{job_id}"),
    ("get", "/v1/classes/{class_id}/result"),
    ("patch", "/v1/classes/{class_id}/review"),
    ("post", "/v1/classes/{class_id}/approve"),
}
OPERATION_ROUTES = {("get", "/health"), ("get", "/ready")}


def test_versioned_openapi_matches_the_declared_api():
    assert OPENAPI_PATH.read_text(encoding="utf-8") == render(), (
        "backend/openapi.json is out of date: run `make -C backend openapi` and review the diff"
    )


def test_check_mode_reports_up_to_date():
    assert main(["--check"]) == 0


def test_contract_version_and_operations():
    spec = create_app().openapi()
    assert spec["info"]["version"] == CONTRACT_VERSION == "0.2.0"
    operations = {(method, path) for path, item in spec["paths"].items() for method in item}
    assert operations == CONTRACT_OPERATIONS | OPERATION_ROUTES


def test_every_operation_requires_a_bearer_token_and_documents_common_errors():
    spec = create_app().openapi()
    assert spec["components"]["securitySchemes"]["bearerToken"]["scheme"] == "bearer"
    for method, path in CONTRACT_OPERATIONS:
        operation = spec["paths"][path][method]
        assert operation["security"] == [{"bearerToken": []}]
        for status in ("401", "403", "404", "422", "500", "503"):
            schema = operation["responses"][status]["content"]["application/json"]["schema"]
            assert schema == {"$ref": "#/components/schemas/ErrorResponse"}


def test_health_and_readiness_need_no_credential():
    spec = create_app().openapi()
    for method, path in OPERATION_ROUTES:
        assert "security" not in spec["paths"][path][method]
    readiness = spec["paths"]["/ready"]["get"]["responses"]
    assert readiness["503"]["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/Readiness"
    }


def test_submit_class_takes_metadata_as_json_and_an_idempotency_key():
    spec = create_app().openapi()
    body = spec["components"]["schemas"]["Body_submitClass"]
    assert body["required"] == ["audio", "metadata"]
    assert body["properties"]["metadata"]["contentSchema"] == {
        "$ref": "#/components/schemas/ClassMetadata"
    }
    operation = spec["paths"]["/v1/classes"]["post"]
    assert "202" in operation["responses"]
    assert {"409", "413", "415"} <= operation["responses"].keys()
    headers = [param["name"] for param in operation["parameters"] if param["in"] == "header"]
    assert headers == ["Idempotency-Key"]


def test_submit_class_documents_the_duration_error():
    spec = create_app().openapi()
    assert "`invalid_audio_duration`" in spec["paths"]["/v1/classes"]["post"]["description"]
    assert "invalid_audio_duration" in spec["components"]["schemas"]["ErrorCode"]["enum"]
