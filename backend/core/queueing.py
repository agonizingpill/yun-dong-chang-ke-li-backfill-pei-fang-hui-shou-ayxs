import json
from uuid import uuid4

from fastapi import HTTPException
from redis import Redis

from core.config import REDIS_URL

broker = Redis.from_url(REDIS_URL, decode_responses=True)
QUEUE = 'compute_requests'

def submit(user, payload):
    token = uuid4().hex
    item = {'token': token, 'owner': user['sub'], 'input': payload}
    with broker.pipeline() as pipe:
        pipe.set(f'compute:{token}', json.dumps({'owner': user['sub'], 'status': 'queued'}), ex=86400)
        pipe.rpush(QUEUE, json.dumps(item))
        pipe.execute()
    return {'token': token, 'status': 'queued'}

def view(user, token):
    raw = broker.get(f'compute:{token}')
    if raw is None:
        raise HTTPException(404, detail='计算任务不存在或已过期')
    record = json.loads(raw)
    if record['owner'] != user['sub'] and user['role'] != 'reviewer':
        raise HTTPException(403, detail='仅提交人和复核员可查看计算')
    return {k: v for k, v in record.items() if k != 'owner'}

def result(user, token):
    data = view(user, token)
    if data['status'] != 'ready':
        raise HTTPException(409, detail='等待计算完成后再提交')
    return data
