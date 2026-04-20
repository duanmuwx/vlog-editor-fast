import { useMemo, useState } from "react";
import { Button, Drawer, Empty, Select, Space, Table, Typography } from "antd";

import type { VersionHistory } from "../types/api";

interface VersionHistoryDrawerProps {
  open: boolean;
  histories: Record<string, VersionHistory>;
  diffs: Record<string, unknown>;
  onClose(): void;
  onLoadDiff(artifactType: string, firstId: string, secondId: string): void;
  onSwitchVersion(artifactType: string, versionId: string): void;
}

export default function VersionHistoryDrawer({
  open,
  histories,
  diffs,
  onClose,
  onLoadDiff,
  onSwitchVersion,
}: VersionHistoryDrawerProps): JSX.Element {
  const artifactTypes = useMemo(() => Object.keys(histories), [histories]);
  const [selectedArtifactType, setSelectedArtifactType] = useState<string | undefined>(artifactTypes[0]);
  const [diffSelection, setDiffSelection] = useState<{ firstId?: string; secondId?: string }>({});

  const history = selectedArtifactType ? histories[selectedArtifactType] : undefined;
  const diffValue = selectedArtifactType ? diffs[selectedArtifactType] : undefined;

  return (
    <Drawer
      title="版本历史"
      width={720}
      open={open}
      onClose={onClose}
      extra={
        <Select
          value={selectedArtifactType}
          placeholder="选择产物类型"
          style={{ width: 180 }}
          onChange={setSelectedArtifactType}
          options={artifactTypes.map((artifactType) => ({
            label: artifactType,
            value: artifactType,
          }))}
        />
      }
    >
      {!history ? (
        <Empty description="暂无版本历史" />
      ) : (
        <Space direction="vertical" style={{ width: "100%" }} size="middle">
          <Typography.Text type="secondary">
            当前激活版本：{history.active_version_id ?? "无"}
          </Typography.Text>
          <Table
            rowKey="version_id"
            pagination={false}
            dataSource={history.versions}
            columns={[
              { title: "版本 ID", dataIndex: "version_id" },
              { title: "状态", dataIndex: "status" },
              { title: "创建时间", dataIndex: "created_at" },
              {
                title: "操作",
                render: (_value, record) => (
                  <Button size="small" onClick={() => onSwitchVersion(history.artifact_type, record.version_id)}>
                    切换为当前
                  </Button>
                ),
              },
            ]}
          />
          <Space wrap>
            <Select
              placeholder="版本 A"
              style={{ width: 220 }}
              value={diffSelection.firstId}
              onChange={(value) => setDiffSelection((current) => ({ ...current, firstId: value }))}
              options={history.versions.map((version) => ({
                label: version.version_id,
                value: version.version_id,
              }))}
            />
            <Select
              placeholder="版本 B"
              style={{ width: 220 }}
              value={diffSelection.secondId}
              onChange={(value) => setDiffSelection((current) => ({ ...current, secondId: value }))}
              options={history.versions.map((version) => ({
                label: version.version_id,
                value: version.version_id,
              }))}
            />
            <Button
              type="primary"
              onClick={() => {
                if (selectedArtifactType && diffSelection.firstId && diffSelection.secondId) {
                  onLoadDiff(selectedArtifactType, diffSelection.firstId, diffSelection.secondId);
                }
              }}
              disabled={!selectedArtifactType || !diffSelection.firstId || !diffSelection.secondId}
            >
              比较差异
            </Button>
          </Space>
          {diffValue && (
            <pre style={{ margin: 0, whiteSpace: "pre-wrap" }}>{JSON.stringify(diffValue, null, 2)}</pre>
          )}
        </Space>
      )}
    </Drawer>
  );
}
