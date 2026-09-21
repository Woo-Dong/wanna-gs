import { catalogContext } from './catalog';
type History=ReadonlyArray<{role:'user'|'assistant';content:string}>;
export const normalizeCatalogText=(text:string)=>text.normalize('NFKC').toLocaleLowerCase('ko').replace(/[^\p{L}\p{N}]/gu,'');
const grams=(text:string)=>new Set(Array.from({length:Math.max(0,text.length-1)},(_,index)=>text.slice(index,index+2)));
function similarity(left:string,right:string){const a=grams(left),b=grams(right);return a.size&&b.size?2*[...a].filter(value=>b.has(value)).length/(a.size+b.size):0}
/** Only complete catalog-name evidence narrows the set; fuzzy evidence only orders it. */
export function retrieveCatalog(text:string,history:History=[]){
 const query=normalizeCatalogText(text),prior=normalizeCatalogText(history.slice(-4).map(h=>h.content).join(' '));
 const ranked=catalogContext.map(product=>{
  const names=[product.name,...product.aliases].map(normalizeCatalogText);
  const literal=Math.max(0,...names.filter(name=>name.length>=3&&query.includes(name)).map(name=>name.length));
  const relevance=Math.max(...names.map(name=>similarity(query,name)))+.3*Math.max(...names.map(name=>similarity(prior,name)));
  return {product,score:literal?100+literal:relevance,literal:Boolean(literal),names};
 }).sort((a,b)=>b.score-a.score||a.product.id.localeCompare(b.product.id));
 const exactNameIds=ranked.filter(row=>row.literal).map(row=>row.product.id);
 // A name inside a rejection, comparison, allergy question, or new condition is
 // not evidence that unrelated products can be removed. Narrow only an ordinary
 // affirmative single-name lookup; unfamiliar phrasing retains full recall.
 let residual=query;
 if(exactNameIds.length===1){const named=ranked.find(row=>row.literal)!;for(const name of [...named.names].sort((a,b)=>b.length-a.length))if(name.length>=3)residual=residual.replaceAll(name,'')}
 const plainLookup=exactNameIds.length===1&&residual.replace(/(?:찾고있습니다|찾고있어요|찾아주세요|찾아줘|구해주세요|부탁해요|원합니다|원해요|있나요|있어요|주세요|제품|상품|혹시|한개|하나|을|를|좀)/g,'').replace(/\d+(?:봉지|개|팩|봉|병|캔)/g,'')==='';
 const selected=plainLookup?ranked.slice(0,24):ranked;
 const selectedIds=new Set(selected.map(row=>row.product.id));
 // A correction can refer to any previously shown SKU, including alternatives.
 const previous=ranked.filter(row=>!selectedIds.has(row.product.id)&&history.some(h=>h.content.includes(row.product.id)));
 return {catalog:[...selected,...previous].map(row=>row.product),fullCatalog:ranked.map(row=>row.product),matchingHints:{exactNameIds,scope:plainLookup?'literal-name-with-related-and-history':'complete-catalog-ranked',note:'Name mentions are retrieval evidence, not consent or proof that additional conditions are met.'}};
}
