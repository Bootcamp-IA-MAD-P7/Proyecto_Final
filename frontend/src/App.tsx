import { useMutation, useQuery } from "@tanstack/react-query";
import { Navigate, Route, Routes, useNavigate, useParams } from "react-router-dom";
import { createApiClient } from "./api/client";
import { useAuth, demoUsers } from "./auth";
import { InlineNotice } from "./components/feedback/InlineNotice/InlineNotice";
import { ProgressIndicator } from "./components/feedback/ProgressIndicator/ProgressIndicator";
import { Button } from "./components/ui/Button/Button";
import { Card } from "./components/ui/Card/Card";
import { StatusBadge } from "./components/ui/StatusBadge/StatusBadge";

function Layout({ children }: { children: React.ReactNode }) {
  const { user, signOut } = useAuth();
  return <main className="app-content"><header className="app-header"><a className="brand" href="/">CoTeach-AI</a>{user && <Button className="sign-out" onClick={signOut} variant="text">Salir</Button>}</header>{children}</main>;
}

function Login() {
  const { user, signIn } = useAuth();
  const enter = useMutation({ mutationFn: signIn });
  if (user) return <Navigate replace to="/upload" />;
  return <Layout><section aria-labelledby="login-title" className="hero"><p className="eyebrow">Demo sintética</p><h1 id="login-title">La clase, lista para repasar.</h1><p>Entra con una identidad de prueba. La autorización siempre corresponde a la API.</p><div className="user-grid">{demoUsers.map((candidate) => <Button className="user-choice" disabled={enter.isPending} key={candidate.id} onClick={() => enter.mutate(candidate)}><strong>{candidate.name}</strong><small>{candidate.role === "teacher" ? "Docente" : "Estudiante"}</small></Button>)}</div>{enter.isError && <InlineNotice tone="error">No se pudo entrar. Comprueba que la API está levantada y con el emisor de pruebas activado.</InlineNotice>}</section></Layout>;
}

function Upload() {
  const { token, user } = useAuth(); const navigate = useNavigate();
  const receptionMessages: Record<string, string> = { audio_too_large: "El audio supera el tamaño permitido. Reduce el tamaño del archivo y vuelve a intentarlo.", unsupported_audio: "El formato del audio no está admitido. Usa Opus (Ogg o WebM), MP3 o AAC (M4A o MP4).", invalid_audio_duration: "La duración del audio está fuera de los límites permitidos." };
  const submit = useMutation({ mutationFn: async (form: FormData) => {
    const { data, error, response } = await createApiClient(token ?? undefined).POST("/v1/classes", { body: form as never });
    if (response.status === 403) throw new Error("No tienes permisos para subir grabaciones. Esta acción está reservada al profesorado");
    if (error || !data) throw new Error(receptionMessages[error?.error.code ?? ""] ?? error?.error.message ?? "No se pudo enviar la clase.");
    return data;
  }, onSuccess: ({ job_id }) => navigate(`/jobs/${job_id}`) });
  if (!user) return <Navigate replace to="/" />;
  return <Layout><Card aria-labelledby="upload-title" className="panel"><p className="eyebrow">Nueva clase</p><h1 id="upload-title">Sube una grabación</h1><p>El audio se conserva solo durante el plazo configurado y después se elimina; el resultado de esta demo es sintético.</p><form onSubmit={(event) => { event.preventDefault(); submit.mutate(new FormData(event.currentTarget)); }}><label>Audio<input accept=".ogg,.opus,.webm,.mp3,.m4a,.mp4,audio/ogg,audio/webm,audio/mpeg,audio/mp4" name="audio" required type="file" /></label><input name="metadata" type="hidden" value={JSON.stringify({ external_class_id: "demo-class-01", participant_count: 2, participants: [{ participant_id: "demo-teacher", role: "teacher" }, { participant_id: "demo-student", role: "student" }], consent_reference: "synthetic-fixture-01" })} /><Button disabled={submit.isPending} type="submit">{submit.isPending ? "Enviando…" : "Enviar a procesar"}</Button>{submit.isError && <InlineNotice tone="error">{submit.error.message}</InlineNotice>}</form></Card></Layout>;
}

function Job() {
  const { token } = useAuth(); const { jobId = "" } = useParams(); const navigate = useNavigate();
  const job = useQuery({ queryKey: ["job", jobId], queryFn: async () => { const { data, error } = await createApiClient(token ?? undefined).GET("/v1/jobs/{job_id}", { params: { path: { job_id: jobId } } }); if (error || !data) throw new Error("No se pudo consultar el trabajo."); return data; }, refetchInterval: (query) => { const state = query.state.data?.state; return state === "ready_for_review" || state === "expired" ? false : 800; } });
  if (!token) return <Navigate replace to="/" />;
  if (job.data?.state === "ready_for_review") return <Navigate replace to={`/classes/${job.data.class_id}/result`} />;
  const expired = job.data?.state === "expired";
  return <Layout><Card aria-labelledby="job-title" className="panel"><p className="eyebrow">Procesamiento</p><h1 id="job-title">{expired ? "Repaso no disponible" : "Estamos preparando el repaso"}</h1>{!expired && <><StatusBadge tone="info">Procesando</StatusBadge><ProgressIndicator label="Progreso de procesamiento" value={65} /></>}{job.isError && <InlineNotice tone="error">{job.error.message}</InlineNotice>}{expired && <InlineNotice tone="warning">El audio ya no está disponible porque ha caducado el plazo de conservación.</InlineNotice>}{!job.isError && !expired && <p>Etapa actual: {job.data?.stage ?? "en cola"}</p>}<Button onClick={() => navigate(0)} variant="secondary">Actualizar ahora</Button></Card></Layout>;
}

function Result() {
  const { token, user } = useAuth(); const { classId = "" } = useParams(); const navigate = useNavigate();
  const result = useQuery({ queryKey: ["result", classId], queryFn: async () => { const { data, error } = await createApiClient(token ?? undefined).GET("/v1/classes/{class_id}/result", { params: { path: { class_id: classId } } }); if (error || !data) throw new Error("El resultado aún no está disponible."); return data; } });
  const approve = useMutation({ mutationFn: async () => { const { data, error } = await createApiClient(token ?? undefined).POST("/v1/classes/{class_id}/approve", { params: { path: { class_id: classId } }, body: { expected_result_version: result.data!.result_version } }); if (error || !data) throw new Error("No se pudo aprobar el resultado."); return data; } });
  if (!token) return <Navigate replace to="/" />;
  if (result.isPending) return <Layout><p>Cargando resultado…</p></Layout>;
  if (result.isError) return <Layout><InlineNotice tone="error">{result.error.message}</InlineNotice></Layout>;
  return <Layout><section aria-labelledby="result-title" className="result"><p className="eyebrow">Resultado · v{result.data.result_version}</p><h1 id="result-title">Repaso de la clase</h1><div className="columns"><Card aria-labelledby="transcript-title"><h2 id="transcript-title">Transcripción</h2>{result.data.transcript.segments.map((segment) => <p key={segment.segment_id}><time>{(segment.start_ms / 1000).toFixed(0)}s</time>{segment.text}</p>)}</Card><Card aria-labelledby="analysis-title"><h2 id="analysis-title">Repaso pedagógico</h2><p>{result.data.analysis.general_summary}</p>{result.data.analysis.items.map((item) => <p key={item.item_id}><strong>{item.category}</strong> · {item.content}</p>)}</Card></div>{user?.role === "teacher" && <div className="actions"><Button disabled={approve.isPending} onClick={() => approve.mutate()}>Aprobar resultado</Button>{approve.isSuccess && <StatusBadge tone="success">Resultado aprobado y publicado.</StatusBadge>}</div>}<Button onClick={() => navigate("/upload")} variant="secondary">Subir otra clase</Button></section></Layout>;
}

export function App() { return <Routes><Route element={<Login />} path="/" /><Route element={<Upload />} path="/upload" /><Route element={<Job />} path="/jobs/:jobId" /><Route element={<Result />} path="/classes/:classId/result" /><Route element={<Navigate replace to="/" />} path="*" /></Routes>; }
