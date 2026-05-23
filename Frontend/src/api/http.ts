import axios, { AxiosError } from "axios";
import { ElMessage } from "element-plus";

export interface ApiResponse<T> {
  code: number;
  msg: string;
  data: T;
}

export const http = axios.create({
  baseURL: "/api",
  timeout: 12000,
});

http.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiResponse<unknown>>) => {
    const message = error.response?.data?.msg || error.message || "请求失败";
    ElMessage.error(message);
    return Promise.reject(error);
  },
);

export async function request<T>(config: Parameters<typeof http.request<ApiResponse<T>>>[0]) {
  const response = await http.request<ApiResponse<T>>(config);
  return response.data;
}
