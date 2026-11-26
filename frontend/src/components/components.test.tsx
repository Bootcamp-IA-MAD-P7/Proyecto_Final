import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { expect, it } from "vitest";
import { InlineNotice } from "./feedback/InlineNotice/InlineNotice";
import { ProgressIndicator } from "./feedback/ProgressIndicator/ProgressIndicator";
import { Button } from "./ui/Button/Button";
import { Card } from "./ui/Card/Card";
import { FilePicker } from "./ui/FilePicker/FilePicker";
import { StatusBadge } from "./ui/StatusBadge/StatusBadge";
import { TopBar } from "./navigation/TopBar/TopBar";

it("renders button variants as accessible buttons", () => {
  render(<><Button>Continuar</Button><Button disabled variant="secondary">Cancelar</Button><Button variant="text">Volver</Button></>);
  expect(screen.getByRole("button", { name: "Continuar" })).toBeEnabled();
  expect(screen.getByRole("button", { name: "Cancelar" })).toBeDisabled();
  expect(screen.getByRole("button", { name: "Volver" })).toBeVisible();
});

it("renders a labelled card as a region", () => {
  render(<Card aria-label="Detalle de la clase">Contenido de la clase</Card>);
  expect(screen.getByRole("region", { name: "Detalle de la clase" })).toHaveTextContent("Contenido de la clase");
});

it("exposes badge text in a status region", () => {
  render(<StatusBadge tone="success">Procesada</StatusBadge>);
  expect(screen.getByRole("status")).toHaveTextContent("Procesada");
});

it("uses an alert for an error notice and a polite status for information", () => {
  const { rerender } = render(<InlineNotice tone="error">No se pudo enviar la clase.</InlineNotice>);
  expect(screen.getByRole("alert")).toHaveTextContent("Error: No se pudo enviar la clase.");
  rerender(<InlineNotice>La clase se está procesando.</InlineNotice>);
  expect(screen.getByRole("status")).toHaveTextContent("Información: La clase se está procesando.");
});

it("announces progress with a bounded accessible value", () => {
  render(<ProgressIndicator label="Procesando grabación" value={120} />);
  expect(screen.getByRole("progressbar", { name: "Procesando grabación" })).toHaveValue(100);
  expect(screen.getByText("100%")).toBeVisible();
});

it("uses indeterminate progress when the API does not provide a percentage", () => {
  render(<ProgressIndicator label="Transcribiendo" />);
  expect(screen.getByRole("progressbar", { name: "Transcribiendo" })).not.toHaveAttribute("value");
  expect(screen.queryByText(/^\d+%$/)).not.toBeInTheDocument();
});

it("keeps the file picker accessible through its associated label", () => {
  render(<FilePicker accept=".mp3" name="audio" required />);
  const input = screen.getByLabelText("Audio") as HTMLInputElement;
  expect(input).toBeRequired();
  expect(input.accept).toBe(".mp3");
});

it("uses router navigation for the signed-in brand", () => {
  render(<MemoryRouter><TopBar onSignOut={() => undefined} user={{ name: "Docente de prueba", role: "teacher" }} /></MemoryRouter>);
  const brand = screen.getByRole("link", { name: "CoTeach-AI" });
  expect(brand).toHaveAttribute("href", "/upload");
  brand.focus();
  expect(document.activeElement).toBe(brand);
  expect(fireEvent.click(brand)).toBe(false);
});
