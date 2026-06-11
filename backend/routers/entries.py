from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import date as DateType
from typing import Optional
from database import db_cursor
from models import EntryCreate, EntryUpdate, EntryResponse
from auth import get_current_user

router = APIRouter(prefix="/api/entries", tags=["entries"])


@router.get("", response_model=list[EntryResponse])
def list_entries(
    start: Optional[DateType] = Query(None),
    end: Optional[DateType] = Query(None),
    user_id: int = Depends(get_current_user),
):
    with db_cursor(commit=False) as conn:
        if start and end:
            rows = conn.execute(
                "SELECT id, user_id, date, category_id, content, duration_minutes, created_at "
                "FROM work_entries WHERE user_id = ? AND date >= ? AND date <= ? ORDER BY date DESC, created_at DESC",
                (user_id, start.isoformat(), end.isoformat()),
            ).fetchall()
        elif start:
            rows = conn.execute(
                "SELECT id, user_id, date, category_id, content, duration_minutes, created_at "
                "FROM work_entries WHERE user_id = ? AND date >= ? ORDER BY date DESC, created_at DESC",
                (user_id, start.isoformat()),
            ).fetchall()
        elif end:
            rows = conn.execute(
                "SELECT id, user_id, date, category_id, content, duration_minutes, created_at "
                "FROM work_entries WHERE user_id = ? AND date <= ? ORDER BY date DESC, created_at DESC",
                (user_id, end.isoformat()),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT id, user_id, date, category_id, content, duration_minutes, created_at "
                "FROM work_entries WHERE user_id = ? ORDER BY date DESC, created_at DESC",
                (user_id,),
            ).fetchall()
    return [dict(r) for r in rows]


@router.post("", response_model=EntryResponse, status_code=201)
def create_entry(body: EntryCreate, user_id: int = Depends(get_current_user)):
    with db_cursor() as conn:
        cat = conn.execute(
            "SELECT id FROM categories WHERE id = ? AND user_id = ?",
            (body.category_id, user_id),
        ).fetchone()
        if not cat:
            raise HTTPException(status_code=400, detail="Category not found")
        cursor = conn.execute(
            "INSERT INTO work_entries (user_id, date, category_id, content, duration_minutes) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                user_id,
                body.date.isoformat(),
                body.category_id,
                body.content,
                body.duration_minutes,
            ),
        )
        row = conn.execute(
            "SELECT id, user_id, date, category_id, content, duration_minutes, created_at "
            "FROM work_entries WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()
    return dict(row)


@router.put("/{entry_id}", response_model=EntryResponse)
def update_entry(
    entry_id: int, body: EntryUpdate, user_id: int = Depends(get_current_user)
):
    with db_cursor() as conn:
        row = conn.execute(
            "SELECT id FROM work_entries WHERE id = ? AND user_id = ?",
            (entry_id, user_id),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Entry not found")
        updates = {}
        if body.date is not None:
            updates["date"] = body.date.isoformat()
        if body.category_id is not None:
            cat = conn.execute(
                "SELECT id FROM categories WHERE id = ? AND user_id = ?",
                (body.category_id, user_id),
            ).fetchone()
            if not cat:
                raise HTTPException(status_code=400, detail="Category not found")
            updates["category_id"] = body.category_id
        if body.content is not None:
            updates["content"] = body.content
        if body.duration_minutes is not None:
            updates["duration_minutes"] = body.duration_minutes
        if updates:
            set_clause = ", ".join(f"{k} = ?" for k in updates)
            conn.execute(
                f"UPDATE work_entries SET {set_clause} WHERE id = ?",
                (*updates.values(), entry_id),
            )
        row = conn.execute(
            "SELECT id, user_id, date, category_id, content, duration_minutes, created_at "
            "FROM work_entries WHERE id = ?",
            (entry_id,),
        ).fetchone()
    return dict(row)


@router.delete("/{entry_id}", status_code=204)
def delete_entry(entry_id: int, user_id: int = Depends(get_current_user)):
    with db_cursor() as conn:
        row = conn.execute(
            "SELECT id FROM work_entries WHERE id = ? AND user_id = ?",
            (entry_id, user_id),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Entry not found")
        conn.execute("DELETE FROM work_entries WHERE id = ?", (entry_id,))
