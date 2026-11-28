package com.navipilot.obf;
import android.os.Bundle;
import android.content.Intent;
import org.json.*;
public final class AutoChecks {
    static void ok(boolean b,String m){if(!b)throw new AssertionError(m);}
    public static void main(String[] a)throws Exception{
        Bundle b=new Bundle();
        b.putInt("KEY_TYPE",13012);
        b.putString("EXTRA_DATA","{\"laneCount\":4,\"frontLane\":[255,0,0,255],\"token\":\"secret\",\"routePointlist\":[{\"lat\":24.0,\"lon\":121.0}],\"unknownText\":\"private\"}");
        b.putByteArray("EXTRA_DRIVE_WAY",new byte[]{-1,0,1});
        b.putString("EXTRA_TOKEN","hidden");
        JSONObject d=WideAutoObservation.decode(b),p=d.getJSONObject("payload"), j=p.getJSONObject("EXTRA_DATA");
        ok(WideAutoObservation.privateKey("poiName"),"redact POI");ok(!WideAutoObservation.privateKey("routePointlist"),"retain route points");ok(p.getInt("KEY_TYPE")==13012,"key");ok(j.getInt("laneCount")==4,"lane");
        ok(j.getJSONArray("routePointlist").getJSONObject(0).getDouble("lat")==24.0,"route");
        ok(p.getJSONArray("EXTRA_DRIVE_WAY").getInt(0)==255,"unsigned byte");
        ok(!d.toString().contains("secret")&&!d.toString().contains("hidden")&&!d.toString().contains("private"),"privacy");
        ok(!d.getBoolean("truncated"),"small packet");
        b.putIntArray("routePoints",new int[9000]);ok(WideAutoObservation.decode(b).getBoolean("truncated"),"limit");
        ok(!WideAutoObservation.Budget.safeDepth("[[[[[[[[[[[[[[[[[]]]]]]]]]]]]]]]]]"),"depth");
        WideBridgeLog.enabled=false;WideAutoObservation.capture(new Intent("AUTONAVI_STANDARD_BROADCAST_SEND",b));ok(WideBridgeLog.events==0,"opt in");
        WideBridgeLog.enabled=true;WideAutoObservation.capture(new Intent("wrong",b));ok(WideBridgeLog.events==0,"wrong action");
        WideAutoObservation.capture(new Intent("AUTONAVI_STANDARD_BROADCAST_SEND",b));ok(WideBridgeLog.events==1,"accepted event");
        ok(!WideBridgeLog.last.getBoolean("control_input"),"no control");
        for(int n=0;n<30;n++)WideAutoObservation.capture(new Intent("AUTONAVI_STANDARD_BROADCAST_SEND",b));
        ok(WideBridgeLog.events<=12,"rate limit");
        Bundle telemetry=new Bundle();telemetry.putInt("KEY_TYPE",10001);
        int before=WideBridgeLog.events;
        for(int n=0;n<30;n++)WideAutoObservation.capture(new Intent("AUTONAVI_STANDARD_BROADCAST_SEND",telemetry));
        ok(WideBridgeLog.events==before+12,"independent telemetry quota");
        Bundle nested=new Bundle();nested.putIntArray("routePoints",new int[]{1,2,3,4});nested.putString("token","private-secret");
        Bundle outer=new Bundle();outer.putBundle("EXTRA_ROUTE",nested);
        JSONObject nestedResult=WideAutoObservation.decode(outer);
        ok(nestedResult.getJSONObject("payload").getJSONObject("EXTRA_ROUTE").getJSONArray("routePoints").length()==4,"nested bundle route");
        ok(!nestedResult.toString().contains("private-secret"),"nested privacy");
        ok(WideAutoObservation.priority(13012)&&!WideAutoObservation.priority(10001),"reserved route and lane event classification");
        Bundle flags=new Bundle();
        flags.putString("EXTRA_DRIVE_WAY","{\"drive_way_enabled\":\"true\",\"drive_way_info\":[{\"trafficLaneAdvised\":\"true\"},{\"trafficLaneAdvised\":\"false\"},{\"trafficLaneAdvised\":\"1\"},{\"trafficLaneAdvised\":\"0\"},{\"trafficLaneAdvised\":true},{\"trafficLaneAdvised\":\"private-unknown\"}],\"unknownText\":\"private-other\"}");
        JSONObject lanes=WideAutoObservation.decode(flags).getJSONObject("payload").getJSONObject("EXTRA_DRIVE_WAY");
        ok(lanes.get("drive_way_enabled")==Boolean.TRUE,"string enabled");
        JSONArray rows=lanes.getJSONArray("drive_way_info");
        for(int n=0;n<5;n++)ok(rows.getJSONObject(n).get("trafficLaneAdvised")==Boolean.valueOf(n%2==0),"flag "+n);
        ok(rows.getJSONObject(5).getJSONObject("trafficLaneAdvised").getInt("_string_chars")==15,"invalid string redacted");
        ok(!lanes.toString().contains("private-unknown")&&!lanes.toString().contains("private-other"),"flag privacy");
        Bundle direct=new Bundle(); direct.putString("trafficLaneAdvised","TRUE");
        ok(WideAutoObservation.decode(direct).getJSONObject("payload").get("trafficLaneAdvised")==Boolean.TRUE,"direct bundle flag");
        System.out.println("wide89 diagnostic flag checks passed");
    }
}
