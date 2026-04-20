import path from "node:path";
import { fileURLToPath } from "node:url";

import { app, BrowserWindow, dialog, ipcMain, shell } from "electron";

import { BackendLauncher } from "./backend/launcher.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const launcher = new BackendLauncher();

let mainWindow: BrowserWindow | null = null;

function getRendererUrl(): string {
  const devServerUrl = process.env.VITE_DEV_SERVER_URL;
  if (devServerUrl) {
    return devServerUrl;
  }

  return `file://${path.join(__dirname, "../../dist/index.html")}`;
}

function createWindow(): BrowserWindow {
  const window = new BrowserWindow({
    width: 1440,
    height: 960,
    minWidth: 1200,
    minHeight: 800,
    show: false,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  window.once("ready-to-show", () => window.show());
  void window.loadURL(getRendererUrl());
  return window;
}

function registerIpcHandlers(): void {
  ipcMain.handle("dialog:select-media-files", async () => {
    const result = await dialog.showOpenDialog({
      properties: ["openFile", "multiSelections"],
      filters: [
        { name: "Media", extensions: ["mp4", "mov", "avi", "mkv", "jpg", "jpeg", "png", "gif", "bmp", "tiff"] },
      ],
    });
    return result.canceled ? [] : result.filePaths;
  });

  ipcMain.handle("dialog:select-bgm-file", async () => {
    const result = await dialog.showOpenDialog({
      properties: ["openFile"],
      filters: [{ name: "Audio", extensions: ["mp3", "wav", "m4a", "aac"] }],
    });
    return result.canceled ? null : result.filePaths[0];
  });

  ipcMain.handle("shell:open-path", async (_event, targetPath: string) => {
    return shell.openPath(targetPath);
  });

  ipcMain.handle("shell:show-item-in-folder", async (_event, targetPath: string) => {
    shell.showItemInFolder(targetPath);
  });

  ipcMain.handle("backend:get-status", async () => launcher.refreshStatus());
  ipcMain.handle("backend:get-api-base-url", async () => launcher.getApiBaseUrl());
}

app.whenReady().then(async () => {
  registerIpcHandlers();
  await launcher.start({ packaged: app.isPackaged });
  mainWindow = createWindow();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      mainWindow = createWindow();
    }
  });
});

app.on("window-all-closed", async () => {
  if (process.platform !== "darwin") {
    await launcher.stop();
    app.quit();
  }
});

app.on("before-quit", async () => {
  await launcher.stop();
});
