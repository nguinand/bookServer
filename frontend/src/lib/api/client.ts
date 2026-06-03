import { PUBLIC_API_BASE_URL } from "$env/static/public";

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
    public readonly errorId?: string,
    public readonly body?: unknown,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export type Fetch = typeof globalThis.fetch;

export type QueryValue = string | number | boolean | undefined | null;
export type Query = Record<string, QueryValue>;

export interface RequestOptions {
  body?: unknown;
  query?: Query;
  signal?: AbortSignal;
}

export class ApiClient {
  constructor(
    private readonly fetch: Fetch,
    private readonly jwt?: string,
    private readonly baseUrl: string = PUBLIC_API_BASE_URL,
  ) {}

  async request<T>(
    method: string,
    path: string,
    opts: RequestOptions = {},
  ): Promise<T> {
    const url = new URL(`${this.baseUrl}/api${path}`);
    if (opts.query) {
      for (const [k, v] of Object.entries(opts.query)) {
        if (v !== undefined && v !== null) url.searchParams.set(k, String(v));
      }
    }

    const headers: Record<string, string> = { Accept: "application/json" };
    if (this.jwt) headers.Authorization = `Bearer ${this.jwt}`;
    if (opts.body !== undefined) headers["Content-Type"] = "application/json";

    const res = await this.fetch(url, {
      method,
      headers,
      body: opts.body !== undefined ? JSON.stringify(opts.body) : undefined,
      signal: opts.signal,
    });

    if (!res.ok) {
      const payload: { detail?: string; error_id?: string } = await res
        .json()
        .catch(() => ({}));
      throw new ApiError(
        res.status,
        payload.detail ?? res.statusText,
        payload.error_id,
        payload,
      );
    }

    if (res.status === 204) return undefined as T;
    return (await res.json()) as T;
  }

  get<T>(path: string, opts: Omit<RequestOptions, "body"> = {}): Promise<T> {
    return this.request<T>("GET", path, opts);
  }

  post<T>(
    path: string,
    body?: unknown,
    opts: Omit<RequestOptions, "body"> = {},
  ): Promise<T> {
    return this.request<T>("POST", path, { ...opts, body });
  }

  put<T>(
    path: string,
    body?: unknown,
    opts: Omit<RequestOptions, "body"> = {},
  ): Promise<T> {
    return this.request<T>("PUT", path, { ...opts, body });
  }

  delete<T>(path: string, opts: Omit<RequestOptions, "body"> = {}): Promise<T> {
    return this.request<T>("DELETE", path, opts);
  }
}
