from datetime import datetime
import logging
from typing import Literal
import aiosqlite
import config
from fastapi import Depends, FastAPI, HTTPException, status, Header
from Functions.get_roblox_id import get_roblox_id
import aiohttp
from pydantic import BaseModel
import uvicorn

app = FastAPI(
    title="Portfolio Bot",
    description="Async REST API endpoints."
)

db_path = "data/kos_blacklist.db"
logger = logging.getLogger(__name__)
API_KEY = config.API_KEY


async def verify_api_key(authorization: str = Header(None)):
    if not authorization or authorization != f"Bearer {API_KEY}":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Invalid or missing API Key."
        )


class SetKosRequest(BaseModel):
    username: str
    status: bool


class SetBlacklistRequest(BaseModel):
    username: str
    action: Literal["add", "remove"] = "add"
    reason: str = "No reason provided"
    added_by: int | str = "Unknown"


class KosResponse(BaseModel):
    success: bool
    user_id: int
    username: str
    status: str


class BlacklistEntry(BaseModel):
    user_id: int
    reason: str
    added_by: int | str = "Unknown"
    last_edit: int
    username: str


class BlacklistResponse(BaseModel):
    success: bool
    status: bool
    blacklist: list[BlacklistEntry] | None = None


class SetBlacklistResponse(BaseModel):
    success: bool
    user_id: int
    username: str
    reason: str
    added_by: int | str = "Unknown"
    last_edit: int


class BlacklistListResponse(BaseModel):
    success: bool
    count: int
    blacklist: list[BlacklistEntry]


@app.post(
    "/api/kos",
    response_model=KosResponse,
    dependencies=[Depends(verify_api_key)],
)
async def set_kos(payload: SetKosRequest):
    user_id, exact_username = await get_roblox_id(payload.username)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    async with aiosqlite.connect(db_path) as conn:
        await conn.execute("""
            INSERT INTO kos (user_id, kos) VALUES (?, ?)
            ON CONFLICT (user_id) DO UPDATE SET
                kos = excluded.kos
        """, (user_id, payload.status))
        await conn.commit()
    return KosResponse(
        success=True,
        user_id=user_id,
        username=exact_username,
        status=str(payload.status),
    )


@app.get(
    "/api/koscheck/{username}",
    response_model=KosResponse,
    dependencies=[Depends(verify_api_key)],
)
async def koscheck(username: str):
    user_id, exact_username = await get_roblox_id(username)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    async with aiosqlite.connect(db_path) as conn:
        async with conn.execute("""
            SELECT kos FROM kos WHERE user_id = ?
        """, (user_id,)) as c:
            row = await c.fetchone()
        if row is None:
            status_str = "never_kos"
        else:
            status_str = "current_kos" if row[0] else "former_kos"
        return KosResponse(
            success=True,
            user_id=user_id,
            username=exact_username,
            status=status_str,
        )


@app.post(
    "/api/blacklist",
    response_model=SetBlacklistResponse,
    dependencies=[Depends(verify_api_key)],
)
async def set_blacklist(payload: SetBlacklistRequest):
    last_edit = int(datetime.now().timestamp())
    user_id, exact_username = await get_roblox_id(payload.username)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    async with aiosqlite.connect(db_path) as conn:
        if payload.action == "remove":
            await conn.execute("""
                DELETE FROM blacklist WHERE user_id = ?
            """, (user_id,))
        else:
            await conn.execute("""
                INSERT INTO blacklist (user_id, reason, added_by, last_edit) VALUES (?, ?, ?, ?)
                ON CONFLICT (user_id) DO UPDATE SET
                    reason = excluded.reason
                    added_by = excluded.added_by
                    last_edit = excluded.last_edit
            """, (user_id, payload.reason, payload.added_by, last_edit))
        await conn.commit()
    return SetBlacklistResponse(
        success=True,
        user_id=user_id,
        username=exact_username,
        reason=payload.reason,
        added_by=payload.added_by,
        last_edit=last_edit,
    )


@app.get(
    "/api/blacklistlist",
    response_model=BlacklistListResponse,
    dependencies=[Depends(verify_api_key)],
)
async def get_blacklist():
    async with aiosqlite.connect(db_path) as conn:
        async with conn.execute("""
            SELECT user_id, reason, added_by, last_edit FROM blacklist
        """) as c:
            rows = await c.fetchall()
        if not rows:
            return BlacklistListResponse(success=True, count=0, blacklist=[])
        user_ids = list({r[0] for r in rows})

        def chunks(items: list[int], size: int):
            for i in range(0, len(items), size):
                yield items[i:i + size]

        username_map = {}
        async with aiohttp.ClientSession() as session:
            for batch in chunks(user_ids, 100):
                try:
                    async with session.post(
                            "https://users.roblox.com/v1/users",
                            json={"userIds": batch, "excludeBannedUsers": False},
                            timeout=5.0
                    ) as response:
                        if response.status == 200:
                            data = (await response.json()).get("data", [])
                            username_map.update({u["id"]: u["name"] for u in data})
                except Exception as e:
                    logger.error(f"Failed to fetch Roblox users: {e}")
        blacklist = [
            BlacklistEntry(
                user_id=r[0],
                reason=r[1],
                added_by=r[2],
                last_edit=r[3],
                username=username_map.get(r[0], "Unknown user")
            )
            for r in rows
        ]
        return BlacklistListResponse(
            success=True,
            count=len(blacklist),
            blacklist=blacklist
        )


@app.get(
    "/api/blacklist/{username}",
    response_model=BlacklistResponse,
    dependencies=[Depends(verify_api_key)],
)
async def is_blacklist(username: str):
    user_id, exact_username = await get_roblox_id(username)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    async with aiosqlite.connect(db_path) as conn:
        async with conn.execute("""
            SELECT user_id, reason, added_by, last_edit FROM blacklist WHERE user_id = ?
        """, (user_id,)) as c:
            row = await c.fetchone()
        if not row:
            return BlacklistResponse(success=True, status=False, blacklist=None)
        entry = BlacklistEntry(
            user_id=row[0],
            reason=row[1],
            added_by=row[2],
            last_edit=row[3],
            username=exact_username,
        )
        return BlacklistResponse(success=True, status=True, blacklist=[entry])


def run_api():
    uvicorn.run(app, host="127.0.0.1", port=5000, log_level="info")


if __name__ == "__main__":
    run_api()
