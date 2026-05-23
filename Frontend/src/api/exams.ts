import { request } from "./http";
import type { PageResult } from "./questions";

export interface Exam {
  id: string;
  paper_id: string;
  paper_title?: string;
  title: string;
  start_time: string;
  end_time: string;
  is_published: boolean;
  is_deleted: boolean;
  created_at: string;
  updated_at: string;
}

export interface ExamQuery {
  title?: string;
  is_published?: "true" | "false" | "";
  currentPage?: number;
  pageSize?: number;
}

export interface ExamPayload {
  paper_id: string;
  title: string;
  start_time: string;
  end_time: string;
  is_published: boolean;
}

export interface ExamEnterPayload {
  exam_id: string;
  student_id: string;
}

export interface ExamEnterResult {
  exam_id: string;
  student_id: string;
  exam_result_id: string;
  start_time: string;
  paper_id: string;
}

export interface OnlineQuestion {
  question_id: string;
  topic: string;
  options: string[] | string;
  type: "select" | "judge";
  marks: number;
  sequence_number: number;
}

export interface OnlinePaperModule {
  module_id: string;
  title: string;
  description: string;
  sequence_number: number;
  questions: OnlineQuestion[];
}

export interface OnlinePaper {
  paper: {
    id: string;
    title: string;
    description: string;
    duration_minutes: number;
    total_marks: number;
  };
  modules: OnlinePaperModule[];
}

export function enterExam(data: ExamEnterPayload) {
  return request<ExamEnterResult>({
    url: "/exams/enter",
    method: "POST",
    data,
  });
}

export function getExams(params: ExamQuery) {
  return request<PageResult<Exam>>({
    url: "/exams",
    method: "GET",
    params,
  });
}

export function createExam(data: ExamPayload) {
  return request<Exam>({
    url: "/exams",
    method: "POST",
    data,
  });
}

export function updateExam(id: string, data: Partial<ExamPayload>) {
  return request<Exam>({
    url: `/exams/${id}`,
    method: "PUT",
    data,
  });
}

export function deleteExam(id: string) {
  return request<null>({
    url: `/exams/${id}`,
    method: "DELETE",
  });
}

export function publishExam(id: string) {
  return request<null>({
    url: `/exams/publish/${id}`,
    method: "POST",
  });
}

export function unpublishExam(id: string) {
  return request<null>({
    url: `/exams/publish/${id}`,
    method: "DELETE",
  });
}

export function getAttendableExams() {
  return request<PageResult<Exam>>({
    url: "/exams/attend",
    method: "GET",
  });
}

export function getOnlinePaper(params: { exam_id?: string; paper_id?: string }) {
  return request<OnlinePaper>({
    url: "/papers/online",
    method: "GET",
    params,
  });
}
