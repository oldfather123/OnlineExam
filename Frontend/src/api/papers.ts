import { request } from "./http";
import type { PageResult } from "./questions";

export interface Paper {
  id: string;
  title: string;
  description: string;
  duration_minutes: number;
  total_marks: number;
  actual_total?: number;
  is_published: boolean;
  created_at: string;
  updated_at: string;
}

export interface PaperQuery {
  title?: string;
  is_published?: "true" | "false" | "";
  currentPage?: number;
  pageSize?: number;
}

export interface PaperModule {
  id: string;
  paper_id: string;
  title: string;
  description: string;
  sequence_number: number;
}

export interface PaperQuestionLink {
  id: string;
  paper_id: string;
  question_id: string;
  sequence_number: number;
  marks: number;
  module: string;
  question_detail?: {
    id: string;
    topic: string;
    options: string[] | string;
    answer: string;
    type: "select" | "judge";
  } | null;
}

export interface PaperDetailModule extends PaperModule {
  questions: PaperQuestionLink[];
}

export function getPapers(params: PaperQuery) {
  return request<PageResult<Paper>>({
    url: "/papers",
    method: "GET",
    params,
  });
}

export function getPaperSelector() {
  return request<PageResult<Paper>>({
    url: "/papers/selector",
    method: "GET",
  });
}

export function getPaper(id: string) {
  return request<Paper>({
    url: `/papers/${id}`,
    method: "GET",
  });
}

export function createPaper(data: Pick<Paper, "title" | "description" | "duration_minutes" | "total_marks" | "is_published">) {
  return request<Paper>({
    url: "/papers",
    method: "POST",
    data,
  });
}

export function updatePaper(id: string, data: Partial<Pick<Paper, "title" | "description" | "duration_minutes" | "total_marks" | "is_published">>) {
  return request<Paper>({
    url: `/papers/${id}`,
    method: "PUT",
    data,
  });
}

export function deletePaper(id: string) {
  return request<null>({
    url: `/papers/${id}`,
    method: "DELETE",
  });
}

export function publishPaper(id: string) {
  return request<null>({
    url: "/papers/publish",
    method: "POST",
    data: { id },
  });
}

export function unpublishPaper(id: string) {
  return request<null>({
    url: "/papers/publish",
    method: "DELETE",
    data: { id },
  });
}

export function getPaperDetail(id: string) {
  return request<PaperDetailModule[]>({
    url: `/papers/${id}/detail`,
    method: "GET",
  });
}

export function createPaperModule(data: Pick<PaperModule, "paper_id" | "title" | "description">) {
  return request<PaperModule>({
    url: "/paper-modules",
    method: "POST",
    data,
  });
}

export function updatePaperModule(id: string, data: Partial<Pick<PaperModule, "title" | "description" | "sequence_number">>) {
  return request<PaperModule>({
    url: `/paper-modules/${id}`,
    method: "PUT",
    data,
  });
}

export function deletePaperModule(id: string, paperId: string) {
  return request<null>({
    url: "/paper-modules",
    method: "DELETE",
    data: { id, paper_id: paperId },
  });
}

export function createPaperQuestionLinks(questionsInfo: Array<Pick<PaperQuestionLink, "paper_id" | "question_id" | "module" | "marks">>) {
  return request<PaperQuestionLink[]>({
    url: "/paper-questions",
    method: "POST",
    data: { questions_info: questionsInfo },
  });
}

export function updatePaperQuestionLink(id: string, data: Partial<Pick<PaperQuestionLink, "marks" | "module" | "sequence_number">>) {
  return request<PaperQuestionLink>({
    url: `/paper-questions/${id}`,
    method: "PUT",
    data,
  });
}

export function deletePaperQuestionLink(id: string) {
  return request<null>({
    url: `/paper-questions/${id}`,
    method: "DELETE",
  });
}
