import OpenAI from 'openai';
import { z } from 'zod';
import type { ModelUsage } from '../contracts/assistant';
export class AssistantError extends Error {
  attempt?:{providerCalled:boolean;model:string|null;usage:ModelUsage|null;latencyMs:number;mode:'live'};
  constructor(public code:string, public publicMessage:string, public retryable:boolean, public httpStatus:number){super(code)}
}
export interface ProviderResult { value:unknown; model:string; usage:ModelUsage }
export type ModelProvider=(instructions:string,input:string,schema:z.ZodType,name:string)=>Promise<ProviderResult>;
let instanceCalls=0,activeCalls=0,instanceEstimatedUsd=0;
export const liveProvider:ModelProvider=async(instructions,input,schema,name)=>{
  if(process.env.LLM_MODE!=='live'||!process.env.OPENAI_API_KEY?.trim())throw new AssistantError('LLM_UNAVAILABLE','모델 연결이 준비되지 않았어요. 입력을 보관하고 잠시 뒤 다시 시도해 주세요.',true,503);
  const maximum=Math.min(4000,Math.max(1,Number(process.env.LLM_MAX_INSTANCE_CALLS)||2000));
  if(instanceCalls>=maximum||instanceEstimatedUsd>=15)throw new AssistantError('LOCAL_CALL_LIMIT','이 서버 인스턴스의 데모 호출 한도에 도달했어요.',false,429);
  if(activeCalls>=6)throw new AssistantError('RATE_LIMITED','요청이 몰렸어요. 잠시 뒤 다시 시도해 주세요.',true,429);
  instanceCalls++;activeCalls++;
  const started=Date.now();let observedUsage:ModelUsage|null=null;let observedModel:string|null=null;
  try{
    const client=new OpenAI({apiKey:process.env.OPENAI_API_KEY,maxRetries:0,timeout:45_000});
    const jsonSchema=z.toJSONSchema(schema);delete jsonSchema.$schema;
    const response=await client.responses.create({model:process.env.OPENAI_MODEL||'gpt-5-mini',instructions,input,store:false,reasoning:{effort:'minimal'},max_output_tokens:1600,text:{format:{type:'json_schema',name,strict:true,schema:jsonSchema}}});
    observedModel=response.model;
    const inputTokens=response.usage?.input_tokens,outputTokens=response.usage?.output_tokens,totalTokens=response.usage?.total_tokens;
    if(Number.isSafeInteger(inputTokens)&&Number.isSafeInteger(outputTokens)&&Number.isSafeInteger(totalTokens)&&inputTokens!==undefined&&outputTokens!==undefined&&totalTokens!==undefined&&inputTokens>=0&&outputTokens>=0&&totalTokens===inputTokens+outputTokens){
      const estimatedCostUsd=response.model.startsWith('gpt-5-mini')?(inputTokens*0.25+outputTokens*2)/1e6:null;
      observedUsage={inputTokens,outputTokens,totalTokens,estimatedCostUsd};instanceEstimatedUsd+=estimatedCostUsd||0;
    }
    if(response.status!=='completed'||!response.output_text){
      console.info(JSON.stringify({event:'model_incomplete',status:response.status,reason:response.incomplete_details?.reason,usage:observedUsage,model:observedModel}));
      throw new AssistantError('INVALID_MODEL_RESPONSE','응답을 완성하지 못했어요. 입력을 그대로 두고 다시 시도해 주세요.',true,502);
    }
    let value:unknown;try{value=JSON.parse(response.output_text)}catch{throw new AssistantError('INVALID_MODEL_RESPONSE','모델 응답 형식을 확인하지 못했어요. 다시 시도해 주세요.',true,502)}
    if(!observedUsage)throw new AssistantError('INVALID_MODEL_RESPONSE','모델 사용량을 확인하지 못했어요. 다시 시도해 주세요.',true,502);
    return {value,model:response.model,usage:observedUsage};
  }catch(error){
    const attach=(safe:AssistantError)=>{safe.attempt={providerCalled:true,model:observedModel,usage:observedUsage,latencyMs:Date.now()-started,mode:'live'};return safe};
    if(error instanceof AssistantError)throw attach(error);
    if(error instanceof OpenAI.APIConnectionTimeoutError)throw attach(new AssistantError('LLM_TIMEOUT','응답 시간이 길어졌어요. 입력을 유지하고 다시 시도해 주세요.',true,504));
    if(error instanceof OpenAI.APIError){
      if(error.status===404)throw attach(new AssistantError('LLM_MODEL_UNAVAILABLE','설정한 모델을 사용할 수 없어요. 모델 설정을 확인해야 해요.',false,503));
      if(error.status===400)throw attach(new AssistantError('LLM_CONFIGURATION','모델 호출 설정을 확인해야 해요. 입력은 유지됩니다.',false,503));
      if(error.status===401||error.status===403)throw attach(new AssistantError('LLM_AUTH_ERROR','모델 연결 인증을 확인해야 해요. 입력은 유지됩니다.',false,503));
      if(error.status===429){const quota=error.code==='insufficient_quota';throw attach(new AssistantError(quota?'LLM_QUOTA':'RATE_LIMITED',quota?'모델 계정의 호출 가능 한도를 확인해야 해요.':'모델 요청이 몰렸어요. 잠시 뒤 다시 시도해 주세요.',!quota,429))}
    }
    throw attach(new AssistantError('LLM_UNAVAILABLE','모델 연결이 잠시 원활하지 않아요. 입력을 유지하고 다시 시도해 주세요.',true,503));
  }finally{activeCalls--}
};
