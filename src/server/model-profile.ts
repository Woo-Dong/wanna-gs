// Standard uncached token prices checked against official model pages on 2026-09-21.
// This is a local conservative estimate, not account billing or a hard spending cap.
export function estimateModelCost(model:string,inputTokens:number,outputTokens:number):number|null{
 if(!Number.isSafeInteger(inputTokens)||!Number.isSafeInteger(outputTokens)||inputTokens<0||outputTokens<0)return null;
 if(/^gpt-5-mini(?:$|-)/.test(model))return (inputTokens*.25+outputTokens*2)/1e6;
 if(/^gpt-4\.1-mini(?:$|-)/.test(model))return (inputTokens*.4+outputTokens*1.6)/1e6;
 return null;
}
export function reasoningOptions(model:string){
 return /^gpt-4\.1(?:$|-)/.test(model)?{}:{reasoning:{effort:'minimal' as const}};
}
