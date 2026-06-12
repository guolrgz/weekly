# 工作周报系统 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a personal weekly work report system with manual entry, auto statistics, chart visualization, and Markdown export.

**Architecture:** FastAPI backend serving RESTful APIs with JWT auth against SQLite. Vue 3 SPA frontend with Element Plus UI and ECharts charts, talking to the backend via axios. Single-user personal tool; all data scoped by user_id.

**Tech Stack:** Python 3 / FastAPI / SQLite / python-jose / passlib | Vue 3 / Vite / Element Plus / ECharts / vue-echarts / marked / axios

---

### Task 1: Backend project scaffold

**Files:**

- Create: `backend/requirements.txt`
- Create: `backend/main.py`
- Create: `backend/database.py`

- [ ] **Step 1: Write requirements.txt**

```
fastapi==0.115.0
uvicorn[standard]==0.30.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
pydantic==2.9.2
```

- [ ] **Step 2: Write database.py — SQLite connection + table creation**

```python
import sqlite3
from contextlib import contextmanager

DB_PATH = "weekly_report.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


@contextmanager
def db_cursor(commit=True):
    conn = get_db()
    try:
        yield conn
        if commit:
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            color TEXT NOT NULL DEFAULT '#6b7280',
            sort_order INTEGER DEFAULT 0,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(name, user_id)
        );

        CREATE TABLE IF NOT EXISTS work_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date DATE NOT NULL,
            category_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            duration_minutes INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (category_id) REFERENCES categories(id)
        );

        CREATE INDEX IF NOT EXISTS idx_entries_user_date
            ON work_entries(user_id, date);
    """)
    conn.commit()
    conn.close()
```

- [ ] **Step 3: Write main.py — FastAPI app entry point with CORS**

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="工作周报系统", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}
```

- [ ] **Step 4: Install dependencies and test health endpoint**

```bash
cd backend && pip install -r requirements.txt
```

Run: `uvicorn main:app --reload --port 8000`
Test: `curl http://localhost:8000/api/health`
Expected: `{"status":"ok"}`

- [ ] **Step 5: Commit**

```bash
git add backend/requirements.txt backend/main.py backend/database.py
git commit -m "feat: scaffold FastAPI backend with SQLite init and CORS"
```

---

### Task 2: Auth — Pydantic models + JWT helpers

**Files:**

- Create: `backend/models.py`
- Create: `backend/auth.py`

- [ ] **Step 1: Write models.py**

```python
from pydantic import BaseModel
from typing import Optional
from datetime import date as DateType, datetime


class UserRegister(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class CategoryCreate(BaseModel):
    name: str
    color: str = "#6b7280"
    sort_order: int = 0


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None
    sort_order: Optional[int] = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    color: str
    sort_order: int
    user_id: int


class EntryCreate(BaseModel):
    date: DateType
    category_id: int
    content: str
    duration_minutes: int


class EntryUpdate(BaseModel):
    date: Optional[DateType] = None
    category_id: Optional[int] = None
    content: Optional[str] = None
    duration_minutes: Optional[int] = None


class EntryResponse(BaseModel):
    id: int
    user_id: int
    date: DateType
    category_id: int
    content: str
    duration_minutes: int
    created_at: datetime


class DailyDistribution(BaseModel):
    date: DateType
    weekday: str
    hours: float
    entry_count: int


class CategoryBreakdown(BaseModel):
    category: str
    color: str
    hours: float
    percentage: int


class WeeklyEntry(BaseModel):
    date: DateType
    category: str
    content: str
    hours: float


class WeeklyReportResponse(BaseModel):
    week_start: DateType
    week_end: DateType
    week_label: str
    total_hours: float
    entry_count: int
    work_days: int
    top_category: str
    daily_distribution: list[DailyDistribution]
    category_breakdown: list[CategoryBreakdown]
    entries: list[WeeklyEntry]
```

- [ ] **Step 2: Write auth.py**

```python
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

SECRET_KEY = "weekly-report-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    return jwt.encode(
        {"sub": str(user_id), "exp": expire}, SECRET_KEY, algorithm=ALGORITHM
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> int:
    try:
        payload = jwt.decode(
            credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM]
        )
        user_id = int(payload.get("sub"))
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")
```

- [ ] **Step 3: Commit**

```bash
git add backend/models.py backend/auth.py
git commit -m "feat: add Pydantic models and JWT auth helpers"
```

---

### Task 3: Auth router — register / login / me

**Files:**

- Create: `backend/routers/__init__.py`
- Create: `backend/routers/auth.py`

- [ ] **Step 1: Create routers **init**.py**

```python

```

- [ ] **Step 2: Write routers/auth.py**

```python
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
```

- [ ] **Step 3: Register router in main.py**

Add to `backend/main.py` after the health endpoint:

```python
from routers.auth import router as auth_router

app.include_router(auth_router)
```

- [ ] **Step 4: Test with curl**

```bash
# Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"123456"}'

# Expected: {"access_token":"...","token_type":"bearer","user":{"id":1,...}}

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"123456"}'

# Me (replace TOKEN)
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer TOKEN"
```

- [ ] **Step 5: Commit**

```bash
git add backend/routers/ backend/main.py
git commit -m "feat: add auth endpoints — register, login, me"
```

---

### Task 4: Categories CRUD router

**Files:**

- Create: `backend/routers/categories.py`

- [ ] **Step 1: Write routers/categories.py**

```python
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
```

- [ ] **Step 2: Register router in main.py**

```python
from routers.categories import router as categories_router

app.include_router(categories_router)
```

- [ ] **Step 3: Commit**

```bash
git add backend/routers/categories.py backend/main.py
git commit -m "feat: add categories CRUD endpoints"
```

---

### Task 5: Work entries CRUD router

**Files:**

- Create: `backend/routers/entries.py`

- [ ] **Step 1: Write routers/entries.py**

```python
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
```

- [ ] **Step 2: Register router in main.py**

```python
from routers.entries import router as entries_router

app.include_router(entries_router)
```

- [ ] **Step 3: Commit**

```bash
git add backend/routers/entries.py backend/main.py
git commit -m "feat: add work entries CRUD endpoints"
```

---

### Task 6: Weekly report endpoint

**Files:**

- Create: `backend/routers/reports.py`

- [ ] **Step 1: Write routers/reports.py**

```python
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
        lines.append(f"- {cb['category']}：{cb['hours']}h ({cb['percentage']}%)")

    lines.extend(["", "## 每日详情", ""])

    for dd in report.daily_distribution:
        day_entries = [e for e in report.entries if e["date"] == dd["date"]]
        items = " · ".join(
            f"{e['category']}: {e['content']}({e['hours']}h)" for e in day_entries
        )
        lines.append(f"**{dd['weekday']}**：{items}")

    return {"markdown": "\n".join(lines)}
```

- [ ] **Step 2: Register router in main.py**

```python
from routers.reports import router as reports_router

app.include_router(reports_router)
```

- [ ] **Step 3: Test weekly report**

```bash
# Create some test entries first, then:
curl "http://localhost:8000/api/reports/weekly?date=2026-06-11" \
  -H "Authorization: Bearer TOKEN"
```

- [ ] **Step 4: Commit**

```bash
git add backend/routers/reports.py backend/main.py
git commit -m "feat: add weekly report and Markdown export endpoints"
```

---

### Task 7: Frontend project scaffold

**Files:**

- Create: `frontend/package.json`
- Create: `frontend/vite.config.js`
- Create: `frontend/index.html`
- Create: `frontend/src/main.js`
- Create: `frontend/src/App.vue`
- Create: `frontend/src/router/index.js`
- Create: `frontend/src/api/index.js`

- [ ] **Step 1: Write package.json**

```json
{
  "name": "weekly-report-frontend",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "axios": "^1.7.7",
    "dayjs": "^1.11.13",
    "echarts": "^5.5.1",
    "element-plus": "^2.8.5",
    "marked": "^14.1.3",
    "pinia": "^2.2.4",
    "vue": "^3.5.11",
    "vue-echarts": "^7.0.3",
    "vue-router": "^4.4.5"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.1.4",
    "vite": "^5.4.9"
  }
}
```

- [ ] **Step 2: Write vite.config.js**

```javascript
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      "/api": "http://localhost:8000",
    },
  },
});
```

- [ ] **Step 3: Write index.html**

```html
<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>工作周报</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.js"></script>
  </body>
</html>
```

- [ ] **Step 4: Write src/main.js**

```javascript
import { createApp } from "vue";
import { createPinia } from "pinia";
import ElementPlus from "element-plus";
import "element-plus/dist/index.css";
import App from "./App.vue";
import router from "./router";

const app = createApp(App);
app.use(createPinia());
app.use(ElementPlus);
app.use(router);
app.mount("#app");
```

- [ ] **Step 5: Write src/App.vue**

```vue
<template>
  <router-view />
</template>
```

- [ ] **Step 6: Write src/router/index.js**

```javascript
import { createRouter, createWebHistory } from "vue-router";

const routes = [
  {
    path: "/login",
    name: "Login",
    component: () => import("../views/Login.vue"),
  },
  {
    path: "/register",
    name: "Register",
    component: () => import("../views/Register.vue"),
  },
  {
    path: "/",
    component: () => import("../views/Layout.vue"),
    meta: { requiresAuth: true },
    children: [
      {
        path: "",
        redirect: "/weekly-report",
      },
      {
        path: "weekly-report",
        name: "WeeklyReport",
        component: () => import("../views/WeeklyReport.vue"),
      },
      {
        path: "categories",
        name: "Categories",
        component: () => import("../views/Categories.vue"),
      },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem("token");
  if (to.meta.requiresAuth && !token) {
    next("/login");
  } else if ((to.path === "/login" || to.path === "/register") && token) {
    next("/");
  } else {
    next();
  }
});

export default router;
```

- [ ] **Step 7: Write src/api/index.js**

```javascript
import axios from "axios";
import { ElMessage } from "element-plus";
import router from "../router";

const api = axios.create({ baseURL: "/api" });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      router.push("/login");
    }
    const msg = err.response?.data?.detail || "请求失败";
    ElMessage.error(msg);
    return Promise.reject(err);
  },
);

export default api;
```

- [ ] **Step 8: Install dependencies and test**

```bash
cd frontend && npm install && npm run dev
```

Open http://localhost:5173 — should redirect to /login (blank page).

- [ ] **Step 9: Commit**

```bash
git add frontend/
git commit -m "feat: scaffold Vue 3 frontend with Vite, router, and axios"
```

---

### Task 8: Auth store + Login/Register views

**Files:**

- Create: `frontend/src/stores/auth.js`
- Create: `frontend/src/views/Login.vue`
- Create: `frontend/src/views/Register.vue`

- [ ] **Step 1: Write stores/auth.js**

```javascript
import { defineStore } from "pinia";
import { ref } from "vue";
import api from "../api";

export const useAuthStore = defineStore("auth", () => {
  const user = ref(JSON.parse(localStorage.getItem("user") || "null"));
  const token = ref(localStorage.getItem("token") || "");

  function setAuth(u, t) {
    user.value = u;
    token.value = t;
    localStorage.setItem("user", JSON.stringify(u));
    localStorage.setItem("token", t);
  }

  function logout() {
    user.value = null;
    token.value = "";
    localStorage.removeItem("user");
    localStorage.removeItem("token");
  }

  async function login(username, password) {
    const { data } = await api.post("/auth/login", { username, password });
    setAuth(data.user, data.access_token);
  }

  async function register(username, password) {
    const { data } = await api.post("/auth/register", { username, password });
    setAuth(data.user, data.access_token);
  }

  return { user, token, login, register, logout };
});
```

- [ ] **Step 2: Write views/Login.vue**

```vue
<template>
  <div class="auth-container">
    <el-card class="auth-card">
      <h2>工作周报系统</h2>
      <el-form :model="form" label-position="top">
        <el-form-item label="用户名">
          <el-input v-model="form.username" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input
            v-model="form.password"
            type="password"
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-button
          type="primary"
          :loading="loading"
          @click="handleLogin"
          style="width:100%"
        >
          登录
        </el-button>
      </el-form>
      <p class="auth-link">
        还没有账号？<router-link to="/register">立即注册</router-link>
      </p>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const auth = useAuthStore();
const loading = ref(false);
const form = reactive({ username: "", password: "" });

async function handleLogin() {
  if (!form.username || !form.password) return;
  loading.value = true;
  try {
    await auth.login(form.username, form.password);
    router.push("/");
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f0f2f5;
}
.auth-card {
  width: 400px;
}
.auth-card h2 {
  text-align: center;
  margin-bottom: 24px;
}
.auth-link {
  text-align: center;
  margin-top: 16px;
  font-size: 13px;
  color: #999;
}
</style>
```

- [ ] **Step 3: Write views/Register.vue**

```vue
<template>
  <div class="auth-container">
    <el-card class="auth-card">
      <h2>注册账号</h2>
      <el-form :model="form" label-position="top">
        <el-form-item label="用户名">
          <el-input v-model="form.username" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" />
        </el-form-item>
        <el-button
          type="primary"
          :loading="loading"
          @click="handleRegister"
          style="width:100%"
        >
          注册
        </el-button>
      </el-form>
      <p class="auth-link">
        已有账号？<router-link to="/login">去登录</router-link>
      </p>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const auth = useAuthStore();
const loading = ref(false);
const form = reactive({ username: "", password: "" });

async function handleRegister() {
  if (!form.username || !form.password) return;
  loading.value = true;
  try {
    await auth.register(form.username, form.password);
    router.push("/");
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f0f2f5;
}
.auth-card {
  width: 400px;
}
.auth-card h2 {
  text-align: center;
  margin-bottom: 24px;
}
.auth-link {
  text-align: center;
  margin-top: 16px;
  font-size: 13px;
  color: #999;
}
</style>
```

- [ ] **Step 4: Verify login/register flow works in browser**

Open http://localhost:5173/login — register a new user, should redirect to / and show Layout (404 for now).

- [ ] **Step 5: Commit**

```bash
git add frontend/src/stores/ frontend/src/views/Login.vue frontend/src/views/Register.vue
git commit -m "feat: add auth store, login and register views"
```

---

### Task 9: Layout with sidebar

**Files:**

- Create: `frontend/src/views/Layout.vue`

- [ ] **Step 1: Write views/Layout.vue**

```vue
<template>
  <el-container class="layout">
    <el-aside width="200px">
      <div class="logo">工作周报</div>
      <el-menu
        :default-active="route.path"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <el-menu-item index="/weekly-report">
          <el-icon><Edit /></el-icon>
          <span>工作周报</span>
        </el-menu-item>
        <el-menu-item index="/categories">
          <el-icon><Collection /></el-icon>
          <span>分类管理</span>
        </el-menu-item>
      </el-menu>
      <div class="sidebar-footer">
        <span>{{ auth.user?.username }}</span>
        <el-button text size="small" @click="handleLogout">退出</el-button>
      </div>
    </el-aside>
    <el-main>
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup>
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();

function handleLogout() {
  auth.logout();
  router.push("/login");
}
</script>

<style scoped>
.layout {
  min-height: 100vh;
}
.el-aside {
  background: #304156;
  display: flex;
  flex-direction: column;
}
.logo {
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  text-align: center;
  padding: 20px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}
.sidebar-footer {
  margin-top: auto;
  padding: 12px 16px;
  color: #bfcbd9;
  font-size: 13px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
```

- [ ] **Step 2: Verify layout renders**

Open http://localhost:5173 — should see sidebar with "工作周报" and "分类管理". Clicking navigates between routes (views not yet created, so blank content area).

- [ ] **Step 3: Commit**

```bash
git add frontend/src/views/Layout.vue
git commit -m "feat: add layout with sidebar navigation"
```

---

### Task 10: WeeklyReport page shell with 4 tabs

**Files:**

- Create: `frontend/src/views/WeeklyReport.vue`

- [ ] **Step 1: Write views/WeeklyReport.vue**

```vue
<template>
  <div class="weekly-report">
    <h3 class="page-title">工作周报</h3>
    <el-tabs v-model="activeTab" type="border-card">
      <el-tab-pane label="工作录入" name="entry">
        <WorkEntryForm @saved="handleEntrySaved" />
        <TodayEntries ref="todayRef" />
      </el-tab-pane>
      <el-tab-pane label="统计看板" name="stats">
        <StatsDashboard :report="report" :loading="loading" />
      </el-tab-pane>
      <el-tab-pane label="周报预览" name="preview">
        <WeeklyPreview :report="report" />
      </el-tab-pane>
      <el-tab-pane label="历史记录" name="history">
        <HistoryList @view="handleViewHistory" />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref } from "vue";
import dayjs from "dayjs";
import isoWeek from "dayjs/plugin/isoWeek";
import api from "../api";
import WorkEntryForm from "../components/WorkEntryForm.vue";
import TodayEntries from "../components/TodayEntries.vue";
import StatsDashboard from "../components/StatsDashboard.vue";
import WeeklyPreview from "../components/WeeklyPreview.vue";
import HistoryList from "../components/HistoryList.vue";

dayjs.extend(isoWeek);

const activeTab = ref("entry");
const report = ref(null);
const loading = ref(false);
const todayRef = ref(null);
const currentDate = ref(dayjs().format("YYYY-MM-DD"));

async function fetchReport(date) {
  loading.value = true;
  try {
    const { data } = await api.get("/reports/weekly", { params: { date } });
    report.value = data;
  } finally {
    loading.value = false;
  }
}

function handleEntrySaved() {
  todayRef.value?.refresh();
  fetchReport(currentDate.value);
}

function handleViewHistory(date) {
  currentDate.value = date;
  fetchReport(date);
  activeTab.value = "stats";
}

fetchReport(currentDate.value);
</script>

<style scoped>
.page-title {
  margin: 0 0 16px 0;
  font-size: 20px;
}
</style>
```

- [ ] **Step 2: Create placeholder components**

```bash
mkdir -p frontend/src/components
```

Write minimal placeholder for each component so the page loads without errors:

`frontend/src/components/WorkEntryForm.vue`:

```vue
<template><div>WorkEntryForm</div></template>
<script setup>
defineEmits(["saved"]);
</script>
```

`frontend/src/components/TodayEntries.vue`:

```vue
<template><div>TodayEntries</div></template>
<script setup>
defineExpose({ refresh() {} });
</script>
```

`frontend/src/components/StatsDashboard.vue`:

```vue
<template><div>StatsDashboard</div></template>
<script setup>
defineProps({ report: Object, loading: Boolean });
</script>
```

`frontend/src/components/WeeklyPreview.vue`:

```vue
<template><div>WeeklyPreview</div></template>
<script setup>
defineProps({ report: Object });
</script>
```

`frontend/src/components/HistoryList.vue`:

```vue
<template><div>HistoryList</div></template>
<script setup>
defineEmits(["view"]);
</script>
```

- [ ] **Step 3: Verify page loads with 4 tabs**

Open http://localhost:5173/weekly-report — should see "工作周报" title with 4 tabs. Switching tabs shows placeholder text.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/views/WeeklyReport.vue frontend/src/components/
git commit -m "feat: add WeeklyReport page shell with 4 tab placeholders"
```

---

### Task 11: Work entry form + today's entries

**Files:**

- Modify: `frontend/src/components/WorkEntryForm.vue`
- Modify: `frontend/src/components/TodayEntries.vue`

- [ ] **Step 1: Rewrite WorkEntryForm.vue**

```vue
<template>
  <el-card class="entry-form-card">
    <template #header>新增工作记录</template>
    <el-form :model="form" label-width="80px" @submit.prevent="handleSubmit">
      <el-row :gutter="16">
        <el-col :span="6">
          <el-form-item label="日期">
            <el-date-picker
              v-model="form.date"
              type="date"
              value-format="YYYY-MM-DD"
              style="width:100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="分类">
            <el-select v-model="form.category_id" style="width:100%">
              <el-option
                v-for="cat in categories"
                :key="cat.id"
                :label="cat.name"
                :value="cat.id"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="耗时(小时)">
            <el-input-number
              v-model="form.hours"
              :min="0.5"
              :max="24"
              :step="0.5"
              style="width:100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="内容">
            <el-input v-model="form.content" placeholder="简要描述工作内容" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-button type="primary" :loading="saving" @click="handleSubmit"
        >保存</el-button
      >
    </el-form>
  </el-card>
</template>

<script setup>
import { reactive, ref, onMounted } from "vue";
import dayjs from "dayjs";
import api from "../api";

const emit = defineEmits(["saved"]);

const categories = ref([]);
const saving = ref(false);
const form = reactive({
  date: dayjs().format("YYYY-MM-DD"),
  category_id: null,
  content: "",
  hours: 1,
});

onMounted(async () => {
  const { data } = await api.get("/categories");
  categories.value = data;
  if (data.length) form.category_id = data[0].id;
});

async function handleSubmit() {
  if (!form.content.trim()) return;
  saving.value = true;
  try {
    await api.post("/entries", {
      date: form.date,
      category_id: form.category_id,
      content: form.content,
      duration_minutes: Math.round(form.hours * 60),
    });
    form.content = "";
    form.hours = 1;
    form.date = dayjs().format("YYYY-MM-DD");
    emit("saved");
  } finally {
    saving.value = false;
  }
}
</script>

<style scoped>
.entry-form-card {
  margin-bottom: 16px;
}
</style>
```

- [ ] **Step 2: Rewrite TodayEntries.vue**

```vue
<template>
  <el-card>
    <template #header>今日记录</template>
    <el-table :data="entries" stripe size="small" v-if="entries.length">
      <el-table-column prop="category_name" label="分类" width="100" />
      <el-table-column prop="content" label="内容" />
      <el-table-column label="耗时" width="100">
        <template #default="{ row }">
          {{ (row.duration_minutes / 60).toFixed(1) }}h
        </template>
      </el-table-column>
      <el-table-column label="操作" width="80">
        <template #default="{ row }">
          <el-button
            type="danger"
            text
            size="small"
            @click="handleDelete(row.id)"
            >删除</el-button
          >
        </template>
      </el-table-column>
    </el-table>
    <el-empty v-else description="暂无记录" :image-size="60" />
  </el-card>
</template>

<script setup>
import { ref, onMounted } from "vue";
import dayjs from "dayjs";
import api from "../api";

const entries = ref([]);
const today = dayjs().format("YYYY-MM-DD");

async function refresh() {
  const { data } = await api.get("/entries", {
    params: { start: today, end: today },
  });
  const { data: cats } = await api.get("/categories");
  const catMap = Object.fromEntries(cats.map((c) => [c.id, c.name]));
  entries.value = data.map((e) => ({
    ...e,
    category_name: catMap[e.category_id] || "",
  }));
}

async function handleDelete(id) {
  await api.delete(`/entries/${id}`);
  refresh();
}

onMounted(refresh);
defineExpose({ refresh });
</script>
```

- [ ] **Step 3: Test entry creation and display**

Open http://localhost:5173/weekly-report — create a few entries, verify they appear in today's list. Verify delete works.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/WorkEntryForm.vue frontend/src/components/TodayEntries.vue
git commit -m "feat: add work entry form and today's entries list"
```

---

### Task 12: Stats dashboard with ECharts

**Files:**

- Modify: `frontend/src/components/StatsDashboard.vue`

- [ ] **Step 1: Rewrite StatsDashboard.vue**

```vue
<template>
  <div v-loading="loading">
    <el-empty
      v-if="!report || report.entry_count === 0"
      description="本周暂无数据"
    />
    <template v-else>
      <el-row :gutter="16" class="stat-cards">
        <el-col :span="6">
          <el-statistic
            title="本周总工时"
            :value="report.total_hours"
            suffix="h"
          />
        </el-col>
        <el-col :span="6">
          <el-statistic title="记录条数" :value="report.entry_count" />
        </el-col>
        <el-col :span="6">
          <el-statistic
            title="工作天数"
            :value="report.work_days"
            suffix="天"
          />
        </el-col>
        <el-col :span="6">
          <el-statistic title="主力分类" :value="report.top_category || '-'" />
        </el-col>
      </el-row>
      <el-row :gutter="16" style="margin-top:20px">
        <el-col :span="12">
          <el-card>
            <template #header>分类占比</template>
            <v-chart :option="pieOption" style="height:300px" autoresize />
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card>
            <template #header>每日耗时分布</template>
            <v-chart :option="barOption" style="height:300px" autoresize />
          </el-card>
        </el-col>
      </el-row>
    </template>
  </div>
</template>

<script setup>
import { computed } from "vue";
import VChart from "vue-echarts";
import { use } from "echarts/core";
import { PieChart, BarChart } from "echarts/charts";
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";

use([
  PieChart,
  BarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  CanvasRenderer,
]);

const props = defineProps({
  report: Object,
  loading: Boolean,
});

const pieOption = computed(() => ({
  tooltip: { trigger: "item", formatter: "{b}: {c}h ({d}%)" },
  legend: { bottom: 0 },
  series: [
    {
      type: "pie",
      radius: ["45%", "75%"],
      center: ["50%", "45%"],
      data: (props.report?.category_breakdown || []).map((c) => ({
        name: c.category,
        value: c.hours,
        itemStyle: { color: c.color },
      })),
      label: { formatter: "{b}\n{d}%" },
    },
  ],
}));

const barOption = computed(() => ({
  tooltip: { trigger: "axis" },
  xAxis: {
    type: "category",
    data: (props.report?.daily_distribution || []).map((d) => d.weekday),
  },
  yAxis: { type: "value", name: "小时" },
  series: [
    {
      type: "bar",
      data: (props.report?.daily_distribution || []).map((d) => d.hours),
      itemStyle: { color: "#409EFF", borderRadius: [4, 4, 0, 0] },
      barWidth: "50%",
    },
  ],
  grid: { left: 50, right: 20, top: 20, bottom: 30 },
}));
</script>

<style scoped>
.stat-cards .el-col {
  text-align: center;
}
</style>
```

- [ ] **Step 2: Test statistics display**

Create work entries across multiple days/categories, switch to Tab 2 (统计看板) — verify stat cards, pie chart, and bar chart render correctly.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/StatsDashboard.vue
git commit -m "feat: add stats dashboard with ECharts pie and bar charts"
```

---

### Task 13: Weekly preview with Markdown

**Files:**

- Modify: `frontend/src/components/WeeklyPreview.vue`

- [ ] **Step 1: Rewrite WeeklyPreview.vue**

```vue
<template>
  <div>
    <el-empty
      v-if="!report || report.entry_count === 0"
      description="本周暂无数据"
    />
    <template v-else>
      <div class="preview-actions">
        <el-button type="primary" @click="handleCopy">复制全文</el-button>
        <el-button @click="handleExport">导出 Markdown</el-button>
      </div>
      <div class="markdown-body" v-html="rendered" />
    </template>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { ElMessage } from "element-plus";
import { marked } from "marked";
import api from "../api";

const props = defineProps({ report: Object });

const rendered = computed(() => {
  if (!props.report) return "";
  return marked(buildMarkdown(props.report));
});

function buildMarkdown(r) {
  let md = `# 工作周报 (${r.week_start} ~ ${r.week_end})\n\n`;
  md += `**总工时**：${r.total_hours} 小时 | **记录**：${r.entry_count} 条 | **工作天数**：${r.work_days} 天\n\n`;
  md += `## 分类统计\n\n`;
  for (const c of r.category_breakdown) {
    md += `- ${c.category}：${c.hours}h (${c.percentage}%)\n`;
  }
  md += `\n## 每日详情\n\n`;
  for (const d of r.daily_distribution) {
    const dayEntries = r.entries.filter((e) => e.date === d.date);
    const items = dayEntries
      .map((e) => `${e.category}: ${e.content}(${e.hours}h)`)
      .join(" · ");
    md += `**${d.weekday}**：${items}\n\n`;
  }
  return md;
}

async function handleCopy() {
  const md = buildMarkdown(props.report);
  await navigator.clipboard.writeText(md);
  ElMessage.success("已复制到剪贴板");
}

async function handleExport() {
  const { data } = await api.get("/reports/weekly/export", {
    params: { date: props.report.week_start },
  });
  const blob = new Blob([data.markdown], { type: "text/markdown" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `周报_${props.report.week_start}_${props.report.week_end}.md`;
  a.click();
  URL.revokeObjectURL(url);
  ElMessage.success("导出成功");
}
</script>

<style scoped>
.preview-actions {
  margin-bottom: 16px;
  display: flex;
  gap: 8px;
}
.markdown-body {
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 24px;
  line-height: 1.8;
}
.markdown-body :deep(h1) {
  font-size: 22px;
  margin-top: 0;
}
.markdown-body :deep(h2) {
  font-size: 17px;
  margin-top: 20px;
}
.markdown-body :deep(ul) {
  padding-left: 20px;
}
</style>
```

- [ ] **Step 2: Test preview and export**

Switch to Tab 3 (周报预览) — verify Markdown renders correctly. Click "复制全文" and paste somewhere to verify. Click "导出 Markdown" and verify file downloads.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/WeeklyPreview.vue
git commit -m "feat: add weekly preview with Markdown render and export"
```

---

### Task 14: History list

**Files:**

- Modify: `frontend/src/components/HistoryList.vue`

- [ ] **Step 1: Rewrite HistoryList.vue**

```vue
<template>
  <el-card>
    <template #header>
      <span>历史周报</span>
      <el-button
        text
        size="small"
        style="float:right"
        @click="fetchWeeks"
        :loading="loading"
        >刷新</el-button
      >
    </template>
    <el-table :data="weeks" stripe v-loading="loading" v-if="weeks.length">
      <el-table-column prop="label" label="周期" width="120" />
      <el-table-column prop="range" label="日期范围" width="220" />
      <el-table-column prop="total_hours" label="总工时" width="100">
        <template #default="{ row }">{{ row.total_hours }}h</template>
      </el-table-column>
      <el-table-column prop="entry_count" label="记录数" width="80" />
      <el-table-column label="操作" width="100">
        <template #default="{ row }">
          <el-button
            type="primary"
            text
            size="small"
            @click="$emit('view', row.start)"
            >查看</el-button
          >
        </template>
      </el-table-column>
    </el-table>
    <el-empty v-else description="暂无历史记录" :image-size="60" />
  </el-card>
</template>

<script setup>
import { ref, onMounted } from "vue";
import dayjs from "dayjs";
import isoWeek from "dayjs/plugin/isoWeek";
import api from "../api";

dayjs.extend(isoWeek);
defineEmits(["view"]);

const weeks = ref([]);
const loading = ref(false);

async function fetchWeeks() {
  loading.value = true;
  try {
    const { data } = await api.get("/entries", {
      params: { start: "2000-01-01", end: dayjs().format("YYYY-MM-DD") },
    });
    const weekMap = new Map();
    for (const e of data) {
      const d = dayjs(e.date);
      const monday = d.startOf("isoWeek").format("YYYY-MM-DD");
      if (!weekMap.has(monday)) {
        const sunday = d.endOf("isoWeek").format("YYYY-MM-DD");
        weekMap.set(monday, {
          start: monday,
          end: sunday,
          range: `${monday} ~ ${sunday}`,
          label: `第${d.isoWeek()}周`,
          total_hours: 0,
          entry_count: 0,
        });
      }
      const w = weekMap.get(monday);
      w.total_hours += e.duration_minutes;
      w.entry_count += 1;
    }
    weeks.value = Array.from(weekMap.values())
      .map((w) => ({ ...w, total_hours: +(w.total_hours / 60).toFixed(1) }))
      .reverse();
  } finally {
    loading.value = false;
  }
}

onMounted(fetchWeeks);
</script>
```

- [ ] **Step 2: Test history list**

Switch to Tab 4 (历史记录) — verify week list shows aggregated data. Click "查看" on a week and verify it switches to statistics tab with that week's data.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/HistoryList.vue
git commit -m "feat: add weekly history list with navigation"
```

---

### Task 15: Categories management page

**Files:**

- Create: `frontend/src/views/Categories.vue`

- [ ] **Step 1: Write views/Categories.vue**

```vue
<template>
  <div class="categories-page">
    <el-card>
      <template #header>
        <span>分类管理</span>
        <el-button
          type="primary"
          size="small"
          style="float:right"
          @click="showAdd = true"
          >新增分类</el-button
        >
      </template>

      <el-table :data="categories" stripe v-loading="loading">
        <el-table-column label="颜色" width="80">
          <template #default="{ row }">
            <span class="color-dot" :style="{ background: row.color }" />
          </template>
        </el-table-column>
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="sort_order" label="排序" width="80" />
        <el-table-column label="操作" width="160">
          <template #default="{ row }">
            <el-button text size="small" @click="editRow(row)">编辑</el-button>
            <el-button
              text
              size="small"
              type="danger"
              @click="handleDelete(row.id)"
              >删除</el-button
            >
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog
      :title="editing.id ? '编辑分类' : '新增分类'"
      v-model="dialogVisible"
      width="400px"
    >
      <el-form :model="form" label-width="80px">
        <el-form-item label="名称">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="颜色">
          <el-color-picker v-model="form.color" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort_order" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave"
          >保存</el-button
        >
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import api from "../api";

const categories = ref([]);
const loading = ref(false);
const saving = ref(false);
const dialogVisible = ref(false);
const editing = ref({});
const form = reactive({ name: "", color: "#409EFF", sort_order: 0 });

async function fetchCategories() {
  loading.value = true;
  try {
    const { data } = await api.get("/categories");
    categories.value = data;
  } finally {
    loading.value = false;
  }
}

function editRow(row) {
  editing.value = row;
  form.name = row.name;
  form.color = row.color;
  form.sort_order = row.sort_order;
  dialogVisible.value = true;
}

async function handleSave() {
  saving.value = true;
  try {
    if (editing.value.id) {
      await api.put(`/categories/${editing.value.id}`, { ...form });
    } else {
      await api.post("/categories", { ...form });
    }
    dialogVisible.value = false;
    editing.value = {};
    await fetchCategories();
  } finally {
    saving.value = false;
  }
}

async function handleDelete(id) {
  try {
    await ElMessageBox.confirm("确定删除该分类？", "提示", { type: "warning" });
    await api.delete(`/categories/${id}`);
    await fetchCategories();
    ElMessage.success("已删除");
  } catch {
    /* cancelled */
  }
}

onMounted(fetchCategories);
</script>

<style scoped>
.color-dot {
  display: inline-block;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  vertical-align: middle;
}
</style>
```

- [ ] **Step 2: Test categories management**

Navigate to 分类管理 — verify list shows 5 preset categories. Test add/edit/delete. Verify delete fails if category has entries (400 error).

- [ ] **Step 3: Commit**

```bash
git add frontend/src/views/Categories.vue
git commit -m "feat: add categories management page"
```

---

### Task 16: Final integration test and polish

- [ ] **Step 1: Full flow test**

Run backend: `cd backend && uvicorn main:app --port 8000`

Run frontend: `cd frontend && npm run dev`

1. Register new user at http://localhost:5173/register
2. Create 5-6 work entries across 3-4 days with different categories
3. Switch to 统计看板 — verify cards, pie chart, bar chart
4. Switch to 周报预览 — verify Markdown, copy, export
5. Switch to 历史记录 — verify week aggregation
6. Add a custom category in 分类管理
7. Use the new category in work entry
8. Logout, login — verify data persists

- [ ] **Step 2: Verify README**

Create `README.md`:

```markdown
# 工作周报系统

## 启动

### 后端

cd backend
pip install -r requirements.txt
uvicorn main:app --port 8000

### 前端

cd frontend
npm install
npm run dev

打开 http://localhost:5173
```

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: add README with startup instructions"
```
