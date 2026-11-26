import {el} from '../dom.js';
import {desk} from '../mill-state.js';

export function pitch(zones, selection) {
  const box = el('div', {class: 'pitch', 'aria-label': '回填场区示意'});
  for (const zone of zones) {
    box.append(el('button', {type: 'button', 'data-zone': zone.code,
      'aria-pressed': String(zone.code === desk.selectedZone), onclick: () => {
        desk.selectedZone = zone.code;
        for (const button of box.querySelectorAll('button')) {
          button.setAttribute('aria-pressed', String(button.dataset.zone === zone.code));
        }
        selection(zone);
      }}, el('strong', {}, zone.label.split(' · ')[1]), el('small', {class: 'mono'}, zone.code)));
  }
  return box;
}
