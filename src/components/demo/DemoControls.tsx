'use client';

import { useRef, useState } from 'react';
import type { Condition, DemoClient, DemoCommand, DemoSnapshot, CommandContext } from '../../contracts/domain';
import { loadDemoScenario, type DemoScenario } from '../../demo/scenarios';
import styles from './demo.module.css';

export interface DemoControlsProps {
  snapshot: DemoSnapshot;
  client: DemoClient;
  onSnapshot: (snapshot: DemoSnapshot) => void;
}
type Pending = { command: DemoCommand; context: CommandContext; message: string };
type ConditionDraft = {
  sku: string; storeId: string; version: number; price: string; cost: string;
  capacity: string; minimum: string; multiple: string; supply: Condition['supplyStatus'];
};
const hour = 3_600_000;
const maximumJump = 30 * 24 * hour;
const scenarios: { value: DemoScenario; label: string; detail: string }[] = [
  { value: 'normal', label: '정상 요청 · 발주 검토부터', detail: '고객 요청과 발주 초안을 준비합니다. 경영주가 직접 승인하며 정상 흐름을 이어갈 수 있어요.' },
  { value: 'minimum', label: '최소 발주 수량 미달', detail: '최소 6개가 필요한 상품에 1개 요청을 남깁니다. 요청은 보존되고 초과 발주는 하지 않아요.' },
  { value: 'shortage', label: '공급 부족 · 전량 대기', detail: '3개 요청에 2개만 확보합니다. 앞선 고객의 전량을 확보할 때까지 기다려요.' },
  { value: 'paymentFailure', label: '모의 결제 실패 · 재시도', detail: '최초 결제를 실패로 준비합니다. 고객이 기한 안에 명시적으로 다시 시도하면 성공해요.' },
  { value: 'pickupReady', label: '입고 완료 · 픽업 가능', detail: '모의 결제와 입고를 마치고 픽업 알림과 48시간 마감을 준비합니다.' },
  { value: 'pickupExpired', label: '픽업 기한 종료', detail: '픽업 알림 이후 48시간을 이동해 수령이 차단되는 상태를 준비합니다.' },
];
function scopeOf(s: DemoSnapshot) {
  return { sessionId: s.session.id, generation: s.session.generation, actorId: s.actor.id, roleEpoch: s.roleEpoch };
}
function sameScope(a: CommandContext, s: DemoSnapshot) {
  const b = scopeOf(s);
  return a.sessionId === b.sessionId && a.generation === b.generation && a.actorId === b.actorId && a.roleEpoch === b.roleEpoch;
}
function date(ms: number) {
  return new Intl.DateTimeFormat('ko-KR', { timeZone: 'Asia/Seoul', dateStyle: 'medium', timeStyle: 'medium' }).format(ms);
}
function inputDate(ms: number) { return new Date(ms + 9 * hour).toISOString().slice(0, 23); }
function number(text: string, minimum = 0) {
  if (!/^\d+$/.test(text)) return null;
  const value = Number(text);
  return Number.isSafeInteger(value) && value >= minimum ? value : null;
}
function messageFor(code: string, fallback: string) {
  const messages: Record<string, string> = {
    VERSION_CONFLICT: '편집 중 상품 조건이 바뀌었습니다. 입력은 보존했어요. 최신 조건을 가져와 다시 확인해 주세요.',
    STALE_GENERATION: '시연이 새로 시작되어 이전 작업을 적용하지 않았습니다. 현재 상태에서 다시 선택해 주세요.',
    STALE_ROLE: '역할이 바뀌어 이전 작업을 적용하지 않았습니다. 현재 경영주 화면에서 다시 확인해 주세요.',
    FORBIDDEN: '현재 점포의 경영주 역할에서만 시연 조건을 바꿀 수 있어요.',
    PERSISTENCE_FAILED: '변경을 저장하지 못했습니다. 마지막 저장 상태를 확인한 뒤 같은 작업을 다시 시도해 주세요.',
  };
  return messages[code] ?? fallback;
}

export function DemoControls({ snapshot, client, onSnapshot }: DemoControlsProps) {
  const live = useRef(snapshot); live.current = snapshot;
  const lock = useRef(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [pending, setPending] = useState<Pending | null>(null);
  const [scenario, setScenario] = useState<DemoScenario>('normal');
  const [resetConfirmed, setResetConfirmed] = useState(false);
  const [scenarioConfirmed, setScenarioConfirmed] = useState(false);
  const [targetTime, setTargetTime] = useState('');
  const [customerId, setCustomerId] = useState('');
  const [paymentOutcome, setPaymentOutcome] = useState<'once' | 'twice'>('once');
  const [draft, setDraft] = useState<ConditionDraft | null>(null);
  const [conditionConfirmed, setConditionConfirmed] = useState(false);
  const merchant = snapshot.actor.role === 'merchant';
  const storeId = snapshot.actor.storeId;
  const store = snapshot.stores.find(s => s.id === storeId);
  const writable = merchant && snapshot.persistence.status === 'ready';
  const disabled = !writable || busy || !!pending;
  const conditions = snapshot.conditions.filter(c => c.storeId === storeId);
  const currentCondition = draft && draft.storeId === storeId ? conditions.find(c => c.sku === draft.sku) : undefined;
  const staleDraft = !!currentCondition && currentCondition.version !== draft?.version;
  const preset = scenarios.find(s => s.value === scenario)!;
  const deadlines = snapshot.requests.filter(r => r.reservation?.pickupDeadlineAt != null);

  function accept(next: DemoSnapshot) { live.current = next; onSnapshot(next); }
  async function perform(command: DemoCommand, successMessage: string, previous?: Pending) {
    if (lock.current || !writable || (pending && !previous)) return;
    lock.current = true; setBusy(true); setError(''); setNotice('');
    const commandId = previous?.context.commandId ?? crypto.randomUUID();
    const context = previous?.context ?? { ...scopeOf(live.current), commandId, correlationId: commandId };
    const job = previous ?? { command, context, message: successMessage };
    try {
      const result = await client.dispatch(job.command, job.context);
      if (result.ok) {
        accept(result.data.snapshot); setPending(null); setNotice(job.message);
        setResetConfirmed(false); setConditionConfirmed(false);
      } else {
        setError(messageFor(result.error.code, result.error.message));
        setPending(result.error.retryable ? job : null);
        const state = await client.snapshot(scopeOf(live.current));
        if (state.ok) accept(state.data);
      }
    } catch {
      setError('처리 결과를 확인하지 못했습니다. 같은 작업으로 다시 확인해 주세요.'); setPending(job);
    } finally { lock.current = false; setBusy(false); }
  }
  function selectCondition(sku: string) {
    const c = conditions.find(c => c.sku === sku);
    if (!c) { setDraft(null); return; }
    setDraft({ sku, storeId: c.storeId, version: c.version, price: String(c.salePriceKrw), cost: String(c.purchaseCostKrw), capacity: String(c.availableOrderQty), minimum: String(c.minimumOrderQty), multiple: String(c.orderMultiple), supply: c.supplyStatus });
    setConditionConfirmed(false); setError('');
  }
  function edit<K extends keyof ConditionDraft>(key: K, value: ConditionDraft[K]) {
    if (draft) setDraft({ ...draft, [key]: value });
    setConditionConfirmed(false);
  }
  function applyCondition() {
    if (!draft || draft.storeId !== storeId || !conditionConfirmed) return;
    const price = number(draft.price), cost = number(draft.cost, 1), capacity = number(draft.capacity), minimum = number(draft.minimum, 1), multiple = number(draft.multiple, 1);
    if (price === null || cost === null || capacity === null || minimum === null || multiple === null) { setError('금액과 수량은 정수로 입력해 주세요. 최소 수량·배수·매입가는 1 이상이어야 합니다.'); return; }
    void perform({ type: 'demo.updateCondition', storeId: draft.storeId, sku: draft.sku, expectedConditionVersion: draft.version, patch: { salePriceKrw: price, purchaseCostKrw: cost, availableOrderQty: capacity, minimumOrderQty: minimum, orderMultiple: multiple, supplyStatus: draft.supply, reason: draft.supply === 'discontinued' ? '모의 공급 종료' : draft.supply === 'restricted' ? '모의 공급 제한' : null } }, '모의 상품 조건을 저장했습니다. 현재 수요와 자동발주 정책을 다시 확인했어요.');
  }
  function jumpToTarget() {
    const target = Date.parse(`${targetTime}+09:00`);
    const deltaMs = Math.trunc(target - live.current.clock.now);
    if (!targetTime || !Number.isFinite(target) || deltaMs <= 0 || deltaMs > maximumJump) { setError('현재 데모 시각 이후, 30일 이내의 시각을 입력해 주세요.'); return; }
    void perform({ type: 'demo.advanceTime', deltaMs }, `지정 시각 ${date(target)}을 기준으로 시간을 이동했습니다. 실제 처리 시각과 기한 상태를 확인해 주세요.`);
  }
  async function prepareScenario() {
    if (lock.current || disabled || !scenarioConfirmed) return;
    lock.current = true; setBusy(true); setError(''); setNotice('');
    const progressClient: DemoClient = {
      initialize: () => client.initialize(), snapshot: scope => client.snapshot(scope), query: (query, scope) => client.query(query, scope), subscribe: listener => client.subscribe(listener),
      async dispatch(command, context) { const result = await client.dispatch(command, context); if (result.ok) accept(result.data.snapshot); return result; },
      async switchRole(actor, scope) { const result = await client.switchRole(actor, scope); if (result.ok) accept(result.data); return result; },
    };
    try {
      const result = await loadDemoScenario(progressClient, live.current, scenario, true);
      if (result.ok) { accept(result.data); setNotice(`${preset.label} 시나리오를 준비했습니다. 합성 요청과 모의 거래예요.`); setScenarioConfirmed(false); setDraft(null); }
      else setError(`${messageFor(result.error.code, result.error.message)} 이미 준비된 단계는 화면에 남아 있습니다. 현재 상태를 확인해 주세요.`);
    } catch { setError('시나리오 준비가 중단됐습니다. 화면의 현재 상태를 확인해 주세요.'); }
    finally { lock.current = false; setBusy(false); }
  }

  return <details className={styles.panel}>
    <summary>시연 도구 <span>모의 조건·시간 조절</span></summary>
    <div className={styles.body} aria-busy={busy}>
      <p className={styles.intro}>점포 위치와 상품 이름은 참고 자료이며, 가격·재고·발주·결제는 모두 모의 데이터입니다. 실제 청구는 없어요. 아래 시나리오는 준비된 합성 사례이며 AI 검색 결과를 대신하지 않습니다.</p>
      <p className={styles.meta}>현재 시연: {snapshot.session.id}<br />{store ? `조정할 점포: ${store.name}` : '현재 고객 역할'} · 데모 시각 {date(snapshot.clock.now)} (한국 시간)</p>
      {!merchant && <p className={styles.hint}>시연 조건을 바꾸려면 경영주 역할로 전환해 주세요. 고객 요청 화면에서는 조건을 변경하지 않습니다.</p>}
      {snapshot.persistence.status !== 'ready' && <p className={styles.error}>저장소를 복구한 뒤 시연 도구를 사용할 수 있어요.</p>}
      {error && <p className={styles.error} role="alert">{error}</p>}
      {notice && <p className={styles.notice} role="status">{notice}</p>}
      {busy && <p role="status">변경을 저장하고 있습니다…</p>}
      {pending && <div className={styles.hint}>
        <p>결과가 불확실한 작업은 새로 실행하지 않고 같은 작업으로 확인합니다.</p>
        <button type="button" disabled={busy || !writable || !sameScope(pending.context, snapshot)} onClick={() => void perform(pending.command, pending.message, pending)}>같은 작업 다시 확인</button>
        {!sameScope(pending.context, snapshot) && <button type="button" disabled={busy} onClick={() => { setPending(null); setError('이전 작업의 재시도를 닫았습니다. 해당 역할의 내역에서 처리 결과를 확인해 주세요.'); }}>이전 작업 확인 닫기</button>}
      </div>}
      <fieldset disabled={disabled} className={styles.section}>
        <legend>준비된 시나리오</legend>
        <label>시연할 상황<select value={scenario} onChange={e => { setScenario(e.target.value as DemoScenario); setScenarioConfirmed(false); }}>{scenarios.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}</select></label>
        <p>{preset.detail}</p>
        <label className={styles.check}><input type="checkbox" checked={scenarioConfirmed} onChange={e => setScenarioConfirmed(e.target.checked)} />현재 시연의 요청·거래·시간을 초기화하고 합성 사례를 준비합니다.</label>
        <button type="button" disabled={disabled || !scenarioConfirmed} onClick={() => void prepareScenario()}>선택한 시나리오로 다시 시작</button>
      </fieldset>
      <fieldset disabled={disabled} className={styles.section}>
        <legend>데모 시간</legend>
        <p>시간은 앞으로만 이동합니다. 동의 유효기간과 결제 대기, 픽업 마감을 함께 확인해요.</p>
        <div className={styles.buttons}>{[1, 24, 48].map(h => <button type="button" key={h} onClick={() => void perform({ type: 'demo.advanceTime', deltaMs: h * hour }, `데모 시간을 ${h}시간 이동했습니다.`)}>+{h}시간</button>)}</div>
        <label>확인할 시각 (한국 시간, 최대 30일)<input type="datetime-local" step="0.001" value={targetTime} onChange={e => setTargetTime(e.target.value)} /></label>
        {deadlines.length > 0 && <label>예약의 픽업 마감 가져오기<select value="" onChange={e => { if (e.target.value) setTargetTime(inputDate(Number(e.target.value))); }}><option value="">예약 선택</option>{deadlines.map(r => <option key={r.id} value={r.reservation!.pickupDeadlineAt!}>{r.displayName} · {snapshot.products.find(p => p.sku === r.sku)?.name} · {date(r.reservation!.pickupDeadlineAt!)}</option>)}</select></label>}
        <button type="button" disabled={disabled || !targetTime} onClick={jumpToTarget}>지정 시각으로 이동해 기한 확인</button>
        <p className={styles.meta}>처리 시각이 마감 이상이면 수령할 수 없습니다. 시간 이동 후 표시된 실제 처리 시각으로 결과를 확인하세요.</p>
      </fieldset>
      <fieldset disabled={disabled} className={styles.section}>
        <legend>다음 모의 결제 결과</legend>
        <label>합성 고객<select value={customerId} onChange={e => setCustomerId(e.target.value)}><option value="">고객 선택</option>{snapshot.actors.filter(a => a.role === 'customer').map(a => <option key={a.id} value={a.id}>{a.displayName}</option>)}</select></label>
        <label>실패 시연<select value={paymentOutcome} onChange={e => setPaymentOutcome(e.target.value as 'once' | 'twice')}><option value="once">최초 실패 · 고객 재시도는 성공</option><option value="twice">최초와 고객 재시도 모두 실패</option></select></label>
        <p>이미 끝난 결제는 바꾸지 않습니다. 선택한 고객의 다음 모의 결제부터 적용해요.</p>
        <button type="button" disabled={disabled || !customerId} onClick={() => void perform({ type: 'demo.setPaymentOutcome', actorId: customerId, outcomes: paymentOutcome === 'once' ? ['failure', 'success'] : ['failure', 'failure'] }, '선택한 고객의 다음 모의 결제 결과를 설정했습니다.')}>다음 결제 실패 설정</button>
      </fieldset>
      <fieldset disabled={disabled} className={styles.section}>
        <legend>현재 점포의 모의 상품 조건</legend>
        <label>상품<select value={draft?.storeId === storeId ? draft.sku : ''} onChange={e => selectCondition(e.target.value)}><option value="">상품 선택</option>{conditions.map(c => <option key={c.sku} value={c.sku}>{snapshot.products.find(p => p.sku === c.sku)?.name ?? c.sku}</option>)}</select></label>
        {draft && draft.storeId === storeId && <>
          <div className={styles.grid}>
            <label>판매가 (원)<input inputMode="numeric" value={draft.price} onChange={e => edit('price', e.target.value)} /></label>
            <label>매입가 (원)<input inputMode="numeric" value={draft.cost} onChange={e => edit('cost', e.target.value)} /></label>
            <label>추가 발주 가능 수량<input inputMode="numeric" value={draft.capacity} onChange={e => edit('capacity', e.target.value)} /></label>
            <label>최소 발주 수량<input inputMode="numeric" value={draft.minimum} onChange={e => edit('minimum', e.target.value)} /></label>
            <label>발주 묶음 단위<input inputMode="numeric" value={draft.multiple} onChange={e => edit('multiple', e.target.value)} /></label>
            <label>모의 공급 상태<select value={draft.supply} onChange={e => edit('supply', e.target.value as Condition['supplyStatus'])}><option value="available">공급 가능</option><option value="restricted">공급 제한</option><option value="discontinued">공급 종료</option><option value="unknown">미확인</option></select></label>
          </div>
          <p>추가 발주 가능 수량은 새 절대값입니다. 점포 재고나 이미 확보한 물량과는 달라요. 가격 변경 시 고객 재동의가 필요하며, 활성 자동발주 정책은 변경 조건을 다시 검토합니다.</p>
          {staleDraft && <p className={styles.hint}>편집을 시작한 뒤 상품 조건이 바뀌었습니다. 이전 기준의 변경은 저장되지 않아요.</p>}
          <button type="button" onClick={() => selectCondition(draft.sku)}>최신 조건 가져오기 · 입력 교체</button>
          <label className={styles.check}><input type="checkbox" checked={conditionConfirmed} onChange={e => setConditionConfirmed(e.target.checked)} />변경할 모의 가격·수량·공급 상태를 확인했습니다.</label>
          <button type="button" disabled={disabled || !conditionConfirmed} onClick={applyCondition}>모의 상품 조건 변경</button>
        </>}
      </fieldset>
      <fieldset disabled={disabled} className={styles.section}>
        <legend>현재 시연 초기화</legend>
        <p>현재 시연의 요청·거래·시간·모의 조건을 처음 상태로 되돌립니다.</p>
        <label className={styles.check}><input type="checkbox" checked={resetConfirmed} onChange={e => setResetConfirmed(e.target.checked)} />현재 시연을 초기화할게요.</label>
        <button type="button" className={styles.reset} disabled={disabled || !resetConfirmed} onClick={() => void perform({ type: 'demo.reset', confirmed: true }, '현재 시연을 초기화했습니다.')}>현재 시연 초기화</button>
      </fieldset>
    </div>
  </details>;
}
