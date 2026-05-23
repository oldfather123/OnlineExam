import { request } from "./http";
import type { PageResult } from "./questions";

export type UserRole = "teacher" | "student";

export interface AppUser {
  id: string;
  username: string;
  real_name: string;
  role: UserRole;
  created_at?: string;
  updated_at?: string;
}

export interface LoginPayload {
  username: string;
  password: string;
}

export interface UserPayload {
  id?: string;
  username: string;
  password?: string;
  real_name?: string;
}

export function login(role: UserRole, data: LoginPayload) {
  return request<AppUser>({
    url: `/auth/${role}/login`,
    method: "POST",
    data,
  });
}

export function getUsers(role: UserRole, params: { keyword?: string; currentPage?: number; pageSize?: number }) {
  return request<PageResult<AppUser>>({
    url: role === "teacher" ? "/teachers" : "/students",
    method: "GET",
    params,
  });
}

export function createUser(role: UserRole, data: UserPayload) {
  return request<AppUser>({
    url: role === "teacher" ? "/teachers" : "/students",
    method: "POST",
    data,
  });
}

export function updateUser(role: UserRole, id: string, data: Partial<UserPayload>) {
  return request<AppUser>({
    url: role === "teacher" ? `/teachers/${id}` : `/students/${id}`,
    method: "PUT",
    data,
  });
}

export function deleteUser(role: UserRole, id: string) {
  return request<null>({
    url: role === "teacher" ? `/teachers/${id}` : `/students/${id}`,
    method: "DELETE",
  });
}

export function changePassword(role: UserRole, id: string, data: { old_password?: string; new_password: string }) {
  return request<null>({
    url: role === "teacher" ? `/teachers/${id}/password` : `/students/${id}/password`,
    method: "PUT",
    data,
  });
}
