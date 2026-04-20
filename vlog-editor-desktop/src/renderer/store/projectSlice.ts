import { createSlice, type PayloadAction } from "@reduxjs/toolkit";

import type { ProjectDetailResponse, ProjectSummary } from "../types/api";

interface ProjectState {
  items: ProjectSummary[];
  currentProjectId: string | null;
  currentProjectDetail: ProjectDetailResponse | null;
  listLoading: boolean;
  detailLoading: boolean;
  error: string | null;
}

const initialState: ProjectState = {
  items: [],
  currentProjectId: null,
  currentProjectDetail: null,
  listLoading: false,
  detailLoading: false,
  error: null,
};

const projectSlice = createSlice({
  name: "project",
  initialState,
  reducers: {
    setProjectList(state, action: PayloadAction<ProjectSummary[]>) {
      state.items = action.payload;
    },
    upsertProjectSummary(state, action: PayloadAction<ProjectSummary>) {
      const index = state.items.findIndex((project) => project.project_id === action.payload.project_id);
      if (index >= 0) {
        state.items[index] = action.payload;
      } else {
        state.items.unshift(action.payload);
      }
    },
    removeProjectSummary(state, action: PayloadAction<string>) {
      state.items = state.items.filter((project) => project.project_id !== action.payload);
      if (state.currentProjectId === action.payload) {
        state.currentProjectId = null;
        state.currentProjectDetail = null;
      }
    },
    setCurrentProjectId(state, action: PayloadAction<string | null>) {
      state.currentProjectId = action.payload;
    },
    setCurrentProjectDetail(state, action: PayloadAction<ProjectDetailResponse | null>) {
      state.currentProjectDetail = action.payload;
    },
    setProjectListLoading(state, action: PayloadAction<boolean>) {
      state.listLoading = action.payload;
    },
    setProjectDetailLoading(state, action: PayloadAction<boolean>) {
      state.detailLoading = action.payload;
    },
    setProjectError(state, action: PayloadAction<string | null>) {
      state.error = action.payload;
    },
  },
});

export const {
  removeProjectSummary,
  setCurrentProjectDetail,
  setCurrentProjectId,
  setProjectDetailLoading,
  setProjectError,
  setProjectList,
  setProjectListLoading,
  upsertProjectSummary,
} = projectSlice.actions;

export const projectReducer = projectSlice.reducer;
