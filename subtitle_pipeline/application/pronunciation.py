"""Quy tắc phát âm tùy chỉnh cho giọng đọc lồng tiếng (TTS) - CHỈ ảnh hưởng
audio, KHÔNG đổi chữ hiển thị trên phụ đề xuất ra.

Hỗ trợ nạp theo LĨNH VỰC / CHUYÊN NGÀNH (IT, Medical, Finance, Gaming, Marketing, Hardware)
từ các file JSON riêng biệt trong `subtitle_pipeline/infrastructure/pronunciation_domains/`.
"""

import json
import re
from pathlib import Path

_INFRA_DIR = Path(__file__).resolve().parent.parent / "infrastructure"
_DEFAULT_GLOSSARY_PATH = _INFRA_DIR / "pronunciation_glossary.json"
_DOMAINS_DIR = _INFRA_DIR / "pronunciation_domains"

DOMAIN_METADATA = [
    {"id": "it", "label": "CNTT / Lập trình / AI", "icon": "💻", "category": "Công nghệ & Khoa học"},
    {"id": "hardware", "label": "Công nghệ / Phần cứng / Ô tô", "icon": "🚗", "category": "Công nghệ & Khoa học"},
    {"id": "medical", "label": "Y tế / Dược / Sức khỏe", "icon": "🩺", "category": "Công nghệ & Khoa học"},
    {"id": "finance", "label": "Tài chính / Ngân hàng / Crypto", "icon": "📈", "category": "Kinh doanh & Đời sống"},
    {"id": "marketing", "label": "Marketing / E-Commerce", "icon": "🛍️", "category": "Kinh doanh & Đời sống"},
    {"id": "realestate", "label": "Bất động sản / Kiến trúc", "icon": "🏢", "category": "Kinh doanh & Đời sống"},
    {"id": "education", "label": "Giáo dục / Học thuật / Du học", "icon": "🎓", "category": "Kinh doanh & Đời sống"},
    {"id": "gaming", "label": "Gaming / Esports / Streamer", "icon": "🎮", "category": "Giải trí & Thể thao"},
    {"id": "sports", "label": "Thể thao / Fitness / Gym", "icon": "⚽", "category": "Giải trí & Thể thao"},
    {"id": "cinema", "label": "Điện ảnh / Phim ảnh / Music", "icon": "🎬", "category": "Giải trí & Thể thao"},
    {"id": "fashion", "label": "Thời trang / Làm đẹp / Skincare", "icon": "💄", "category": "Văn hóa & Đời sống"},
    {"id": "culinary", "label": "Ẩm thực / Nấu ăn / Nhà hàng", "icon": "☕", "category": "Văn hóa & Đời sống"},
]


def list_available_domains() -> list[dict[str, str]]:
  """Trả về danh sách tất cả các chuyên ngành có sẵn từ điển."""
  return DOMAIN_METADATA


def load_default_pronunciation(language: str) -> dict[str, str]:
  if not _DEFAULT_GLOSSARY_PATH.exists():
    return {}
  data = json.loads(_DEFAULT_GLOSSARY_PATH.read_text(encoding="utf-8"))
  return dict(data.get(language, {}))


def load_domain_pronunciation(domain_id: str) -> dict[str, str]:
  domain_file = _DOMAINS_DIR / f"{domain_id}.json"
  if not domain_file.exists():
    return {}
  return json.loads(domain_file.read_text(encoding="utf-8"))


def parse_pronunciation_overrides(text: str) -> dict[str, str]:
  overrides: dict[str, str] = {}
  for line in text.splitlines():
    if "=" not in line:
      continue
    term, _, pronunciation = line.partition("=")
    term, pronunciation = term.strip(), pronunciation.strip()
    if term and pronunciation:
      overrides[term] = pronunciation
  return overrides


def resolve_pronunciation_glossary(
    language: str,
    overrides_text: str = "",
    selected_domains: list[str] | None = None,
) -> dict[str, str]:
  merged: dict[str, str] = {}

  # 1. Nạp từ điển chung
  for k, v in load_default_pronunciation(language).items():
    merged[k.lower()] = v

  # 2. Nạp từ điển các chuyên ngành được chọn (ít nhất nạp 'it' làm mặc định nếu không chọn)
  domains = selected_domains or ["it"]
  for dom in domains:
    for k, v in load_domain_pronunciation(dom).items():
      merged[k.lower()] = v

  # 3. Nạp override thủ công từ textarea (ghi đè cao nhất)
  for k, v in parse_pronunciation_overrides(overrides_text).items():
    merged[k.lower()] = v

  return merged


def apply_pronunciation(text: str, glossary: dict[str, str]) -> str:
  for term, pronunciation in sorted(
      glossary.items(), key=lambda kv: len(kv[0]), reverse=True
  ):
    pattern = r"\b" + re.escape(term) + r"\b"
    text = re.sub(pattern, pronunciation, text, flags=re.IGNORECASE)
  return text
