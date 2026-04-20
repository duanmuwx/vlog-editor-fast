import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Button, Card, Empty, Space, Tag, Typography, message } from "antd";

import SegmentEditor, { type EditableSegment, buildSkeletonConfirmationEdits } from "../components/SegmentEditor";
import { apiService } from "../services/api";
import { useAppDispatch, useAppSelector } from "../store/hooks";
import { setCurrentProjectDetail, setCurrentProjectId } from "../store/projectSlice";
import { setSkeleton, setWorkflowStage } from "../store/workflowSlice";
import type { SkeletonEdit, StorySkeleton } from "../types/api";

export default function SkeletonReview(): JSX.Element {
  const { projectId = "" } = useParams();
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const skeleton = useAppSelector((state) => state.workflow.skeleton);
  const [loading, setLoading] = useState(false);
  const [editableSegments, setEditableSegments] = useState<EditableSegment[]>([]);
  const [pendingEdits, setPendingEdits] = useState<SkeletonEdit[]>([]);

  const loadSkeleton = async () => {
    try {
      const detail = await apiService.getProject(projectId);
      dispatch(setCurrentProjectId(projectId));
      dispatch(setCurrentProjectDetail(detail));
      const currentSkeleton = await apiService.getCurrentSkeleton(projectId);
      dispatch(setSkeleton(currentSkeleton));
      dispatch(setWorkflowStage("skeleton"));
    } catch {
      dispatch(setSkeleton(null));
    }
  };

  useEffect(() => {
    void loadSkeleton();
  }, [projectId]);

  const parseStory = async () => {
    setLoading(true);
    try {
      const nextSkeleton = await apiService.parseStory(projectId);
      dispatch(setSkeleton(nextSkeleton));
      message.success("故事骨架已生成");
    } catch (error) {
      message.error(error instanceof Error ? error.message : "解析故事失败");
    } finally {
      setLoading(false);
    }
  };

  const confirmSkeleton = async () => {
    const currentSkeleton = skeleton;
    if (!currentSkeleton) {
      return;
    }

    const edits =
      editableSegments.length > 0
        ? buildSkeletonConfirmationEdits(currentSkeleton.segments, editableSegments)
        : pendingEdits;

    setLoading(true);
    try {
      const confirmed = await apiService.confirmSkeleton(projectId, currentSkeleton.skeleton_id, edits);
      dispatch(setSkeleton(confirmed));
      message.success("骨架已确认");
      navigate(`/projects/${projectId}/highlights`);
    } catch (error) {
      message.error(error instanceof Error ? error.message : "确认骨架失败");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-stack">
      <Card
        title="骨架确认"
        extra={
          <Space>
            <Button onClick={() => void parseStory()} loading={loading}>
              {skeleton ? "重新生成骨架" : "解析故事"}
            </Button>
            <Button type="primary" onClick={() => void confirmSkeleton()} disabled={!skeleton} loading={loading}>
              确认骨架
            </Button>
          </Space>
        }
      >
        {skeleton ? (
          <Space direction="vertical" style={{ width: "100%" }}>
            <Space wrap>
              <Tag>版本 {skeleton.version}</Tag>
              <Tag color="blue">覆盖率 {skeleton.narrative_coverage.toFixed(2)}</Tag>
              <Tag color="purple">置信度 {skeleton.parsing_confidence.toFixed(2)}</Tag>
              <Tag>{skeleton.status}</Tag>
            </Space>
            <SegmentEditor
              segments={skeleton.segments}
              onChange={(segments, edits) => {
                setEditableSegments(segments);
                setPendingEdits(edits);
              }}
            />
          </Space>
        ) : (
          <Empty description="还没有故事骨架，先执行一次解析。" />
        )}
      </Card>
    </div>
  );
}
