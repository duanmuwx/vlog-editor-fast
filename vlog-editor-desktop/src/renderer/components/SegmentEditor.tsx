import { useEffect, useMemo, useState } from "react";
import { Button, Card, List, Select, Space, Tag, Typography } from "antd";

import type { SkeletonEdit, StorySegment } from "../types/api";

export interface EditableSegment extends StorySegment {
  sourceSegmentIds: string[];
  markType?: "must_keep" | "optional";
}

export function toEditableSegments(segments: StorySegment[]): EditableSegment[] {
  return segments.map((segment) => ({
    ...segment,
    sourceSegmentIds: [segment.segment_id],
  }));
}

export function buildSkeletonConfirmationEdits(
  originalSegments: StorySegment[],
  editableSegments: EditableSegment[],
): SkeletonEdit[] {
  const originalIds = originalSegments.map((segment) => segment.segment_id);
  const visibleSourceIds = editableSegments.flatMap((segment) => segment.sourceSegmentIds);
  const deletedIds = originalIds.filter((segmentId) => !visibleSourceIds.includes(segmentId));
  const reorderIds = [...visibleSourceIds, ...deletedIds];

  const edits: SkeletonEdit[] = [];

  if (reorderIds.some((segmentId, index) => segmentId !== originalIds[index])) {
    edits.push({
      operation: "reorder",
      segment_ids: reorderIds,
    });
  }

  editableSegments
    .filter((segment) => segment.sourceSegmentIds.length > 1)
    .forEach((segment) => {
      edits.push({
        operation: "merge",
        segment_ids: segment.sourceSegmentIds,
      });
    });

  if (deletedIds.length > 0) {
    edits.push({
      operation: "delete",
      segment_ids: deletedIds,
    });
  }

  editableSegments
    .filter((segment) => segment.markType)
    .forEach((segment) => {
      edits.push({
        operation: "mark",
        segment_ids: segment.sourceSegmentIds,
        payload: { mark_type: segment.markType },
      });
    });

  return edits;
}

interface SegmentEditorProps {
  segments: StorySegment[];
  onChange?(segments: EditableSegment[], edits: SkeletonEdit[]): void;
}

function mergeSegments(first: EditableSegment, second: EditableSegment): EditableSegment {
  return {
    ...first,
    segment_id: `merged-${first.sourceSegmentIds.join("-")}-${second.sourceSegmentIds.join("-")}`,
    title: `${first.title} + ${second.title}`.slice(0, 100),
    summary: `${first.summary} ${second.summary}`.slice(0, 200),
    start_index: Math.min(first.start_index, second.start_index),
    end_index: Math.max(first.end_index, second.end_index),
    confidence: Number(((first.confidence + second.confidence) / 2).toFixed(2)),
    keywords: Array.from(new Set([...first.keywords, ...second.keywords])),
    locations: Array.from(new Set([...first.locations, ...second.locations])),
    timestamps: Array.from(new Set([...first.timestamps, ...second.timestamps])),
    sourceSegmentIds: [...first.sourceSegmentIds, ...second.sourceSegmentIds],
  };
}

export default function SegmentEditor({ segments, onChange }: SegmentEditorProps): JSX.Element {
  const [editableSegments, setEditableSegments] = useState<EditableSegment[]>(() =>
    toEditableSegments(segments),
  );

  useEffect(() => {
    setEditableSegments(toEditableSegments(segments));
  }, [segments]);

  const edits = useMemo(
    () => buildSkeletonConfirmationEdits(segments, editableSegments),
    [editableSegments, segments],
  );

  useEffect(() => {
    onChange?.(editableSegments, edits);
  }, [editableSegments, edits, onChange]);

  const applyNextSegments = (nextSegments: EditableSegment[]) => {
    setEditableSegments(nextSegments);
  };

  const moveSegment = (index: number, direction: -1 | 1) => {
    const targetIndex = index + direction;
    if (targetIndex < 0 || targetIndex >= editableSegments.length) {
      return;
    }

    const nextSegments = [...editableSegments];
    const [item] = nextSegments.splice(index, 1);
    nextSegments.splice(targetIndex, 0, item);
    applyNextSegments(nextSegments);
  };

  const mergeWithNext = (index: number) => {
    if (index >= editableSegments.length - 1) {
      return;
    }

    const nextSegments = [...editableSegments];
    const merged = mergeSegments(nextSegments[index], nextSegments[index + 1]);
    nextSegments.splice(index, 2, merged);
    applyNextSegments(nextSegments);
  };

  const deleteSegment = (index: number) => {
    if (editableSegments.length <= 3) {
      return;
    }

    applyNextSegments(editableSegments.filter((_segment, currentIndex) => currentIndex !== index));
  };

  const updateMark = (index: number, markType?: "must_keep" | "optional") => {
    const nextSegments = [...editableSegments];
    nextSegments[index] = {
      ...nextSegments[index],
      markType,
    };
    applyNextSegments(nextSegments);
  };

  return (
    <Space direction="vertical" style={{ width: "100%" }} size="middle">
      <Typography.Text type="secondary">
        支持排序、删除、合并相邻段落，以及标记必保留片段。
      </Typography.Text>
      <List
        dataSource={editableSegments}
        renderItem={(segment, index) => (
          <List.Item>
            <Card
              title={
                <Space>
                  <Typography.Text strong>{segment.title}</Typography.Text>
                  <Tag>{segment.importance}</Tag>
                  <Tag color="blue">置信度 {segment.confidence.toFixed(2)}</Tag>
                  {segment.sourceSegmentIds.length > 1 && <Tag color="purple">已合并</Tag>}
                </Space>
              }
              style={{ width: "100%" }}
              extra={
                <Space wrap>
                  <Button size="small" onClick={() => moveSegment(index, -1)} disabled={index === 0}>
                    上移
                  </Button>
                  <Button
                    size="small"
                    onClick={() => moveSegment(index, 1)}
                    disabled={index === editableSegments.length - 1}
                  >
                    下移
                  </Button>
                  <Button
                    size="small"
                    onClick={() => mergeWithNext(index)}
                    disabled={index === editableSegments.length - 1}
                  >
                    与下一段合并
                  </Button>
                  <Button danger size="small" onClick={() => deleteSegment(index)} disabled={editableSegments.length <= 3}>
                    删除
                  </Button>
                </Space>
              }
            >
              <Space direction="vertical" style={{ width: "100%" }}>
                <Typography.Paragraph>{segment.summary}</Typography.Paragraph>
                <Space wrap>
                  <Typography.Text type="secondary">
                    源片段：{segment.sourceSegmentIds.join(", ")}
                  </Typography.Text>
                  <Select
                    allowClear
                    placeholder="标记片段"
                    value={segment.markType}
                    style={{ width: 180 }}
                    onChange={(value) => updateMark(index, value)}
                    options={[
                      { label: "必保留", value: "must_keep" },
                      { label: "可裁剪", value: "optional" },
                    ]}
                  />
                </Space>
              </Space>
            </Card>
          </List.Item>
        )}
      />
      <Card size="small" title="将要提交的编辑请求">
        <pre style={{ margin: 0, whiteSpace: "pre-wrap" }}>{JSON.stringify(edits, null, 2)}</pre>
      </Card>
    </Space>
  );
}
