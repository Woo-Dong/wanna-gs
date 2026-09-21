import fs from 'node:fs';import path from 'node:path';import {execFileSync}from'node:child_process';
import {PLAN_HASH,STUDY_ID,RUN_IDS,hash,HISTORY,CLOCK,canonical}from'./plan.mjs';
export const BUDGET_SOURCES=['scripts/run_nl_eval.py','evals/adapter.py','evals/scorer.py'];
export function budgetSources(root){return Object.fromEntries(BUDGET_SOURCES.map(f=>[f,hash(fs.readFileSync(path.join(root,f)))]))}
export const HARNESS=['run.mts','plan.mjs','metrics.mjs','binding.mjs','live.mts','budget_bridge.py'];
export function runtimeFiles(root){/** @type {Record<string,string>} */const files={};for(const tree of ['app','src','public','data/seed','data/schema']){const walk=dir=>{for(const e of fs.readdirSync(path.join(root,dir),{withFileTypes:true})){const f=dir+'/'+e.name;if(e.isSymbolicLink())throw Error('V3_RUNTIME_SYMLINK');if(e.isDirectory())walk(f);else if(e.isFile())files[f]=hash(fs.readFileSync(path.join(root,f)))}};walk(tree)}for(const f of ['package.json','package-lock.json','tsconfig.json','vercel.json','next.config.js','next.config.mjs','next.config.ts'])if(fs.existsSync(path.join(root,f)))files[f]=hash(fs.readFileSync(path.join(root,f)));return files}
export function validate(configPath,appRoot,budgetRoot,origin,output,{git=true}={}){
 const c=JSON.parse(fs.readFileSync(configPath,'utf8')),need=(ok,s)=>{if(!ok)throw Error(s)};
 need(c.approved===true&&c.study_id===STUDY_ID&&c.run_id===RUN_IDS[c.stage]&&c.authorized_calls===42&&c.prior_call_reserve===50,'V3_APPROVAL_REQUIRED');
 need(fs.realpathSync(appRoot)===c.app_root&&fs.realpathSync(budgetRoot)===c.budget_root&&c.origin===origin&&new URL(origin).origin===origin&&['localhost','127.0.0.1'].includes(new URL(origin).hostname),'V3_ROOT_OR_ORIGIN_MISMATCH');
 need(c.plan_hash===PLAN_HASH&&c.clock===CLOCK&&canonical(c.history)===canonical(HISTORY),'V3_PLAN_HISTORY_MISMATCH');
 need(hash(fs.readFileSync(path.join(budgetRoot,'scripts/run_nl_eval.py')))===c.budget_runner_hash&&canonical(budgetSources(budgetRoot))===canonical(c.budget_source_files),'V3_BUDGET_SOURCE_MISMATCH');
 need(c.output===path.resolve(output)&&!fs.existsSync(output),'V3_OUTPUT_REPLAY_OR_MISMATCH');
 const files=runtimeFiles(appRoot);need(canonical(c.runtime_files)===canonical(files)&&c.runtime_hash===hash(files),'V3_RUNTIME_MISMATCH');
 need(/^[0-9a-f]{40}$/.test(c.source_sha),'V3_SOURCE_SHA');
 if(git)for(const [file,digest]of Object.entries(files))need(hash(execFileSync('git',['show',`${c.source_sha}:${file}`],{cwd:appRoot,maxBuffer:20000000}))===digest,'V3_COMMIT_MISMATCH');
 const harness=Object.fromEntries(HARNESS.map(f=>[f,hash(fs.readFileSync(new URL(f,import.meta.url)))]));harness['seed.mts']=hash(fs.readFileSync(new URL('../seed.mts',import.meta.url)));harness['v2-metrics.mjs']=hash(fs.readFileSync(new URL('../metrics.mjs',import.meta.url)));
 need(canonical(c.harness_hashes)===canonical(harness),'V3_HARNESS_MISMATCH');
 need(c.seed_hash===files['public/demo/seed.sqlite']&&c.catalog_hash===JSON.parse(fs.readFileSync(path.join(appRoot,'public/demo/manifest.json'),'utf8')).catalogHash,'V3_SEED_CATALOG_MISMATCH');
 need(typeof c.build_id==='string'&&c.build_id===fs.readFileSync(path.join(appRoot,'.next/BUILD_ID'),'utf8').trim(),'V3_BUILD_MISMATCH');
 need(c.server_proof?.origin===origin&&c.server_proof?.buildId===c.build_id&&c.server_proof?.sourceSha===c.source_sha&&c.server_proof?.runtimeHash===c.runtime_hash&&Number.isSafeInteger(c.server_proof?.processId)&&c.server_proof.processId>0,'V3_SERVER_ATTESTATION_REQUIRED');
 if(c.stage==='baseline')need(c.source_sha==='10c00723d0b64ea47a06dcbd00e2b671e7c62daf'&&c.model==='gpt-5-mini-2025-08-07'&&c.prompt_version==='baseline-v1','V3_BASELINE_BINDING');
 need(typeof c.candidate_id==='string'&&typeof c.model==='string'&&typeof c.prompt_version==='string','V3_CANDIDATE_BINDING');
 return {config:c,files,harness};
}
