import {el} from '../dom.js';

export function pill(label, type = '') {
  return el('span', {class: 'section-label ' + type, 'data-kind': type}, label);
}
