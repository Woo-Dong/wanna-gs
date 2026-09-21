export class ProbeStore {
  constructor(SQL, seed, persist) { this.SQL=SQL; this.seed=seed; this.persist=persist; this.generation=0; this.db=null; this.last=null; this.writable=false; }
  open(bytes) {
    const db=new this.SQL.Database(bytes);
    try {
      db.run('PRAGMA foreign_keys=ON');
      if(db.exec('PRAGMA integrity_check')[0]?.values[0][0]!=='ok') throw new Error('SNAPSHOT_CORRUPT');
      const metadata=Object.fromEntries(db.exec('SELECT key,value FROM metadata')[0].values);
      if(metadata.schema!=='probe-v1'||metadata.seed!=='20260921-v1') throw new Error('SNAPSHOT_VERSION');
      if(db.exec('PRAGMA foreign_key_check').length) throw new Error('SNAPSHOT_CONSTRAINT');
      return db;
    } catch(error) { db.close(); throw error; }
  }
  bytes() { const bytes=this.db.export(); this.db.run('PRAGMA foreign_keys=ON'); return bytes; }
  async initialize(snapshot) {
    if(snapshot && (snapshot.schema!=='probe-v1'||snapshot.seed!=='20260921-v1'||!Number.isSafeInteger(snapshot.generation)||snapshot.generation<0)) throw new Error('SNAPSHOT_VERSION');
    const bytes=snapshot ? new Uint8Array(snapshot.bytes) : this.seed;
    this.db=this.open(bytes); this.last=bytes.slice(); this.generation=snapshot?.generation??0;
    if(!snapshot) await this.persist(this.snapshot(bytes,this.generation));
    this.writable=true; return this.state();
  }
  snapshot(bytes,generation) { return {bytes:bytes.slice(),generation,schema:'probe-v1',seed:'20260921-v1'}; }
  state() { return {writable:this.writable,generation:this.generation,notes:(this.db.exec('SELECT id,actor_id,body FROM notes ORDER BY rowid')[0]?.values??[]).map(([id,actor,body])=>({id,actor,body})),foreignKeys:this.db.exec('PRAGMA foreign_keys')[0].values[0][0]}; }
  async add({id,actor,body,generation}) {
    if(!this.writable) throw new Error('STORAGE_NOT_READY');
    if(generation!==this.generation) throw new Error('STALE_GENERATION');
    if(typeof id!=='string'||!id||typeof body!=='string'||!body.trim()||body.trim().length>80||!['customer','merchant'].includes(actor)) throw new Error('INVALID_INPUT');
    const existing=this.db.exec('SELECT body,actor_id FROM notes WHERE id=?',[id]);
    if(existing.length) { if(existing[0].values[0][0]!==body.trim()||existing[0].values[0][1]!==actor) throw new Error('ID_CONFLICT'); return this.state(); }
    try {
      this.db.run('BEGIN'); this.db.run('INSERT INTO notes VALUES(?,?,?)',[id,actor,body.trim()]); this.db.run('COMMIT');
      const bytes=this.bytes(); await this.persist(this.snapshot(bytes,this.generation)); this.last=bytes.slice(); return this.state();
    } catch(error) { this.db.close(); this.db=this.open(this.last); throw error; }
  }
  async reset() {
    const next=this.open(this.seed), generation=this.generation+1;
    try { await this.persist(this.snapshot(this.seed,generation)); } catch(error) { next.close(); throw error; }
    this.db?.close(); this.db=next; this.last=this.seed.slice(); this.generation=generation; this.writable=true; return this.state();
  }
}
