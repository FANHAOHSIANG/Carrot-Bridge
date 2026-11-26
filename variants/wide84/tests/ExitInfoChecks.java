package com.navipilot.obf;
import android.content.Intent;
import android.os.Bundle;
import java.util.Map;
import org.json.JSONObject;
public class ExitInfoChecks {
 static int checks;
 static void check(boolean b) { if(!b)throw new AssertionError("check "+checks);checks++; }
 static JSONObject out(JSONObject original,long stamp) {
  return WideAmapExitInfo.decorate("guidance_current",original,Map.of("guidance_current",stamp));
 }
 public static void main(String[] args) throws Exception {
  JSONObject g=new JSONObject().put("distance_m",800).put("turn_type",51);
  WideAmapSource.allowed=true; WideAmapSource.selectedSince=1;
  WideAmapExitInfo.capture(new Intent(new Bundle().put("EXIT_NAME_INFO","Example exit")
      .put("CUR_SEG_NUM",12).put("CUR_POINT_NUM",2).put("SEG_REMAIN_DIS",800)
      .put("ROUTE_REMAIN_DIS",12000).put("ROUTE_ALL_DIS",15000).put("NEW_ICON",12)
      .put("EXTRA_DRIVE_WAY",new int[]{1,2}).put("CUR_ROAD_NAME","Main")));
  long now=System.currentTimeMillis();
  JSONObject r=out(g,now);
  JSONObject info=r.getJSONObject("amap_exit_info"), f=info.getJSONObject("fields");
  check(info.getString("scope").equals("display_only"));
  check(f.getString("EXIT_NAME_INFO").equals("Example exit"));
  check(f.getInt("CUR_SEG_NUM")==12);
  check(f.getInt("ROUTE_REMAIN_DIS")==12000);
  check(f.getInt("ROUTE_ALL_DIS")==15000);
  check(f.getInt("NEW_ICON")==12);
  check(f.getJSONArray("EXTRA_DRIVE_WAY").length()==2);
  check(r.getInt("distance_m")==800 && r.getInt("turn_type")==51);
  check(!g.has("amap_exit_info"));
  check(!out(g,now-600).has("amap_exit_info"));
  check(WideAmapExitInfo.decorate("speed",g,Map.of())==g);
  WideAmapSource.allowed=false;
  check(!out(g,now).has("amap_exit_info"));
  WideAmapSource.allowed=true;
  WideAmapExitInfo.capture(new Intent(new Bundle().put("CUR_SEG_NUM",-1).put("EXIT_NAME_INFO"," ")));
  check(!out(g,System.currentTimeMillis()).has("amap_exit_info"));
  WideAmapExitInfo.capture(null);
  check(!out(g,System.currentTimeMillis()).has("amap_exit_info"));
  System.out.println(checks+" display-only exit metadata checks passed");
 }
}
