export type ExecutionMode = "CLOUD_FREE_API" | "GPU_LOCAL";

interface ExecutionEngineToggleProps {
  mode: ExecutionMode;
  onChange: (mode: ExecutionMode) => void;
  compact?: boolean;
}

export default function ExecutionEngineToggle({
  mode,
  onChange,
  compact = false,
}: ExecutionEngineToggleProps) {
  if (compact) {
    return (
      <div className="inline-flex items-center rounded-xl bg-cream-soft p-1 border border-line shadow-xs">
        <button
          type="button"
          onClick={() => onChange("CLOUD_FREE_API")}
          className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg transition-all ${
            mode === "CLOUD_FREE_API"
              ? "bg-primary text-white shadow-sm"
              : "text-ink-soft hover:text-ink hover:bg-cream"
          }`}
          title="Miễn phí 100%, 0% GPU VRAM, Tốc độ cực nhanh qua Groq & Gemini APIs"
        >
          <span>⚡</span> Cloud API Free
        </button>
        <button
          type="button"
          onClick={() => onChange("GPU_LOCAL")}
          className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg transition-all ${
            mode === "GPU_LOCAL"
              ? "bg-primary text-white shadow-sm"
              : "text-ink-soft hover:text-ink hover:bg-cream"
          }`}
          title="Chạy phần cứng GPU local/máy chủ riêng"
        >
          <span>🖥️</span> GPU Máy chủ
        </button>
      </div>
    );
  }

  return (
    <div className="rounded-2xl border border-line bg-white p-5 shadow-xs transition-all hover:shadow-md">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-base font-bold text-ink flex items-center gap-2">
            <span>⚙️</span> Chế độ Vận hành Engine AI
          </h3>
          <p className="text-xs text-ink-soft mt-0.5">
            Lựa chọn hạ tầng xử lý AI cho tiến trình dịch và lồng tiếng của bạn
          </p>
        </div>
        <span
          className={`inline-flex items-center gap-1 px-2.5 py-1 text-xs font-bold rounded-full ${
            mode === "CLOUD_FREE_API"
              ? "bg-emerald-100 text-emerald-800 border border-emerald-300"
              : "bg-indigo-100 text-indigo-800 border border-indigo-300"
          }`}
        >
          {mode === "CLOUD_FREE_API" ? "⚡ Cloud API Free Active" : "🖥️ GPU Local Active"}
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Option 1: Cloud API Free */}
        <div
          onClick={() => onChange("CLOUD_FREE_API")}
          className={`cursor-pointer rounded-xl border-2 p-4 transition-all ${
            mode === "CLOUD_FREE_API"
              ? "border-primary bg-primary/5 shadow-sm"
              : "border-line bg-cream/30 hover:border-primary/50 hover:bg-cream/60"
          }`}
        >
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-2">
              <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-emerald-500 text-white text-lg shadow-xs">
                ⚡
              </span>
              <div>
                <h4 className="font-bold text-sm text-ink">Cloud API Miễn phí</h4>
                <span className="text-[11px] font-semibold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-md">
                  Khuyên dùng cho CPU / VM Free
                </span>
              </div>
            </div>
            <input
              type="radio"
              name="execution_mode"
              checked={mode === "CLOUD_FREE_API"}
              onChange={() => onChange("CLOUD_FREE_API")}
              className="mt-1 h-4 w-4 text-primary focus:ring-primary"
            />
          </div>
          <ul className="mt-3 text-xs text-ink-soft space-y-1.5">
            <li className="flex items-center gap-1.5">
              <span className="text-emerald-500 font-bold">✓</span> Miễn phí 100%, 0% GPU VRAM tiêu tốn
            </li>
            <li className="flex items-center gap-1.5">
              <span className="text-emerald-500 font-bold">✓</span> Groq API (Whisper v3 siêu tốc 200 từ/s)
            </li>
            <li className="flex items-center gap-1.5">
              <span className="text-emerald-500 font-bold">✓</span> Gemini LLM (Dịch ngữ cảnh chuẩn xác)
            </li>
            <li className="flex items-center gap-1.5">
              <span className="text-emerald-500 font-bold">✓</span> Edge-TTS (Giọng đọc Neural tự nhiên)
            </li>
          </ul>
        </div>

        {/* Option 2: GPU Local */}
        <div
          onClick={() => onChange("GPU_LOCAL")}
          className={`cursor-pointer rounded-xl border-2 p-4 transition-all ${
            mode === "GPU_LOCAL"
              ? "border-primary bg-primary/5 shadow-sm"
              : "border-line bg-cream/30 hover:border-primary/50 hover:bg-cream/60"
          }`}
        >
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-2">
              <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-600 text-white text-lg shadow-xs">
                🖥️
              </span>
              <div>
                <h4 className="font-bold text-sm text-ink">GPU Máy chủ Local</h4>
                <span className="text-[11px] font-semibold text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded-md">
                  Cần GPU NVIDIA (6GB+ VRAM)
                </span>
              </div>
            </div>
            <input
              type="radio"
              name="execution_mode"
              checked={mode === "GPU_LOCAL"}
              onChange={() => onChange("GPU_LOCAL")}
              className="mt-1 h-4 w-4 text-primary focus:ring-primary"
            />
          </div>
          <ul className="mt-3 text-xs text-ink-soft space-y-1.5">
            <li className="flex items-center gap-1.5">
              <span className="text-indigo-500 font-bold">✓</span> Bảo mật 100% nội bộ không qua API ngoài
            </li>
            <li className="flex items-center gap-1.5">
              <span className="text-indigo-500 font-bold">✓</span> Faster-Whisper + Pyannote Diarization
            </li>
            <li className="flex items-center gap-1.5">
              <span className="text-indigo-500 font-bold">✓</span> DeepFilterNet khử ồn nhiễu âm thanh
            </li>
            <li className="flex items-center gap-1.5">
              <span className="text-indigo-500 font-bold">✓</span> VieNeu-TTS Voice Cloning cá nhân
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
