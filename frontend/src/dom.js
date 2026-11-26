export function el(tag, props = {}, ...children) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(props)) {
    if (key === 'class') node.className = value;
    else if (key.startsWith('on')) node.addEventListener(key.slice(2), value);
    else if (value !== undefined) node.setAttribute(key, value);
  }
  node.append(...children.flat().filter(x => x !== null && x !== undefined));
  return node;
}

export function display(value) {
  if (value === null || value === undefined || value === '') return '—';
  if (typeof value === 'boolean') return value ? '是' : '否';
  if (Array.isArray(value)) return value.map(display).join(' · ');
  if (typeof value === 'object') return Object.entries(value).map(([key, val]) => key + ' ' + display(val)).join(' / ');
  return String(value);
}
