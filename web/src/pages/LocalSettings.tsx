import { useMutation, useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router-dom";

import NavBar from "../components/AppNavigation";
import Spinner from "../components/Spinner";
import { api, ApiError } from "../lib/api_client";
import { STATUS_LABELS } from "../lib/job_options";
import type { JobOut } from "../lib/api_models";

export default function Admin() {
  const [refreshMessage, setRefreshMessage] = useState<string | null>(null);

  const refreshCookies = useMutation({
    mutationFn: () =>
      api.post<{ cookie_count: number; path: string }>("/api/admin/refresh-cookies", {}),
    onSuccess: (result) =>
      setRefreshMessage(`Đã lấy ${result.cookie_count} cookie, lưu vào ${result.path}.`),
    onError: (err) =>
      setRefreshMessage(err instanceof ApiError ? err.message : "Làm mới cookie thất bại."),
  });

  const { data: jobs = [], isLoading: jobsLoading } = useQuery({
    queryKey: ["admin-jobs"],
    queryFn: () => api.get<JobOut[]>("/api/admin/jobs"),
    refetchInterval: 5000,
  });


  return (
    <div className="min-h-screen">
      <NavBar />
      <main className="mx-auto max-w-6xl px-4 py-8">
        <h1 className="mb-6 text-2xl font-bold">Quản trềEhềEthống</h1>

        <section className="card mb-8">
          <h2 className="mb-2 text-lg font-semibold">Cookie tải video (YouTube)</h2>
          <p className="mb-3 text-sm text-ink-soft">
            Lấy lại cookie mới từ trình duyệt đã đăng nhập sẵn (cần chạy{" "}
            <code className="rounded bg-cream px-1">
              python -m pipeline.infrastructure.cookie_refresh --setup
            </code>{" "}
            một lần trên máy chủ trước). Dùng khi tải video báo lỗi "YouTube yêu cầu xác thực".
          </p>
          <button
            className="btn-primary"
            disabled={refreshCookies.isPending}
            onClick={() => refreshCookies.mutate()}
          >
            {refreshCookies.isPending && <Spinner />}
            {refreshCookies.isPending ? "Đang lấy cookie..." : "Làm mới cookie"}
          </button>
          {refreshMessage && <p className="mt-3 text-sm">{refreshMessage}</p>}
        </section>

        <section className="card">
          <h2 className="mb-4 text-lg font-semibold">Toàn bộ job ({jobs.length})</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-line text-ink-soft">
                  <th className="py-2 pr-4">File</th>
                  <th className="py-2 pr-4">Trạng thái</th>
                  <th className="py-2 pr-4">Bước</th>
                  <th className="py-2">Tạo lúc</th>
                </tr>
              </thead>
              <tbody>
                {jobs.map((j) => (
                  <tr key={j.id} className="border-b border-line/60">
                    <td className="max-w-xs truncate py-2 pr-4 font-medium" title={j.filename}>
                      <Link to={`/studio/jobs/${j.id}`} className="hover:text-primary">
                        {j.filename}
                      </Link>
                    </td>
                    <td className="py-2 pr-4">{STATUS_LABELS[j.status] ?? j.status}</td>
                    <td className="py-2 pr-4 text-ink-soft">{j.stage_label}</td>
                    <td className="py-2 text-ink-soft">
                      {new Date(j.created_at).toLocaleString("vi-VN")}
                    </td>
                  </tr>
                ))}
                {jobsLoading && (
                  <tr>
                    <td colSpan={4} className="py-4 text-center text-ink-soft">
                      <span className="inline-flex items-center gap-2">
                        <Spinner /> Đang tải...
                      </span>
                    </td>
                  </tr>
                )}
                {!jobsLoading && jobs.length === 0 && (
                  <tr>
                    <td colSpan={4} className="py-4 text-center text-ink-soft">
                      Chưa có job nào.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </section>
      </main>
    </div>
  );
}
