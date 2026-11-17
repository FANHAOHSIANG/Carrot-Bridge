package com.navipilot.obf;
import android.content.Context;
import android.content.SharedPreferences;
import java.util.Map;
import org.json.JSONObject;
/** Selected-provider permission for receiver-side turn pre-adjust. */
public final class WideSharedPreAdjust {
 private static volatile SharedPreferences preferences;
 public static void init(Context c) {
  if(c != null) preferences=c.getApplicationContext().getSharedPreferences("CarrotAmap",0);
 }
 public static JSONObject decorate(String stream, JSONObject value, Map timestamps) {
  if(!"navigation_status".equals(stream)||value==null)return value;
  SharedPreferences p=preferences;
  Object stamp=timestamps==null?null:timestamps.get(stream);
  return status(value,WideAmapSource.preAdjustSource(),WideAmapSource.preAdjustSelectedAt(),
    stamp instanceof Long?(Long)stamp:0,System.currentTimeMillis(),
    p!=null&&p.getBoolean("smart_speed_enabled",true));
 }
 static JSONObject status(JSONObject value,String source,long selectedAt,long generated,long now,boolean enabled) {
  if(value==null)return null;
  try {
   JSONObject result=new JSONObject(value.toString()); result.remove("pre_adjust_control");
   if(enabled && ("amap_auto".equals(source)||"amap_phone".equals(source)||"google_noo".equals(source))
      && Boolean.TRUE.equals(value.opt("guidance_active"))&&!value.optBoolean("off_route",false)
      && generated>0&&generated>=selectedAt&&now>=generated&&now-generated<2000) {
    result.put("pre_adjust_control",new JSONObject().put("source",source).put("enabled",true).put("generated_at_ms",generated));
   }
   return result;
  }catch(Exception invalid){return null;}
 }
}
