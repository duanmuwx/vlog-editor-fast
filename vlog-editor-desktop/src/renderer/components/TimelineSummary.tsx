import { Card, Col, Empty, Row, Statistic, Table } from "antd";

import type { TimelineDetail, TimelineSummary } from "../types/api";

interface TimelineSummaryProps {
  summary: TimelineSummary | null;
  detail: TimelineDetail | null;
}

export default function TimelineSummaryPanel({
  summary,
  detail,
}: TimelineSummaryProps): JSX.Element {
  if (!summary) {
    return <Empty description="还没有时间线结果" />;
  }

  return (
    <Card title="时间线摘要">
      <Row gutter={16}>
        <Col span={8}>
          <Statistic title="总时长" value={summary.total_duration_seconds} suffix="秒" />
        </Col>
        <Col span={8}>
          <Statistic title="目标时长" value={summary.target_duration_seconds} suffix="秒" />
        </Col>
        <Col span={8}>
          <Statistic title="版本" value={summary.version_id} />
        </Col>
      </Row>
      {detail && (
        <Table
          pagination={false}
          style={{ marginTop: 16 }}
          dataSource={[
            {
              key: detail.version_id,
              timeline_id: detail.timeline_id,
              segments_count: detail.segments_count,
              created_at: detail.created_at,
            },
          ]}
          columns={[
            { title: "Timeline ID", dataIndex: "timeline_id" },
            { title: "片段数", dataIndex: "segments_count" },
            { title: "创建时间", dataIndex: "created_at" },
          ]}
        />
      )}
    </Card>
  );
}
