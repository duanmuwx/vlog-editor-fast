import axios, { AxiosError, type AxiosRequestConfig } from "axios";

import { ipc } from "./ipc";
import type {
  AlignmentCandidatesResponse,
  AlignmentSummary,
  AssetIndexResponse,
  AudioMixSummary,
  CreateProjectResponse,
  DiagnosticBundle,
  ExportHistoryResponse,
  ExportSummary,
  HighlightsResponse,
  MediaAnalysis,
  NarrationSummary,
  ProjectDetailResponse,
  ProjectInputContract,
  ProjectListResponse,
  RetryStageResponse,
  RunHistoryResponse,
  SkeletonEdit,
  StorySkeleton,
  TimelineDetail,
  TimelineSummary,
  ValidationResponse,
  VersionHistory,
} from "../types/api";

class ApiService {
  private readonly client = axios.create({
    timeout: 60_000,
  });

  private baseUrlPromise: Promise<string> | null = null;

  async getProjects(): Promise<ProjectListResponse> {
    return this.request<ProjectListResponse>({ method: "GET", url: "/projects" });
  }

  async createProject(input: ProjectInputContract): Promise<CreateProjectResponse> {
    return this.request<CreateProjectResponse>({
      method: "POST",
      url: "/projects/create",
      data: input,
    });
  }

  async getProject(projectId: string): Promise<ProjectDetailResponse> {
    return this.request<ProjectDetailResponse>({ method: "GET", url: `/projects/${projectId}` });
  }

  async deleteProject(projectId: string): Promise<void> {
    await this.request<void>({ method: "DELETE", url: `/projects/${projectId}` });
  }

  async validateProject(projectId: string): Promise<ValidationResponse> {
    return this.request<ValidationResponse>({
      method: "POST",
      url: `/projects/${projectId}/validate`,
    });
  }

  async getAssets(projectId: string): Promise<AssetIndexResponse> {
    return this.request<AssetIndexResponse>({ method: "GET", url: `/projects/${projectId}/assets` });
  }

  async parseStory(projectId: string): Promise<StorySkeleton> {
    return this.request<StorySkeleton>({ method: "POST", url: `/projects/${projectId}/story/parse` });
  }

  async getCurrentSkeleton(projectId: string): Promise<StorySkeleton> {
    return this.request<StorySkeleton>({
      method: "GET",
      url: `/projects/${projectId}/skeleton/current`,
    });
  }

  async getSkeleton(projectId: string, skeletonId: string): Promise<StorySkeleton> {
    return this.request<StorySkeleton>({
      method: "GET",
      url: `/projects/${projectId}/skeleton/${skeletonId}`,
    });
  }

  async confirmSkeleton(projectId: string, skeletonId: string, edits: SkeletonEdit[]): Promise<StorySkeleton> {
    return this.request<StorySkeleton>({
      method: "POST",
      url: `/projects/${projectId}/skeleton/${skeletonId}/confirm`,
      data: {
        skeleton_id: skeletonId,
        edits,
      },
    });
  }

  async analyzeMedia(projectId: string): Promise<MediaAnalysis> {
    return this.request<MediaAnalysis>({
      method: "POST",
      url: `/projects/${projectId}/analyze-media`,
    });
  }

  async getMediaAnalysis(projectId: string): Promise<MediaAnalysis> {
    return this.request<MediaAnalysis>({
      method: "GET",
      url: `/projects/${projectId}/media-analysis`,
    });
  }

  async alignMedia(projectId: string): Promise<AlignmentSummary> {
    return this.request<AlignmentSummary>({
      method: "POST",
      url: `/projects/${projectId}/align-media`,
    });
  }

  async getAlignmentCandidates(projectId: string, segmentId: string): Promise<AlignmentCandidatesResponse> {
    return this.request<AlignmentCandidatesResponse>({
      method: "GET",
      url: `/projects/${projectId}/alignment-candidates/${segmentId}`,
    });
  }

  async confirmHighlights(
    projectId: string,
    selections: { segment_id: string; shot_id: string; user_confirmed: boolean }[],
  ): Promise<HighlightsResponse> {
    return this.request<HighlightsResponse>({
      method: "POST",
      url: `/projects/${projectId}/confirm-highlights`,
      data: { selections },
    });
  }

  async getCurrentHighlights(projectId: string): Promise<HighlightsResponse> {
    return this.request<HighlightsResponse>({
      method: "GET",
      url: `/projects/${projectId}/highlights/current`,
    });
  }

  async createEditPlan(projectId: string): Promise<TimelineSummary> {
    return this.request<TimelineSummary>({
      method: "POST",
      url: `/projects/${projectId}/edit-plan`,
    });
  }

  async getVersionHistory(projectId: string, artifactType: string): Promise<VersionHistory> {
    return this.request<VersionHistory>({
      method: "GET",
      url: `/projects/${projectId}/versions/${artifactType}`,
    });
  }

  async switchVersion(projectId: string, artifactType: string, versionId: string): Promise<VersionHistory> {
    await this.request<void>({
      method: "POST",
      url: `/projects/${projectId}/versions/${artifactType}/${versionId}/switch`,
    });
    return this.getVersionHistory(projectId, artifactType);
  }

  async getVersionDiff(projectId: string, artifactType: string, firstId: string, secondId: string): Promise<unknown> {
    return this.request<unknown>({
      method: "GET",
      url: `/projects/${projectId}/versions/${artifactType}/${firstId}/diff/${secondId}`,
    });
  }

  async getTimeline(projectId: string, versionId: string): Promise<TimelineDetail> {
    return this.request<TimelineDetail>({
      method: "GET",
      url: `/projects/${projectId}/timeline/${versionId}`,
    });
  }

  async generateNarration(projectId: string): Promise<NarrationSummary> {
    return this.request<NarrationSummary>({
      method: "POST",
      url: `/projects/${projectId}/generate-narration`,
    });
  }

  async mixAudio(projectId: string): Promise<AudioMixSummary> {
    return this.request<AudioMixSummary>({
      method: "POST",
      url: `/projects/${projectId}/mix-audio`,
    });
  }

  async renderExport(projectId: string): Promise<ExportSummary> {
    return this.request<ExportSummary>({
      method: "POST",
      url: `/projects/${projectId}/render-export`,
    });
  }

  async getExports(projectId: string): Promise<ExportHistoryResponse> {
    return this.request<ExportHistoryResponse>({
      method: "GET",
      url: `/projects/${projectId}/exports`,
    });
  }

  async getRuns(projectId: string): Promise<RunHistoryResponse> {
    return this.request<RunHistoryResponse>({
      method: "GET",
      url: `/projects/${projectId}/runs`,
    });
  }

  async getRunDiagnostics(projectId: string, runId: string, format = "json"): Promise<DiagnosticBundle> {
    return this.request<DiagnosticBundle>({
      method: "GET",
      url: `/projects/${projectId}/runs/${runId}/diagnostics`,
      params: { format },
    });
  }

  async getDiagnostics(projectId: string, runId: string): Promise<DiagnosticBundle> {
    return this.request<DiagnosticBundle>({
      method: "GET",
      url: `/projects/${projectId}/diagnostics/${runId}`,
    });
  }

  async retryStage(projectId: string, runId: string, stageName: string): Promise<RetryStageResponse> {
    return this.request<RetryStageResponse>({
      method: "POST",
      url: `/projects/${projectId}/runs/${runId}/retry/${stageName}`,
    });
  }

  async resumeRun(projectId: string, runId: string, failedStage?: string): Promise<ExportSummary> {
    return this.request<ExportSummary>({
      method: "POST",
      url: `/projects/${projectId}/runs/${runId}/resume`,
      data: failedStage ? { failed_stage: failedStage } : undefined,
    });
  }

  async regenerate(projectId: string, regenType: string, payload?: Record<string, unknown>): Promise<ExportSummary> {
    return this.request<ExportSummary>({
      method: "POST",
      url: `/projects/${projectId}/regenerate/${regenType}`,
      data: payload,
    });
  }

  private async request<T>(config: AxiosRequestConfig): Promise<T> {
    const baseURL = await this.getBaseUrl();

    try {
      const response = await this.client.request<T>({
        ...config,
        baseURL,
      });
      return response.data;
    } catch (error) {
      throw this.normalizeError(error);
    }
  }

  private async getBaseUrl(): Promise<string> {
    if (!this.baseUrlPromise) {
      this.baseUrlPromise = ipc
        .getApiBaseUrl()
        .catch(() => import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000/api")
        .then((baseUrl) => baseUrl.replace(/\/$/, ""));
    }

    return this.baseUrlPromise;
  }

  private normalizeError(error: unknown): Error {
    if (error instanceof Error && !axios.isAxiosError(error)) {
      return error;
    }

    const axiosError = error as AxiosError<{ detail?: string }>;
    const message =
      axiosError.response?.data?.detail ?? axiosError.message ?? "Unknown API request failure";
    return new Error(message);
  }
}

export const apiService = new ApiService();
