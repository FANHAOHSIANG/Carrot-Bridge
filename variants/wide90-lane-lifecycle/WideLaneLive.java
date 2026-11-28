package com.navipilot.obf;
import android.content.Intent;
import android.os.Bundle;
import android.os.SystemClock;
import java.util.Map;
import org.json.*;
/** Display-only extension to existing guidance_current; no writes to driving fields. */
public final class WideLaneLive {
    private static final String FIELD="amap_lane_candidate";
    private static final long TTL=2000, MATCH=1000, AUTO_MAX_AGE=180000, AUTO_PROGRESS_TTL=3000;
    private static long autoAt=-1, autoSeg=-1, autoTotal=-1, autoRemain=-1, autoPoint=-1;
    private static String selected="";
    private static long epoch, lastLink=-1, path=-1, progress=-1, receipt=-1, wall=-1;
    private static JSONObject candidate;
    private static void clear(){candidate=null;receipt=wall=-1;}
    private static void clearAuto(){clear();autoAt=autoSeg=autoTotal=autoRemain=autoPoint=-1;}
    public static synchronized void select(String name){
        selected=name==null?"":name;epoch=0;lastLink=path=progress=-1;clearAuto();
    }
    public static synchronized void reset(long next){epoch=next>0?next:0;lastLink=path=progress=-1;clear();}
    public static synchronized void invalidate(){reset(0);}
    private static boolean fresh(long time,long now){return time>=0&&now>=time&&now-time<TTL;}
    private static long id(Object n){
        if(!(n instanceof Number))return -1;
        double d=((Number)n).doubleValue();return Double.isFinite(d)&&d>=0&&d<=4294967295L&&d==Math.floor(d)?(long)d:-1;
    }
    private static void accept(JSONObject c,long at,long stamp)throws JSONException{
        clear();
        if(c==null||c.optJSONArray("lanes")==null||stamp<=0)return;
        candidate=c;receipt=at;wall=stamp;
    }
    // Route evidence is a continuity guard, not a confirmed route ID.
    // Preserve a provider lane event only during a fresh, continuous guidance stream.
    static synchronized void autoProgress(long at,long seg,long total,long remain,long point){
        if(seg<0||total<=0||remain<=0||remain>total+100||point<0||at<0){clearAuto();return;}
        if(autoAt>=0&&(at<autoAt||at-autoAt>=AUTO_PROGRESS_TTL||seg!=autoSeg||total!=autoTotal||remain>autoRemain+80||point<autoPoint)){clear();}
        autoAt=at;autoSeg=seg;autoTotal=total;autoRemain=remain;autoPoint=point;
    }
    static synchronized boolean autoFresh(long now){
        return candidate!=null&&receipt>=0&&now>=receipt&&now-receipt<AUTO_MAX_AGE&&autoAt>=0&&now>=autoAt&&now-autoAt<AUTO_PROGRESS_TTL;
    }
    public static synchronized void auto(Intent i){
        try{
            if(!"com.autonavi.amapauto".equals(selected)||i==null||!"AUTONAVI_STANDARD_BROADCAST_SEND".equals(i.getAction()))return;
            Bundle b=i.getExtras();if(b==null)return;
            Object t=b.get("KEY_TYPE");if(!(t instanceof Number))return;
            double type=((Number)t).doubleValue();
            if(type==10019){Object state=b.get("EXTRA_STATE");if(state instanceof Number&&(((Number)state).intValue()==9||((Number)state).intValue()==25))clearAuto();return;}
            if(type==10001){autoProgress(SystemClock.elapsedRealtime(),id(b.get("CUR_SEG_NUM")),id(b.get("ROUTE_ALL_DIS")),id(b.get("ROUTE_REMAIN_DIS")),id(b.get("CUR_POINT_NUM")));return;}
            if(type!=13012)return;
            clear();
            if(autoAt<0||SystemClock.elapsedRealtime()<autoAt||SystemClock.elapsedRealtime()-autoAt>=AUTO_PROGRESS_TTL)return;
            Object raw=b.get("EXTRA_DRIVE_WAY");
            if(!(raw instanceof String)||((String)raw).length()>65536)return;
            String s=((String)raw).trim();
            if(!WideAutoObservation.Budget.safeDepth(s))return;
            JSONTokener parser=new JSONTokener(s);
            Object obj=parser.nextValue();if(!(obj instanceof JSONObject)||parser.nextClean()!=0)return;
            accept(WideLaneCandidate.auto((JSONObject)obj),SystemClock.elapsedRealtime(),System.currentTimeMillis());
        }catch(Exception invalid){clear();}
    }
    public static synchronized void link(long e,int type,JSONObject data,long at,long stamp){
        if(!"com.autonavi.minimap".equals(selected)||e<=0||e!=epoch||at<0||at<lastLink||!fresh(at,SystemClock.elapsedRealtime())||stamp<=0)return;
        lastLink=at;
        try{
            if(type==1||type==2||type==3||type==19||type==20||type==100||type==200){path=progress=-1;clear();return;}
            if(type==4){
                long p=id(data==null?null:data.opt("pathID"));
                if(p<0||p!=path)clear();
                path=p;progress=p<0?-1:at;return;
            }
            if(type!=14)return;
            clear();
            if(path<0||!fresh(progress,at))return;
            if(data!=null&&data.has("pathID")&&id(data.opt("pathID"))!=path)return;
            accept(WideLaneCandidate.link(data),at,stamp);
        }catch(Exception invalid){clear();}
    }
    public static synchronized JSONObject decorate(String stream,JSONObject value,Map stamps){
        if(!"guidance_current".equals(stream)||value==null)return value;
        try{
            JSONObject out=new JSONObject(value.toString());out.remove(FIELD);
            long now=SystemClock.elapsedRealtime(),w=System.currentTimeMillis();
            Object ts=stamps==null?null:stamps.get(stream);
            boolean auto="com.autonavi.amapauto".equals(selected);
            if(candidate==null||wall<=0||w<wall||!(ts instanceof Long))return out;
            if(auto ? (!autoFresh(now)||w-wall>=AUTO_MAX_AGE) : (!fresh(receipt,now)||w-wall>=TTL))return out;
            long stamp=(Long)ts;
            if(stamp<=0||w<stamp||w-stamp>=TTL||(!auto&&Math.abs(stamp-wall)>MATCH))return out;
            if("com.autonavi.minimap".equals(selected)&&!fresh(progress,now))return out;
            if(!"com.autonavi.minimap".equals(selected)&&!"com.autonavi.amapauto".equals(selected))return out;
            out.put(FIELD,new JSONObject().put("version",1).put("scope","display_only")
                .put("generated_at_ms",auto?stamp:wall).put("observed_at_ms",wall)
                .put("observation_age_ms",now-receipt).put("candidate",candidate));
            return out;
        }catch(Exception invalid){return value;}
    }
}
