export interface ProjectInputContract {
  project_name: string;
  travel_note: string;
  media_files: string[];
  bgm_asset?: string | null;
  tts_voice?: string | null;
  metadata_pack?: Record<string, unknown> | null;
}

export interface ProjectSummary {
  project_id: string;
  project_name: string;
  status: string;
  created_at: string;
  updated_at: string;
  total_videos: number;
  total_photos: number;
  total_duration: number;
}

export interface ProjectListResponse {
  total_projects: number;
  projects: ProjectSummary[];
}

export interface ProjectConfig {
  project_id: string;
  travel_note: string;
  bgm_asset?: string | null;
  tts_voice?: string | null;
  metadata_pack?: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
}

export interface ProjectDetailResponse {
  metadata: ProjectSummary;
  config: ProjectConfig | null;
}

export interface ValidationReport {
  project_id: string;
  is_valid: boolean;
  validation_timestamp: string;
  errors: string[];
  warnings: string[];
  media_summary: Record<string, number>;
  metadata_coverage: Record<string, number>;
  recommendations: string[];
}

export interface ValidationResponse {
  validation_report: ValidationReport;
}

export interface AssetItem {
  file_id: string;
  file_path: string;
  file_type: string;
  file_size: number;
  duration?: number | null;
  resolution?: number[] | null;
  creation_time?: string | null;
  has_audio?: boolean | null;
  exif_data?: Record<string, unknown> | null;
}

export interface AssetIndexResponse {
  index_id: string;
  project_id: string;
  total_videos: number;
  total_photos: number;
  total_duration: number;
  media_items: AssetItem[];
  metadata_availability: Record<string, number>;
  indexed_at: string;
}

export interface StorySegment {
  segment_id: string;
  title: string;
  summary: string;
  start_index: number;
  end_index: number;
  importance: string;
  confidence: number;
  keywords: string[];
  locations: string[];
  timestamps: string[];
}

export interface StorySkeleton {
  skeleton_id: string;
  project_id: string;
  version: number;
  total_segments: number;
  narrative_coverage: number;
  parsing_confidence: number;
  status: string;
  segments: StorySegment[];
  created_at: string;
  confirmed_at?: string | null;
  user_edits?: Record<string, unknown> | null;
}

export interface SkeletonEdit {
  operation: "merge" | "delete" | "reorder" | "mark";
  segment_ids: string[];
  payload?: Record<string, unknown>;
}

export interface MediaShot {
  shot_id: string;
  file_id: string;
  shot_type: string;
  start_time?: number | null;
  end_time?: number | null;
  duration?: number | null;
  quality_score: number;
  has_audio: boolean;
  visual_features: Record<string, unknown>;
  confidence: number;
}

export interface MediaAnalysis {
  analysis_id: string;
  project_id: string;
  total_shots: number;
  analysis_status: string;
  shots: MediaShot[];
  created_at: string;
}

export interface AlignmentCandidate {
  candidate_id: string;
  segment_id: string;
  shot_id: string;
  match_score: number;
  text_match_score: number;
  time_match_score?: number | null;
  location_match_score?: number | null;
  reasoning: string;
}

export interface AlignmentSummary {
  total_candidates: number;
  candidates: AlignmentCandidate[];
}

export interface AlignmentCandidatesResponse {
  segment_id: string;
  total_candidates: number;
  candidates: AlignmentCandidate[];
}

export interface HighlightSelectionInput {
  segment_id: string;
  shot_id: string;
  user_confirmed: boolean;
}

export interface HighlightSelection {
  selection_id: string;
  project_id: string;
  segment_id: string;
  selected_shot_id: string;
  user_confirmed: boolean;
  alternatives_available: number;
  confirmed_at?: string | null;
}

export interface HighlightsResponse {
  total_selections: number;
  selections: HighlightSelection[];
}

export interface TimelineSegmentSummary {
  segment_id: string;
  narration_start: number;
  narration_end: number;
  total_duration: number;
  clips?: TimelineClip[];
}

export interface TimelineClip {
  clip_id: string;
  shot_id: string;
  start_time: number;
  end_time: number;
  transition: string;
  duration?: number;
}

export interface TimelineSummary {
  timeline_id: string;
  version_id: string;
  total_duration_seconds: number;
  target_duration_seconds: number;
  segments?: TimelineSegmentSummary[];
  created_at: string;
}

export interface TimelineDetail {
  timeline_id: string;
  version_id: string;
  total_duration_seconds: number;
  target_duration_seconds: number;
  segments_count: number;
  created_at: string;
}

export interface NarrationSummary {
  narration_id: string;
  version_id: string;
  narration_text: string;
  tts_voice: string;
  subtitles_count: number;
  text_cards_count: number;
  created_at: string;
}

export interface AudioMixSummary {
  audio_mix_id: string;
  version_id: string;
  total_duration_seconds: number;
  tracks_count: number;
  created_at: string;
}

export interface ExportSummary {
  export_id: string;
  version_id: string;
  video_path: string;
  subtitle_path?: string;
  narration_path?: string;
  manifest_path?: string;
  status: string;
  created_at: string;
}

export interface ExportHistoryResponse {
  total_exports: number;
  exports: ExportSummary[];
}

export interface VersionEntry {
  version_id: string;
  status: string;
  created_at: string;
  upstream_versions?: Record<string, string>;
}

export interface VersionHistory {
  artifact_type: string;
  project_id: string;
  active_version_id?: string | null;
  versions: VersionEntry[];
}

export interface RunSummary {
  run_id: string;
  run_type: string;
  state: string;
  started_at: string;
  ended_at?: string | null;
}

export interface RunHistoryResponse {
  total_runs: number;
  runs: RunSummary[];
}

export interface DiagnosticBundle {
  run_id?: string;
  project_id?: string;
  content?: string;
  created_at?: string;
  [key: string]: unknown;
}

export interface RetryStageResponse {
  task_id: string;
  stage_name: string;
  attempt: number;
  status: string;
}

export interface CreateProjectResponse {
  project_id: string;
  validation_report: ValidationReport;
  asset_index: AssetIndexResponse;
}
