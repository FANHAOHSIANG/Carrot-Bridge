package com.navipilot.obf;
import org.json.*;
public final class ObservationChecks {
  static void check(boolean b,String m){if(!b)throw new AssertionError(m);}
  static JSONObject packet(int type,JSONObject data)throws Exception{
    return new JSONObject().put("bizType",113).put("datas",new JSONArray().put(new JSONObject().put("type",type).put("data",data)));
  }
  public static void main(String[] args)throws Exception{
    JSONArray pts=new JSONArray();
    for(int i=0;i<8000;i++)pts.put(new JSONObject().put("lat",24.0+i*0.00001).put("lon",121.0));
    JSONObject route=new JSONObject().put("highlightRoute",7).put("info",new JSONObject().put("7",new JSONObject().put("points",pts).put("token","secret")));
    JSONObject cap=WideAmapLinkTrace.capture(packet(2,route).toString());
    check(!cap.getBoolean("truncated"),"long route");
    check(cap.getJSONObject("payload").getJSONArray("datas").getJSONObject(0).getJSONObject("data").getJSONObject("info").getJSONObject("7").getJSONArray("points").length()==8000,"all points retained");
    check(!cap.toString().contains("\"secret\""),"redaction");
    JSONObject lane=new JSONObject().put("laneCount",4).put("backLane",new JSONArray("[1,0,0,21]")).put("frontLane",new JSONArray("[255,0,0,255]"));
    JSONObject obs=WideAmapLinkTrace.capture(packet(14,lane).toString()).getJSONObject("observation");
    check(obs.getJSONArray("items").getJSONObject(0).getJSONArray("frontLane").getInt(0)==255,"raw code");
    JSONObject candidate=obs.getJSONArray("items").getJSONObject(0).getJSONObject("lane_candidate");
    check("recommendation_candidate".equals(candidate.getString("status")),"app Link candidate");
    check(!candidate.getJSONArray("lanes").getJSONObject(0).getBoolean("advised")&&candidate.getJSONArray("lanes").getJSONObject(1).getBoolean("advised"),"Link advice");
    check(candidate.isNull("absolute_lane_index")&&!candidate.getBoolean("control_input"),"no lane position or control");
    check("invalid_count".equals(WideLaneCandidate.link(new JSONObject().put("laneCount",3)).getString("status")),"incomplete");
    check(!obs.getBoolean("control_input"),"read only");
    JSONObject match=new JSONObject().put("laneMatchResult",new JSONObject().put("laneNum",0).put("laneCnt",0));
    JSONObject m=WideAmapLinkTrace.capture(packet(4,match).toString()).getJSONObject("observation").getJSONArray("items").getJSONObject(0);
    check(!m.getJSONObject("laneMatchResult").getBoolean("positive_count_reported"),"zero is not verified match");
    JSONObject nonroute=WideAmapLinkTrace.capture(packet(14,new JSONObject().put("large",pts)).toString());
    check(nonroute.getBoolean("truncated"),"ordinary limits retained");
    check(!WideAmapLinkTrace.capture("not json").has("payload"),"invalid");
    System.out.println("wide86 observation checks passed");
  }
}
