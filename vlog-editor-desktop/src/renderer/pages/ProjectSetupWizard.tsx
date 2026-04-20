import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button, Card, Form, Input, Select, Space, Typography, message } from "antd";

import { apiService } from "../services/api";
import { ipc } from "../services/ipc";
import { useAppDispatch, useAppSelector } from "../store/hooks";
import { resetCreationDraft, updateCreationDraft } from "../store/creationDraftSlice";
import { setCurrentProjectDetail, setCurrentProjectId, upsertProjectSummary } from "../store/projectSlice";
import { setAssetIndex, setValidationReport, setWorkflowStage } from "../store/workflowSlice";

export default function ProjectSetupWizard(): JSX.Element {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const draft = useAppSelector((state) => state.creationDraft);
  const [submitting, setSubmitting] = useState(false);
  const [metadataPackText, setMetadataPackText] = useState(
    draft.metadata_pack ? JSON.stringify(draft.metadata_pack, null, 2) : "",
  );

  const selectMediaFiles = async () => {
    const filePaths = await ipc.selectMediaFiles();
    dispatch(updateCreationDraft({ media_files: filePaths }));
  };

  const selectBgmFile = async () => {
    const filePath = await ipc.selectBgmFile();
    dispatch(updateCreationDraft({ bgm_asset: filePath }));
  };

  const handleSubmit = async () => {
    let metadataPack = null;
    if (metadataPackText.trim()) {
      try {
        metadataPack = JSON.parse(metadataPackText);
      } catch {
        message.error("metadata pack 必须是合法 JSON");
        return;
      }
    }

    setSubmitting(true);
    try {
      const response = await apiService.createProject({
        ...draft,
        metadata_pack: metadataPack,
      });

      const detail = await apiService.getProject(response.project_id);
      dispatch(setCurrentProjectId(response.project_id));
      dispatch(setCurrentProjectDetail(detail));
      dispatch(
        upsertProjectSummary({
          ...detail.metadata,
        }),
      );
      dispatch(setValidationReport(response.validation_report));
      dispatch(setAssetIndex(response.asset_index));
      dispatch(setWorkflowStage("validation"));
      dispatch(resetCreationDraft());
      message.success("项目创建成功");
      navigate(`/projects/${response.project_id}/validation`);
    } catch (error) {
      message.error(error instanceof Error ? error.message : "创建项目失败");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="page-stack">
      <Card title="项目创建向导">
        <Form layout="vertical" onFinish={handleSubmit} initialValues={draft}>
          <Form.Item
            label="项目名称"
            required
            rules={[{ required: true, message: "请输入项目名称" }]}
          >
            <Input
              value={draft.project_name}
              onChange={(event) => dispatch(updateCreationDraft({ project_name: event.target.value }))}
            />
          </Form.Item>
          <Form.Item
            label="Travel Note"
            required
            rules={[{ required: true, message: "请输入 travel note" }]}
          >
            <Input.TextArea
              rows={8}
              value={draft.travel_note}
              onChange={(event) => dispatch(updateCreationDraft({ travel_note: event.target.value }))}
            />
          </Form.Item>
          <Form.Item label="素材文件">
            <Space direction="vertical" style={{ width: "100%" }}>
              <Space>
                <Button onClick={() => void selectMediaFiles()}>选择媒体文件</Button>
                <Typography.Text type="secondary">已选择 {draft.media_files.length} 个文件</Typography.Text>
              </Space>
              <div className="path-list">
                {draft.media_files.map((filePath) => (
                  <Typography.Text key={filePath} ellipsis>
                    {filePath}
                  </Typography.Text>
                ))}
              </div>
            </Space>
          </Form.Item>
          <Form.Item label="BGM 文件">
            <Space>
              <Button onClick={() => void selectBgmFile()}>选择 BGM</Button>
              <Typography.Text type="secondary">{draft.bgm_asset ?? "未选择"}</Typography.Text>
            </Space>
          </Form.Item>
          <Form.Item label="TTS Voice">
            <Select
              allowClear
              value={draft.tts_voice ?? undefined}
              onChange={(value) => dispatch(updateCreationDraft({ tts_voice: value ?? null }))}
              options={[
                { label: "default", value: "default" },
                { label: "female", value: "female" },
                { label: "male", value: "male" },
              ]}
            />
          </Form.Item>
          <Form.Item label="Metadata Pack (JSON，可选)">
            <Input.TextArea rows={6} value={metadataPackText} onChange={(event) => setMetadataPackText(event.target.value)} />
          </Form.Item>
          <Button type="primary" htmlType="submit" loading={submitting}>
            创建项目
          </Button>
        </Form>
      </Card>
    </div>
  );
}
