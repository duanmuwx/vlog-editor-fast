import { spawn, type ChildProcess } from "node:child_process";

export interface BackendStatus {
  healthy: boolean;
  message?: string;
  apiBaseUrl: string;
}

interface StartOptions {
  packaged: boolean;
}

const DEFAULT_HOST = "127.0.0.1";
const DEFAULT_PORT = "8000";

export class BackendLauncher {
  private backendProcess: ChildProcess | null = null;

  private status: BackendStatus = {
    healthy: false,
    message: "Backend not started",
    apiBaseUrl: `http://${DEFAULT_HOST}:${DEFAULT_PORT}/api`,
  };

  async start(options: StartOptions): Promise<BackendStatus> {
    const host = process.env.SERVER_HOST ?? DEFAULT_HOST;
    const port = process.env.SERVER_PORT ?? DEFAULT_PORT;
    this.status.apiBaseUrl = `http://${host}:${port}/api`;

    if (!options.packaged) {
      return this.refreshStatus();
    }

    const backendCommand = process.env.VLOG_EDITOR_BACKEND_COMMAND;
    if (!backendCommand) {
      this.status = {
        ...this.status,
        healthy: false,
        message: "Packaged backend command is not configured",
      };
      return this.status;
    }

    this.backendProcess = spawn(backendCommand, {
      shell: true,
      env: {
        ...process.env,
        APP_ENV: "production",
        SERVER_HOST: host,
        SERVER_PORT: port,
      },
      stdio: "ignore",
    });

    this.backendProcess.on("exit", (code) => {
      this.status = {
        ...this.status,
        healthy: false,
        message: `Backend exited with code ${code ?? "unknown"}`,
      };
    });

    return this.waitForHealth();
  }

  async refreshStatus(): Promise<BackendStatus> {
    try {
      const response = await fetch(this.getHealthUrl());
      if (!response.ok) {
        throw new Error(`Health check failed with ${response.status}`);
      }

      this.status = {
        healthy: true,
        message: "Backend healthy",
        apiBaseUrl: this.status.apiBaseUrl,
      };
      return this.status;
    } catch (error) {
      this.status = {
        healthy: false,
        message: error instanceof Error ? error.message : "Backend unavailable",
        apiBaseUrl: this.status.apiBaseUrl,
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

    return this.status;
  }

  private getHealthUrl(): string {
    return this.status.apiBaseUrl.replace(/\/api$/, "/health");
  }
}
