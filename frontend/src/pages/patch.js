import {el} from '../dom.js';
import {mill} from '../mill-api.js';
import {desk} from '../mill-state.js';
import {actionForm, input, kilograms, mayWrite, select} from '../weights.js';
import {dataView, status, titleBlock} from '../widgets.js';

const coordinates = [...'ABCD'].flatMap(row => Array.from({length:8}, (_, column) => row + (column + 1)));
const points = [
  ['first_mm','起点（mm）'], ['middle_mm','中点（mm）'], ['last_mm','终点（mm）'],
];
const stage = p => p.opened_by ? '已签开场' : p.laid_by ? '已实铺' : '待实铺';
const last = cell => cell.history.at(-1);
const condition = cell => last(cell) === undefined ? '待测' : last(cell).passed ? '合格' : '待复测';

function planner(board, preferred, complete) {
  if (!board.eligible_tickets.length) return status('有已发料的称量单后可划定补坪范围。');
  const ticketSelect = select('ticket','已发料单',board.eligible_tickets.map(ticket =>
    [ticket.code, ticket.code + ' · ' + ticket.zone_code + ' · ' + kilograms(ticket.total_g)]));
  const control = ticketSelect.querySelector('select');
  if (board.eligible_tickets.some(ticket => ticket.code === preferred)) control.value = preferred;
  const grid = el('fieldset',{class:'patch-plan','aria-label':'待补坪网格'});
  function layout() {
    const ticket = board.eligible_tickets.find(item => item.code === control.value);
    const taken = new Set(board.active_cells.filter(c => c.zone_code === ticket.zone_code).map(c => c.grid_ref));
    grid.replaceChildren(el('legend',{},ticket.zone_code + ' · 选 1–8 格'),
      ...coordinates.map(ref => el('label',{class:'patch-choice'},
        el('input',{type:'checkbox',name:'grid_refs',value:ref,disabled:taken.has(ref) ? '' : undefined,
          'aria-label':'网格 ' + ref}),el('span',{},ref))));
  }
  control.addEventListener('change',layout);
  layout();
  return actionForm('mark-patch',[ticketSelect,grid],'划定补坪范围',async values => {
    const refs = values.getAll('grid_refs');
    if (refs.length < 1 || refs.length > 8) throw new Error('请选择 1–8 个可用网格。');
    const code = values.get('ticket');
    await mill.markPatch(code,{grid_refs:refs});
    await complete(code);
  });
}

function cellHistory(cell) {
  const rows = [...cell.history].reverse().map(r => ({
    id:r.id, depth:[r.first_mm,r.middle_mm,r.last_mm].join(' / '), spread:r.spread_mm,
    outcome:r.passed ? '合格' : '未通过', prior:r.repeat_of, by:r.measured_by,
  }));
  return dataView(rows,[
    {name:'id',label:'读数号'},{name:'depth',label:'三点（mm）'},{name:'spread',label:'极差（mm）'},
    {name:'outcome',label:'结论'},{name:'prior',label:'复测自'},{name:'by',label:'登记人'},
  ],'table');
}

export async function patchPage(root, role) {
  const rail = el('div',{class:'cardrail'});
  const controls = el('section',{class:'ledger'});
  const panel = el('section',{class:'ledger patch-detail'});
  root.replaceChildren(titleBlock('现场 · 局部施工','补坪验收与开场',
    '按发料单划定网格。每格在起点、中点、终点测厚，三点须在 12–16 mm 内且极差不超过 2 mm。'),
  el('div',{class:'workspace-split'},panel,controls));
  let code = desk.activeTicket;
  let gridRef = null;
  let viewId = 0;

  function show(detail) {
    if (detail.patch.code !== code) return;
    const work = detail.patch;
    gridRef = detail.cells.some(cell => cell.grid_ref === gridRef) ? gridRef : detail.cells[0].grid_ref;
    const current = detail.cells.find(cell => cell.grid_ref === gridRef);
    const mark = el('div',{class:'patch-map','aria-label':'工单网格'},detail.cells.map(cell =>
      el('button',{class:'quiet',type:'button','data-grid':cell.grid_ref,'data-condition':condition(cell),
        'aria-pressed':String(cell === current),onclick:() => { gridRef = cell.grid_ref; show(detail); }},
      cell.grid_ref + ' · ' + condition(cell))));
    const body = el('div',{class:'patch-evidence'},el('h3',{},current.grid_ref + ' 测读记录'),cellHistory(current));
    panel.replaceChildren(el('div',{class:'section-label'},work.zone_code + ' · ' + stage(work)),
      el('h2',{},work.code),el('p',{},'合格网格 ' + detail.passed_cells + ' / ' + detail.cells.length),mark,body);
    if (work.opened_by) {
      panel.append(status('已签开场 · ' + work.opened_by,'ok'));
    } else if (!work.laid_by && mayWrite(role)) {
      panel.append(actionForm('lay-patch',[],'登记实铺',async () => show(await mill.layPatch(work.code))));
    } else if (work.laid_by) {
      const previous = last(current);
      if (mayWrite(role) && !previous?.passed) {
        const fields = points.map(([name,label]) => input(name,label,{type:'number',min:'0',max:'35',step:'1'}));
        panel.append(actionForm('measure-patch',[el('div',{class:'depth-inputs'},fields)],
          previous ? '提交复测' : '提交测读',async values => {
            const readings = Object.fromEntries(points.map(([name]) => [name,Number(values.get(name))]));
            show(await mill.measurePatch(work.code,current.grid_ref,{...readings,repeat_of:previous?.id ?? null}));
          }));
      }
      if (role === 'reviewer' && detail.passed_cells === detail.cells.length) {
        panel.append(actionForm('open-patch',[],'签开场许可',async () => {
          show(await mill.openPatch(work.code));
          await refreshBoard();
        }));
      }
    }
  }

  async function open(target) {
    if (target !== code) gridRef = null;
    code = desk.activeTicket = target;
    for (const button of rail.querySelectorAll('button')) {
      button.setAttribute('aria-pressed', String(button.textContent === target));
    }
    const currentView = ++viewId;
    const detail = await mill.patch(target);
    if (currentView === viewId) show(detail);
  }

  async function refreshBoard() {
    const board = await mill.patchBoard();
    rail.replaceChildren(...board.patches.map(work => el('button',{class:'quiet',type:'button',
      'aria-pressed':String(work.code === code),
      onclick:() => open(work.code).catch(error => panel.replaceChildren(status(error.message,'error')))},work.code)));
    controls.replaceChildren(el('h2',{},'补坪工单'),rail);
    if (mayWrite(role)) controls.append(planner(board,code,async target => {
      await refreshBoard();
      await open(target);
    }));
    return board;
  }

  const board = await refreshBoard();
  if (board.patches.some(work => work.code === code)) await open(code);
  else if (mayWrite(role) && board.eligible_tickets.some(ticket => ticket.code === code)) {
    panel.append(status('当前发料单可在右侧划定补坪网格。'));
  } else if (board.patches.length) await open(board.patches[0].code);
  else panel.append(status('暂无补坪工单。'));
}
