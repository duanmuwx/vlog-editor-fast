import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Alert, Button, Card, Empty, Space, Typography, message } from "antd";

import CandidatePicker from "../components/CandidatePicker";
import { apiService } from "../services/api";
import { useAppDispatch, useAppSelector } from "../store/hooks";
import { setCurrentProjectDetail, setCurrentProjectId } from "../store/projectSlice";
import {
  resetAlignmentCandidates,
  setAlignmentCandidates,
  setHighlights,
  setMediaAnalysis,
  setSkeleton,
  setWorkflowStage,
} from "../store/workflowSlice";

export default function HighlightReview(): JSX.Element {
  const { projectId = "" } = useParams();
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const skeleton = useAppSelector((state) => state.workflow.skeleton);
  const mediaAnalysis = useAppSelector((state) => state.workflow.mediaAnalysis);
  const alignmentCandidates = useAppSelector((state) => state.workflow.alignmentCandidates);
  const [loading, setLoading] = useState(false);
  const [selectedShots, setSelectedShots] = useState<Record<string, string>>({});

  const segments = skeleton?.segments ?? [];
  const hasMissingCandidates = segments.some(
    (segment) => (alignmentCandidates[segment.segment_id]?.candidates.length ?? 0) === 0,
  );

  const loadPage = async () => {
    try {
      const [detail, currentSkeleton] = await Promise.all([
        apiService.getProject(projectId),
        apiService.getCurrentSkeleton(projectId),
      ]);
      dispatch(setCurrentProjectId(projectId));
      dispatch(setCurrentProjectDetail(detail));
      dispatch(setSkeleton(currentSkeleton));
      dispatch(setWorkflowStage("highlights"));

      try {
        const highlights = await apiService.getCurrentHighlights(projectId);
        dispatch(setHighlights(highlights));
        const nextSelections = Object.fromEntries(
          highlights.selections.map((selection) => [selection.segment_id, selection.selected_shot_id]),
        );
        setSelectedShots(nextSelections);
      } catch {
        dispatch(setHighlights(null));
      }
    } catch (error) {
      message.error(error instanceof Error ? error.message : "加载高光页失败");
    }
  };

  useEffect(() => {
    void loadPage();
  }, [projectId]);

  const analyzeMedia = async () => {
    setLoading(true);
    try {
      const analysis = await apiService.analyzeMedia(projectId);
      dispatch(setMediaAnalysis(analysis));
      message.success("媒体分析完成");
    } catch (error) {
      message.error(error instanceof Error ? error.message : "媒体分析失败");
    } finally {
      setLoading(false);
    }
  };

  const alignMedia = async () => {
    if (!skeleton) {
      message.warning("请先确认骨架");
      return;
    }

    setLoading(true);
    dispatch(resetAlignmentCandidates());
    try {
      await apiService.alignMedia(projectId);
      const responses = await Promise.all(
        skeleton.segments.map(async (segment) => {
          const response = await apiService.getAlignmentCandidates(projectId, segment.segment_id);
          dispatch(setAlignmentCandidates(response));
          return response;
        }),
      );

      const defaultSelections = Object.fromEntries(
        responses
          .filter((response) => response.candidates.length > 0)
          .map((response) => [response.segment_id, response.candidates[0].shot_id]),
      );
      setSelectedShots((current) => ({ ...defaultSelections, ...current }));
      message.success("镜头候选已生成");
    } catch (error) {
      message.error(error instanceof Error ? error.message : "镜头对齐失败");
    } finally {
      setLoading(false);
    }
  };

  const confirmHighlights = async () => {
    if (!skeleton) {
      return;
    }

    const selections = skeleton.segments
      .filter((segment) => selectedShots[segment.segment_id])
      .map((segment) => ({
        segment_id: segment.segment_id,
        shot_id: selectedShots[segment.segment_id],
        user_confirmed: true,
      }));

    if (selections.length !== skeleton.segments.length) {
      message.warning("请为每个段落选择一个镜头");
      return;
    }

    setLoading(true);
    try {
      const highlights = await apiService.confirmHighlights(projectId, selections);
      dispatch(setHighlights(highlights));
      message.success("高光镜头已确认");
      navigate(`/projects/${projectId}/render`);
    } catch (error) {
      message.error(error instanceof Error ? error.message : "确认高光失败");
    } finally {
      setLoading(false);
    }
  };

  const candidateCount = useMemo(
    () =>
      Object.values(alignmentCandidates).reduce(
        (total, response) => total + response.candidates.length,
        0,
      ),
    [alignmentCandidates],
  );

  return (
    <div className="page-stack">
      <Card
        title="高光确认"
        extra={
          <Space>
            <Button onClick={() => void analyzeMedia()} loading={loading}>
              执行媒体分析
            </Button>
            <Button onClick={() => void alignMedia()} loading={loading} disabled={!skeleton}>
              重新对齐候选
            </Button>
            <Button type="primary" onClick={() => void confirmHighlights()} disabled={!skeleton} loading={loading}>
              确认高光
            </Button>
          </Space>
        }
      >
        <Space direction="vertical" style={{ width: "100%" }}>
          {mediaAnalysis ? (
            <Typography.Text type="secondary">
              已分析 {mediaAnalysis.total_shots} 个镜头，当前候选总数 {candidateCount}。
            </Typography.Text>
          ) : (
            <Typography.Text type="secondary">先执行媒体分析，再生成候选镜头。</Typography.Text>
          )}
          {hasMissingCandidates && (
            <Alert
              type="warning"
              showIcon
              message="存在无候选片段"
              description="部分段落没有候选镜头，确认前请重新分析媒体或重新对齐。"
            />
          )}
          {!skeleton ? (
            <Empty description="还没有已确认骨架" />
          ) : (
            skeleton.segments.map((segment) => (
              <CandidatePicker
                key={segment.segment_id}
                segment={segment}
                candidates={alignmentCandidates[segment.segment_id]?.candidates ?? []}
                selectedShotId={selectedShots[segment.segment_id]}
                onSelect={(shotId) =>
                  setSelectedShots((current) => ({
                    ...current,
                    [segment.segment_id]: shotId,
                  }))
                }
              />
            ))
          )}
        </Space>
      </Card>
    </div>
  );
}
