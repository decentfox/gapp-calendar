"""initial

Revision ID: dd764b86683e
Revises:
Create Date: 2020-06-15 17:20:39.914874

"""
import uuid
from datetime import datetime

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "dd764b86683e"
down_revision = None
branch_labels = ("calendar",)
depends_on = None

TERMS = [
    "小寒",
    "大寒",
    "立春",
    "雨水",
    "惊蛰",
    "春分",
    "清明",
    "谷雨",
    "立夏",
    "小满",
    "芒种",
    "夏至",
    "小暑",
    "大暑",
    "立秋",
    "处暑",
    "白露",
    "秋分",
    "寒露",
    "霜降",
    "立冬",
    "小雪",
    "大雪",
    "冬至",
]

FESTIVALS = """
001010,元旦
002140,情人节
003080,妇女节
003120,植树节
004010,愚人节
005010,劳动节
005040,青年节
005120,护士节
006010,儿童节
008010,建军节
009100,教师节
010010,国庆节
010310,万圣夜
011010,万圣节
012240,平安夜
012250,圣诞节

101010,春节
101150,元宵节
105050,端午节
107070,七夕
107150,中元节
108150,中秋节
109090,重阳节
112080,腊八节
112240,小年

205026,母亲节
206036,父亲节
211043,感恩节

312011,除夕
"""

# 一、元旦：2020年1月1日放假，共1天。
# 二、春节：1月24日至2月2日放假调休，共10天。
# 三、清明节：4月4日至6日放假调休，共3天。
# 四、劳动节：5月1日至5日放假调休，共5天。4月26日（星期日）、5月9日（星期六）上班。
# 五、端午节：6月25日至27日放假调休，共3天。6月28日（星期日）上班。
# 六、国庆节、中秋节：10月1日至8日放假调休，共8天。9月27日（星期日）、10月10日（星期六）上班。
HOLIDAYS_2020 = """
5202001011,休

5202001241,休
5202001251,休
5202001261,休
5202001271,休
5202001281,休
5202001291,休
5202001301,休
5202001311,休
5202002011,休
5202002021,休

5202004041,休
5202004051,休
5202004061,休

5202004260,班
5202005011,休
5202005021,休
5202005031,休
5202005041,休
5202005051,休
5202005090,班

5202006251,休
5202006261,休
5202006271,休
5202006280,班

5202009270,班
5202010011,休
5202010021,休
5202010031,休
5202010041,休
5202010051,休
5202010061,休
5202010071,休
5202010081,休
5202010100,班
"""


def upgrade():
    calendars = op.create_table(
        "calendars",
        sa.Column("id", postgresql.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("profile", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    events = op.create_table(
        "events",
        sa.Column("id", postgresql.UUID(), nullable=False),
        sa.Column("calendar_id", postgresql.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("date_code", sa.String(), nullable=False),
        sa.Column("profile", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.ForeignKeyConstraint(["calendar_id"], ["calendars.id"],),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_events_date_code"), "events", ["date_code"], unique=False)

    now = datetime.utcnow()

    # 节气
    terms_id = str(uuid.uuid4())
    op.execute(
        calendars.insert()
        .values(
            id=terms_id,
            created_at=now,
            profile=dict(name="二十四节气", version=str(uuid.uuid4().hex[-10:])),
        )
        .returning(calendars.c.id)
    )
    for idx, term_name in enumerate(TERMS):
        op.execute(
            events.insert().values(
                id=str(uuid.uuid4()),
                calendar_id=terms_id,
                created_at=now,
                date_code="4000000{:02d}0".format(idx),
                profile=dict(summary=term_name,),
            )
        )

    # 节日
    festival_id = str(uuid.uuid4())
    op.execute(
        calendars.insert()
        .values(
            id=festival_id,
            created_at=now,
            profile=dict(name="节日", version=str(uuid.uuid4().hex[-10:])),
        )
        .returning(calendars.c.id)
    )
    for festival in FESTIVALS.split("\n"):
        if not festival:
            continue
        date_code, summary = festival.split(",")
        op.execute(
            events.insert().values(
                id=str(uuid.uuid4()),
                calendar_id=festival_id,
                created_at=now,
                date_code=date_code,
                profile=dict(summary=summary,),
            )
        )

    # 2020 法定节假日
    holiday_id = str(uuid.uuid4())
    op.execute(
        calendars.insert()
        .values(
            id=holiday_id,
            created_at=now,
            profile=dict(name="法定节假日", version=str(uuid.uuid4().hex[-10:])),
        )
        .returning(calendars.c.id)
    )
    for holiday in HOLIDAYS_2020.split("\n"):
        if not holiday:
            continue
        date_code, summary = holiday.split(",")
        op.execute(
            events.insert().values(
                id=str(uuid.uuid4()),
                calendar_id=holiday_id,
                created_at=now,
                date_code=date_code,
                profile=dict(summary=summary,),
            )
        )


def downgrade():
    op.drop_index(op.f("ix_events_date_code"), table_name="events")
    op.drop_table("events")
    op.drop_table("calendars")
