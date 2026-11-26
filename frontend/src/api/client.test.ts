import { describe, expect, it } from "vitest";
import { expiredJobHandler, receptionRejections } from "../mocks/handlers";
import { server } from "../mocks/server";
import { createApiClient } from "./client";

describe("API client", () => {
  it("uses a bearer token only when supplied in memory", () => {
    const client = createApiClient("ephemeral-token");
    expect(client).toBeDefined();
  });

  it("reads a synthetic processing job through MSW", async () => {
    const { data, error } = await createApiClient("ephemeral-token").GET("/v1/jobs/{job_id}", { params: { path: { job_id: "job-demo-01" } } });
    expect(error).toBeUndefined();
    expect(data?.state).toBe("analyzing");
  });

  it("rejects a class submission from the synthetic student", async () => {
    const form = new FormData();
    form.append("audio", new File(["audio"], "class.mp3", { type: "audio/mpeg" }));
    form.append("metadata", "{}");
    const { data, error, response } = await createApiClient("synthetic-demo-student").POST("/v1/classes", { body: form as never });
    expect(data).toBeUndefined();
    expect(response.status).toBe(403);
    expect(error).toMatchObject({ error: { code: "forbidden" } });
  });

  it("accepts a class submission from the synthetic CoTeach service credential", async () => {
    const form = new FormData();
    form.append("audio", new File(["audio"], "class.mp3", { type: "audio/mpeg" }));
    form.append("metadata", "{}");
    const { data, error, response } = await createApiClient("synthetic-coteach-service").POST("/v1/classes", { body: form as never });
    expect(error).toBeUndefined();
    expect(response.status).toBe(202);
    expect(data?.state).toBe("queued");
  });

  it.each(receptionRejections)("mocks the reception error for $fileName", async ({ handler, status, code }) => {
    server.use(handler);
    const form = new FormData();
    form.append("audio", new File(["audio"], "class.mp3", { type: "audio/mpeg" }));
    form.append("metadata", "{}");
    const { data, error, response } = await createApiClient("synthetic-demo-teacher").POST("/v1/classes", { body: form as never });
    expect(data).toBeUndefined();
    expect(response.status).toBe(status);
    expect(error).toMatchObject({ error: { code } });
  });

  it("exposes an expired job through MSW", async () => {
    server.use(expiredJobHandler);
    const { data, error } = await createApiClient("synthetic-demo-teacher").GET("/v1/jobs/{job_id}", { params: { path: { job_id: "job-demo-expired" } } });
    expect(error).toBeUndefined();
    expect(data?.state).toBe("expired");
    expect(data?.error).toBeNull();
  });
});
