import {request} from './api.js';
import {el} from './dom.js';
import {ROLES, setSession} from './store.js';
import {status, titleBlock} from './widgets.js';

export function login(root, info, done) {
  const notice = status('');
  const selector = el('select',{name:'role'},Object.entries(ROLES).map(([role,label]) =>
    el('option',{value:role},label)));
  const button = el('button',{type:'submit'},'进入工作台');
  const form = el('form',{class:'login',id:'login'},
    el('label',{},'演示角色', selector),
    el('label',{},'演示密码', el('input',{name:'password',type:'password',value:'DemoC0de!2026',required:''})),
    button,notice);
  root.replaceChildren(el('main',{class:'welcome'},titleBlock(info.customer,info.title,info.purpose),form));
  form.addEventListener('submit',async e => {
    e.preventDefault();
    button.disabled = true;
    try {
      setSession(await request('/auth/login',{email:selector.value+'@demo.test',password:form.password.value}));
      done();
    } catch (error) {
      notice.textContent = error.message;
      notice.classList.add('error');
    } finally { button.disabled = false; }
  });
}
