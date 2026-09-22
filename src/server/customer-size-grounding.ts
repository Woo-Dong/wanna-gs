type Product={id:string;name:string;brand:string;size:string|null;aliases:readonly string[]};
type History=ReadonlyArray<{role:'user'|'assistant';content:string}>;
type Quantity={dimension:'volume'|'mass';minorAmount:number;amount:number;unit:'ml'|'g'};
export type CustomerSizeCertificate=Quantity&{kind:'explicit-positive-size';eligibleIds:string[];excludedIds:string[]};
const normalize=(text:string)=>text.normalize('NFKC').toLowerCase().replace(/[^\p{L}\p{N}]/gu,'');
function quantity(number:string,unit:string):Quantity|null{
 const [whole,fraction='']=number.split('.');if(whole.length+fraction.length>12)return null;
 const coefficient=Number(whole+fraction),u=unit.toLowerCase(),scale=u==='l'||u==='kg'?1_000_000:1_000;
 const minorAmount=coefficient*(scale/10**fraction.length);if(!Number.isSafeInteger(minorAmount)||minorAmount<=0)return null;
 return {dimension:u==='ml'||u==='l'?'volume':'mass',minorAmount,amount:minorAmount/1000,unit:u==='ml'||u==='l'?'ml':'g'};
}
function singleMention(text:string):Quantity|null{
 const matches=[...text.matchAll(/(?<![\d.+-])(\d+(?:\.\d{1,3})?)\s*(ml|kg|g|l)(?![a-z\d])/gi)];
 return matches.length===1?quantity(matches[0][1],matches[0][2]):null;
}
function knownSize(text:string|null):Quantity|null{
 // Multipacks, ranges, extra quantities and unknown units are not asserted to be comparable.
 const m=text?.normalize('NFKC').match(/^\s*(\d+(?:\.\d{1,3})?)\s*(ml|kg|g|l)\s*$/i);return m?quantity(m[1],m[2]):null;
}
/** Only a fully consumed affirmative grammar certifies size. All unknown language falls back.
 * History is deliberately uncertified: earlier exclusions/corrections must remain model-visible.
 * Full input catalog and existing IDs remain intact; this only certifies an output-ID constraint.
 */
export function certifyCustomerSize(text:string,products:readonly Product[],history:History=[]):CustomerSizeCertificate|null{
 if(history.length)return null;
 const t=text.normalize('NFKC').trim();let subject:string|null=null;
 const label=t.match(/^(?:(.+?)\s+제품인데\s+)?(?:이름|상품명|제품명)에\s+(.+?)(?:가|이|라고)\s+(?:적혀|표기되어)\s+있어요[.!?]?\s*(?:이\s*상품\s*(?:후보를\s*)?(?:보여\s*주세요|찾아\s*주세요)[.!?]?)?$/);
 if(label){
  const brand=label[1],atoms=label[2].split(/\s*\/\s*/);
  if(brand&&!products.some(p=>normalize(p.brand)===normalize(brand)))return null;
  if(!atoms.every(atom=>{const a=normalize(atom);return a.length>=2&&products.some(p=>normalize(p.name).includes(a))}))return null;
  subject=label[2];
 }else{
  const lookup=t.match(/^(.+?)(?:을|를)?\s*(?:찾고\s*있어요|찾아\s*주세요|찾아줘|주세요|보여\s*주세요)[.!?]?$/);
  if(!lookup)return null;
  const name=normalize(lookup[1]);
  if(!products.some(p=>[p.name,...p.aliases].some(n=>normalize(n)===name)))return null;
  subject=lookup[1];
 }
 const wanted=singleMention(subject);if(!wanted)return null;
 const eligibleIds:string[]=[],excludedIds:string[]=[];
 for(const p of products){const size=knownSize(p.size);(size&&size.dimension===wanted.dimension&&size.minorAmount!==wanted.minorAmount?excludedIds:eligibleIds).push(p.id)}
 // Never create an empty enum or assert an ineligible candidate when no safe set is available.
 if(!eligibleIds.length||!excludedIds.length)return null;
 return {kind:'explicit-positive-size',...wanted,eligibleIds,excludedIds};
}
