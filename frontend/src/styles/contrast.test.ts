// @vitest-environment node
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { expect, it } from "vitest";

const tokensPath = fileURLToPath(new URL("./tokens.css", import.meta.url));
const source = readFileSync(tokensPath, "utf8");

function token(name: string) {
  const match = source.match(new RegExp(`--ct-${name}:\\s*(#[0-9a-fA-F]{6})`));
  if (!match) throw new Error(`Missing color token: ${name}`);
  return match[1];
}

function luminance(hex: string) {
  const channels = [1, 3, 5].map((offset) => Number.parseInt(hex.slice(offset, offset + 2), 16) / 255);
  const linear = channels.map((channel) => channel <= 0.04045 ? channel / 12.92 : ((channel + 0.055) / 1.055) ** 2.4);
  return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2];
}

function contrast(foreground: string, background: string) {
  const [light, dark] = [luminance(foreground), luminance(background)].sort((a, b) => b - a);
  return (light + 0.05) / (dark + 0.05);
}

const pairs: Array<[string, string]> = [
  ["color-ink", "color-card"],
  ["color-ink", "color-surface"],
  ["color-ink", "color-info-soft"],
  ["color-ink", "color-teal-soft"],
  ["color-card", "color-primary"],
  ["color-card", "color-primary-strong"],
  ["color-card", "color-teal"],
  ["color-success", "color-success-soft"],
  ["color-warning", "color-warning-soft"],
  ["color-danger", "color-danger-soft"],
  ["color-primary-strong", "color-info-soft"],
  ["color-text-muted", "color-teal-soft"],
];

it.each(pairs)("keeps %s on %s at WCAG AA contrast", (foreground, background) => {
  expect(contrast(token(foreground), token(background))).toBeGreaterThanOrEqual(4.5);
});
