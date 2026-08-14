"""Tests for CloudGroqTranscriber and execution mode handling."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from subtitle_pipeline.config import PipelineConfig
from subtitle_pipeline.domain.models import TranscriptSegment
from subtitle_pipeline.infrastructure.transcriber_groq import CloudGroqTranscriber


def test_pipeline_config_execution_mode():
    config = PipelineConfig.from_env()
    assert config.execution_mode in ("CLOUD_FREE_API", "GPU_LOCAL")


@patch("urllib.request.urlopen")
def test_groq_transcriber_success(mock_urlopen, tmp_path: Path):
    audio_file = tmp_path / "test.wav"
    audio_file.write_bytes(b"dummy wav content")

    mock_response = MagicMock()
    mock_response.read.return_value = (
        b'{"language": "vi", "segments": [{"start": 0.0, "end": 2.5, "text": "Xin chào thế giới"}]}'
    )
    mock_response.__enter__.return_value = mock_response
    mock_urlopen.return_value = mock_response

    transcriber = CloudGroqTranscriber(api_key="gsk_fake_key")
    with transcriber as tr:
        segments, lang = tr.transcribe(audio_file)

    assert lang == "vi"
    assert len(segments) == 1
    assert segments[0].text == "Xin chào thế giới"
    assert segments[0].start == 0.0
    assert segments[0].end == 2.5


@patch("subtitle_pipeline.infrastructure.transcriber_faster_whisper.FasterWhisperTranscriber.transcribe")
def test_groq_transcriber_fallback_when_no_key(mock_fallback_transcribe, tmp_path: Path):
    audio_file = tmp_path / "test.wav"
    audio_file.write_bytes(b"dummy wav content")

    mock_fallback_transcribe.return_value = ([TranscriptSegment(start=0.0, end=1.0, text="Fallback text")], "en")

    transcriber = CloudGroqTranscriber(api_key="")
    with transcriber as tr:
        segments, lang = tr.transcribe(audio_file)

    assert lang == "en"
    assert len(segments) == 1
    assert segments[0].text == "Fallback text"
