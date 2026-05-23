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
