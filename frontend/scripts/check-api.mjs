import { execFileSync } from "node:child_process";
import { readFile } from "node:fs/promises";
import { resolve } from "node:path";
import process from "node:process";

const repositoryRoot = process.env.REPOSITORY_ROOT ?? resolve(process.cwd(), "..");
const schemaPath = "frontend/src/api/schema.ts";
const generatedSchemaPath = resolve(process.cwd(), "src/api/schema.ts");
const [generatedSchema, versionedSchema] = await Promise.all([
  readFile(generatedSchemaPath),
  Promise.resolve(execFileSync("git", ["-C", repositoryRoot, "show", `HEAD:${schemaPath}`]))
]);

if (!generatedSchema.equals(versionedSchema)) {
  process.stderr.write("The generated OpenAPI schema differs from the versioned schema.\n");
  process.exitCode = 1;
}
