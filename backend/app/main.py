from fastapi import FastAPI, HTTPException, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field, model_validator

from .data import SESSIONS

app = FastAPI(title="Shuttle Kampus API")

# CORS: izinkan origin frontend Vite (dev server default port 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class SessionIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    route: str = Field(min_length=3, max_length=80)
    driver: str = Field(min_length=2, max_length=50)
    departure: str = Field(pattern=r"^([01]\d|2[0-3]):[0-5]\d$", description="Format HH:MM")
    capacity: int = Field(ge=1, le=60)
    booked: int = Field(ge=0, default=0)

    @model_validator(mode="after")
    def booked_not_over_capacity(self):
        if self.booked > self.capacity:
            raise ValueError("booked tidak boleh melebihi capacity")
        return self


class SessionOut(SessionIn):
    id: int


class SessionPage(BaseModel):
    items: list[SessionOut]
    total: int
    page: int
    page_size: int


def _next_id() -> int:
    return max((s["id"] for s in SESSIONS), default=0) + 1


@app.get("/sessions", response_model=SessionPage)
def list_sessions(
    page: int = Query(1, ge=1),
    page_size: int = Query(5, ge=1, le=50),
    search: str = Query("", max_length=80),
):
    q = search.strip().lower()
    rows = [
        s for s in SESSIONS
        if not q or q in s["route"].lower() or q in s["driver"].lower()
    ]
    start = (page - 1) * page_size
    return {
        "items": rows[start:start + page_size],
        "total": len(rows),
        "page": page,
        "page_size": page_size,
    }


@app.get("/sessions/{session_id}", response_model=SessionOut)
def get_session(session_id: int):
    for s in SESSIONS:
        if s["id"] == session_id:
            return s
    raise HTTPException(status_code=404, detail="Sesi tidak ditemukan")


@app.post("/sessions", response_model=SessionOut, status_code=status.HTTP_201_CREATED)
def create_session(payload: SessionIn):
    new = {"id": _next_id(), **payload.model_dump()}
    SESSIONS.append(new)
    return new


@app.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(session_id: int):
    for i, s in enumerate(SESSIONS):
        if s["id"] == session_id:
            SESSIONS.pop(i)
            return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(status_code=404, detail="Sesi tidak ditemukan")
