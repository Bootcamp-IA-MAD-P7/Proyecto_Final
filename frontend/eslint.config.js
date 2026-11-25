import js from "@eslint/js";
import reactHooks from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh";
import tseslint from "typescript-eslint";

export default tseslint.config(
  { ignores: ["dist", "src/api/schema.ts"] },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  reactHooks.configs["recommended-latest"],
  reactRefresh.configs.vite,
  { files: ["src/auth.tsx"], rules: { "react-refresh/only-export-components": "off" } },
  { languageOptions: { ecmaVersion: 2022, globals: { document: "readonly", window: "readonly" } } }
);
