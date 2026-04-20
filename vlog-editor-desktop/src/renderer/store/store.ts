import { configureStore } from "@reduxjs/toolkit";

import { artifactReducer } from "./artifactSlice";
import { creationDraftReducer } from "./creationDraftSlice";
import { projectReducer } from "./projectSlice";
import { runReducer } from "./runSlice";
import { workflowReducer } from "./workflowSlice";

export const store = configureStore({
  reducer: {
    artifact: artifactReducer,
    creationDraft: creationDraftReducer,
    project: projectReducer,
    run: runReducer,
    workflow: workflowReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
