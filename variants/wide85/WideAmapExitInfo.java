package com.navipilot.obf;

import android.content.Intent;
import android.os.Bundle;
import java.util.Map;
import java.util.UUID;
import org.json.JSONArray;
import org.json.JSONObject;

/** Raw Amap Auto guidance metadata, display only. Never supplies a speed or steering request. */
public final class WideAmapExitInfo {
    private static final long TTL_MS = 2000L, MATCH_MS = 500L;
    private static final String FIELD = "amap_exit_info";
    private static final String[] TEXT = {"EXIT_NAME_INFO", "EXIT_DIRECTION_INFO", "SEG_REMAIN_DIS_AUTO",
        "CUR_ROAD_NAME", "NEXT_ROAD_NAME", "ROUTE_REMAIN_DIS_AUTO", "ROUTE_REMAIN_TIME_AUTO"};
    private static final String[] NUMBER = {"SEG_REMAIN_DIS", "CUR_SEG_NUM", "CUR_POINT_NUM",
        "ROAD_TYPE", "ICON", "CAR_DIRECTION", "NEW_ICON", "ROUTE_REMAIN_DIS", "ROUTE_ALL_DIS", "ROUTE_REMAIN_TIME"};
    private static final class Sample {
        final JSONObject data;
        final long wall, nano;
        Sample(JSONObject data, long wall, long nano) { this.data=data; this.wall=wall; this.nano=nano; }
    }
    private static volatile Sample latest;
    // Process-local observation stream, not a route ID or a confirmed ramp event.
    private static String observationSession;
    private static long selectedAt;
    private static int sequence;
    private static void resetObservation() { latest=null; observationSession=null; selectedAt=0; sequence=0; }

    /** Called only at the existing Z3.l Amap Auto navigation update entry. */
    public static synchronized void capture(Intent intent) {
        try {
            long wall=System.currentTimeMillis(), nano=System.nanoTime();
            if(intent==null || !WideAmapSource.preAdjustAllowed(wall)) { resetObservation(); return; }
            Bundle extras=intent.getExtras();
            JSONObject info=new JSONObject();
            if(extras!=null) {
                for(String key:TEXT) {
                    Object raw=extras.get(key);
                    if(raw instanceof String) {
                        String value=((String)raw).trim();
                        if(!value.isEmpty() && value.length()<=160) info.put(key,value);
                    } else if("EXIT_DIRECTION_INFO".equals(key) && raw instanceof Integer) {
                        info.put(key,raw);
                    }
                }
                for(String key:NUMBER) {
                    Object raw=extras.get(key);
                    if(raw instanceof Integer && (Integer)raw>=0 && (Integer)raw<=2000000) info.put(key,raw);
                }
                // Lane encoding differs across Amap releases. Preserve a bounded raw value only.
                Object lane=extras.get("EXTRA_DRIVE_WAY");
                if(lane instanceof String && ((String)lane).length()<=256 && !((String)lane).isEmpty()) {
                    info.put("EXTRA_DRIVE_WAY",lane);
                } else if(lane instanceof int[] && ((int[])lane).length>0 && ((int[])lane).length<=32) {
                    JSONArray values=new JSONArray();
                    for(int item:(int[])lane) values.put(item);
                    info.put("EXTRA_DRIVE_WAY",values);
                } else if(lane instanceof byte[] && ((byte[])lane).length>0 && ((byte[])lane).length<=32) {
                    JSONArray values=new JSONArray();
                    for(byte item:(byte[])lane) values.put(item&255);
                    info.put("EXTRA_DRIVE_WAY",values);
                }
            }
            if(info.length()==0) { resetObservation(); return; }
            long selection=WideAmapSource.preAdjustSelectedAt();
            Sample prior=latest;
            if(observationSession==null || selectedAt!=selection || prior==null
                || nano<prior.nano || nano-prior.nano>=TTL_MS*1000000L || wall<prior.wall
                || sequence>=2000000) {
                observationSession=UUID.randomUUID().toString();
                selectedAt=selection;
                sequence=0;
            }
            info.put("BRIDGE_OBS_VERSION",1);
            info.put("BRIDGE_OBS_SESSION",observationSession);
            info.put("BRIDGE_OBS_SEQUENCE",++sequence);
            latest=new Sample(info,wall,nano);
        } catch(Exception invalid) { resetObservation(); }
    }

    public static JSONObject decorate(String stream, JSONObject value, Map stamps) {
        if(!"guidance_current".equals(stream) || value==null) return value;
        try {
            JSONObject result=new JSONObject(value.toString());
            result.remove(FIELD);
            Sample sample=latest;
            Object stamp=stamps==null?null:stamps.get(stream);
            long now=System.currentTimeMillis(), elapsed=sample==null?-1:System.nanoTime()-sample.nano;
            if(sample==null || !(stamp instanceof Long) || !WideAmapSource.preAdjustAllowed(sample.wall)
                || now<sample.wall || now-sample.wall>=TTL_MS || elapsed<0 || elapsed>=TTL_MS*1000000L
                || (Long)stamp<=0 || (Long)stamp>now || now-(Long)stamp>=TTL_MS
                || Math.abs((Long)stamp-sample.wall)>MATCH_MS) return result;
            result.put(FIELD,new JSONObject().put("source","amap_auto").put("scope","display_only")
                .put("generated_at_ms",sample.wall).put("fields",sample.data));
            return result;
        } catch(Exception invalid) { return value; }
    }
}
