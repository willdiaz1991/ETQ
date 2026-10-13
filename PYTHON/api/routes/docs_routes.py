from fastapi import APIRouter
from fastapi.responses import RedirectResponse

router = APIRouter(include_in_schema=False)


@router.get("/")
async def root_redirect():
    return RedirectResponse(url="/docs")
