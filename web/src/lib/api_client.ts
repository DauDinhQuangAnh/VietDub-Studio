export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  const res = await fetch(path, { ...init, headers });
  if (!res.ok) {
    let detail = `Yêu cầu không thành công (${res.status}).`;
    try {
      const body: unknown = await res.json();
      if (
        typeof body === "object" &&
        body !== null &&
        "detail" in body &&
        typeof body.detail === "string"
      ) {
        detail = body.detail;
      }
    } catch {
      /* Phản hồi không phải JSON. */
    }
    throw new ApiError(res.status, detail);
  }
  const contentType = res.headers.get("content-type") ?? "";
  if (contentType.includes("application/json")) return (await res.json()) as T;
  return (await res.blob()) as unknown as T;
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body: unknown) =>
    request<T>(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }),
  put: <T>(path: string, body: unknown) =>
    request<T>(path, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }),
  postForm: <T>(path: string, form: FormData) =>
    request<T>(path, { method: "POST", body: form }),
  del: <T>(path: string) => request<T>(path, { method: "DELETE" }),
};

/** URL file ket qua local. */
export function fileUrl(jobId: string, name: string): string {
  return `/api/jobs/${jobId}/files/${encodeURIComponent(name)}`;
}

/** URL video/audio GOC (chua qua dich/long tieng) - dung o trang Editor de
 *  xem lai khi sua phu de. */
export function originalUrl(jobId: string): string {
  return `/api/jobs/${jobId}/original`;
}
