import { createSlice, type PayloadAction } from "@reduxjs/toolkit";

import type { ProjectInputContract } from "../types/api";

type CreationDraftState = ProjectInputContract;

const initialState: CreationDraftState = {
  project_name: "",
  travel_note: "",
  media_files: [],
  bgm_asset: null,
  tts_voice: null,
  metadata_pack: null,
};

const creationDraftSlice = createSlice({
  name: "creationDraft",
  initialState,
  reducers: {
    updateCreationDraft(state, action: PayloadAction<Partial<ProjectInputContract>>) {
      return { ...state, ...action.payload };
    },
    resetCreationDraft() {
      return initialState;
    },
  },
});

export const { resetCreationDraft, updateCreationDraft } = creationDraftSlice.actions;
export const creationDraftReducer = creationDraftSlice.reducer;
