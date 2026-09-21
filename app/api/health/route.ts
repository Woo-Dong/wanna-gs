import versions from '../../../public/demo/manifest.json';
export function GET(){
 return Response.json({
  app:'wanna-gs',phase:'demo',transactions:'browser-local-simulated',
  storage:'browser-sqlite-single-tab',versions,
  model:{provider:'openai',mode:process.env.LLM_MODE==='live'?'live':'unavailable',configured:Boolean(process.env.OPENAI_API_KEY?.trim()),verification:'requires-actual-call'},
 },{headers:{'Cache-Control':'no-store'}});
}
