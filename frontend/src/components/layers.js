import {el} from '../dom.js';
import {binNames} from '../mill-state.js';

export function layers(values, unit = ' g') {
  return el('div', {}, el('div', {class: 'strata', role: 'img', 'aria-label': '粒径构成'},
    values.map((value, index) => el('span', {class: 'layer-' + index, style: 'flex-grow:' + value}))),
  el('div', {class: 'binline'}, values.map((value, index) => binNames[index] + ' ' + value + unit).join(' · ')));
}
