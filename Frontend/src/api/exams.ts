import { request } from "./http";

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

export function getOnlinePaper(params: { exam_id?: string; paper_id?: string }) {
  return request<OnlinePaper>({
    url: "/papers/online",
    method: "GET",
    params,
  });
}
