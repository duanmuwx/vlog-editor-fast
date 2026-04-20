// @vitest-environment node

import path from "node:path";

import { describe, expect, it } from "vitest";

import { getApiBaseUrl, resolvePackagedBackendPaths } from "./launcher.js";

describe("launcher helpers", () => {
  it("builds renderer-facing API base urls on localhost", () => {
    expect(getApiBaseUrl("127.0.0.1", "8001")).toBe("http://127.0.0.1:8001/api");
  });

  it("resolves packaged backend runtime paths for linux", () => {
    const paths = resolvePackagedBackendPaths("/tmp/resources", {
      homeDir: "/home/tester",
      platform: "linux",
    });

    expect(paths.runtimeRoot).toBe("/tmp/resources/backend-runtime");
    expect(paths.appDir).toBe("/tmp/resources/backend-runtime/app");
    expect(paths.pythonBinary).toBe("/tmp/resources/backend-runtime/venv/bin/python");
    expect(paths.dataDir).toBe("/home/tester/.vlog-editor");
    expect(paths.logPath).toBe("/home/tester/.vlog-editor/logs/backend.log");
  });

  it("resolves packaged backend runtime paths for macOS", () => {
    const paths = resolvePackagedBackendPaths("/Applications/Vlog/resources", {
      homeDir: "/Users/tester",
      platform: "darwin",
    });

    expect(paths.pythonBinary).toBe(
      path.join("/Applications/Vlog/resources", "backend-runtime", "venv", "bin", "python"),
    );
    expect(paths.appDir).toBe(path.join("/Applications/Vlog/resources", "backend-runtime", "app"));
  });
});
