import sys
from pathlib import Path
from types import SimpleNamespace

from pipeline.pipeline_settings import PipelineConfig
from worker.jobs import celery_app as celery_module


def test_pipeline_config_falls_back_to_cpu_without_cuda(monkeypatch):
    fake_torch = SimpleNamespace(cuda=SimpleNamespace(is_available=lambda: False))
    monkeypatch.setitem(sys.modules, "torch", fake_torch)
    monkeypatch.setenv("PIPELINE_DEVICE", "cuda")
    monkeypatch.setenv("WHISPER_COMPUTE_TYPE", "int8_float16")

    config = PipelineConfig.from_env()

    assert config.device == "cpu"
    assert config.whisper_compute_type == "int8"


def test_celery_uses_sqlite_queue_when_redis_is_not_configured(tmp_path, monkeypatch):
    queue_path = tmp_path / "storage" / "celery.db"
    monkeypatch.setattr(celery_module, "LOCAL_QUEUE_DB_PATH", queue_path)
    monkeypatch.delenv("REDIS_URL", raising=False)

    broker_url, result_backend = celery_module._resolve_broker_url()

    assert broker_url == f"sqla+sqlite:///{queue_path.as_posix()}"
    assert result_backend == f"db+sqlite:///{queue_path.as_posix()}"
    assert queue_path.parent.is_dir()


def test_celery_falls_back_to_sqlite_when_local_redis_is_unavailable(tmp_path, monkeypatch):
    queue_path = tmp_path / "storage" / "celery.db"
    monkeypatch.setattr(celery_module, "LOCAL_QUEUE_DB_PATH", queue_path)
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")

    def fail_connection(*args, **kwargs):
        raise OSError("Redis is unavailable")

    monkeypatch.setattr(celery_module.socket, "create_connection", fail_connection)

    broker_url, result_backend = celery_module._resolve_broker_url()

    assert broker_url == f"sqla+sqlite:///{queue_path.as_posix()}"
    assert result_backend == f"db+sqlite:///{queue_path.as_posix()}"
    assert Path(queue_path).parent.is_dir()
