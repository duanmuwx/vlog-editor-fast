import { spawn, type ChildProcess } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

export type BackendState = "starting" | "ready" | "error";

export interface BackendStatus {
  state: BackendState;
  healthy: boolean;
  message?: string;
  apiBaseUrl: string;
  logPath?: string;
  details?: string;
}

interface StartOptions {
  packaged: boolean;
}

interface LauncherDependencies {
  fetchImpl?: typeof fetch;
  resourcesPath?: string;
  homeDir?: string;
  platform?: NodeJS.Platform;
}

export interface PackagedBackendPaths {
  runtimeRoot: string;
  appDir: string;
  pythonBinary: string;
  dataDir: string;
  logPath: string;
}

const DEFAULT_HOST = "127.0.0.1";
const DEFAULT_PORT = "8000";

export function getApiBaseUrl(host: string = DEFAULT_HOST, port: string = DEFAULT_PORT): string {
  return `http://${host}:${port}/api`;
}

export function resolvePackagedBackendPaths(
  resourcesPath: string,
  options?: { homeDir?: string; platform?: NodeJS.Platform },
): PackagedBackendPaths {
  const platform = options?.platform ?? process.platform;
  const homeDir = options?.homeDir ?? os.homedir();
  const runtimeRoot = path.join(resourcesPath, "backend-runtime");
  const appDir = path.join(runtimeRoot, "app");
  const dataDir = path.join(homeDir, ".vlog-editor");
  const logPath = path.join(dataDir, "logs", "backend.log");

  const pythonBinary =
    platform === "win32"
      ? path.join(runtimeRoot, "venv", "Scripts", "python.exe")
      : path.join(runtimeRoot, "venv", "bin", "python");

  return {
    runtimeRoot,
    appDir,
    pythonBinary,
    dataDir,
    logPath,
  };
}

function pathExists(targetPath: string): boolean {
  try {
    fs.accessSync(targetPath, fs.constants.R_OK);
    return true;
  } catch {
    return false;
  }
}

export class BackendLauncher {
  private readonly fetchImpl: typeof fetch;

  private readonly resourcesPath: string;

  private readonly homeDir: string;

  private readonly platform: NodeJS.Platform;

  private backendProcess: ChildProcess | null = null;

  private packaged = false;

  private bindHost = DEFAULT_HOST;

  private port = DEFAULT_PORT;

  private status: BackendStatus = {
    state: "error",
    healthy: false,
    message: "Backend not started",
    apiBaseUrl: getApiBaseUrl(),
  };

  constructor(dependencies: LauncherDependencies = {}) {
    this.fetchImpl = dependencies.fetchImpl ?? fetch;
    this.resourcesPath = dependencies.resourcesPath ?? process.resourcesPath;
    this.homeDir = dependencies.homeDir ?? os.homedir();
    this.platform = dependencies.platform ?? process.platform;
  }

  async start(options: StartOptions): Promise<BackendStatus> {
    this.packaged = options.packaged;
    this.bindHost = process.env.SERVER_HOST ?? (options.packaged ? DEFAULT_HOST : "0.0.0.0");
    this.port = process.env.SERVER_PORT ?? DEFAULT_PORT;
    this.status = {
      ...this.status,
      apiBaseUrl: getApiBaseUrl(DEFAULT_HOST, this.port),
      logPath: options.packaged
        ? resolvePackagedBackendPaths(this.resourcesPath, {
            homeDir: this.homeDir,
            platform: this.platform,
          }).logPath
        : path.join(process.env.APP_DATA_DIR ?? path.join(this.homeDir, ".vlog-editor"), "logs", "backend.log"),
    };

    if (!options.packaged) {
      return this.refreshStatus();
    }

    const packagedPaths = resolvePackagedBackendPaths(this.resourcesPath, {
      homeDir: this.homeDir,
      platform: this.platform,
    });

    if (!pathExists(packagedPaths.pythonBinary) || !pathExists(packagedPaths.appDir)) {
      this.status = {
        ...this.status,
        state: "error",
        healthy: false,
        message: "Packaged backend runtime is missing",
        details: `Expected runtime at ${packagedPaths.runtimeRoot}`,
      };
      return this.status;
    }

    fs.mkdirSync(path.join(packagedPaths.dataDir, "projects"), { recursive: true });
    fs.mkdirSync(path.join(packagedPaths.dataDir, "logs"), { recursive: true });

    this.status = {
      ...this.status,
      state: "starting",
      healthy: false,
      message: "正在启动本地服务…",
    };

    this.backendProcess = spawn(
      packagedPaths.pythonBinary,
      [
        "-m",
        "uvicorn",
        "src.server.main:app",
        "--host",
        this.bindHost,
        "--port",
        this.port,
      ],
      {
        cwd: packagedPaths.appDir,
        env: {
          ...process.env,
          PYTHONPATH: packagedPaths.appDir,
          APP_ENV: "production",
          APP_DATA_DIR: packagedPaths.dataDir,
          SERVER_HOST: this.bindHost,
          SERVER_PORT: this.port,
          LOG_LEVEL: process.env.LOG_LEVEL ?? "INFO",
        },
        stdio: "ignore",
      },
    );

    this.backendProcess.on("exit", (code, signal) => {
      this.status = {
        ...this.status,
        state: "error",
        healthy: false,
        message: "本地服务已退出",
        details: `Backend exited with code ${code ?? "unknown"} signal ${signal ?? "none"}`,
      };
    });

    return this.waitForHealth();
  }

  async refreshStatus(): Promise<BackendStatus> {
    try {
      const response = await this.fetchImpl(this.getHealthUrl());
      if (!response.ok) {
        throw new Error(`Health check failed with ${response.status}`);
      }

      this.status = {
        ...this.status,
        state: "ready",
        healthy: true,
        message: "Backend healthy",
      };
      return this.status;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Backend unavailable";
      const processRunning =
        this.packaged && this.backendProcess !== null && this.backendProcess.exitCode === null;

      this.status = {
        ...this.status,
        state: processRunning ? "starting" : "error",
        healthy: false,
        message: processRunning ? "正在启动本地服务…" : errorMessage,
        details: processRunning ? this.status.details : errorMessage,
      };
      return this.status;
    }
  }

  async stop(): Promise<void> {
    if (!this.backendProcess) {
      return;
    }

    this.backendProcess.kill();
    this.backendProcess = null;
  }

  getStatus(): BackendStatus {
    return this.status;
  }

  getApiBaseUrl(): string {
    return this.status.apiBaseUrl;
  }

  private async waitForHealth(): Promise<BackendStatus> {
    const maxAttempts = 20;

    for (let attempt = 0; attempt < maxAttempts; attempt += 1) {
      const status = await this.refreshStatus();
      if (status.healthy) {
        return status;
      }

      await new Promise((resolve) => setTimeout(resolve, 500));
    }

    this.status = {
      ...this.status,
      state: "error",
      healthy: false,
      message: "Timed out waiting for local backend",
      details: `Health check did not succeed at ${this.getHealthUrl()}`,
    };
    return this.status;
  }

  private getHealthUrl(): string {
    return this.status.apiBaseUrl.replace(/\/api$/, "/health");
  }
}
