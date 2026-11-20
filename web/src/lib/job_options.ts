// Cac lua chon co dinh cua wizard - khop worker/pages/1_Upload.py (legacy) va
// api options schema.

export const TRIM_CHOICES: { label: string; value: number | null }[] = [
  { label: "Toàn bộ video", value: null },
  { label: "Chạy thử 60 giây đầu", value: 60 },
  { label: "Chạy thử 120 giây đầu", value: 120 },
];

export const TRANSLATE_PRESETS: {
  label: string;
  maxChars: number;
  maxLines: number;
}[] = [
  { label: "Cân bằng (mặc định)", maxChars: 42, maxLines: 2 },
  { label: "Súc tích (dòng ngắn, dễ đọc nhanh)", maxChars: 32, maxLines: 1 },
  { label: "Thoải mái (dòng dài, ít ngắt)", maxChars: 50, maxLines: 2 },
];

export const RENDER_QUALITY_CHOICES: {
  label: string;
  value: "fast" | "balanced" | "high";
}[] = [
  { label: "Cân bằng", value: "balanced" },
  { label: "Nhanh", value: "fast" },
  { label: "Cao", value: "high" },
];

export const FONT_CHOICES = [
  "Arial",
  "Segoe UI",
  "Tahoma",
  "Verdana",
  "Roboto",
  "Times New Roman",
];

// Ten hien thi tieng Viet cho ma ngon ngu ISO 639-1 - khop
// NLLB_LANGUAGE_CODES (pipeline/infrastructure/translator_nllb.py,
// danh sach ngon ngu NGUON) + SUPPORTED_LANGUAGES (danh sach ngon ngu DICH).
export const LANGUAGE_NAMES: Record<string, string> = {
  vi: "Tiếng Việt",
  en: "Tiếng Anh",
  zh: "Tiếng Trung",
  ja: "Tiếng Nhật",
  ko: "Tiếng Hàn",
  fr: "Tiếng Pháp",
  es: "Tiếng Tây Ban Nha",
  de: "Tiếng Đức",
  ru: "Tiếng Nga",
  it: "Tiếng Ý",
  pt: "Tiếng Bồ Đào Nha",
  th: "Tiếng Thái",
  hi: "Tiếng Hindi",
  id: "Tiếng Indonesia",
  nl: "Tiếng Hà Lan",
  tr: "Tiếng Thổ Nhĩ Kỳ",
  pl: "Tiếng Ba Lan",
  ar: "Tiếng Ả Rập",
  uk: "Tiếng Ukraina",
};

export function languageName(code: string): string {
  return LANGUAGE_NAMES[code] ?? code;
}

export const STATUS_LABELS: Record<string, string> = {
  queued: "Đang chờ",
  running: "Đang chạy",
  done: "Hoàn thành",
  failed: "Thất bại",
};

// Khop worker/jobs/stages.py PIPELINE_STAGES (11 buoc) - dung cho progress bar
// nhieu doan.
export const PIPELINE_STEPS = [
  { key: "starting", label: "Khởi động" },
  { key: "download", label: "Tải video" },
  { key: "extract_audio", label: "Tách âm thanh" },
  { key: "denoise", label: "Khử ồn" },
  { key: "transcribe", label: "Nhận diện lời nói" },
  { key: "align", label: "Căn thời gian" },
  { key: "diarize", label: "Tách người nói" },
  { key: "merge", label: "Ghép kết quả" },
  { key: "translate", label: "Dịch" },
  { key: "dub", label: "Lồng tiếng" },
  { key: "done", label: "Hoàn thành" },
];

export const TOTAL_STAGES = PIPELINE_STEPS.length;

export const STT_MODEL_CHOICES: { label: string; value: string }[] = [
  { label: "Large v3 Turbo (khuyên dùng, nhanh và nhẹ ~3,5 GB bộ nhớ GPU)", value: "large-v3-turbo" },
  { label: "Medium (cân bằng ~1,5 GB bộ nhớ GPU)", value: "medium" },
  { label: "Large v3 (độ chính xác cao nhất ~10 GB bộ nhớ GPU)", value: "large-v3" },
  { label: "Small (nhanh trên máy cấu hình thấp ~1 GB bộ nhớ GPU)", value: "small" },
];

export const PRONUNCIATION_DOMAIN_CHOICES: { id: string; label: string; icon: string; category: string }[] = [
  { id: "it", label: "Công nghệ thông tin / Lập trình / AI", icon: "💻", category: "Công nghệ & Khoa học" },
  { id: "hardware", label: "Công nghệ / Phần cứng / Ô tô", icon: "🚗", category: "Công nghệ & Khoa học" },
  { id: "medical", label: "Y tế / Dược / Sức khỏe", icon: "🩺", category: "Công nghệ & Khoa học" },
  { id: "finance", label: "Tài chính / Ngân hàng / Tiền mã hóa", icon: "📈", category: "Kinh doanh & Đời sống" },
  { id: "marketing", label: "Tiếp thị / Thương mại điện tử", icon: "🛍️", category: "Kinh doanh & Đời sống" },
  { id: "realestate", label: "Bất động sản / Kiến trúc", icon: "🏢", category: "Kinh doanh & Đời sống" },
  { id: "education", label: "Giáo dục / Học thuật / Du học", icon: "🎓", category: "Kinh doanh & Đời sống" },
  { id: "gaming", label: "Trò chơi / Thể thao điện tử / Nhà sáng tạo nội dung", icon: "🎮", category: "Giải trí & Thể thao" },
  { id: "sports", label: "Thể thao / Thể hình", icon: "⚽", category: "Giải trí & Thể thao" },
  { id: "cinema", label: "Điện ảnh / Phim ảnh / Âm nhạc", icon: "🎬", category: "Giải trí & Thể thao" },
  { id: "fashion", label: "Thời trang / Làm đẹp / Chăm sóc da", icon: "💄", category: "Văn hóa & Đời sống" },
  { id: "culinary", label: "Ẩm thực / Nấu ăn / Nhà hàng", icon: "☕", category: "Văn hóa & Đời sống" },
];
