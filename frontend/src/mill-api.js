import {awaitCompute, request} from './api.js';

export const mill = {
  bay: () => request('/bay'),
  intake: body => request('/bay', body),
  reports: () => request('/sieve'),
  screen: (code, body) => request('/sieve/' + code, body),
  fit: body => request('/fit', body),
  result: awaitCompute,
  reserve: body => request('/fit/reserve', body),
  tickets: () => request('/weigh'),
  ticket: code => request('/weigh/' + code),
  read: (code, body) => request('/weigh/' + code + '/read', body),
  finalize: (code, action) => request('/weigh/' + code + '/' + action, {}),
  movements: () => request('/weigh/ledger'),
  patchBoard: () => request('/patches'),
  patch: code => request('/patches/' + code),
  markPatch: (code, body) => request('/patches/' + code, body),
  layPatch: code => request('/patches/' + code + '/lay', {}),
  measurePatch: (code, grid, body) => request('/patches/' + code + '/cells/' + grid + '/measure', body),
  openPatch: code => request('/patches/' + code + '/open', {}),
};
