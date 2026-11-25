import { execFileSync } from "node:child_process";
import { resolve } from "node:path";
import process from "node:process";

const repositoryRoot = process.env.REPOSITORY_ROOT ?? resolve(process.cwd(), "..");

execFileSync(
  "git",
  ["-C", repositoryRoot, "diff", "--exit-code", "--", "frontend/src/api/schema.ts"],
  { stdio: "inherit" }
);
