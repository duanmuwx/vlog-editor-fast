import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { Button, Card, Space, Table, Tag, message } from "antd";

import { apiService } from "../services/api";
import { ipc } from "../services/ipc";
import { useAppDispatch, useAppSelector } from "../store/hooks";
import { setExports } from "../store/artifactSlice";

export default function ExportHistory(): JSX.Element {
  const { projectId = "" } = useParams();
  const dispatch = useAppDispatch();
  const exportsData = useAppSelector((state) => state.artifact.exports);
  const [loading, setLoading] = useState(false);

  const loadExports = async () => {
    setLoading(true);
    try {
      const response = await apiService.getExports(projectId);
      dispatch(setExports(response));
    } catch (error) {
      message.error(error instanceof Error ? error.message : "加载导出历史失败");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadExports();
  }, [projectId]);

  return (
    <div className="page-stack">
      <Card
        title="导出历史"
        extra={
          <Button onClick={() => void loadExports()} loading={loading}>
            刷新
          </Button>
        }
      >
        <Table
          rowKey="export_id"
          dataSource={exportsData?.exports ?? []}
          columns={[
            { title: "Export ID", dataIndex: "export_id" },
            { title: "版本", dataIndex: "version_id" },
            {
              title: "状态",
              render: (_value, record) => (
                <Tag color={record.status === "success" ? "success" : "warning"}>{record.status}</Tag>
              ),
            },
            { title: "视频路径", dataIndex: "video_path", ellipsis: true },
            { title: "创建时间", dataIndex: "created_at" },
            {
              title: "操作",
              render: (_value, record) => (
                <Space>
                  <Button size="small" onClick={() => void ipc.openPath(record.video_path)}>
                    打开文件
                  </Button>
                  <Button size="small" onClick={() => void ipc.showItemInFolder(record.video_path)}>
                    打开目录
                  </Button>
                </Space>
              ),
            },
          ]}
        />
      </Card>
    </div>
  );
}
