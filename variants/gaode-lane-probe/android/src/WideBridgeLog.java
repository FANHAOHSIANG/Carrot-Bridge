package com.navipilot.obf;
import android.content.Context;
import android.os.SystemClock;
import org.json.JSONObject;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicLong;
public final class WideBridgeLog {
  private static final long LIMIT=12L*1024*1024;
  private static final ThreadPoolExecutor worker=new ThreadPoolExecutor(1,1,0,TimeUnit.MILLISECONDS,new ArrayBlockingQueue<Runnable>(128));
  private static volatile boolean active;
  private static volatile File file;
  private static final AtomicLong count=new AtomicLong(),dropped=new AtomicLong();
  private static volatile String error="";
  public static synchronized boolean start(Context ctx){
    if(active||worker.getActiveCount()!=0||!worker.getQueue().isEmpty())return false;
    file=existing(ctx);
    try(FileOutputStream out=new FileOutputStream(file,false)){}catch(IOException e){error="open_failed";return false;}
    count.set(0);dropped.set(0);error="";active=true;event("start","gaodeprobe_link_observe");return true;
  }
  public static boolean recording(){return active;}
  public static synchronized void stop(){if(active){event("stop","user");active=false;}}
  public static long count(){return count.get();}
  public static long dropped(){return dropped.get();}
  public static String error(){return error;}
  public static boolean idle(){return !active&&worker.getActiveCount()==0&&worker.getQueue().isEmpty();}
  public static File existing(Context c){return new File(c.getFilesDir(),"gaode-events.jsonl");}
  public static synchronized void event(String type,Object data){
    if(!active||file==null)return;
    try{
      JSONObject j=new JSONObject().put("event",type).put("wall_ms",System.currentTimeMillis()).put("mono_ms",SystemClock.elapsedRealtime()).put("data",data);
      final byte[] bytes=(j.toString()+"\n").getBytes(StandardCharsets.UTF_8);final File target=file;
      if(bytes.length>1024*1024){dropped.incrementAndGet();return;}
      worker.execute(()->{try{if(target.length()+bytes.length>LIMIT){dropped.incrementAndGet();return;}try(FileOutputStream stream=new FileOutputStream(target,true)){stream.write(bytes);}count.incrementAndGet();}catch(IOException e){error="write_failed";dropped.incrementAndGet();}});
    }catch(Exception e){dropped.incrementAndGet();}
  }
}
