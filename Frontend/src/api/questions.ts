import { request } from "./http";

export type QuestionType = "select" | "judge";

export interface Question {
  id: string;
  topic: string;
  options: string;
  answer: string;
  type: QuestionType;
  created_at: string;
}

export interface QuestionQuery {
  topic?: string;
  type?: QuestionType | "";
  currentPage?: number;
  pageSize?: number;
}

export interface PageResult<T> {
  total: number;
  data: T[];
}

export interface ErrorArchive {
  id: string;
  question_id: string;
  collector: string;
  explanation: string;
  created_at: string;
  question_detail?: {
    id: string;
    topic: string;
    options: string[] | string;
    answer: string;
    type: QuestionType;
  } | null;
}

export function getQuestions(params: QuestionQuery) {
  return request<PageResult<Question>>({
    url: "/questions",
    method: "GET",
    params,
  });
}

export function createQuestion(data: Pick<Question, "topic" | "options" | "answer" | "type">) {
  return request<Question>({
    url: "/questions",
    method: "POST",
    data,
  });
}

export function updateQuestion(id: string, data: Partial<Pick<Question, "topic" | "options" | "answer" | "type">>) {
  return request<Question>({
    url: `/questions/${id}`,
    method: "PUT",
    data,
  });
}

export function deleteQuestion(id: string) {
  return request<null>({
    url: `/questions/${id}`,
    method: "DELETE",
  });
}

export function getPaperAvailableQuestions(params: Pick<QuestionQuery, "topic" | "type">) {
  return request<Question[]>({
    url: "/questions/paper-available",
    method: "GET",
    params,
  });
}

export function getErrorArchives(params: { collector: string; topic?: string; currentPage?: number; pageSize?: number }) {
  return request<PageResult<ErrorArchive>>({
    url: "/error-archives",
    method: "GET",
    params,
  });
}

export function createErrorArchive(data: Pick<ErrorArchive, "collector" | "question_id"> & { explanation?: string }) {
  return request<ErrorArchive>({
    url: "/error-archives",
    method: "POST",
    data,
  });
}

export function updateErrorArchive(id: string, data: Partial<Pick<ErrorArchive, "explanation">>) {
  return request<ErrorArchive>({
    url: `/error-archives/${id}`,
    method: "PUT",
    data,
  });
}

export function deleteErrorArchive(collector: string, questionId: string) {
  return request<null>({
    url: "/error-archives",
    method: "DELETE",
    data: { collector, question_id: questionId },
  });
}
