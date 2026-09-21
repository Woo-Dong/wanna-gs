/* Isolated preflight worker: SQL never runs on a server. */
importScripts('/probe/sql-wasm.js');
let store, queue=Promise.resolve(), failNext=false;
const namespace='wanna-gs-preflight-20260921';
function storage(mode, value, abortForTest=false) {
  return new Promise((resolve,reject)=>{
    const opening=indexedDB.open(namespace,1);
    opening.onupgradeneeded=()=>opening.result.createObjectStore('snapshots');
    opening.onerror=()=>reject(new Error('STORAGE_OPEN_FAILED'));
    opening.onsuccess=()=>{
      const db=opening.result;
      const tx=db.transaction('snapshots', mode==='get'?'readonly':'readwrite');
      const object=tx.objectStore('snapshots');
      const request=mode==='get'?object.get('current'):object.put(value,'current');
      tx.oncomplete=()=>{const result=request.result; db.close(); resolve(result);};
      tx.onabort=tx.onerror=()=>{db.close(); reject(new Error(abortForTest?'STORAGE_FAILED_TEST':'STORAGE_FAILED'));};
      if(abortForTest)tx.abort();
    };
  });
}
async function setup() {
  const [{ProbeStore}, SQL, response]=await Promise.all([import('/probe/core.mjs'),initSqlJs({locateFile:()=>'/probe/sql-wasm.wasm'}),fetch('/probe/seed.sqlite')]);
  if(!response.ok) throw new Error('SEED_LOAD_FAILED');
  const bytes=new Uint8Array(await response.arrayBuffer());
  const manifest=await (await fetch('/probe/manifest.json')).json();
  const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))).map(b=>b.toString(16).padStart(2,'0')).join('');
  if(hash!==manifest.seedSha256) throw new Error('SEED_HASH_MISMATCH');
  store=new ProbeStore(SQL,bytes,async snapshot=>{const abortForTest=failNext;failNext=false;await storage('put',snapshot,abortForTest);});
  return store.initialize(await storage('get'));
}
self.onmessage=({data})=>{
  queue=queue.then(async()=>{
    try {
      let state;
      if(data.type==='init') state=await setup();
      else if(data.type==='reset') {if(!store) await setup(); state=await store.reset();}
      else if(data.type==='add') {failNext=Boolean(data.fail); state=await store.add(data.payload);}
      else throw new Error('INVALID_COMMAND');
      self.postMessage({id:data.id,ok:true,state});
    } catch(error) {self.postMessage({id:data.id,ok:false,error:error.message,state:store?.db?store.state():null});}
  });
};
