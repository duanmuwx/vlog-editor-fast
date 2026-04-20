export interface BackendStatus {
  state: "starting" | "ready" | "error";
  healthy: boolean;
  message?: string;
  apiBaseUrl: string;
  logPath?: string;
  details?: string;
}

export interface DesktopBridge {
  selectMediaFiles(): Promise<string[]>;
  selectBgmFile(): Promise<string | null>;
  openPath(targetPath: string): Promise<string>;
  showItemInFolder(targetPath: string): Promise<void>;
  getBackendStatus(): Promise<BackendStatus>;
  getApiBaseUrl(): Promise<string>;
}

declare global {
  interface Window {
    vlogEditor?: DesktopBridge;
  }
}

const defaultApiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000/api";

const fallbackBridge: DesktopBridge = {
  async selectMediaFiles() {
    return [];
  },
  async selectBgmFile() {
    return null;
  },
  async openPath() {
    return "";
  },
  async showItemInFolder() {
    return undefined;
  },
  async getBackendStatus() {
    return {
      state: "error" as const,
      healthy: false,
      message: "Electron bridge unavailable",
      apiBaseUrl: defaultApiBaseUrl,
    };
  },
  async getApiBaseUrl() {
    return defaultApiBaseUrl;
  },
};

export const ipc = window.vlogEditor ?? fallbackBridge;
