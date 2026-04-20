import { describe, expect, it } from "vitest";

import { creationDraftReducer, resetCreationDraft, updateCreationDraft } from "./creationDraftSlice";

describe("creationDraftSlice", () => {
  it("updates only the provided draft fields", () => {
    const state = creationDraftReducer(
      undefined,
      updateCreationDraft({
        project_name: "Summer Trip",
        media_files: ["/tmp/a.mp4"],
      }),
    );

    expect(state.project_name).toBe("Summer Trip");
    expect(state.media_files).toEqual(["/tmp/a.mp4"]);
    expect(state.travel_note).toBe("");
  });

  it("resets back to the initial draft", () => {
    const updated = creationDraftReducer(
      undefined,
      updateCreationDraft({
        project_name: "Summer Trip",
        travel_note: "Long note",
      }),
    );

    const reset = creationDraftReducer(updated, resetCreationDraft());
    expect(reset).toEqual(creationDraftReducer(undefined, { type: "unknown" }));
  });
});
