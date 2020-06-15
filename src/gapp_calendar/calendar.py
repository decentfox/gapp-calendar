from datetime import date

from borax.calendars.festivals import (
    YEAR_ANY,
    DateSchema,
    DayLunarSchema,
    LunarSchema,
    SolarSchema,
    TermSchema,
    WeekSchema,
)
from borax.calendars.store import Field, f_year, f_month, f_day, f_schema


class HolidaySchema(DateSchema):
    date_class = date
    schema = 5
    fields = [f_schema, f_year, f_month, f_day, Field(name="holiday", length=1)]

    def __init__(self, month, day, year=YEAR_ANY, holiday=1, **kwargs):
        self.year = year
        self.month = month
        self.day = day
        self.holiday = holiday
        super().__init__(**kwargs)

    def _resolve(self, year):
        return date(year, self.month, self.day)


class DateSchemaFactory:
    schema_dict = {
        0: SolarSchema,
        1: LunarSchema,
        2: WeekSchema,
        3: DayLunarSchema,
        4: TermSchema,
        5: HolidaySchema,
    }

    @classmethod
    def from_string(cls, raw, **kwargs):
        lg = len(raw)
        if lg == 10:
            short = False
        elif lg == 6:
            short = True
        else:
            raise ValueError("Length expects 6 or 10, but {} got".format(lg))
        schema_code = int(raw[0])
        schema_class = cls.schema_dict.get(schema_code)
        schema = schema_class.decode(raw, short)
        for k, v in kwargs.items():
            setattr(schema, k, v)
        return schema

    @classmethod
    def decode(cls, raw):
        return cls.from_string(raw)
