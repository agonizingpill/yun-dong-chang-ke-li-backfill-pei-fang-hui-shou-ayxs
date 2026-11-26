import {el} from '../dom.js';
import {mill} from '../mill-api.js';
import {binNames, decisions, zeroModes} from '../mill-state.js';
import {actionForm, input, mayWrite, numbers, select} from '../weights.js';
import {status, titleBlock} from '../widgets.js';
import {layers} from '../components/layers.js';
import {pill} from '../components/state-pill.js';

const fields = ['fine_g', 'medium_g', 'coarse_g', 'foreign_g'];

export async function sieve(root, role) {
  const capture = el('div', {});
  const reportList = el('div', {class:'folds'});
  const {lots} = await mill.bay();
  async function load(open) {
    const reports = await mill.reports();
    reportList.replaceChildren(...reports.map(report => el('details',
      {open: open === report.code ? '' : undefined}, el('summary', {}, report.code + ' · ',
        pill(decisions[report.decision], report.decision)),
        layers(fields.map(name => report[name])),
        status('零档说明 ' + zeroModes[report.zero_mode] + ' · 检验员 ' + report.chemist))));
  }
  if (mayWrite(role)) capture.append(actionForm('screen', [
    select('lot', '待检或复筛批', lots.map(item => [item.code, item.code + ' · ' + item.donor_surface])),
    el('div', {class:'fields'}, fields.map((name, i) => input(name, binNames[i] + '（g）',
      {type:'number', min:'0', max:'1000', value: i === 3 ? '0' : undefined}))),
    select('zero_mode', '零档说明', Object.entries(zeroModes)),
  ], '签筛分单', async values => {
    const result = await mill.screen(values.get('lot'), {...numbers(values, fields), zero_mode: values.get('zero_mode')});
    await load(result.report.code);
    return result.report.code + ' · ' + decisions[result.report.decision];
  }));
  else capture.append(status('只读角色可从右侧展开筛分单。'));
  root.replaceChildren(titleBlock('质量 · 1 kg 样', '一公斤筛分', '合计须为 1000 g。杂物超过 10 g 或真实缺档的袋批立即隔离。'),
    el('div', {class:'workspace-split sieve'}, el('section',{class:'action'}, el('h2',{},'落秤记录'), capture),
      el('section',{class:'ledger'},el('h2',{},'筛分版本'),reportList)));
  await load(null);
}
