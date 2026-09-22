import type { CustomerInterpretation } from '../contracts/assistant';
type Candidate=CustomerInterpretation['candidates'][number];
export type CustomerWireCandidate={id:string;assessment:Omit<Candidate,'id'>};
type Common={reason:string;confirmationRequired:true};
export type CustomerWire={decision:Common&(
 | {action:'show_candidates';primaryCandidate:CustomerWireCandidate;additionalCandidates:CustomerWireCandidate[];question:null}
 | {action:'ask_clarification';candidates:CustomerWireCandidate[];question:string}
 | {action:'unidentified';candidates:CustomerWireCandidate[];question:null}
)};
/** Called only after the supplied-catalog wire schema succeeds. No field correction. */
export function canonicalCustomer(wire:CustomerWire):CustomerInterpretation{
 const d=wire.decision;
 const candidates=d.action==='show_candidates'?[d.primaryCandidate,...d.additionalCandidates]:d.candidates;
 return {action:d.action,candidates:candidates.map(c=>({id:c.id,...c.assessment})),question:d.question,reason:d.reason,confirmationRequired:d.confirmationRequired};
}
