import {el} from '../dom.js';
import {mill} from '../mill-api.js';
import {desk} from '../mill-state.js';
import {actionForm, input, kilograms, mayWrite, select} from '../weights.js';
import {status, titleBlock} from '../widgets.js';
import {layers} from '../components/layers.js';

function recipe(box, payload) {
  const result = payload.result;
  const rows = result.lines.map(line => el('tr', {}, el('td', {}, line.lot_code || '新料'),
    el('td', {class:'mono'}, kilograms(line.grams))));
  box.replaceChildren(el('div',{class:'result-sheet flash'},el('h2',{},'配方预览'),
    el('p',{class:'mono'},'CLR 距离 ' + result.distance.toFixed(4) + ' · 回收料 ' + kilograms(result.reclaimed_g)),
    el('p',{},'现场秤距 50 g。称量单以原始筛分版本为依据。'),
    el('table',{},el('thead',{},el('tr',{},el('th',{},'料批来源'),el('th',{},'设置重量'))),el('tbody',{},rows)),
    el('h3',{},'回收料闭合后组成'),result.restored.map(item => el('div',{},el('code',{},item.code),
      layers(item.parts.map(value => +(value * 100).toFixed(3)), '%'),
      el('p',{class:'mono'},'CLR [' + item.clr.map(value => value.toFixed(4)).join(', ') +
        '] · 低限替换 ' + item.zero_replacements + ' 档')))));
}

export async function fit(root, role) {
  const {zones, lots} = await mill.bay();
  const reference = el('section', {class:'ledger'}, el('h2',{},'未计算配方'),
    status('选择同材质的一个或两个可用批次，查看秤量读数和粒径比例。'));
  const certain = el('div', {});
  const batchChoices = el('fieldset',{});
  function choices(code) {
    const zone = zones.find(item => item.code === code);
    batchChoices.replaceChildren(el('legend',{},'可用回收批'),
      ...lots.filter(lot => lot.state === 'eligible' && lot.family === zone.family).map(lot =>
        el('label',{class:'choice'},el('input',{name:'lot',type:'checkbox',value:lot.code}),
          lot.code + ' · 未预占 ' + kilograms(lot.available_g - lot.reserved_g))));
    if (batchChoices.children.length === 1) batchChoices.append(status('此场区没有通过筛分的同材质批次。'));
  }
  const area = select('zone_code','回填场区',zones.map(zone => [zone.code,zone.label]));
  const zonePicker = area.querySelector('select');
  zonePicker.value = desk.selectedZone || 'YH-NORTH';
  choices(zonePicker.value);
  zonePicker.addEventListener('change', () => {
    desk.selectedZone = zonePicker.value;
    choices(zonePicker.value);
    certain.replaceChildren();
  });
  const form = mayWrite(role) ? actionForm('preview',[area,batchChoices,
    input('total_g','配方总重（g）',{type:'number', min:'1000',max:'60000',step:'50',value:'12000'})],
    '计算可落秤配方',async values => {
      certain.replaceChildren();
      const selection = values.getAll('lot');
      if (selection.length < 1 || selection.length > 2) throw new Error('请选择一或两个批次');
      const queued = await mill.fit({zone_code:values.get('zone_code'),total_g:Number(values.get('total_g')),lot_codes:selection});
      const report = await mill.result(queued.token, item => {
        if (item.status === 'queued') reference.replaceChildren(status('称量刻度搜索中…'));
      });
      if (report.status !== 'ready') {
        reference.replaceChildren(status(report.detail,'error'));
        throw new Error(report.detail);
      }
      recipe(reference,report);
      certain.replaceChildren(actionForm('reserve',[input('code','称量单编号',{placeholder:'WT-1124-A'})],
        '锁定回收料',async data => {
          const ticket = await mill.reserve({code:data.get('code'),token:queued.token});
          desk.activeTicket = ticket.code;
          certain.append(el('a',{href:'#scale'},'前往称量单 ' + ticket.code));
          return '已锁料，请逐行核对秤读';
        }));
      return '计算完成';
    }) : status('作业员或复核员可生成配方。');
  root.replaceChildren(titleBlock('配料 · CLR', '粒径配方对照', '计算每 50 g 的候选配方，优先保留满足场区容差的最大回收量。'),
    el('div',{class:'workspace-split sieve'},el('section',{class:'action'},el('h2',{},'选择候选料批'),form,certain),reference));
}
