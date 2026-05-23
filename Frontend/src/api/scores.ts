import { request } from "./http";

export interface AnswerItem {
  question_id: string;
  type: "select" | "judge" | "blank" | "subjective";
  payload: {
    value: string | string[];
  };
}

export interface AnswerCommitPayload {
  exam_result_id?: string;
  exam_id?: string;
  student_id?: string;
  action: "save" | "submit";
  client_ts: number;
  answers: AnswerItem[];
}

export interface ReviewPaperItem {
  exam_id: string;
  exam_title: string;
  start_time: string;
  end_time: string;
  paper: {
    paper_id: string;
    title: string;
  };
  review_stats: {
    total_students: number;
    submitted_students: number;
  };
}

export interface ReviewStudentItem {
  exam_result_id: string;
  student_id: string;
  submit_status: boolean;
  start_time: string | null;
  submitted_at: string | null;
  result_mark: number;
}

export interface ReviewQuestionItem {
  question_id: string;
  topic: string;
  type: "select" | "judge" | "blank" | "subjective";
  marks: number;
  standard_answer: string;
  student_answer: {
    value?: string | string[];
  };
  score: number;
  comment: string;
}

export interface ReviewResultDetail {
  exam_result: {
    id: string;
    exam_id: string;
    student_id: string;
    submit_status: boolean;
    submitted_at: string | null;
    result_mark: number;
  };
  questions: ReviewQuestionItem[];
}

export interface ReviewStatistics {
  exam_id: string;
  student_count: number;
  submitted_count: number;
  average_score: number;
  student_summary: Array<{
    exam_result_id: string;
    student_id: string;
    submit_status: boolean;
    total_score: number;
  }>;
  question_type_stats: Record<string, { full_mark: number; actual_mark: number; score_rate: number }>;
}

export interface PageItems<T> {
  total: number;
  page: number;
  page_size: number;
  items: T[];
}

export interface ScoreAnalyzeResult {
  student_id: string;
  exam_count: number;
  submitted_count: number;
  average_score: number;
  trend: Array<{
    exam_result_id: string;
    exam_id: string;
    exam_title: string;
    score: number;
    submit_status: boolean;
    start_time: string | null;
    submitted_at: string | null;
  }>;
  question_type_stats: Record<string, { full_mark: number; actual_mark: number; score_rate: number }>;
}

export function commitAnswers(data: AnswerCommitPayload) {
  return request<{
    exam_result_id: string;
    submit_status: boolean;
    last_client_ts: number;
    last_save_at: string;
    submitted_at: string | null;
  }>({
    url: "/answers/commit",
    method: "POST",
    data,
  });
}

export function getReviewPapers(params: { page?: number; page_size?: number }) {
  return request<PageItems<ReviewPaperItem>>({
    url: "/reviews/papers",
    method: "GET",
    params,
  });
}

export function getReviewStudents(examId: string, params: { page?: number; page_size?: number }) {
  return request<PageItems<ReviewStudentItem>>({
    url: `/reviews/exams/${examId}/students`,
    method: "GET",
    params,
  });
}

export function getReviewStatistics(examId: string) {
  return request<ReviewStatistics>({
    url: `/reviews/exams/${examId}/statistics`,
    method: "GET",
  });
}

export function getReviewResultDetail(examResultId: string) {
  return request<ReviewResultDetail>({
    url: `/reviews/exam-results/${examResultId}`,
    method: "GET",
  });
}

export function autoGrade(examResultId: string) {
  return request<{
    exam_result_id: string;
    auto_graded_count: number;
    subjective_pending_count: number;
    result_mark: number;
  }>({
    url: `/reviews/exam-results/${examResultId}/auto-grade`,
    method: "POST",
  });
}

export function submitReviewScores(
  examResultId: string,
  data: {
    grader_id?: string;
    finalize?: boolean;
    items: Array<{ question_id: string; mark: number; comment?: string }>;
  },
) {
  return request<{ exam_result_id: string; result_mark: number; finalize: boolean }>({
    url: `/reviews/exam-results/${examResultId}/grade`,
    method: "POST",
    data,
  });
}

export function getScoreAnalyze(studentId: string) {
  return request<ScoreAnalyzeResult>({
    url: "/scores/analyze",
    method: "GET",
    params: { student_id: studentId },
  });
}
