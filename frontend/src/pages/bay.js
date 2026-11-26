import {el} from '../dom.js';
import {mill} from '../mill-api.js';
import {desk, lotStates} from '../mill-state.js';
import {actionForm, input, kilograms, mayWrite, select} from '../weights.js';
import {status, titleBlock} from '../widgets.js';
import {layers} from '../components/layers.js';
import {pitch} from '../components/pitch.js';
import {pill} from '../components/state-pill.js';

export async function bay(root, role) {
  const physical = el('div', {class: 'records'});
  const section = el('div', {});
  const zones = el('div', {});
  function displayZone(zone) {
    section.replaceChildren(el('h3', {}, zone.label), layers([zone.fine_pt, zone.medium_pt, zone.coarse_pt], '%'),
      status('回收占比上限 ' + zone.max_reclaimed_pt + '% · CLR 容差 ' + zone.max_clearance));
  }
  async function load() {
    const data = await mill.bay();
    physical.replaceChildren(...data.lots.map(lot => el('article',
      {class: 'record ' + (lot.state === 'quarantined' ? 'warn' : '')},
      el('h3', {class: 'mono'}, lot.code), el('p', {}, lot.donor_surface),
      pill(lotStates[lot.state], lot.state),
      el('p', {}, '余量 ' + kilograms(lot.available_g) + ' / 已锁 ' + kilograms(lot.reserved_g)))));
    desk.selectedZone ||= data.zones.find(zone => zone.code === 'YH-NORTH').code;
    zones.replaceChildren(pitch(data.zones, displayZone));
    displayZone(data.zones.find(zone => zone.code === desk.selectedZone));
  }
  const intake = mayWrite(role) ? actionForm('lot-intake', [
    input('code', '袋批编号', {placeholder: 'EP-1124-E'}),
    input('donor_surface', '旧料来源', {placeholder: '北端边线 · 第三段'}),
    select('family', '胶粒材质', [['epdm', 'EPDM'], ['tpe', 'TPE']]),
    input('gross_g', '入袋净重（g）', {type: 'number', min: '1000', value: '18000'}),
  ], '登记回收袋批', async fields => {
    const body = Object.fromEntries(fields);
    body.gross_g = Number(body.gross_g);
    await mill.intake(body);
    await load();
    return body.code + ' 待筛分';
  }) : status('只读角色可核对批次与场区的净重。');
  root.replaceChildren(titleBlock('场地 · 回收袋', '回收袋和回填场区', '白线两侧有不同粒径目标。先登记净重，再将袋批送筛分。'),
    el('div', {class: 'workspace-split'}, el('section', {class: 'ledger'}, zones, section,
      el('h2', {}, '本班袋批'), physical),
    el('section', {class: 'action'}, el('h2', {}, '回收收料'), intake)));
  try { await load(); } catch (error) { physical.replaceChildren(status(error.message, 'error')); }
}
