import type {MerchantInterpretation} from '../contracts/assistant';
export type MerchantWire={decision:MerchantInterpretation};
// Called only after the generated wire schema succeeds; never fill, drop or repair fields.
export function canonicalMerchant(wire:MerchantWire):MerchantInterpretation{return wire.decision}
