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
          title="Cần Internet; dùng Groq và Gemini, không sử dụng GPU trên máy này"
        >
          <span>⚡</span> Dịch vụ đám mây
        </button>
        <button
          type="button"
          onClick={() => onChange("GPU_LOCAL")}
          className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg transition-all ${
            mode === "GPU_LOCAL"
              ? "bg-primary text-white shadow-sm"
              : "text-ink-soft hover:text-ink hover:bg-cream"
          }`}
          title="Xử lý bằng phần cứng trên máy tính của bạn"
        >
          <span>🖥️</span> GPU trên máy
        </button>
      </div>
    );
  }

  return (
    <div className="rounded-2xl border border-line bg-white p-5 shadow-xs transition-all hover:shadow-md">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-base font-bold text-ink flex items-center gap-2">
            <span>⚙️</span> Chế độ xử lý AI
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
          {mode === "CLOUD_FREE_API" ? "⚡ Đang dùng dịch vụ đám mây" : "🖥️ Đang dùng GPU trên máy"}
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
                <h4 className="font-bold text-sm text-ink">Dịch vụ đám mây</h4>
                <span className="text-[11px] font-semibold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-md">
                  Cần Internet · có hạn mức miễn phí
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
              <span className="text-emerald-500 font-bold">✓</span> Không sử dụng GPU trên máy này
            </li>
            <li className="flex items-center gap-1.5">
              <span className="text-emerald-500 font-bold">✓</span> Groq (nhận dạng lời nói Whisper v3)
            </li>
            <li className="flex items-center gap-1.5">
              <span className="text-emerald-500 font-bold">✓</span> Gemini (dịch theo ngữ cảnh)
            </li>
            <li className="flex items-center gap-1.5">
              <span className="text-emerald-500 font-bold">✓</span> Edge-TTS (giọng đọc AI tự nhiên)
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
                <h4 className="font-bold text-sm text-ink">GPU trên máy tính</h4>
                <span className="text-[11px] font-semibold text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded-md">
                  Cần GPU NVIDIA (từ 6 GB bộ nhớ)
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
              <span className="text-indigo-500 font-bold">✓</span> Xử lý trên máy, không gửi dữ liệu qua dịch vụ ngoài
            </li>
            <li className="flex items-center gap-1.5">
              <span className="text-indigo-500 font-bold">✓</span> Faster-Whisper + Pyannote (nhận diện người nói)
            </li>
            <li className="flex items-center gap-1.5">
              <span className="text-indigo-500 font-bold">✓</span> DeepFilterNet (lọc tạp âm)
            </li>
            <li className="flex items-center gap-1.5">
              <span className="text-indigo-500 font-bold">✓</span> VieNeu-TTS (nhân bản giọng nói)
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
