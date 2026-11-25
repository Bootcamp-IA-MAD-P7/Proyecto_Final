"""Integration with PostgreSQL: migrations, claims with SKIP LOCKED, readiness and the API."""

from alembic.autogenerate import compare_metadata
from alembic.runtime.migration import MigrationContext
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.contract import ClassMetadata, JobState, Result
from app.db import make_engine, metadata
from app.db.tables import jobs
from app.jobs import PostgresJobStore
from app.main import create_app
from tests.conftest import SETTINGS, auth, load_fixture
from tests.test_routes import submit


def class_metadata() -> ClassMetadata:
    return ClassMetadata.model_validate(load_fixture("valid/class-metadata.json"))


def test_migrations_match_the_tables(pg):
    with pg.connect() as connection:
        differences = compare_metadata(MigrationContext.configure(connection), metadata)

    assert differences == []


def test_claim_skips_jobs_locked_by_another_worker(pg):
    store = PostgresJobStore(pg)
    first = store.create_class(class_metadata(), "demo-teacher")
    second = store.create_class(class_metadata(), "demo-teacher")

    with pg.begin() as other_worker:
        other_worker.execute(
            select(jobs.c.job_id).where(jobs.c.job_id == first.job_id).with_for_update()
        )
        claimed = store.claim_next()

    assert claimed.job_id == second.job_id
    assert store.get_job(first.job_id).state is JobState.QUEUED


def test_participants_keep_their_order_and_roles(pg):
    store = PostgresJobStore(pg)
    stored = store.create_class(class_metadata(), "demo-teacher")

    assert store.get_class(stored.class_id).metadata == class_metadata()


def test_ready_with_the_database(pg):
    client = TestClient(create_app(SETTINGS, engine=pg))

    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready", "dependencies": {"database": "ok"}}


def test_ready_without_the_database_names_it_without_the_url():
    engine = make_engine("postgresql+psycopg://secret-user:secret-pass@127.0.0.1:1/nowhere")
    client = TestClient(create_app(SETTINGS, engine=engine))

    response = client.get("/ready")

    assert response.status_code == 503
    assert response.json() == {"status": "unavailable", "dependencies": {"database": "unavailable"}}
    assert "secret" not in response.text


def test_submitted_class_is_followed_and_read_from_postgres(pg, audio_storage, probe):
    store = PostgresJobStore(pg)
    client = TestClient(
        create_app(SETTINGS, store=store, engine=pg, storage=audio_storage, probe=probe)
    )

    accepted = submit(client, load_fixture("valid/class-metadata.json"), headers=auth()).json()
    job = client.get(f"/v1/jobs/{accepted['job_id']}", headers=auth("demo-student", "student"))
    claimed = store.claim_next()
    result = Result.model_validate(
        {**load_fixture("valid/result-draft.json"), "class_id": accepted["class_id"]}
    )
    store.complete(claimed.job_id, result)
    read = client.get(f"/v1/classes/{accepted['class_id']}/result", headers=auth())

    assert accepted["state"] == "queued"
    assert job.json()["state"] == "queued"
    assert read.status_code == 200
    assert Result.model_validate(read.json()) == result
