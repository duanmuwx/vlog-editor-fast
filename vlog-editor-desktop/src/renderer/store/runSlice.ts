import { createSlice, type PayloadAction } from "@reduxjs/toolkit";

import type { DiagnosticBundle, RunHistoryResponse } from "../types/api";

interface RunState {
  runs: RunHistoryResponse | null;
  diagnostics: Record<string, DiagnosticBundle>;
  loading: boolean;
  error: string | null;
}

const initialState: RunState = {
  runs: null,
  diagnostics: {},
  loading: false,
  error: null,
};

const runSlice = createSlice({
  name: "run",
  initialState,
  reducers: {
    setRuns(state, action: PayloadAction<RunHistoryResponse | null>) {
      state.runs = action.payload;
    },
    setDiagnostics(
      state,
      action: PayloadAction<{ runId: string; bundle: DiagnosticBundle }>,
    ) {
      state.diagnostics[action.payload.runId] = action.payload.bundle;
    },
    setRunLoading(state, action: PayloadAction<boolean>) {
      state.loading = action.payload;
    },
    setRunError(state, action: PayloadAction<string | null>) {
      state.error = action.payload;
    },
    resetRunState() {
      return initialState;
    },
  },
});

export const { resetRunState, setDiagnostics, setRunError, setRunLoading, setRuns } =
  runSlice.actions;
export const runReducer = runSlice.reducer;
