"""Repository cho CustomVoice (nhan session_factory de test bang SQLite)."""

import uuid
from collections.abc import Callable, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from worker.db.database import make_session_factory
from worker.db.database_models import CustomVoice


class CustomVoiceRepository:
    def __init__(self, session_factory: Callable[[], Session] | None = None):
        self._session_factory = session_factory or make_session_factory()

    def create(self, name: str, ref_audio_path: str) -> CustomVoice:
        with self._session_factory() as session:
            voice = CustomVoice(id=str(uuid.uuid4()), name=name, ref_audio_path=ref_audio_path)
            session.add(voice)
            session.commit()
            session.refresh(voice)
            return voice

    def get(self, voice_id: str) -> CustomVoice | None:
        with self._session_factory() as session:
            return session.get(CustomVoice, voice_id)

    def list_all(self) -> Sequence[CustomVoice]:
        with self._session_factory() as session:
            stmt = select(CustomVoice).order_by(CustomVoice.created_at.desc())
            return session.scalars(stmt).all()

    def delete(self, voice_id: str) -> None:
        with self._session_factory() as session:
            voice = session.get(CustomVoice, voice_id)
            if voice is None:
                return
            session.delete(voice)
            session.commit()
