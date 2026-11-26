function makeProbe(){
  const MAX_KEYS=4096, MAX_NODES=12000, MAX_TYPES=256, MAX_EVENTS=64, TTL=3000;
  const keys=new Map(), counts=new Map(), latest=new Map(), history=[];
  let epoch=null, route=null, generation=0, watermark=-1, sequence=0, invalid=0, truncated=0, resetReason="initial", ended=false;
  const integer=x=>Number.isSafeInteger(x)&&x>=0;
  const rid=x=>integer(x)&&x<=4294967295?String(x):null;
  const object=x=>x!==null&&typeof x==="object"&&!Array.isArray(x);
  const secret=k=>/token|secret|password|signature|cookie|authorization|apikey|aeskey|sessionid|account|phone|email|userid|nonce/i.test(k.replace(/[_-]/g,""));
  function clear(reason){latest.clear();route=null;generation++;resetReason=reason;}
  function scan(data,type,t){
    const stack=[[data,"type"+type,0]];let n=0;
    while(stack.length&&n++<MAX_NODES){
      const [v,p,d]=stack.pop();
      if(d>20||p.length>512){truncated++;continue;}
      if(Array.isArray(v)){
        if(v.length>4096)truncated++;
        for(let i=Math.min(v.length,4096)-1;i>=0;i--)stack.push([v[i],p+"[]",d+1]);
      }else if(object(v)){
        const entries=Object.entries(v);
        if(entries.length>256)truncated++;
        for(const [k,val] of entries.slice(0,256)){
          if(k.length>128||secret(k))continue;
          stack.push([val,p+"."+( /^\d+$/.test(k)?"{id}":k),d+1]);
        }
      }else{
        if(!keys.has(p)&&keys.size>=MAX_KEYS){truncated++;continue;}
        const prior=keys.get(p);
        keys.set(p,{path:p,type:v===null?"null":typeof v,count:(prior?.count||0)+1,last_mono_ms:t,
          candidate:/lane|guidearrow|recommend|hdmatch|lanematch|lanerat|roadwidth|topology/i.test(p),
          value:typeof v==="number"&&Number.isFinite(v)||typeof v==="boolean"?v:null});
      }
    }
    if(stack.length)truncated++;
  }
  function ingest(record){
    if(!object(record))return false;
    const e=record.event,d=record.data;
    if(e==="start"){
      ended=false;clear("recording_start");epoch=null;watermark=-1;history.length=0;keys.clear();counts.clear();return true;
    }
    if(e==="stop"||e==="export"){
      ended=true;clear(e);return true;
    }
    if(e==="amap_link_reset"&&object(d)&&integer(d.epoch)){
      if(epoch!==null&&d.epoch<epoch)return false;
      epoch=d.epoch;watermark=-1;ended=false;clear("link_reset");return true;
    }
    if(e!=="amap_link_packet"||!object(d))return false;
    if(!integer(d.epoch)||!integer(d.received_mono_ms)||d.parse_status!=="decoded"||!object(d.payload)||d.payload.bizType!==113||!Array.isArray(d.payload.datas)){invalid++;return false;}
    if(epoch!==null&&d.epoch<epoch){invalid++;return false;}
    if(epoch!==d.epoch){epoch=d.epoch;watermark=-1;ended=false;clear("new_link_epoch");}
    const t=d.received_mono_ms;
    if(t<watermark){invalid++;return false;}
    watermark=t;
    if(d.truncated)truncated++;
    for(const item of d.payload.datas.slice(0,512)){
      if(!object(item)||!integer(item.type)||!object(item.data)){invalid++;continue;}
      const type=item.type,body=item.data;
      if(!counts.has(type)&&counts.size>=MAX_TYPES){truncated++;continue;}
      counts.set(type,(counts.get(type)||0)+1);
      if([19,100,200].includes(type)){ended=true;clear("navigation_end_or_reset");}
      else if(type===2||type===20){
        const next=rid(type===2?body.highlightRoute:body.routeId);
        if(next!==route){clear("route_change");route=next;}
        if(next!==null)ended=false;
      }else if(type===4){
        const next=rid(body.pathID);
        if(next!==null&&route!==null&&next!==route){clear("route_mismatch");}
      }
      scan(body,type,t);
      const entry={seq:++sequence,type,epoch,generation,route_id:route,received_mono_ms:t,control_usable:false,
        truncated:!!d.truncated,fields:Object.keys(body).filter(k=>!secret(k)).slice(0,128)};
      history.push(entry);if(history.length>MAX_EVENTS)history.shift();
      if(!ended&&![19,100,200].includes(type)&&!d.truncated)latest.set(type,entry);
    }
    if(d.payload.datas.length>512)truncated++;
    return true;
  }
  function snapshot(at=watermark){
    return {schema:1,source:"amap_link_authorized_log",mode:"replay_only",control_usable:false,
      epoch,route_id:route,route_generation:generation,seq:sequence,source_mono_ms:watermark,
      reset_reason:resetReason,invalid,truncated,
      latest:[...latest.values()].filter(x=>at>=x.received_mono_ms&&at-x.received_mono_ms<=TTL),
      channels:{L1:"authorized Link log replay",L2:"not implemented: no verified lane query",L3:"disabled",L4:"not implemented: no verified HD location listener"},
      lane:{ego_index:null,physical_lane_count:null,recommended_lane:null,centerline:null,verified:false}};
  }
  return {ingest,snapshot,keys:()=>[...keys.values()].sort((a,b)=>a.path.localeCompare(b.path)),
    events:()=>[...counts].map(([type,count])=>({type,count})),event:type=>history.filter(x=>x.type===type)};
}
function selfTest(){
  let checks=0;const a=(condition)=>{if(!condition)throw new Error("assertion "+(checks+1));checks++;};
  const p=makeProbe();
  const packet=(epoch,t,type,data,truncated=false)=>({event:"amap_link_packet",data:{epoch,received_mono_ms:t,parse_status:"decoded",truncated,payload:{bizType:113,datas:[{type,data}]}}});
  a(p.ingest(packet(1,100,2,{highlightRoute:7,info:{"7":{segmentInfo:[{laneCount:3}]}}})));
  a(p.snapshot().route_id==="7");a(p.keys().some(x=>x.path.includes("{id}")&&x.candidate));
  a(p.ingest(packet(1,200,77,{laneIndex:1,token:"secret"})));a(!p.keys().some(x=>x.path.includes("token")));
  a(p.snapshot().lane.ego_index===null);a(p.snapshot().control_usable===false);
  a(p.snapshot(3201).latest.length===0);a(!p.ingest(packet(1,199,77,{laneIndex:2})));
  a(p.ingest(packet(1,300,20,{routeId:8})));a(p.snapshot().route_id==="8");a(p.snapshot().latest.every(x=>x.type!==77));
  a(p.ingest(packet(1,400,100,{})));a(p.snapshot().route_id===null&&p.snapshot().latest.length===0);
  a(p.ingest(packet(1,450,4,{pathID:8})));a(p.snapshot().latest.length===0);
  a(p.ingest(packet(2,500,77,{laneCount:3},true)));a(p.snapshot().latest.length===0);
  a(!p.ingest(packet(1,600,77,{})));a(p.ingest({event:"stop"}));a(p.snapshot().latest.length===0);
  a(p.ingest({event:"start"}));a(p.keys().length===0);
  return checks;
}
module.exports={makeProbe,selfTest};
if(require.main===module)console.log(selfTest()+" assertions passed");
