from fastapi import APIRouter, Depends, HTTPException
from database import db_cursor
from models import CategoryCreate, CategoryUpdate, CategoryResponse
from auth import get_current_user

router = APIRouter(prefix="/api/categories", tags=["categories"])


@router.get("", response_model=list[CategoryResponse])
def list_categories(user_id: int = Depends(get_current_user)):
    with db_cursor(commit=False) as conn:
        rows = conn.execute(
            "SELECT id, name, color, sort_order, user_id FROM categories WHERE user_id = ? ORDER BY sort_order",
            (user_id,),
        ).fetchall()
    return [dict(r) for r in rows]


@router.post("", response_model=CategoryResponse, status_code=201)
def create_category(body: CategoryCreate, user_id: int = Depends(get_current_user)):
    with db_cursor() as conn:
        existing = conn.execute(
            "SELECT id FROM categories WHERE name = ? AND user_id = ?",
            (body.name, user_id),
        ).fetchone()
        if existing:
            raise HTTPException(status_code=400, detail="Category name already exists")
        cursor = conn.execute(
            "INSERT INTO categories (name, color, sort_order, user_id) VALUES (?, ?, ?, ?)",
            (body.name, body.color, body.sort_order, user_id),
        )
        row = conn.execute(
            "SELECT id, name, color, sort_order, user_id FROM categories WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()
    return dict(row)


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    body: CategoryUpdate,
    user_id: int = Depends(get_current_user),
):
    with db_cursor() as conn:
        row = conn.execute(
            "SELECT id FROM categories WHERE id = ? AND user_id = ?",
            (category_id, user_id),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Category not found")
        updates = {}
        if body.name is not None:
            updates["name"] = body.name
        if body.color is not None:
            updates["color"] = body.color
        if body.sort_order is not None:
            updates["sort_order"] = body.sort_order
        if updates:
            set_clause = ", ".join(f"{k} = ?" for k in updates)
            conn.execute(
                f"UPDATE categories SET {set_clause} WHERE id = ?",
                (*updates.values(), category_id),
            )
        row = conn.execute(
            "SELECT id, name, color, sort_order, user_id FROM categories WHERE id = ?",
            (category_id,),
        ).fetchone()
    return dict(row)


@router.delete("/{category_id}", status_code=204)
def delete_category(
    category_id: int, user_id: int = Depends(get_current_user)
):
    with db_cursor() as conn:
        row = conn.execute(
            "SELECT id FROM categories WHERE id = ? AND user_id = ?",
            (category_id, user_id),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Category not found")
        ref = conn.execute(
            "SELECT COUNT(*) as cnt FROM work_entries WHERE category_id = ?",
            (category_id,),
        ).fetchone()
        if ref["cnt"] > 0:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete category with existing work entries",
            )
        conn.execute("DELETE FROM categories WHERE id = ?", (category_id,))
