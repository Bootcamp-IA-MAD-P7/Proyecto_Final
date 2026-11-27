// @vitest-environment node
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { expect, it } from "vitest";

const styles = readFileSync(fileURLToPath(new URL("./AnalysisPanel.module.css", import.meta.url)), "utf8");
const resultStyles = readFileSync(fileURLToPath(new URL("../../../styles.css", import.meta.url)), "utf8");

it("keeps the pedagogical analysis grid responsive and its cards wide enough to read", () => {
  expect(styles).toContain("grid-template-columns: repeat(auto-fit, minmax(14rem, 1fr))");
  expect(styles).toContain("min-width: 0");
  expect(styles).toContain("overflow-wrap: anywhere");
});

it("allocates result panels by content priority without stretching their height", () => {
  expect(resultStyles).toContain(".result { display: grid; gap: var(--ct-space-4); max-width: none; width: 100%; }");
  expect(resultStyles).toContain(".result-columns { align-items: start; display: grid; gap: var(--ct-space-4); grid-template-columns: minmax(18rem, 2fr) minmax(0, 3fr); }");
  expect(resultStyles).toContain("@media (max-width: 62rem) { .result-columns { grid-template-columns: 1fr; } }");
});
