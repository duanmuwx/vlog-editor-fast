import { createSlice, type PayloadAction } from "@reduxjs/toolkit";

import type {
  AlignmentCandidatesResponse,
  HighlightsResponse,
  MediaAnalysis,
  StorySkeleton,
  ValidationReport,
  AssetIndexResponse,
} from "../types/api";

export type WorkflowStage =
  | "project"
  | "validation"
  | "skeleton"
  | "highlights"
  | "render"
  | "exports";

interface WorkflowState {
  stage: WorkflowStage;
  validationReport: ValidationReport | null;
  assetIndex: AssetIndexResponse | null;
  skeleton: StorySkeleton | null;
  mediaAnalysis: MediaAnalysis | null;
  alignmentCandidates: Record<string, AlignmentCandidatesResponse>;
  highlights: HighlightsResponse | null;
}

const initialState: WorkflowState = {
  stage: "project",
  validationReport: null,
  assetIndex: null,
  skeleton: null,
  mediaAnalysis: null,
  alignmentCandidates: {},
  highlights: null,
};

const workflowSlice = createSlice({
  name: "workflow",
  initialState,
  reducers: {
    setWorkflowStage(state, action: PayloadAction<WorkflowStage>) {
      state.stage = action.payload;
    },
    setValidationReport(state, action: PayloadAction<ValidationReport | null>) {
      state.validationReport = action.payload;
    },
    setAssetIndex(state, action: PayloadAction<AssetIndexResponse | null>) {
      state.assetIndex = action.payload;
    },
    setSkeleton(state, action: PayloadAction<StorySkeleton | null>) {
      state.skeleton = action.payload;
    },
    setMediaAnalysis(state, action: PayloadAction<MediaAnalysis | null>) {
      state.mediaAnalysis = action.payload;
    },
    setAlignmentCandidates(state, action: PayloadAction<AlignmentCandidatesResponse>) {
      state.alignmentCandidates[action.payload.segment_id] = action.payload;
    },
    resetAlignmentCandidates(state) {
      state.alignmentCandidates = {};
    },
    setHighlights(state, action: PayloadAction<HighlightsResponse | null>) {
      state.highlights = action.payload;
    },
    resetWorkflowState() {
      return initialState;
    },
  },
});

export const {
  resetAlignmentCandidates,
  resetWorkflowState,
  setAlignmentCandidates,
  setAssetIndex,
  setHighlights,
  setMediaAnalysis,
  setSkeleton,
  setValidationReport,
  setWorkflowStage,
} = workflowSlice.actions;

export const workflowReducer = workflowSlice.reducer;
