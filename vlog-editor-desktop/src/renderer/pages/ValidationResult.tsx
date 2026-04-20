import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Button, Card, Col, List, Row, Space, Statistic, Table, Tag, Typography, message } from "antd";

import { apiService } from "../services/api";
import { useAppDispatch, useAppSelector } from "../store/hooks";
import { setCurrentProjectDetail, setCurrentProjectId } from "../store/projectSlice";
import { setAssetIndex, setValidationReport, setWorkflowStage } from "../store/workflowSlice";

export default function ValidationResult(): JSX.Element {
  const { projectId = "" } = useParams();
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const validationReport = useAppSelector((state) => state.workflow.validationReport);
  const assetIndex = useAppSelector((state) => state.workflow.assetIndex);
  const [loading, setLoading] = useState(false);

  const loadPage = async () => {
    setLoading(true);
    try {
      const [detail, validation, assets] = await Promise.all([
        apiService.getProject(projectId),
        apiService.validateProject(projectId),
        apiService.getAssets(projectId),
      ]);

      dispatch(setCurrentProjectId(projectId));
      dispatch(setCurrentProjectDetail(detail));
      dispatch(setValidationReport(validation.validation_report));
      dispatch(setAssetIndex(assets));
      dispatch(setWorkflowStage("validation"));
    } catch (error) {
      message.error(error instanceof Error ? error.message : "加载校验页失败");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadPage();
  }, [projectId]);

  return (
    <div className="page-stack">
      <Card
        title="输入校验结果"
        extra={
          <Space>
            <Button onClick={() => void loadPage()} loading={loading}>
              重新校验
            </Button>
            <Button type="primary" onClick={() => navigate(`/projects/${projectId}/skeleton`)}>
              进入骨架确认
            </Button>
          </Space>
        }
      >
        {validationReport ? (
          <Space direction="vertical" style={{ width: "100%" }}>
            <Row gutter={16}>
              <Col span={6}>
                <Statistic title="是否通过" value={validationReport.is_valid ? "是" : "否"} />
              </Col>
              <Col span={6}>
                <Statistic title="文件总数" value={validationReport.media_summary.total_files ?? 0} />
              </Col>
              <Col span={6}>
                <Statistic title="视频数" value={validationReport.media_summary.total_videos ?? 0} />
              </Col>
              <Col span={6}>
                <Statistic title="照片数" value={validationReport.media_summary.total_photos ?? 0} />
              </Col>
            </Row>
            <Row gutter={16}>
              <Col span={8}>
                <Card size="small" title="错误">
                  <List
                    locale={{ emptyText: "无" }}
                    dataSource={validationReport.errors}
                    renderItem={(item) => <List.Item><Tag color="error">{item}</Tag></List.Item>}
                  />
                </Card>
              </Col>
              <Col span={8}>
                <Card size="small" title="警告">
                  <List
                    locale={{ emptyText: "无" }}
                    dataSource={validationReport.warnings}
                    renderItem={(item) => <List.Item><Tag color="warning">{item}</Tag></List.Item>}
                  />
                </Card>
              </Col>
              <Col span={8}>
                <Card size="small" title="建议">
                  <List
                    locale={{ emptyText: "无" }}
                    dataSource={validationReport.recommendations}
                    renderItem={(item) => <List.Item><Typography.Text>{item}</Typography.Text></List.Item>}
                  />
                </Card>
              </Col>
            </Row>
          </Space>
        ) : (
          <Typography.Text type="secondary">尚未加载校验信息</Typography.Text>
        )}
      </Card>
      <Card title="资产明细">
        <Table
          rowKey="file_id"
          dataSource={assetIndex?.media_items ?? []}
          columns={[
            { title: "文件路径", dataIndex: "file_path", ellipsis: true },
            { title: "类型", dataIndex: "file_type" },
            { title: "大小", dataIndex: "file_size" },
            { title: "时长", dataIndex: "duration" },
            {
              title: "分辨率",
              render: (_value, record) =>
                Array.isArray(record.resolution) ? record.resolution.join("x") : "-",
            },
            {
              title: "音频",
              render: (_value, record) => (record.has_audio ? "有" : "无"),
            },
          ]}
        />
      </Card>
    </div>
  );
}
