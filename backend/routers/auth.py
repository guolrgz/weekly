from fastapi import APIRouter, Depends, HTTPException, status
from database import db_cursor
from models import UserRegister, UserLogin, TokenResponse, UserResponse
from auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])

PRESET_CATEGORIES = [
    ("开发", "#1a73e8", 1),
    ("会议", "#16a34a", 2),
    ("文档", "#ea580c", 3),
    ("沟通", "#8b5cf6", 4),
    ("其他", "#6b7280", 5),
]


@router.post("/register", response_model=TokenResponse)
def register(body: UserRegister):
    with db_cursor() as conn:
        existing = conn.execute(
            "SELECT id FROM users WHERE username = ?", (body.username,)
        ).fetchone()
        if existing:
            raise HTTPException(
                status_code=400, detail="Username already exists"
            )
        cursor = conn.execute(
            "INSERT INTO users (username, hashed_password) VALUES (?, ?)",
            (body.username, hash_password(body.password)),
        )
        user_id = cursor.lastrowid
        for name, color, sort_order in PRESET_CATEGORIES:
            conn.execute(
                "INSERT INTO categories (name, color, sort_order, user_id) VALUES (?, ?, ?, ?)",
                (name, color, sort_order, user_id),
            )
        token = create_access_token(user_id)
        user = dict(
            conn.execute(
                "SELECT id, username, created_at FROM users WHERE id = ?", (user_id,)
            ).fetchone()
        )
    return {"access_token": token, "token_type": "bearer", "user": user}


@router.post("/login", response_model=TokenResponse)
def login(body: UserLogin):
    with db_cursor(commit=False) as conn:
        row = conn.execute(
            "SELECT id, username, hashed_password, created_at FROM users WHERE username = ?",
            (body.username,),
        ).fetchone()
        if not row or not verify_password(body.password, row["hashed_password"]):
            raise HTTPException(
                status_code=401, detail="Invalid username or password"
            )
        token = create_access_token(row["id"])
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": row["id"], "username": row["username"], "created_at": row["created_at"]},
    }


@router.get("/me", response_model=UserResponse)
def me(user_id: int = Depends(get_current_user)):
    with db_cursor(commit=False) as conn:
        row = conn.execute(
            "SELECT id, username, created_at FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="User not found")
    return dict(row)
