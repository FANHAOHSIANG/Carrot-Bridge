package com.navipilot.obf;

import android.content.Intent;
import android.os.Bundle;
import android.os.SystemClock;
import java.lang.reflect.Array;
import java.util.Locale;
import org.json.*;

/** Passive capture only; called after existing selected-source acceptance.
 * No broadcasts, RPC, service binding, or navigation/control output. */
public final class WideAutoObservation {
    private static final int MAX_NODES=18000, MAX_CHARS=360000, MAX_TEXT=220000;
    private static long window=-1;
    private static int count, priorityCount, rateDropped;
    private static long sequence;
    static boolean priority(Object type) {
        // High-frequency observed streams cannot starve infrequent route/lane events.
        if (!(type instanceof Number)) return true;
        int t=((Number)type).intValue();
        return t!=10001 && t!=12205 && t!=13011;
    }
    public static synchronized void capture(Intent i) {
        try {
            if(!WideBridgeLog.recording() || i==null ||
               !"AUTONAVI_STANDARD_BROADCAST_SEND".equals(i.getAction())) return;
            long now=SystemClock.elapsedRealtime(), second=now/1000;
            if(second!=window){window=second;count=0;priorityCount=0;}
            Bundle b=i.getExtras();
            if(b==null)return;
            Object type=b.get("KEY_TYPE");
            boolean reserved=priority(type);
            if(reserved ? ++priorityCount>12 : ++count>12){rateDropped++;return;}
            JSONObject data=decode(b);
            data.put("capture_sequence",++sequence).put("priority_bucket",reserved?"event":"telemetry");
            data.put("source","amap_auto").put("action",i.getAction())
                .put("receipt_mono_ms",now).put("control_input",false)
                .put("coordinate_reference","unverified").put("schema",2)
                .put("sender_verification","existing_source_filter")
                .put("rate_limited_since_last_record",rateDropped);
            rateDropped=0;
            WideBridgeLog.event("amap_auto_packet",data);
        } catch(Exception | LinkageError ignored) {
            // Diagnostic faults must not block the existing receiver.
        }
    }
    static boolean privateKey(String key) {
        String k=key.toLowerCase(Locale.ROOT).replaceAll("[^a-z0-9]","");
        return k.matches(".*(token|secret|password|credential|signature|cookie|authorization|apikey|aeskey|sessionid|deviceid|serialnumber|phone|email|address|account|userid|username|poi(?!nt)|destination|origin|home|workplace).*")
            || k.matches("key|nonce|iv|uid|imei|imsi|mac|androidid");
    }
    static boolean candidate(String key){
        String k=key.toLowerCase(Locale.ROOT).replaceAll("[^a-z0-9]","");
        return !privateKey(key) && k.matches(".*(lane|route|path|point|segment|link|road|lat|lon|lng|coord|geometry|curve|curvature|horizon|adas|position|location|match|topo|hud|guide|driv[e]?way|exit|direction|traffic|speed|dist|remain|bearing|heading|accuracy|longitude|latitude|altitude|maneuver|icon|tbt|json|payload).*|keytype|type|datatype|eventtype|data|extradata|extra|result|status|x|y|z|id");
    }
    // Preserve only the recognized boolean tokens, not arbitrary text.
    static boolean laneFlagKey(String key) {
        return "trafficLaneAdvised".equals(key) || "drive_way_enabled".equals(key);
    }
    static boolean textAllowed(String key){
        return key.toLowerCase(Locale.ROOT).replaceAll("[^a-z0-9]","").matches(".*roadname|exitnameinfo|exitdirectioninfo|segremaindisauto|routeremaindisauto|routeremaintimeauto|extradriveway|direction|type|status");
    }
    static JSONObject decode(Bundle b)throws JSONException{
        JSONObject payload=new JSONObject(), types=new JSONObject();
        Budget budget=new Budget();int n=0;
        for(String key:b.keySet()){
            if(++n>128){budget.cut=true;break;}
            if(key==null||key.length()>100||privateKey(key))continue;
            Object v=b.get(key);
            types.put(key,v==null?"null":v.getClass().getSimpleName());
            if(candidate(key))payload.put(key,budget.copy(v,key,0));
            else if(v instanceof Number || v instanceof Boolean || v instanceof Bundle)payload.put(key,budget.copy(v,key,0));
        }
        return new JSONObject().put("key_types",types).put("payload",payload)
            .put("truncated",budget.cut).put("visited_nodes",budget.nodes)
            .put("raw_bytes_preserved",false).put("redacted_fields",budget.redacted);
    }
    static final class Budget {
        int nodes,chars,redacted;boolean cut;
        Object copy(Object v,String key,int depth)throws JSONException{
            if(++nodes>MAX_NODES||chars>MAX_CHARS||depth>16){cut=true;return JSONObject.NULL;}
            if(privateKey(key)){redacted++;return JSONObject.NULL;}
            if(v==null||v==JSONObject.NULL)return JSONObject.NULL;
            if(v instanceof Boolean){chars+=8;return v;}
            if(v instanceof Number){chars+=24;return Double.isFinite(((Number)v).doubleValue())?v:JSONObject.NULL;}
            if(v instanceof String){
                String s=(String)v;chars+=Math.min(s.length(),MAX_CHARS);
                if(s.length()>MAX_TEXT){cut=true;return new JSONObject().put("_string_chars",s.length());}
                String t=s.trim();
                if(laneFlagKey(key)){
                    if("true".equalsIgnoreCase(t) || "1".equals(t))return Boolean.TRUE;
                    if("false".equalsIgnoreCase(t) || "0".equals(t))return Boolean.FALSE;
                    redacted++;return new JSONObject().put("_string_chars",s.length());
                }
                if((t.startsWith("{")||t.startsWith("[")) && depth<16 && safeDepth(t)){
                    try{
                        JSONTokener parser=new JSONTokener(t);Object x=parser.nextValue();
                        if(parser.nextClean()==0)return copy(x,key,depth+1);
                    }catch(JSONException ignored){}
                }
                if(t.length()<=4096 && t.matches("[0-9,.;| :+\\-Ee\\[\\]]+"))return t;
                if(textAllowed(key) && t.length()<=160)return t.replaceAll("[\\p{Cntrl}]"," ");
                redacted++;return new JSONObject().put("_string_chars",s.length());
            }
            if(v instanceof Bundle){
                JSONObject result=new JSONObject();Bundle in=(Bundle)v;int n=0;
                for(String k:in.keySet()){
                    if(++n>128||nodes>=MAX_NODES||chars>=MAX_CHARS){cut=true;break;}
                    if(k==null||k.length()>100||privateKey(k)){redacted++;continue;}
                    chars+=k.length();Object value=in.get(k);
                    if(candidate(k)||value instanceof Number||value instanceof Boolean||value instanceof Bundle)
                        result.put(k,copy(value,k,depth+1));
                }
                return result;
            }
            if(v instanceof JSONObject){
                JSONObject result=new JSONObject(), in=(JSONObject)v;
                java.util.Iterator<String> keys=in.keys();int n=0;
                while(keys.hasNext()){
                    String k=keys.next();
                    if(++n>128||nodes>=MAX_NODES||chars>=MAX_CHARS){cut=true;break;}
                    if(k.length()>100||privateKey(k)){redacted++;continue;}
                    chars+=k.length();
                    Object val=in.opt(k);
                    if(candidate(k)||val instanceof Number||val instanceof Boolean)result.put(k,copy(val,k,depth+1));
                    else if(val instanceof JSONObject||val instanceof JSONArray)result.put(k,copy(val,k,depth+1));
                    else {redacted++;result.put(k,new JSONObject().put("_string_chars",val instanceof String?((String)val).length():0));}
                }
                return result;
            }
            if(v instanceof JSONArray || v.getClass().isArray()){
                if(v.getClass().isArray()&&!v.getClass().getComponentType().isPrimitive()&&v.getClass().getComponentType()!=String.class){redacted++;return JSONObject.NULL;}
                int n=v instanceof JSONArray?((JSONArray)v).length():Array.getLength(v);
                JSONArray a=new JSONArray();
                for(int j=0;j<n;j++){
                    if(j>=8192||nodes>=MAX_NODES||chars>=MAX_CHARS){cut=true;break;}
                    Object x=v instanceof JSONArray?((JSONArray)v).opt(j):Array.get(v,j);
                    if(v instanceof byte[])x=((Byte)x)&255;
                    a.put(copy(x,key,depth+1));
                }
                return a;
            }
            redacted++;return JSONObject.NULL;
        }
        static boolean safeDepth(String s){
            int depth=0;boolean quote=false,esc=false;
            for(int j=0;j<s.length();j++){
                char c=s.charAt(j);
                if(quote){if(esc)esc=false;else if(c=='\\')esc=true;else if(c=='"')quote=false;}
                else if(c=='"')quote=true;
                else if(c=='{'||c=='['){if(++depth>16)return false;}
                else if(c=='}'||c==']'){if(--depth<0)return false;}
            }
            return depth==0&&!quote;
        }
    }
}
