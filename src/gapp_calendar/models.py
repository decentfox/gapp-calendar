import uuid
from datetime import datetime

from authlib_gino.fastapi_session.gino_app import load_entry_point
from gino import Gino
from sqlalchemy.dialects.postgresql import JSONB, UUID

db = load_entry_point("db", Gino)


class Calendar(db.Model):
    __tablename__ = "calendars"

    id: uuid.UUID = db.Column(UUID(), primary_key=True, default=uuid.uuid4)
    created_at = db.Column(db.DateTime(), nullable=False, default=datetime.utcnow)
    profile = db.Column(JSONB(), nullable=False, default={})
    name = db.StringProperty()
    version = db.StringProperty()


class Event(db.Model):
    __tablename__ = "events"

    id: uuid.UUID = db.Column(UUID(), primary_key=True, default=uuid.uuid4)
    calendar_id = db.Column(db.ForeignKey("calendars.id"), nullable=False)
    created_at = db.Column(db.DateTime(), nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime())
    date_code = db.Column(db.String(), nullable=False, index=True)
    profile = db.Column(JSONB(), nullable=False, default={})
    summary = db.StringProperty()
    description = db.StringProperty()
