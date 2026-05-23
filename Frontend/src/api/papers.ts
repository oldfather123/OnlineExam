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

export function getPapers(params: PaperQuery) {
  return request<PageResult<Paper>>({
    url: "/papers",
    method: "GET",
    params,
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
