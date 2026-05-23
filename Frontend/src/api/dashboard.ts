import { request } from "./http";
import type { UserRole } from "./users";

export interface TeacherDashboardSummary {
  role: "teacher";
  question_count: number;
  paper_count: number;
  exam_count: number;
  student_count: number;
  teacher_count: number;
  submitted_count: number;
  waiting_review_count: number;
}

export interface StudentDashboardSummary {
  role: "student";
  exam_count: number;
  submitted_count: number;
  average_score: number;
  upcoming_exam_count: number;
  error_archive_count: number;
}

export type DashboardSummary = TeacherDashboardSummary | StudentDashboardSummary;

export function getDashboardSummary(params: { role: UserRole; user_id?: string }) {
  return request<DashboardSummary>({
    url: "/dashboard/summary",
    method: "GET",
    params,
  });
}
