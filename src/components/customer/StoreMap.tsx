'use client';
import {useState} from 'react';
import type {Store} from '../../contracts/domain';
import styles from './customer.module.css';
const project=(lat:number,lng:number,z:number)=>({x:(lng+180)/360*2**z*256,y:(1-Math.asinh(Math.tan(lat*Math.PI/180))/Math.PI)/2*2**z*256});
export function StoreMap({stores,selected,onSelect}:{stores:Store[];selected:string;onSelect:(id:string)=>void}){
 const [failed,setFailed]=useState(false);if(!stores.length)return null;
 const center={lat:stores.reduce((a,s)=>a+s.lat,0)/stores.length,lng:stores.reduce((a,s)=>a+s.lng,0)/stores.length};
 let zoom=16;while(zoom>8){const pts=stores.map(s=>project(s.lat,s.lng,zoom));if(Math.max(...pts.map(p=>p.x))-Math.min(...pts.map(p=>p.x))<270&&Math.max(...pts.map(p=>p.y))-Math.min(...pts.map(p=>p.y))<165)break;zoom--;}
 const c=project(center.lat,center.lng,zoom),left=c.x-160,top=c.y-110;
 const tiles=[];for(let x=Math.floor(left/256);x<=Math.floor((left+320)/256);x++)for(let y=Math.floor(top/256);y<=Math.floor((top+220)/256);y++)tiles.push({x,y});
 return <><div className={styles.map} aria-label="실제 점포 위치 지도">{!failed&&tiles.map(t=><img key={`${zoom}/${t.x}/${t.y}`} src={`https://tile.openstreetmap.org/${zoom}/${t.x}/${t.y}.png`} width={256} height={256} alt="" onError={()=>setFailed(true)} style={{position:'absolute',left:t.x*256-left,top:t.y*256-top}}/>)}{stores.map((s,i)=>{const p=project(s.lat,s.lng,zoom);return <button type="button" key={s.id} className={styles.pin} aria-label={`${s.name} 선택`} aria-pressed={selected===s.id} onClick={()=>onSelect(s.id)} style={{left:p.x-left,top:p.y-top}}>{i+1}</button>;})}<a className={styles.attribution} href="https://www.openstreetmap.org/copyright" target="_blank" rel="noreferrer">© OpenStreetMap contributors</a></div>{failed&&<p role="status">지도를 불러오지 못했어요. 아래 점포 목록에서 계속 선택하세요.</p>}</>;
}
