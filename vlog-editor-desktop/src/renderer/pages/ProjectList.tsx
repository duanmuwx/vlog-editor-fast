import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button, Card, Popconfirm, Space, Table, Typography, message } from "antd";

import { apiService } from "../services/api";
import { useAppDispatch, useAppSelector } from "../store/hooks";
import {
  removeProjectSummary,
  setCurrentProjectDetail,
  setCurrentProjectId,
  setProjectError,
  setProjectList,
  setProjectListLoading,
} from "../store/projectSlice";
import { setWorkflowStage } from "../store/workflowSlice";

export default function ProjectList(): JSX.Element {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const projects = useAppSelector((state) => state.project.items);
  const loading = useAppSelector((state) => state.project.listLoading);

  const loadProjects = async () => {
    dispatch(setProjectListLoading(true));
    dispatch(setProjectError(null));
    try {
      const response = await apiService.getProjects();
      dispatch(setProjectList(response.projects));
    } catch (error) {
      dispatch(setProjectError(error instanceof Error ? error.message : "加载项目失败"));
      message.error(error instanceof Error ? error.message : "加载项目失败");
    } finally {
      dispatch(setProjectListLoading(false));
    }
  };

  useEffect(() => {
    void loadProjects();
  }, []);

  const openProject = async (projectId: string) => {
    try {
      const detail = await apiService.getProject(projectId);
      dispatch(setCurrentProjectId(projectId));
      dispatch(setCurrentProjectDetail(detail));
      dispatch(setWorkflowStage("validation"));
      navigate(`/projects/${projectId}/validation`);
    } catch (error) {
      message.error(error instanceof Error ? error.message : "打开项目失败");
    }
  };

  const deleteProject = async (projectId: string) => {
    try {
      await apiService.deleteProject(projectId);
      dispatch(removeProjectSummary(projectId));
      message.success("项目已删除");
    } catch (error) {
      message.error(error instanceof Error ? error.message : "删除项目失败");
    }
  };

  return (
    <div className="page-stack">
      <Card
        title="项目列表"
        extra={
          <Button type="primary" onClick={() => navigate("/projects/new")}>
            新建项目
          </Button>
        }
      >
        <Typography.Paragraph type="secondary">
          桌面端直接读取本地项目工作区；打开后会继续进入工作流。
        </Typography.Paragraph>
        <Table
          rowKey="project_id"
          loading={loading}
          dataSource={projects}
          columns={[
            { title: "项目名", dataIndex: "project_name" },
            { title: "状态", dataIndex: "status" },
            { title: "视频数", dataIndex: "total_videos" },
            { title: "照片数", dataIndex: "total_photos" },
            { title: "总时长(秒)", dataIndex: "total_duration" },
            { title: "更新时间", dataIndex: "updated_at" },
            {
              title: "操作",
              render: (_value, record) => (
                <Space>
                  <Button size="small" type="link" onClick={() => openProject(record.project_id)}>
                    打开
                  </Button>
                  <Popconfirm
                    title="确认删除项目？"
                    description="会同时删除数据库和工作目录。"
                    onConfirm={() => deleteProject(record.project_id)}
                  >
                    <Button size="small" danger type="link">
                      删除
                    </Button>
                  </Popconfirm>
                </Space>
              ),
            },
          ]}
        />
      </Card>
    </div>
  );
}
