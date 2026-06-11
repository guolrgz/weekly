from datetime import date as DateType, timedelta
from fastapi import APIRouter, Depends, Query
from database import db_cursor
from models import WeeklyReportResponse
from auth import get_current_user

router = APIRouter(prefix="/api/reports", tags=["reports"])

WEEKDAYS = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


def get_week_range(d: DateType):
    weekday = d.weekday()
    monday = d - timedelta(days=weekday)
    sunday = monday + timedelta(days=6)
    iso = monday.isocalendar()
    week_label = f"第{iso[1]}周"
    return monday, sunday, week_label


def build_report(user_id: int, monday: DateType, sunday: DateType, week_label: str):
    with db_cursor(commit=False) as conn:
        entries = conn.execute(
            "SELECT e.date, c.name as category, c.color, e.content, e.duration_minutes "
            "FROM work_entries e JOIN categories c ON e.category_id = c.id "
            "WHERE e.user_id = ? AND e.date >= ? AND e.date <= ? "
            "ORDER BY e.date, e.created_at",
            (user_id, monday.isoformat(), sunday.isoformat()),
        ).fetchall()

    if not entries:
        return WeeklyReportResponse(
            week_start=monday,
            week_end=sunday,
            week_label=week_label,
            total_hours=0,
            entry_count=0,
            work_days=0,
            top_category="",
            daily_distribution=[],
            category_breakdown=[],
            entries=[],
        )

    total_minutes = sum(e["duration_minutes"] for e in entries)
    days_set = set()
    cat_hours = {}
    daily_data = {}

    weekly_entries = []

    for e in entries:
        d = e["date"]
        days_set.add(d)
        cat_hours[e["category"]] = cat_hours.get(e["category"], 0) + e["duration_minutes"]
        if d not in daily_data:
            daily_data[d] = {"hours": 0, "count": 0}
        daily_data[d]["hours"] += e["duration_minutes"]
        daily_data[d]["count"] += 1
        weekly_entries.append({
            "date": d,
            "category": e["category"],
            "content": e["content"],
            "hours": round(e["duration_minutes"] / 60, 1),
        })

    category_breakdown = sorted(
        [
            {
                "category": k,
                "color": "",
                "hours": round(v / 60, 1),
                "percentage": round(v / total_minutes * 100),
            }
            for k, v in cat_hours.items()
        ],
        key=lambda x: x["hours"],
        reverse=True,
    )

    top = category_breakdown[0]["category"] if category_breakdown else ""

    daily_distribution = [
        {
            "date": d,
            "weekday": WEEKDAYS[DateType.fromisoformat(d).weekday()],
            "hours": round(v["hours"] / 60, 1),
            "entry_count": v["count"],
        }
        for d, v in sorted(daily_data.items())
    ]

    return WeeklyReportResponse(
        week_start=monday,
        week_end=sunday,
        week_label=week_label,
        total_hours=round(total_minutes / 60, 1),
        entry_count=len(entries),
        work_days=len(days_set),
        top_category=top,
        daily_distribution=daily_distribution,
        category_breakdown=category_breakdown,
        entries=weekly_entries,
    )


@router.get("/weekly", response_model=WeeklyReportResponse)
def weekly_report(
    date: DateType = Query(...),
    user_id: int = Depends(get_current_user),
):
    monday, sunday, week_label = get_week_range(date)
    return build_report(user_id, monday, sunday, week_label)


@router.get("/weekly/export")
def weekly_report_export(
    date: DateType = Query(...),
    user_id: int = Depends(get_current_user),
):
    monday, sunday, week_label = get_week_range(date)
    report = build_report(user_id, monday, sunday, week_label)

    lines = [
        f"# 工作周报 ({monday} ~ {sunday})",
        "",
        f"**总工时**：{report.total_hours} 小时 | **记录**：{report.entry_count} 条 | **工作天数**：{report.work_days} 天",
        "",
        "## 分类统计",
        "",
    ]

    for cb in report.category_breakdown:
        lines.append(f"- {cb.category}：{cb.hours}h ({cb.percentage}%)")

    lines.extend(["", "## 每日详情", ""])

    for dd in report.daily_distribution:
        day_entries = [e for e in report.entries if e.date == dd.date]
        items = " · ".join(
            f"{e.category}: {e.content}({e.hours}h)" for e in day_entries
        )
        lines.append(f"**{dd.weekday}**：{items}")

    return {"markdown": "\n".join(lines)}
