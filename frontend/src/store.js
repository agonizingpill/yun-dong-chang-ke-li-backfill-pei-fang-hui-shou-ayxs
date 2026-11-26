export const ROLES = Object.freeze({operator: '作业员', reviewer: '复核员', viewer: '只读访客'});
export const COMPUTE_STATES = Object.freeze({queued: '排队中', ready: '已计算', rejected: '计算被拒绝'});
export function session() {
  try { return JSON.parse(sessionStorage.getItem('session')); } catch { return null; }
}
export function setSession(value) {
  if (value) sessionStorage.setItem('session', JSON.stringify(value));
  else sessionStorage.removeItem('session');
}
export const evidence = {
  get: () => sessionStorage.getItem('latest-computation') || '',
  save: token => sessionStorage.setItem('latest-computation', token)
};
