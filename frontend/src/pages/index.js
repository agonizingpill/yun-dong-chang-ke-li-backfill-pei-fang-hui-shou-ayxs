import {bay} from './bay.js';
import {sieve} from './sieve.js';
import {fit} from './fit.js';
import {scale} from './scale.js';
import {patchPage} from './patch.js';

export const info = {title:'屿岸回收料称量',customer:'屿岸运动铺装维护队',
  purpose:'为可回收胶粒保留筛分证据，按场区目标规划秤料并记录现场补坪验收。'};
export const pages = [
  {key:'bay',title:'回收与场区',render:bay}, {key:'sieve',title:'筛分记录',render:sieve},
  {key:'fit',title:'粒径配方',render:fit}, {key:'scale',title:'称量发料',render:scale},
  {key:'patch',title:'补坪验收',render:patchPage},
];
