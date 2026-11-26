import {display, el} from './dom.js';

export function status(message, variant = '') {
  return el('p', {class:'status ' + variant, role:'status'}, message);
}
export function dataView(rows, columns, layout) {
  if (!rows.length) return status('暂无可用记录。可先填入一条领域凭证。');
  if (layout === 'table') {
    return el('div', {class:'scroll'}, el('table', {},
      el('thead', {}, el('tr', {}, columns.map(x => el('th', {scope:'col'}, x.label)))),
      el('tbody', {}, rows.map(r => el('tr', {}, columns.map(x => el('td', {}, display(r[x.name]))))))));
  }
  return el('div', {class:'records ' + layout}, rows.map(row =>
    el('article', {class:'record'}, el('h3',{},display(row[columns[0].name])),
      el('dl',{},columns.slice(1).flatMap(x => [
        el('dt',{},x.label), el('dd',{},display(row[x.name]))])))));
}
export function titleBlock(kicker, title, detail) {
  return el('header', {class:'title'}, el('span', {class:'kicker'}, kicker), el('h1', {}, title),
    el('p', {class:'intro'}, detail));
}
