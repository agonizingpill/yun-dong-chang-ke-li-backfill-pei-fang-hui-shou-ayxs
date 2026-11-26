export const zoneLabels = {epdm: 'EPDM', tpe: 'TPE'};
export const lotStates = {awaiting: '待筛分', eligible: '可配料', quarantined: '隔离'};
export const zeroModes = {none: '无零档', below_limit: '低于检出限', structural: '真实缺档'};
export const decisions = {passed: '筛分通过', structural_zero: '真实缺档',
  foreign_material: '杂物超限', zero_declaration: '零档声明不符'};
export const ticketStates = {reserved: '锁料待秤', weighed: '已逐行称量', released: '已扣减发料', cancelled: '已退订'};
export const movements = {reserve: '预占', return: '返还预占', consume: '扣减发料'};
export const binNames = ['细粒', '中粒', '粗粒', '杂物'];

export const desk = {selectedZone: null, activeTicket: null};
