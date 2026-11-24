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


def test_versioned_openapi_matches_the_declared_api():
    assert OPENAPI_PATH.read_text(encoding="utf-8") == render(), (
        "backend/openapi.json is out of date: run `make -C backend openapi` and review the diff"
    )


def test_check_mode_reports_up_to_date():
    assert main(["--check"]) == 0


def test_contract_version_and_operations():
    spec = create_app().openapi()
    assert spec["info"]["version"] == CONTRACT_VERSION == "0.1.0"
    operations = {(method, path) for path, item in spec["paths"].items() for method in item}
    assert operations == CONTRACT_OPERATIONS


def test_every_operation_requires_a_bearer_token_and_documents_common_errors():
    spec = create_app().openapi()
    assert spec["components"]["securitySchemes"]["bearerToken"]["scheme"] == "bearer"
    for item in spec["paths"].values():
        for operation in item.values():
            assert operation["security"] == [{"bearerToken": []}]
            for status in ("401", "404", "422", "503"):
                schema = operation["responses"][status]["content"]["application/json"]["schema"]
                assert schema == {"$ref": "#/components/schemas/ErrorResponse"}


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
