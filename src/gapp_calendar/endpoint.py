import uuid
from datetime import date

from fastapi import APIRouter, FastAPI

from .calendar import DateSchemaFactory
from .models import Calendar, Event

router = APIRouter()


@router.get("/calenders", summary="List all calenders.")
async def calenders():
    """
    List all active calenders.
    """
    return [c.to_dict() for c in await Calendar.query.gino.all()]


@router.get("/calenders/{calendar_id}", summary="List all events in a given calendar.")
async def calender_events(
    calendar_id: uuid.UUID, date_start: date = None, date_end: date = None
):
    """
    List all events in a given calendar.
    """
    date_start = date_start or date(1900, 1, 1)
    date_end = date_end or date(2100, 12, 31)
    year_start = date_start.year
    year_end = date_end.year
    calendar = await Calendar.get_or_404(calendar_id)
    events = []
    for event in await Event.query.where(Event.calendar_id == calendar_id).gino.all():
        event_schema = DateSchemaFactory.from_string(
            event.date_code, name=event.summary
        )
        if event_schema.year == 0:
            for year_delta in range(year_end - year_start + 1):
                year = year_delta + year_start
                date_ = event_schema.resolve_solar(year)
                if date_ < date_start or date_ > date_end:
                    continue
                events.append(
                    dict(
                        date=date_,
                        summary=event.summary,
                        description=event.description,
                    )
                )
        else:
            events.append(
                dict(
                    date=event_schema.resolve_solar(event_schema.year),
                    summary=event.summary,
                    description=event.description,
                )
            )
    return dict(calendar=calendar.to_dict(), events=events,)


def init_app(app: FastAPI):
    app.include_router(router, tags=["Calendar App"])
