import type { z } from 'zod';
import { customerInputSchema,customerOutputSchema,merchantInputSchema,merchantOutputSchema,modelOutputSchema } from './schemas';
import { catalogContext,catalogHash,catalogVersion,categories,productById } from './catalog';
import { retrieveCatalog } from './retrieval';
import { packCatalog,packContext,packHistory,packIds,unpackResult,literalSkuReferences } from './packing';
import { CUSTOMER_PROMPT,MERCHANT_PROMPT,PROMPT_VERSION } from './prompts';
import { AssistantError,liveProvider,type ModelProvider } from './provider';
import type { AssistantEnvelope,CustomerInterpretation,MerchantInterpretation,AssistantResponse } from '../contracts/assistant';
const invalid=(diagnostic='OUTPUT_CONTRACT')=>Object.assign(new AssistantError('INVALID_MODEL_RESPONSE','응답에 확인할 수 없는 내용이 있어요. 다시 시도해 주세요.',true,502),{diagnostic});
export function verifyCustomer(value:unknown,clarificationCount:number):CustomerInterpretation{
 const parsed=customerOutputSchema.safeParse(value);if(!parsed.success)throw invalid('OUTPUT_SCHEMA');const out=parsed.data;
 if(out.candidates.length>6)throw invalid('CANDIDATE_LIMIT');
 if(new Set(out.candidates.map(c=>c.id)).size!==out.candidates.length)throw invalid('CANDIDATE_DUPLICATE');
 if(out.candidates.some(c=>!productById.has(c.id)))throw invalid('CANDIDATE_UNKNOWN_ID');
 if(out.candidates.some(c=>[...c.sharedEvidence,...c.differences,...c.unknownConditions].some(x=>x.length>300))||out.reason.length>500)throw invalid('OUTPUT_TEXT_LIMIT');
 const primary=out.candidates.filter(c=>c.kind!=='alternative');
 if(out.action==='show_candidates'&&(!primary.length||out.question!==null))throw invalid('CANDIDATE_ACTION_CONTRACT');
 if(out.action==='unidentified'&&(primary.length||out.question!==null))throw invalid('UNIDENTIFIED_ACTION_CONTRACT');
 if(out.action==='ask_clarification'&&(!out.question?.trim()||clarificationCount>=2||out.question.length>300))throw invalid('CLARIFICATION_CONTRACT');
 if(out.candidates.some(c=>c.kind==='exact'&&c.unknownConditions.length))throw invalid('EXACT_WITH_UNKNOWN_CONDITION');
 return out;
}
export function verifyMerchant(value:unknown):MerchantInterpretation{
 const parsed=merchantOutputSchema.safeParse(value);if(!parsed.success)throw invalid();const out=parsed.data,c=out.constraints;
 if(c.excludeProductIds.some(id=>!productById.has(id))||c.excludeCategories.some(category=>!categories.includes(category))||new Set(c.excludeProductIds).size!==c.excludeProductIds.length||new Set(c.excludeCategories).size!==c.excludeCategories.length||out.reason.length>500)throw invalid();
 const empty=c.budgetLimitKrw===null&&!c.excludeCategories.length&&!c.excludeProductIds.length&&c.maxQuantity===null&&!c.restorePrevious;
 if(out.intent==='clarify'&&(out.scope!==null||!out.question?.trim()||!empty))throw invalid();
 if(out.intent!=='clarify'&&(!out.scope||out.question!==null))throw invalid();
 if(out.intent==='restore'&&(out.scope!=='current_proposal'||!c.restorePrevious||c.budgetLimitKrw!==null||c.excludeCategories.length||c.excludeProductIds.length||c.maxQuantity!==null))throw invalid();
 if(out.intent==='modify'&&(c.restorePrevious||empty))throw invalid();
 return out;
}
export async function interpret(role:'customer'|'merchant',body:unknown,provider:ModelProvider=liveProvider,mode:'live'|'fixture'='live'):Promise<AssistantResponse<CustomerInterpretation|MerchantInterpretation>>{
 const started=Date.now();const schema=role==='customer'?customerInputSchema:merchantInputSchema;
 const parsed=schema.safeParse(body);if(!parsed.success)throw new AssistantError('INVALID_INPUT','입력 형식을 확인해 주세요.',false,400);
 const request=parsed.data;
 if(request.catalogHash!==catalogHash)throw new AssistantError('CATALOG_MISMATCH','상품 목록이 바뀌었어요. 진행 중인 내용을 확인하고 새로고침해 주세요.',false,409);
 if('state' in request&&request.state.groups.some(g=>!productById.has(g.sku)))throw new AssistantError('INVALID_INPUT','상품 목록에 없는 묶음이 포함되어 있어요.',false,400);
 const {text,history,...context}=request;
 const retrieved=retrieveCatalog(text,history);
 const suppliedCatalog=role==='customer'?retrieved.catalog:retrieved.fullCatalog;
 const matchingHints=role==='customer'?retrieved.matchingHints:{...retrieved.matchingHints,scope:'complete-catalog-ranked'};
 const input=JSON.stringify({catalog:packCatalog(suppliedCatalog),literalSkuReferences:literalSkuReferences(text,history),categories,matchingHints:{...matchingHints,exactNameIds:packIds(matchingHints.exactNameIds)},context:packContext(context),history:packHistory(history),text});
 const outputSchema=modelOutputSchema(role,packIds(suppliedCatalog.map(product=>product.id)),categories);
 const response=await provider(role==='customer'?CUSTOMER_PROMPT:MERCHANT_PROMPT,input,outputSchema,role+'_interpretation');
 let result:CustomerInterpretation|MerchantInterpretation;
 try{
  if(!outputSchema.safeParse(response.value).success)throw invalid('SUPPLIED_CATALOG_SCHEMA');
  const unpacked=unpackResult(role,response.value);
  result=role==='customer'?verifyCustomer(unpacked,'clarificationCount' in request?request.clarificationCount:0):verifyMerchant(unpacked);
  if(role==='merchant'&&'state' in request&&(result as MerchantInterpretation).intent==='restore'&&!request.state.previousConstraints)throw invalid();
 }catch(error){
  const safe=error instanceof AssistantError?error:invalid();safe.attempt={providerCalled:mode==='live',model:response.model,usage:response.usage,latencyMs:Date.now()-started,mode:'live'};throw safe;
 }
 const {sessionId,generation,actorId,roleEpoch,requestId,conversationId,inputRevision}=request;
 const envelope:AssistantEnvelope={sessionId,generation,actorId,roleEpoch,requestId,conversationId,inputRevision,catalogHash};
 const data={...envelope,mode,model:response.model,promptVersion:PROMPT_VERSION,catalogVersion,result,usage:response.usage,latencyMs:Date.now()-started};
 return {ok:true,data};
}
export async function handleAssistant(role:'customer'|'merchant',request:Request):Promise<Response>{
 let id:string|undefined;
 try{
   if(Number(request.headers.get('content-length')||0)>65536)throw new AssistantError('INVALID_INPUT','입력이 너무 길어요.',false,413);
   const text=await request.text();if(new TextEncoder().encode(text).length>65536)throw new AssistantError('INVALID_INPUT','입력이 너무 길어요.',false,413);
   let body:unknown;try{body=JSON.parse(text)}catch{throw new AssistantError('INVALID_INPUT','입력 형식을 확인해 주세요.',false,400)}
   const result=await interpret(role,body);
   if(result.ok){id=result.data.requestId;console.info(JSON.stringify({event:'assistant_run',role,requestId:id,mode:result.data.mode,model:result.data.model,promptVersion:PROMPT_VERSION,catalogHash,usage:result.data.usage,latencyMs:result.data.latencyMs,status:'ok'}))}
   return Response.json(result,{headers:{'Cache-Control':'no-store'}});
 }catch(error){
   const safe=error instanceof AssistantError?error:new AssistantError('LLM_UNAVAILABLE','처리하지 못했어요. 입력을 유지하고 다시 시도해 주세요.',true,503);
   console.info(JSON.stringify({event:'assistant_error',role,requestId:id,code:safe.code,diagnostic:safe.diagnostic,attempt:safe.attempt}));
   return Response.json({ok:false,error:{code:safe.code,diagnostic:safe.diagnostic,message:safe.publicMessage,retryable:safe.retryable,attempt:safe.attempt||{providerCalled:false,model:null,usage:null,latencyMs:0,mode:'live'}}},{status:safe.httpStatus,headers:{'Cache-Control':'no-store'}});
 }
}
