package com.navipilot.obf;
import org.json.JSONObject;
public final class SharedChecks {
 static int checks;
 static void check(boolean b){checks++;if(!b)throw new AssertionError("check "+checks);}
 public static void main(String[] args)throws Exception{
  for(String source:new String[]{"amap_auto","amap_phone","google_noo"}){
   JSONObject input=new JSONObject().put("guidance_active",true).put("off_route",false);
   check(WideSharedPreAdjust.status(input,source,100,1000,1500,true).getJSONObject("pre_adjust_control").getString("source").equals(source));
   check(!input.has("pre_adjust_control"));
   check(!WideSharedPreAdjust.status(input,source,100,1000,1500,false).has("pre_adjust_control"));
   check(!WideSharedPreAdjust.status(input,source,100,1000,3000,true).has("pre_adjust_control"));
   check(!WideSharedPreAdjust.status(input,source,100,2000,1500,true).has("pre_adjust_control"));
   check(!WideSharedPreAdjust.status(input,source,1100,1000,1500,true).has("pre_adjust_control"));
   input.put("off_route",true);
   check(!WideSharedPreAdjust.status(input,source,100,1000,1500,true).has("pre_adjust_control"));
   input.put("off_route",false).put("guidance_active",false);
   check(!WideSharedPreAdjust.status(input,source,100,1000,1500,true).has("pre_adjust_control"));
  }
  check(!WideSharedPreAdjust.status(new JSONObject().put("guidance_active",true),"unknown",100,1000,1500,true).has("pre_adjust_control"));
  System.out.println(checks+" shared-provider checks passed");
 }
}
