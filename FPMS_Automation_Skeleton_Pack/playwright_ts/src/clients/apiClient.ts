import type { APIRequestContext, APIResponse } from "@playwright/test";

export class ApiClient {
  constructor(
    private readonly request: APIRequestContext,
    private readonly apiBaseUrl: string
  ) {}

  async get(path: string): Promise<APIResponse> {
    return this.request.get(`${this.apiBaseUrl.replace(/\/$/, "")}/${path.replace(/^\//, "")}`);
  }

  async post(path: string, data?: unknown): Promise<APIResponse> {
    return this.request.post(`${this.apiBaseUrl.replace(/\/$/, "")}/${path.replace(/^\//, "")}`, { data });
  }

  async patch(path: string, data?: unknown): Promise<APIResponse> {
    return this.request.patch(`${this.apiBaseUrl.replace(/\/$/, "")}/${path.replace(/^\//, "")}`, { data });
  }
}
