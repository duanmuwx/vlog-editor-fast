import { contextBridge, ipcRenderer } from "electron";

const api = {
  selectMediaFiles: (): Promise<string[]> => ipcRenderer.invoke("dialog:select-media-files"),
  selectBgmFile: (): Promise<string | null> => ipcRenderer.invoke("dialog:select-bgm-file"),
  openPath: (targetPath: string): Promise<string> => ipcRenderer.invoke("shell:open-path", targetPath),
  showItemInFolder: (targetPath: string): Promise<void> =>
    ipcRenderer.invoke("shell:show-item-in-folder", targetPath),
  getBackendStatus: (): Promise<{
    state: "starting" | "ready" | "error";
    healthy: boolean;
    message?: string;
    apiBaseUrl: string;
    logPath?: string;
    details?: string;
  }> => ipcRenderer.invoke("backend:get-status"),
  getApiBaseUrl: (): Promise<string> => ipcRenderer.invoke("backend:get-api-base-url"),
};

contextBridge.exposeInMainWorld("vlogEditor", api);
