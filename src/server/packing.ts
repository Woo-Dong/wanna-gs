import { catalogContext } from './catalog';
const fields=['id','name','brand','category','size','flavor','aliases','observed'] as const;
const refs=new Map(catalogContext.map((p,i)=>[p.id,`p${i}`]));
const ids=new Map([...refs].map(([id,ref])=>[ref,id]));
const reference=(id:string)=>refs.get(id)??id;
// Only schema-defined identifiers are remapped; free user prose is never rewritten.
function identifiers(value:unknown):unknown{
 if(Array.isArray(value))return value.map(identifiers);
 if(!value||typeof value!=='object')return value;
 return Object.fromEntries(Object.entries(value).map(([key,v])=>[key,
  (key==='id'||key==='sku')&&typeof v==='string'?reference(v):
  key==='excludeProductIds'&&Array.isArray(v)?v.map(x=>typeof x==='string'?reference(x):x):identifiers(v)]));
}
export function packCatalog(catalog:typeof catalogContext){
 return {columns:fields,rows:catalog.map(p=>fields.map(f=>f==='id'?reference(p.id):p[f]))};
}
export function packContext(context:unknown){return identifiers(context)}
export function packHistory(history:{role:'user'|'assistant';content:string}[]){
 return history.map(turn=>{
  if(turn.role==='user')return turn;
  try{return {...turn,content:JSON.stringify(identifiers(JSON.parse(turn.content)))}}catch{return turn}
 });
}
export function packIds(values:string[]){return values.map(reference)}
export function unpackResult(role:'customer'|'merchant',value:unknown):unknown{
 if(!value||typeof value!=='object')return value;
 const out=structuredClone(value) as Record<string,unknown>;
 const resolve=(ref:unknown)=>typeof ref==='string'?(ids.get(ref)??ref):ref;
 if(role==='customer'&&Array.isArray(out.candidates))out.candidates=out.candidates.map(candidate=>candidate&&typeof candidate==='object'?{...candidate,id:resolve(candidate.id)}:candidate);
 if(role==='merchant'&&out.constraints&&typeof out.constraints==='object'){
  const c=out.constraints as Record<string,unknown>;
  if(Array.isArray(c.excludeProductIds))c.excludeProductIds=c.excludeProductIds.map(resolve);
 }
 return out;
}
export function literalSkuReferences(text:string,history:{role:'user'|'assistant';content:string}[]){
 const userText=[text,...history.filter(t=>t.role==='user').map(t=>t.content)].join('\n');
 return [...refs].filter(([sku])=>userText.includes(sku)).map(([sku,ref])=>({sku,ref}));
}
