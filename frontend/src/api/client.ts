import createClient from "openapi-fetch";
import type { paths } from "./schema";

export const baseUrl = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export function createApiClient(token?: string) {
  return createClient<paths>({
    baseUrl,
    headers: token ? { Authorization: `Bearer ${token}` } : undefined
  });
}
