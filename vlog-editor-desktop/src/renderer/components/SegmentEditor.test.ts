import { describe, expect, it } from "vitest";

import { buildSkeletonConfirmationEdits, type EditableSegment } from "./SegmentEditor";
import type { StorySegment } from "../types/api";

const originalSegments: StorySegment[] = [
  {
    segment_id: "seg-a",
    title: "A",
    summary: "Segment A",
    start_index: 0,
    end_index: 10,
    importance: "high",
    confidence: 0.9,
    keywords: [],
    locations: [],
    timestamps: [],
  },
  {
    segment_id: "seg-b",
    title: "B",
    summary: "Segment B",
    start_index: 11,
    end_index: 20,
    importance: "medium",
    confidence: 0.8,
    keywords: [],
    locations: [],
    timestamps: [],
  },
  {
    segment_id: "seg-c",
    title: "C",
    summary: "Segment C",
    start_index: 21,
    end_index: 30,
    importance: "medium",
    confidence: 0.7,
    keywords: [],
    locations: [],
    timestamps: [],
  },
  {
    segment_id: "seg-d",
    title: "D",
    summary: "Segment D",
    start_index: 31,
    end_index: 40,
    importance: "low",
    confidence: 0.6,
    keywords: [],
    locations: [],
    timestamps: [],
  },
];

describe("buildSkeletonConfirmationEdits", () => {
  it("maps reorder, merge, delete, and mark into backend edits", () => {
    const editableSegments: EditableSegment[] = [
      {
        ...originalSegments[1],
        segment_id: "merged-b-c",
        title: "B + C",
        summary: "Merged",
        sourceSegmentIds: ["seg-b", "seg-c"],
      },
      {
        ...originalSegments[0],
        sourceSegmentIds: ["seg-a"],
        markType: "must_keep",
      },
    ];

    expect(buildSkeletonConfirmationEdits(originalSegments, editableSegments)).toEqual([
      {
        operation: "reorder",
        segment_ids: ["seg-b", "seg-c", "seg-a", "seg-d"],
      },
      {
        operation: "merge",
        segment_ids: ["seg-b", "seg-c"],
      },
      {
        operation: "delete",
        segment_ids: ["seg-d"],
      },
      {
        operation: "mark",
        segment_ids: ["seg-a"],
        payload: { mark_type: "must_keep" },
      },
    ]);
  });
});
