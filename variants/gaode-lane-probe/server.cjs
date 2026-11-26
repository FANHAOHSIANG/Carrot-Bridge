"use strict";
const fs=require("node:fs"),http=require("node:http"),readline=require("node:readline");
const {makeProbe}=require("./probe.cjs");
async function main(){
  const paths=process.argv.slice(2);
  if(!paths.length)throw new Error("Usage: node server.cjs events2.jsonl events1.jsonl events0.jsonl (oldest first, only files that exist)");
  const p=makeProbe();let skipped=0;
  for(const path of paths){
    const stat=fs.statSync(path);
    if(!stat.isFile()||stat.size>64*1024*1024)throw new Error("Expected regular JSONL file <=64 MiB");
    const lines=readline.createInterface({input:fs.createReadStream(path),crlfDelay:Infinity});
    for await(const line of lines){
      if(line.length>1024*1024){skipped++;continue;}
      try{p.ingest(JSON.parse(line));}catch{skipped++;}
    }
  }
  const page='<!doctype html><meta charset="utf-8"><title>GaodeProbe replay</title><style>body{font:16px system-ui;margin:24px;max-width:1000px}pre{white-space:pre-wrap;overflow-wrap:anywhere}input{padding:8px;width:90%}</style><h1>高德一般版 GaodeProbe</h1><p>離線回放，不是即時車況。車道候選欄位未經語意驗證，不可控車。</p><p><a href="/app">快照</a> · <a href="/events">事件</a> · <a href="/keys">欄位</a></p><input id="q" placeholder="搜尋 lane / recommend / HD"><pre id="out"></pre><script>let rows=[];fetch("/keys").then(r=>r.json()).then(j=>{rows=j;show()});function show(){document.getElementById("out").textContent=JSON.stringify(rows.filter(x=>x.path.toLowerCase().includes(document.getElementById("q").value.toLowerCase())),null,2)}document.getElementById("q").oninput=show;</script>';
  const server=http.createServer((req,res)=>{
    if(req.method!=="GET"){res.writeHead(405).end();return;}
    if(!/^127\.0\.0\.1:8888$/.test(req.headers.host||"")){res.writeHead(403).end();return;}
    const u=new URL(req.url,"http://127.0.0.1:8888");let data;
    res.setHeader("Cache-Control","no-store");res.setHeader("X-Content-Type-Options","nosniff");
    if(u.pathname==="/"||u.pathname==="/keys-view"){res.setHeader("Content-Type","text/html; charset=utf-8");res.end(page);return;}
    if(u.pathname==="/app")data={...p.snapshot(),skipped_lines:skipped};
    else if(u.pathname==="/keys")data=p.keys();
    else if(u.pathname==="/events")data=p.events();
    else if(u.pathname==="/event"&&/^\d{1,10}$/.test(u.searchParams.get("type")||""))data=p.event(Number(u.searchParams.get("type")));
    else if(u.pathname==="/stream"){res.setHeader("Content-Type","text/event-stream");res.end("event: snapshot\ndata: "+JSON.stringify(p.snapshot())+"\n\n");return;}
    else{res.writeHead(404).end();return;}
    res.setHeader("Content-Type","application/json; charset=utf-8");res.end(JSON.stringify(data));
  });
  server.listen(8888,"127.0.0.1",()=>console.log("Replay only: http://127.0.0.1:8888/"));
}
main().catch(e=>{console.error(e.message);process.exitCode=1;});
