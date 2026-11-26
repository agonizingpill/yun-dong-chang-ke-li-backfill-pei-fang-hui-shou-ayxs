import logging
from time import perf_counter
from uuid import uuid4

from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

log = logging.getLogger('uvicorn.error')

def install(app):
    @app.middleware('http')
    async def trace(request: Request, call_next):
        request.state.trace_id = uuid4().hex[:12]
        start = perf_counter()
        response = await call_next(request)
        response.headers['X-Request-ID'] = request.state.trace_id
        response.headers['Server-Timing'] = f'app;dur={(perf_counter() - start)*1000:.2f}'
        return response

    @app.middleware('http')
    async def body_limit(request: Request, call_next):
        if request.headers.get('content-length', '0').isdigit() and int(request.headers.get('content-length', 0)) > 262144:
            return JSONResponse({'detail': '请求体超过 256 KiB'}, status_code=413)
        return await call_next(request)

    @app.exception_handler(IntegrityError)
    async def conflict(request: Request, exc: IntegrityError):
        log.info('database constraint rejected trace=%s', getattr(request.state, 'trace_id', 'unknown'))
        return JSONResponse({'detail': '编号或引用冲突，请刷新后重试'}, status_code=409)
