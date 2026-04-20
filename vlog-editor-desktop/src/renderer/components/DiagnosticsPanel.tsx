import { Button, Card, Empty, List, Segmented, Space, Table, Typography } from "antd";

import type { DiagnosticBundle, RunHistoryResponse } from "../types/api";

interface DiagnosticsPanelProps {
  runs: RunHistoryResponse | null;
  diagnostics: Record<string, DiagnosticBundle>;
  onLoad(runId: string, format: "json" | "markdown" | "html"): void;
  onRetry(runId: string, stageName: string): void;
  onResume(runId: string): void;
}

export default function DiagnosticsPanel({
  runs,
  diagnostics,
  onLoad,
  onRetry,
  onResume,
}: DiagnosticsPanelProps): JSX.Element {
  if (!runs || runs.runs.length === 0) {
    return <Empty description="暂无运行记录" />;
  }

  return (
    <Space direction="vertical" style={{ width: "100%" }} size="middle">
      <Table
        rowKey="run_id"
        pagination={false}
        dataSource={runs.runs}
        columns={[
          { title: "Run ID", dataIndex: "run_id" },
          { title: "类型", dataIndex: "run_type" },
          { title: "状态", dataIndex: "state" },
          { title: "开始时间", dataIndex: "started_at" },
          {
            title: "操作",
            render: (_value, record) => (
              <Space wrap>
                <Segmented
                  size="small"
                  options={["json", "markdown", "html"]}
                  defaultValue="json"
                  onChange={(value) => onLoad(record.run_id, value as "json" | "markdown" | "html")}
                />
                <Button size="small" onClick={() => onResume(record.run_id)}>
                  Resume
                </Button>
                <Button size="small" onClick={() => onRetry(record.run_id, "edit_planning")}>
                  Retry 编辑规划
                </Button>
              </Space>
            ),
          },
        ]}
      />
      <List
        dataSource={Object.entries(diagnostics)}
        renderItem={([runId, bundle]) => (
          <List.Item>
            <Card title={`诊断：${runId}`} style={{ width: "100%" }}>
              {"content" in bundle && typeof bundle.content === "string" ? (
                <Typography.Paragraph style={{ whiteSpace: "pre-wrap" }}>
                  {bundle.content}
                </Typography.Paragraph>
              ) : (
                <pre style={{ margin: 0, whiteSpace: "pre-wrap" }}>{JSON.stringify(bundle, null, 2)}</pre>
              )}
            </Card>
          </List.Item>
        )}
      />
    </Space>
  );
}
