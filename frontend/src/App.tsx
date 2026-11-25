import { useMutation, useQuery } from "@tanstack/react-query";
import { Navigate, Route, Routes, useNavigate, useParams } from "react-router-dom";
import { demoUsers, useAuth } from "./auth";
import { createApiClient } from "./api/client";

function Layout({ children }: { children: React.ReactNode }) {
  const { user, signOut } = useAuth();
  return <main><header><a href="/" className="brand">CoTeach <span>AI</span></a>{user && <button className="quiet" onClick={signOut}>Salir</button>}</header>{children}</main>;
}

function Login() {
  const { user, signIn } = useAuth();
  if (user) return <Navigate to="/upload" replace />;
  return <Layout><section className="hero"><p className="eyebrow">DEMO SINTÉTICA</p><h1>La clase, lista para repasar.</h1><p>Entra con una identidad de prueba. La autorización siempre corresponde a la API.</p><div className="user-grid">{demoUsers.map((candidate) => <button key={candidate.id} onClick={() => signIn(candidate)}><strong>{candidate.name}</strong><small>{candidate.role === "teacher" ? "Docente" : "Estudiante"}</small></button>)}</div></section></Layout>;
}

function Upload() {
  const { token, user } = useAuth(); const navigate = useNavigate();
  const submit = useMutation({ mutationFn: async (form: FormData) => {
    // FastAPI exposes multipart fields as strings in OpenAPI 3.1; FormData is the runtime representation.
    const { data, error, response } = await createApiClient(token ?? undefined).POST("/v1/classes", { body: form as never });
    if (response.status === 403) throw new Error("No tienes permisos para subir grabaciones. Esta acción está reservada al profesorado");
    if (error || !data) throw new Error("No se pudo enviar la clase.");
    return data;
  }, onSuccess: ({ job_id }) => navigate(`/jobs/${job_id}`) });
  if (!user) return <Navigate to="/" replace />;
  return <Layout><section className="panel"><p className="eyebrow">NUEVA CLASE</p><h1>Sube una grabación</h1><p>El audio de esta demo no se conserva; se usa un resultado sintético del contrato.</p><form onSubmit={(event) => { event.preventDefault(); submit.mutate(new FormData(event.currentTarget)); }}><label>Audio<input required name="audio" type="file" accept="audio/*" /></label><input type="hidden" name="metadata" value={JSON.stringify({ external_class_id: "demo-class-01", participant_count: 2, participants: [{ participant_id: "demo-teacher", role: "teacher" }, { participant_id: "demo-student", role: "student" }], consent_reference: "synthetic-fixture-01" })} /><button disabled={submit.isPending}>{submit.isPending ? "Enviando…" : "Enviar a procesar"}</button>{submit.isError && <p role="alert">{submit.error.message}</p>}</form></section></Layout>;
}

function Job() {
  const { token } = useAuth(); const { jobId = "" } = useParams(); const navigate = useNavigate();
  const job = useQuery({ queryKey: ["job", jobId], queryFn: async () => { const { data, error } = await createApiClient(token ?? undefined).GET("/v1/jobs/{job_id}", { params: { path: { job_id: jobId } } }); if (error || !data) throw new Error("No se pudo consultar el trabajo."); return data; }, refetchInterval: (query) => query.state.data?.state === "ready_for_review" ? false : 800 });
  if (!token) return <Navigate to="/" replace />;
  if (job.data?.state === "ready_for_review") return <Navigate to={`/classes/${job.data.class_id}/result`} replace />;
  return <Layout><section className="panel"><p className="eyebrow">PROCESAMIENTO</p><h1>Estamos preparando el repaso</h1><div className="progress" aria-label="Progreso de procesamiento"><i /></div><p>{job.isError ? job.error.message : `Etapa actual: ${job.data?.stage ?? "en cola"}`}</p><button className="quiet" onClick={() => navigate(0)}>Actualizar ahora</button></section></Layout>;
}

function Result() {
  const { token, user } = useAuth(); const { classId = "" } = useParams(); const navigate = useNavigate();
  const result = useQuery({ queryKey: ["result", classId], queryFn: async () => { const { data, error } = await createApiClient(token ?? undefined).GET("/v1/classes/{class_id}/result", { params: { path: { class_id: classId } } }); if (error || !data) throw new Error("El resultado aún no está disponible."); return data; } });
  const approve = useMutation({ mutationFn: async () => { const { data, error } = await createApiClient(token ?? undefined).POST("/v1/classes/{class_id}/approve", { params: { path: { class_id: classId } }, body: { expected_result_version: result.data!.result_version } }); if (error || !data) throw new Error("No se pudo aprobar el resultado."); return data; } });
  if (!token) return <Navigate to="/" replace />;
  if (result.isPending) return <Layout><p>Cargando resultado…</p></Layout>;
  if (result.isError) return <Layout><p role="alert">{result.error.message}</p></Layout>;
  return <Layout><section className="result"><p className="eyebrow">RESULTADO · V{result.data.result_version}</p><h1>Repaso de la clase</h1><div className="columns"><article><h2>Transcripción</h2>{result.data.transcript.segments.map((segment) => <p key={segment.segment_id}><time>{(segment.start_ms / 1000).toFixed(0)}s</time>{segment.text}</p>)}</article><article><h2>Repaso pedagógico</h2><p>{result.data.analysis.general_summary}</p>{result.data.analysis.items.map((item) => <p key={item.item_id}><strong>{item.category}</strong> · {item.content}</p>)}</article></div>{user?.role === "teacher" && <div className="actions"><button onClick={() => approve.mutate()} disabled={approve.isPending}>Aprobar resultado</button>{approve.isSuccess && <p role="status">Resultado aprobado y publicado.</p>}</div>}<button className="quiet" onClick={() => navigate("/upload")}>Subir otra clase</button></section></Layout>;
}

export function App() { return <Routes><Route path="/" element={<Login />} /><Route path="/upload" element={<Upload />} /><Route path="/jobs/:jobId" element={<Job />} /><Route path="/classes/:classId/result" element={<Result />} /><Route path="*" element={<Navigate to="/" replace />} /></Routes>; }
