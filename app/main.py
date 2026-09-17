import logging
from time import perf_counter

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers.category import router as category_router
from app.api.routers.task import router as task_router
from app.core.config import get_settings
from app.core.logging import configure_logging

configure_logging()


settings = get_settings()

app = FastAPI()
logger = logging.getLogger("app.middleware")


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origin,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


@app.middleware(
    "http"
)  # log_requests выполнится до и после обработки каждого HTTP-запроса
async def log_requests(request: Request, call_next) -> Response:
    started_at = perf_counter()
    try:
        response: Response = await call_next(request)  # Работа самого эндпоинта
    except Exception:
        duration_ms = (perf_counter() - started_at) * 1000
        logger.exception(
            "Request failed: %s %s completed_in=%.2fms",
            request.method,
            request.url.path,
            duration_ms,
        )
        raise

    duration_ms = (perf_counter() - started_at) * 1000
    logger.info(
        "%s %s -> %s (%.2f ms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


request_counter = 0


@app.middleware("http")
async def add_request_number(request: Request, call_next) -> Response:
    global request_counter

    request_counter += 1
    current_request_number = request_counter

    response = await call_next(request)

    response.headers["X-Request-Number"] = str(current_request_number)

    return response


app.include_router(router=task_router)
app.include_router(router=category_router)
