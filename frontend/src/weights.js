import {el} from './dom.js';
import {status} from './widgets.js';

export const kilograms = grams => (grams / 1000).toFixed(3) + ' kg';

export function input(name, label, properties = {}) {
  return el('label', {}, el('span', {}, label), el('input', {name, required: '', ...properties}));
}

export function select(name, label, options) {
  return el('label', {}, el('span', {}, label), el('select', {name, required: ''},
    options.map(([value, text]) => el('option', {value}, text))));
}

export function actionForm(id, children, label, success) {
  const notice = status('');
  const button = el('button', {type: 'submit'}, label);
  const form = el('form', {id}, children, button, notice);
  form.addEventListener('submit', async event => {
    event.preventDefault();
    notice.textContent = '';
    button.disabled = true;
    try {
      const result = await success(new FormData(form));
      notice.className = 'status ok';
      notice.textContent = result || '';
    } catch (error) {
      notice.className = 'status error';
      notice.textContent = error.message;
    } finally { button.disabled = false; }
  });
  return form;
}

export function numbers(values, keys) {
  return Object.fromEntries(keys.map(key => [key, Number(values.get(key))]));
}

export function mayWrite(role) {
  return ['operator', 'reviewer'].includes(role);
}
