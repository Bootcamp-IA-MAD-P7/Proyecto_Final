import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterAll, afterEach, beforeAll } from "vitest";
import { server } from "../mocks/server";

beforeAll(() => server.listen());
// Without vitest globals, Testing Library does not unmount each test on its own.
afterEach(() => { cleanup(); server.resetHandlers(); });
afterAll(() => server.close());
