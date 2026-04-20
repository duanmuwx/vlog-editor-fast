import { createSlice, type PayloadAction } from "@reduxjs/toolkit";

import type {
  AudioMixSummary,
  ExportHistoryResponse,
  NarrationSummary,
  TimelineDetail,
  TimelineSummary,
  VersionHistory,
} from "../types/api";

interface ArtifactState {
  timelineSummary: TimelineSummary | null;
  currentTimeline: TimelineDetail | null;
  narration: NarrationSummary | null;
  audioMix: AudioMixSummary | null;
  exports: ExportHistoryResponse | null;
  versionHistories: Record<string, VersionHistory>;
  versionDiffs: Record<string, unknown>;
}

const initialState: ArtifactState = {
  timelineSummary: null,
  currentTimeline: null,
  narration: null,
  audioMix: null,
  exports: null,
  versionHistories: {},
  versionDiffs: {},
};

const artifactSlice = createSlice({
  name: "artifact",
  initialState,
  reducers: {
    setTimelineSummary(state, action: PayloadAction<TimelineSummary | null>) {
      state.timelineSummary = action.payload;
    },
    setCurrentTimeline(state, action: PayloadAction<TimelineDetail | null>) {
      state.currentTimeline = action.payload;
    },
    setNarration(state, action: PayloadAction<NarrationSummary | null>) {
      state.narration = action.payload;
    },
    setAudioMix(state, action: PayloadAction<AudioMixSummary | null>) {
      state.audioMix = action.payload;
    },
    setExports(state, action: PayloadAction<ExportHistoryResponse | null>) {
      state.exports = action.payload;
    },
    setVersionHistory(state, action: PayloadAction<VersionHistory>) {
      state.versionHistories[action.payload.artifact_type] = action.payload;
    },
    setVersionDiff(
      state,
      action: PayloadAction<{ artifactType: string; diff: unknown }>,
    ) {
      state.versionDiffs[action.payload.artifactType] = action.payload.diff;
    },
    resetArtifactState() {
      return initialState;
    },
  },
});

export const {
  resetArtifactState,
  setAudioMix,
  setCurrentTimeline,
  setExports,
  setNarration,
  setTimelineSummary,
  setVersionDiff,
  setVersionHistory,
} = artifactSlice.actions;

export const artifactReducer = artifactSlice.reducer;
