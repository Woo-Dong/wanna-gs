/** A sufficient syntactic certificate, never a general Korean intent classifier.
 * null preserves the ordinary model schema. This module never edits model output.
 */
export interface GroundingProduct { id:string; name:string; category?:string }
export interface SkuOnlyExclusionCertificate {
  onlySkuExclusions:true;
  exactSkuIds:string[];
  normalizedText:string;
  /** Product spans in normalizedText (UTF-16 offsets), not offsets in raw input. */
  consumedSpans:Array<{start:number;end:number;sku:string;matchedText:string}>;
}
const normalize=(value:string)=>value.normalize('NFKC').replace(/\s+/gu,' ').trim().toLocaleLowerCase('ko');
const escape=(value:string)=>value.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
const markerStart='\uE000',markerEnd='\uE001';
const token=`${markerStart}\\d+${markerEnd}`;
const ending='(?:해\\s*주세요|해\\s*줘(?:요)?|해요|합니다|하고|해|요)';
const exclusion=new RegExp(`^(?<targets>${token}(?:\\s*(?:와|과|및|,|하고)\\s*${token})*)\\s*(?:은|는|을|를|만|도)?\\s*(?:제외(?:\\s*조건을\\s*적용)?(?:${ending})?|빼\\s*(?:주세요|줘(?:요)?|고|요))`,'u');
const money='(?:\\d+(?:,\\d{3})*(?:만|천)?|[일이삼사오육칠팔구십백천]+만)\\s*원';
const limit=`(?:제한(?:${ending})?|바꿔\\s*제안해\\s*주세요)`;
const budget=new RegExp(`^예산\\s*(?:은|을)?\\s*${money}\\s*(?:이하(?:로)?|으로|로)?\\s*(?:${limit})?`,'u');
const quantity=new RegExp(`^(?:최대\\s*수량|수량)\\s*(?:은|을|도)?\\s*\\d+\\s*개\\s*(?:이하(?:로)?|으로|로)?\\s*${limit}`,'u');
const preserveOthers=/^다른 상품은 그대로(?: 검토할게요| 둬 주세요| 유지해 주세요)/u;

export function certifySkuOnlyExclusions(
  text:string,
  catalog:readonly GroundingProduct[],
  knownStoreNames:readonly string[]=[],
):SkuOnlyExclusionCertificate|null {
  const input=normalize(text);
  // Quotation attribution and injected internal markers are outside this grammar.
  if(!input||/["'“”‘’「」『』`\uE000\uE001]/u.test(input))return null;
  const categories=new Set(catalog.flatMap(p=>p.category?[p.category,...p.category.split(/[·/]/u)].map(normalize):[]));
  const entities=new Map<string,Set<string>>();
  for(const product of catalog){
    for(const candidate of [product.id,product.name]){
      const name=normalize(candidate);
      // Bare category names never prove a singular SKU, even in a unique catalog.
      if(!name||categories.has(name))continue;
      const ids=entities.get(name)??new Set<string>();ids.add(product.id);entities.set(name,ids);
    }
  }
  const matches:Array<{start:number;end:number;sku:string;matchedText:string}>=[];
  for(const [name,ids]of entities){
    let from=0;
    for(;;){
      const start=input.indexOf(name,from);if(start<0)break;from=start+1;
      // Do not recognize a name embedded inside another word or brand.
      if(start>0&&!/[\s,.;!]/u.test(input[start-1]))continue;
      if(ids.size!==1)return null;
      matches.push({start,end:start+name.length,sku:[...ids][0],matchedText:name});
    }
  }
  matches.sort((a,b)=>a.start-b.start||b.end-a.end);
  const spans:typeof matches=[];
  for(const match of matches){
    const prior=spans.at(-1);
    if(prior&&match.start<prior.end){
      if(match.end<=prior.end)continue; // Longest complete variant is one atom.
      return null;
    }
    spans.push(match);
  }
  if(!spans.length)return null;
  let parsed='',position=0;
  for(const [index,span]of spans.entries()){
    parsed+=input.slice(position,span.start)+markerStart+index+markerEnd;position=span.end;
  }
  parsed+=input.slice(position);
  const stores=[...new Set(knownStoreNames.map(normalize).filter(Boolean))].sort((a,b)=>b.length-a.length);
  const store=stores.length?`(?:(?:${stores.map(escape).join('|')})\\s+)?`:'';
  const current=new RegExp(`^이번\\s+(?:${store}(?:발주안|검토안|묶음)(?:에서|에만|에는|만|은|을)?\\s+)?`,'u');
  const future=/^앞으로(?:의)?\s+(?:(?:자동발주\s+)?정책(?:에|에는|으로)?\s+(?:계속\s+)?)?/u;
  // Scope is only consumed at the start. Referent-copy/undo/history is not parsed.
  const prefix=current.exec(parsed)??future.exec(parsed);
  if(prefix)parsed=parsed.slice(prefix[0].length);
  const used=new Set<number>();let clauses=0;
  while(parsed.length){
    const match=exclusion.exec(parsed)??budget.exec(parsed)??quantity.exec(parsed)??preserveOthers.exec(parsed);
    if(!match)return null;
    if(match.groups?.targets){
      const indices=match.groups.targets.matchAll(new RegExp(`${markerStart}(\\d+)${markerEnd}`,'gu'));
      for(const index of indices)used.add(Number(index[1]));
    }
    clauses++;parsed=parsed.slice(match[0].length).trimStart();
    // Separators connect already-proven clauses; no arbitrary prose is discarded.
    const separator=/^(?:[,.;!]\s*|그리고\s+|및\s+|또\s+)*/u.exec(parsed)![0];
    parsed=parsed.slice(separator.length).trimStart();
  }
  if(!clauses||used.size!==spans.length)return null;
  return {onlySkuExclusions:true,exactSkuIds:[...new Set(spans.map(span=>span.sku))],normalizedText:input,consumedSpans:spans};
}
