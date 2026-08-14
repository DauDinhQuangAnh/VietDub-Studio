import { useState } from "react";
import NavBar from "../components/NavBar";
import Spinner from "../components/Spinner";
import { api } from "../lib/api";

interface VideoQuality {
  id: string;
  label: string;
  format: string;
}

interface VideoInfo {
  url: string;
  title: string;
  thumbnail?: string;
  duration?: number;
  uploader?: string;
  source?: string;
  qualities: VideoQuality[];
}

export default function Downloader() {
  const [url, setUrl] = useState("");
  const [loadingInfo, setLoadingInfo] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [videoInfo, setVideoInfo] = useState<VideoInfo | null>(null);
  const [selectedQuality, setSelectedQuality] = useState("best");
  const [audioOnly, setAudioOnly] = useState(false);

  const formatDuration = (seconds?: number) => {
    if (!seconds) return "N/A";
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return `${m}:${s < 10 ? "0" : ""}${s}`;
  };

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;
    setLoadingInfo(true);
    setError(null);
    setVideoInfo(null);

    try {
      const res = await api.post<VideoInfo>("/downloader/info", { url: url.trim() });
      setVideoInfo(res.data);
      if (res.data.qualities && res.data.qualities.length > 0) {
        setSelectedQuality(res.data.qualities[0].id);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || "Không đọc được video từ liên kết này.");
    } finally {
      setLoadingInfo(false);
    }
  };

  const handleDownload = async () => {
    if (!url.trim()) return;
    setDownloading(true);
    setError(null);

    try {
      const response = await api.post(
        "/downloader/download",
        {
          url: url.trim(),
          quality: selectedQuality,
          extract_audio_only: audioOnly,
        },
        { responseType: "blob" }
      );

      // Create browser download link
      const blob = new Blob([response.data]);
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = downloadUrl;
      const fileExt = audioOnly ? "mp3" : "mp4";
      const cleanTitle = (videoInfo?.title || "video").replace(/[^a-zA-Z0-9_-]/g, "_");
      link.setAttribute("download", `${cleanTitle}.${fileExt}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err: any) {
      setError("Có lỗi xảy ra khi tải video. Vui lòng thử lại.");
    } finally {
      setDownloading(false);
    }
  };

  return (
    <div className="min-h-screen bg-cream/50 text-ink">
      <NavBar />
      <main className="mx-auto max-w-4xl px-4 py-8">
        <div className="rounded-2xl border border-line bg-white p-6 shadow-sm sm:p-8">
          <div className="mb-6 flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-ink">📥 Tải Video & Audio Trực Tiếp</h1>
              <p className="mt-1 text-sm text-ink-soft">
                Tải video gốc hoặc tách nhạc mp3 từ YouTube, TikTok (không logo), Bilibili, Douyin...
              </p>
            </div>
            <span className="rounded-full bg-primary/10 px-3 py-1 text-xs font-semibold text-primary">
              Tải Nhanh Direct
            </span>
          </div>

          <form onSubmit={handleAnalyze} className="mb-6 space-y-4">
            <div>
              <label className="label">Dán đường dẫn Video</label>
              <div className="flex gap-2">
                <input
                  type="url"
                  className="input flex-1"
                  placeholder="https://www.youtube.com/watch?v=... hoặc link TikTok/Bilibili"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  required
                />
                <button
                  type="submit"
                  disabled={loadingInfo || !url.trim()}
                  className="btn-primary flex items-center gap-2"
                >
                  {loadingInfo && <Spinner />}
                  {loadingInfo ? "Đang đọc..." : "🔍 Kiểm tra Video"}
                </button>
              </div>
            </div>
          </form>

          {error && (
            <div className="mb-6 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
              ⚠️ {error}
            </div>
          )}

          {videoInfo && (
            <div className="space-y-6 rounded-xl border border-line/80 bg-cream/20 p-5">
              <div className="flex flex-col gap-4 sm:flex-row">
                {videoInfo.thumbnail && (
                  <img
                    src={videoInfo.thumbnail}
                    alt={videoInfo.title}
                    className="h-36 w-60 rounded-lg object-cover shadow-sm"
                  />
                )}
                <div className="flex-1 space-y-2">
                  <h3 className="text-lg font-bold line-clamp-2">{videoInfo.title}</h3>
                  <div className="flex flex-wrap gap-4 text-xs text-ink-soft">
                    {videoInfo.uploader && (
                      <span>
                        👤 Kênh: <strong>{videoInfo.uploader}</strong>
                      </span>
                    )}
                    {videoInfo.duration && (
                      <span>
                        ⏱️ Thời lượng: <strong>{formatDuration(videoInfo.duration)}</strong>
                      </span>
                    )}
                    {videoInfo.source && (
                      <span>
                        🌐 Nguồn: <strong>{videoInfo.source}</strong>
                      </span>
                    )}
                  </div>
                </div>
              </div>

              <hr className="border-line/60" />

              <div className="grid gap-6 sm:grid-cols-2">
                <div>
                  <label className="label">Định dạng muốn lấy</label>
                  <div className="flex gap-3">
                    <button
                      type="button"
                      onClick={() => setAudioOnly(false)}
                      className={
                        "flex-1 rounded-xl border p-3 text-center transition " +
                        (!audioOnly
                          ? "border-primary bg-primary-soft font-semibold text-primary"
                          : "border-line bg-white hover:border-primary/40")
                      }
                    >
                      🎬 Video MP4
                    </button>
                    <button
                      type="button"
                      onClick={() => setAudioOnly(true)}
                      className={
                        "flex-1 rounded-xl border p-3 text-center transition " +
                        (audioOnly
                          ? "border-primary bg-primary-soft font-semibold text-primary"
                          : "border-line bg-white hover:border-primary/40")
                      }
                    >
                      🎵 Tách nhạc MP3
                    </button>
                  </div>
                </div>

                {!audioOnly && (
                  <div>
                    <label className="label">Chất lượng Video</label>
                    <select
                      className="input"
                      value={selectedQuality}
                      onChange={(e) => setSelectedQuality(e.target.value)}
                    >
                      {videoInfo.qualities.map((q) => (
                        <option key={q.id} value={q.id}>
                          {q.label} ({q.id})
                        </option>
                      ))}
                    </select>
                  </div>
                )}
              </div>

              <div className="pt-2">
                <button
                  type="button"
                  onClick={handleDownload}
                  disabled={downloading}
                  className="w-full btn-primary flex items-center justify-center gap-2 py-3 text-base"
                >
                  {downloading && <Spinner />}
                  {downloading
                    ? "Đang tải video về máy..."
                    : audioOnly
                    ? "⬇️ Tải file MP3 về máy"
                    : `⬇️ Tải Video MP4 (${selectedQuality}) về máy`}
                </button>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
