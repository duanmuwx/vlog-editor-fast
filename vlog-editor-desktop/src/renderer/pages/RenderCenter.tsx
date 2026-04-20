import { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import { Button, Card, Col, Empty, Row, Space, Typography, message } from "antd";

import DiagnosticsPanel from "../components/DiagnosticsPanel";
import TimelineSummaryPanel from "../components/TimelineSummary";
import VersionHistoryDrawer from "../components/VersionHistoryDrawer";
import { apiService } from "../services/api";
import { useAppDispatch, useAppSelector } from "../store/hooks";
import {
  setAudioMix,
  setCurrentTimeline,
  setExports,
  setNarration,
  setTimelineSummary,
  setVersionDiff,
  setVersionHistory,
} from "../store/artifactSlice";
import { setCurrentProjectDetail, setCurrentProjectId } from "../store/projectSlice";
import { setDiagnostics, setRuns } from "../store/runSlice";
import { setWorkflowStage } from "../store/workflowSlice";

const VERSION_TYPES = ["timeline", "narration", "audio_mix", "export"];

export default function RenderCenter(): JSX.Element {
  const { projectId = "" } = useParams();
  const dispatch = useAppDispatch();
  const timelineSummary = useAppSelector((state) => state.artifact.timelineSummary);
  const currentTimeline = useAppSelector((state) => state.artifact.currentTimeline);
  const narration = useAppSelector((state) => state.artifact.narration);
  const audioMix = useAppSelector((state) => state.artifact.audioMix);
  const exportsData = useAppSelector((state) => state.artifact.exports);
  const versionHistories = useAppSelector((state) => state.artifact.versionHistories);
  const versionDiffs = useAppSelector((state) => state.artifact.versionDiffs);
  const runs = useAppSelector((state) => state.run.runs);
  const diagnostics = useAppSelector((state) => state.run.diagnostics);
  const [loading, setLoading] = useState(false);
  const [historyOpen, setHistoryOpen] = useState(false);

  const loadPage = async () => {
    try {
      const detail = await apiService.getProject(projectId);
      dispatch(setCurrentProjectId(projectId));
      dispatch(setCurrentProjectDetail(detail));
      dispatch(setWorkflowStage("render"));
      const [exportsResponse, runsResponse] = await Promise.all([
        apiService.getExports(projectId).catch(() => null),
        apiService.getRuns(projectId).catch(() => null),
      ]);

      if (exportsResponse) {
        dispatch(setExports(exportsResponse));
      }
      if (runsResponse) {
        dispatch(setRuns(runsResponse));
      }
    } catch (error) {
      message.error(error instanceof Error ? error.message : "加载渲染中心失败");
    }
  };

  useEffect(() => {
    void loadPage();
  }, [projectId]);

  const loadVersions = async () => {
    const histories = await Promise.all(
      VERSION_TYPES.map((artifactType) =>
        apiService.getVersionHistory(projectId, artifactType).then((history) => {
          dispatch(setVersionHistory(history));
          return history;
        }),
      ),
    );
    return histories;
  };

  const createEditPlan = async () => {
    setLoading(true);
    try {
      const summary = await apiService.createEditPlan(projectId);
      dispatch(setTimelineSummary(summary));
      const detail = await apiService.getTimeline(projectId, summary.version_id);
      dispatch(setCurrentTimeline(detail));
      message.success("时间线已生成");
    } catch (error) {
      message.error(error instanceof Error ? error.message : "生成时间线失败");
    } finally {
      setLoading(false);
    }
  };

  const generateNarration = async () => {
    setLoading(true);
    try {
      const result = await apiService.generateNarration(projectId);
      dispatch(setNarration(result));
      message.success("旁白生成完成");
    } catch (error) {
      message.error(error instanceof Error ? error.message : "生成旁白失败");
    } finally {
      setLoading(false);
    }
  };

  const mixAudio = async () => {
    setLoading(true);
    try {
      const result = await apiService.mixAudio(projectId);
      dispatch(setAudioMix(result));
      message.success("音频混合完成");
    } catch (error) {
      message.error(error instanceof Error ? error.message : "混音失败");
    } finally {
      setLoading(false);
    }
  };

  const renderExport = async () => {
    setLoading(true);
    try {
      const result = await apiService.renderExport(projectId);
      dispatch(
        setExports({
          total_exports: (exportsData?.total_exports ?? 0) + 1,
          exports: [result, ...(exportsData?.exports ?? [])],
        }),
      );
      message.success("导出完成");
    } catch (error) {
      message.error(error instanceof Error ? error.message : "导出失败");
    } finally {
      setLoading(false);
    }
  };

  const summaryCards = useMemo(
    () => [
      { title: "Timeline", value: timelineSummary?.version_id ?? "-" },
      { title: "Narration", value: narration?.version_id ?? "-" },
      { title: "Audio Mix", value: audioMix?.version_id ?? "-" },
      { title: "Exports", value: exportsData?.total_exports ?? 0 },
    ],
    [audioMix, exportsData, narration, timelineSummary],
  );

  return (
    <div className="page-stack">
      <Card
        title="渲染中心"
        extra={
          <Space>
            <Button onClick={() => void loadVersions().then(() => setHistoryOpen(true))}>版本历史</Button>
            <Button onClick={() => void loadPage()}>刷新数据</Button>
          </Space>
        }
      >
        <Space direction="vertical" style={{ width: "100%" }}>
          <Row gutter={16}>
            {summaryCards.map((item) => (
              <Col span={6} key={item.title}>
                <Card size="small" title={item.title}>
                  <Typography.Text strong>{String(item.value)}</Typography.Text>
                </Card>
              </Col>
            ))}
          </Row>
          <Space wrap>
            <Button onClick={() => void createEditPlan()} loading={loading}>
              生成 Timeline
            </Button>
            <Button onClick={() => void generateNarration()} loading={loading} disabled={!timelineSummary}>
              生成旁白
            </Button>
            <Button onClick={() => void mixAudio()} loading={loading} disabled={!narration}>
              混合音频
            </Button>
            <Button type="primary" onClick={() => void renderExport()} loading={loading} disabled={!audioMix}>
              执行导出
            </Button>
          </Space>
        </Space>
      </Card>
      <TimelineSummaryPanel summary={timelineSummary} detail={currentTimeline} />
      <Card title="阶段结果">
        {timelineSummary || narration || audioMix ? (
          <Space direction="vertical">
            {narration && <Typography.Text>旁白版本：{narration.version_id}</Typography.Text>}
            {audioMix && <Typography.Text>混音版本：{audioMix.version_id}</Typography.Text>}
            {exportsData && <Typography.Text>导出记录：{exportsData.total_exports}</Typography.Text>}
          </Space>
        ) : (
          <Empty description="还没有生成任何渲染产物" />
        )}
      </Card>
      <Card title="运行记录与诊断">
        <DiagnosticsPanel
          runs={runs}
          diagnostics={diagnostics}
          onLoad={(runId, format) => {
            void apiService
              .getRunDiagnostics(projectId, runId, format)
              .then((bundle) => dispatch(setDiagnostics({ runId, bundle })))
              .catch((error) => {
                message.error(error instanceof Error ? error.message : "加载诊断失败");
              });
          }}
          onRetry={(runId, stageName) => {
            void apiService
              .retryStage(projectId, runId, stageName)
              .then(() => {
                message.success("已触发 Retry");
              })
              .catch((error) => {
                message.error(error instanceof Error ? error.message : "Retry 失败");
              });
          }}
          onResume={(runId) => {
            void apiService
              .resumeRun(projectId, runId)
              .then(() => {
                message.success("已触发 Resume");
              })
              .catch((error) => {
                message.error(error instanceof Error ? error.message : "Resume 失败");
              });
          }}
        />
      </Card>
      <VersionHistoryDrawer
        open={historyOpen}
        histories={versionHistories}
        diffs={versionDiffs}
        onClose={() => setHistoryOpen(false)}
        onLoadDiff={(artifactType, firstId, secondId) => {
          void apiService
            .getVersionDiff(projectId, artifactType, firstId, secondId)
            .then((diff) => dispatch(setVersionDiff({ artifactType, diff })))
            .catch((error) => {
              message.error(error instanceof Error ? error.message : "加载 diff 失败");
            });
        }}
        onSwitchVersion={(artifactType, versionId) => {
          void apiService
            .switchVersion(projectId, artifactType, versionId)
            .then((history) => {
              dispatch(setVersionHistory(history));
              message.success("已切换激活版本");
            })
            .catch((error) => {
              message.error(error instanceof Error ? error.message : "切换版本失败");
            });
        }}
      />
    </div>
  );
}
