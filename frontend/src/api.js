import {session} from './store.js';

export async function request(path, data) {
  const headers = {'Content-Type':'application/json'};
  if (session()) headers.Authorization = 'Bearer ' + session().token;
  const response = await fetch('/api' + path, data === undefined ? {headers} :
    {method:'POST', headers, body:JSON.stringify(data)});
  const payload = await response.json();
  if (!response.ok) {
    const detail = Array.isArray(payload.detail) ? payload.detail.map(x => x.loc.at(-1) + ' ' + x.msg).join(' / ') : payload.detail;
    throw new Error(detail || '请求未完成');
  }
  return payload;
}

export async function awaitCompute(token, report) {
  for (let i = 0; i < 40; i++) {
    const data = await request('/compute/' + token);
    report(data);
    if (data.status !== 'queued') return data;
    await new Promise(resolve => setTimeout(resolve, 250));
  }
  throw new Error('计算仍在排队，可回到工作页继续查询任务号');
}
