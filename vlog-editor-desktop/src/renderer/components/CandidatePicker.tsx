import { Card, List, Radio, Space, Tag, Typography } from "antd";

import type { AlignmentCandidate, StorySegment } from "../types/api";

interface CandidatePickerProps {
  segment: StorySegment;
  candidates: AlignmentCandidate[];
  selectedShotId?: string;
  onSelect(shotId: string): void;
}

export default function CandidatePicker({
  segment,
  candidates,
  selectedShotId,
  onSelect,
}: CandidatePickerProps): JSX.Element {
  return (
    <Card
      title={
        <Space>
          <Typography.Text strong>{segment.title}</Typography.Text>
          <Tag>{segment.importance}</Tag>
        </Space>
      }
    >
      <Typography.Paragraph>{segment.summary}</Typography.Paragraph>
      <Radio.Group
        value={selectedShotId}
        onChange={(event) => onSelect(event.target.value)}
        style={{ width: "100%" }}
      >
        <List
          dataSource={candidates}
          renderItem={(candidate) => (
            <List.Item>
              <Card style={{ width: "100%" }} size="small">
                <Space direction="vertical" style={{ width: "100%" }}>
                  <Space wrap>
                    <Radio value={candidate.shot_id}>镜头 {candidate.shot_id}</Radio>
                    <Tag color="blue">匹配 {candidate.match_score.toFixed(2)}</Tag>
                    <Tag>文本 {candidate.text_match_score.toFixed(2)}</Tag>
                    {typeof candidate.time_match_score === "number" && (
                      <Tag>时间 {candidate.time_match_score.toFixed(2)}</Tag>
                    )}
                    {typeof candidate.location_match_score === "number" && (
                      <Tag>地点 {candidate.location_match_score.toFixed(2)}</Tag>
                    )}
                  </Space>
                  <Typography.Text type="secondary">{candidate.reasoning}</Typography.Text>
                </Space>
              </Card>
            </List.Item>
          )}
        />
      </Radio.Group>
    </Card>
  );
}
