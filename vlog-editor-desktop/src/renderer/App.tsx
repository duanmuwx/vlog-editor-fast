import { useEffect, useMemo, useState } from "react";
import { Link, Route, Routes, useLocation, useNavigate } from "react-router-dom";
import { Alert, Button, Layout, Menu, Space, Spin, Tag, Typography } from "antd";

import { ipc } from "./services/ipc";
import ExportHistory from "./pages/ExportHistory";
import HighlightReview from "./pages/HighlightReview";
import ProjectList from "./pages/ProjectList";
import ProjectSetupWizard from "./pages/ProjectSetupWizard";
import RenderCenter from "./pages/RenderCenter";
import SkeletonReview from "./pages/SkeletonReview";
import ValidationResult from "./pages/ValidationResult";
import { useAppSelector } from "./store/hooks";

const { Header, Content, Sider } = Layout;

function App(): JSX.Element {
  const location = useLocation();
  const navigate = useNavigate();
  const currentProjectId = useAppSelector((state) => state.project.currentProjectId);
  const currentProject = useAppSelector((state) => state.project.currentProjectDetail?.metadata);
  const [backendLoading, setBackendLoading] = useState(true);
  const [backendHealthy, setBackendHealthy] = useState(false);
  const [backendMessage, setBackendMessage] = useState("正在检测本地服务…");

  useEffect(() => {
    let mounted = true;

    void ipc.getBackendStatus().then((status) => {
      if (!mounted) {
        return;
      }

      setBackendHealthy(status.healthy);
      setBackendMessage(status.message ?? (status.healthy ? "服务正常" : "服务不可用"));
      setBackendLoading(false);
    });

    return () => {
      mounted = false;
    };
  }, []);

  const selectedKeys = useMemo(() => [location.pathname], [location.pathname]);

  if (backendLoading) {
    return (
      <div className="fullscreen-center">
        <Spin size="large" />
        <Typography.Text type="secondary">正在启动本地服务…</Typography.Text>
      </div>
    );
  }

  return (
    <Layout className="app-shell">
      <Sider width={240} theme="light" className="app-sider">
        <div className="app-logo">Vlog Editor Fast</div>
        <Menu
          mode="inline"
          selectedKeys={selectedKeys}
          items={[
            { key: "/", label: <Link to="/">项目列表</Link> },
            { key: "/projects/new", label: <Link to="/projects/new">新建项目</Link> },
            {
              key: `/projects/${currentProjectId ?? "none"}/validation`,
              label: (
                <Link to={currentProjectId ? `/projects/${currentProjectId}/validation` : "/"}>
                  校验结果
                </Link>
              ),
            },
            {
              key: `/projects/${currentProjectId ?? "none"}/skeleton`,
              label: (
                <Link to={currentProjectId ? `/projects/${currentProjectId}/skeleton` : "/"}>
                  骨架确认
                </Link>
              ),
            },
            {
              key: `/projects/${currentProjectId ?? "none"}/highlights`,
              label: (
                <Link to={currentProjectId ? `/projects/${currentProjectId}/highlights` : "/"}>
                  高光确认
                </Link>
              ),
            },
            {
              key: `/projects/${currentProjectId ?? "none"}/render`,
              label: (
                <Link to={currentProjectId ? `/projects/${currentProjectId}/render` : "/"}>
                  渲染中心
                </Link>
              ),
            },
            {
              key: `/projects/${currentProjectId ?? "none"}/exports`,
              label: (
                <Link to={currentProjectId ? `/projects/${currentProjectId}/exports` : "/"}>
                  导出历史
                </Link>
              ),
            },
          ]}
        />
      </Sider>
      <Layout>
        <Header className="app-header">
          <Space size="middle">
            <Typography.Title level={4} style={{ margin: 0 }}>
              {currentProject?.project_name ?? "未选择项目"}
            </Typography.Title>
            <Tag color={backendHealthy ? "success" : "error"}>{backendHealthy ? "后端在线" : "后端异常"}</Tag>
            <Typography.Text type="secondary">{backendMessage}</Typography.Text>
          </Space>
          {!currentProjectId && (
            <Button type="primary" onClick={() => navigate("/projects/new")}>
              创建项目
            </Button>
          )}
        </Header>
        <Content className="app-content">
          {!backendHealthy && (
            <Alert
              type="warning"
              showIcon
              message="本地服务未就绪"
              description="你仍然可以查看桌面端界面，但大部分操作会失败。请先启动 FastAPI 后端。"
              style={{ marginBottom: 16 }}
            />
          )}
          <Routes>
            <Route path="/" element={<ProjectList />} />
            <Route path="/projects/new" element={<ProjectSetupWizard />} />
            <Route path="/projects/:projectId/validation" element={<ValidationResult />} />
            <Route path="/projects/:projectId/skeleton" element={<SkeletonReview />} />
            <Route path="/projects/:projectId/highlights" element={<HighlightReview />} />
            <Route path="/projects/:projectId/render" element={<RenderCenter />} />
            <Route path="/projects/:projectId/exports" element={<ExportHistory />} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  );
}

export default App;
