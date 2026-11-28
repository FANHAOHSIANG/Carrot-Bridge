package com.navipilot.obf;
import org.json.*;
/** AMap accepted-packet lane candidate normalizer; no control, no route association. */
public final class WideLaneCandidate {
    private WideLaneCandidate(){}
    private static int integer(Object o,int max){
        if(!(o instanceof Number))return -1;
        double d=((Number)o).doubleValue();
        return Double.isFinite(d)&&d>=0&&d<=max&&d==Math.floor(d)?(int)d:-1;
    }
    private static int icon(Object o){
        if(o instanceof String && ((String)o).matches("[0-9]{1,5}"))return integer(Integer.valueOf((String)o),65535);
        return integer(o,65535);
    }
    private static Boolean flag(Object o){
        if(o instanceof Boolean)return (Boolean)o;
        if(o instanceof String){
            String s=((String)o).trim();
            if("true".equalsIgnoreCase(s)||"1".equals(s))return Boolean.TRUE;
            if("false".equalsIgnoreCase(s)||"0".equals(s))return Boolean.FALSE;
        }
        int i=integer(o,1);return i==0?Boolean.FALSE:i==1?Boolean.TRUE:null;
    }
    private static JSONObject result(String source,String state,JSONArray rows)throws JSONException{
        return new JSONObject().put("source",source).put("status",state)
            .put("count",rows==null?JSONObject.NULL:rows.length()).put("lanes",rows==null?JSONObject.NULL:rows)
            .put("absolute_lane_index",JSONObject.NULL).put("absolute_mapping_verified",false)
            .put("advice_semantics","candidate_screen_validation_pending").put("control_input",false);
    }
    private static JSONObject row(int index,int back,Object front,Boolean advice)throws JSONException{
        return new JSONObject().put("index",index).put("back_code",back).put("front_code",front)
            .put("advised",advice==null?JSONObject.NULL:advice);
    }
    private static JSONObject finish(String source,JSONArray rows)throws JSONException{
        boolean yes=false,unknown=false;
        for(int i=0;i<rows.length();i++){
            Object a=rows.getJSONObject(i).opt("advised");
            yes|=Boolean.TRUE.equals(a);unknown|=a==null||a==JSONObject.NULL;
        }
        return result(source,yes?"recommendation_candidate":unknown?"advice_unknown":"no_positive_advice",rows);
    }
    public static JSONObject auto(JSONObject d)throws JSONException{
        String source="amap_auto_13012";
        Boolean enabled=flag(d==null?null:d.opt("drive_way_enabled"));
        if(Boolean.FALSE.equals(enabled))return result(source,"withdrawn",null);
        if(!Boolean.TRUE.equals(enabled))return result(source,"missing_enabled",null);
        int n=integer(d.opt("drive_way_size"),32);
        JSONArray a=d.optJSONArray("drive_way_info");
        if(n<1||a==null||a.length()!=n)return result(source,"invalid_count",null);
        JSONObject[] ordered=new JSONObject[n];
        for(int k=0;k<n;k++){
            JSONObject r=a.optJSONObject(k);
            if(r==null)return result(source,"invalid_lane",null);
            int i=integer(r.opt("drive_way_number"),n-1),c=icon(r.opt("drive_way_lane_Back_icon"));
            if(i<0||c<0||ordered[i]!=null)return result(source,"invalid_lane",null);
            ordered[i]=row(i,c,JSONObject.NULL,flag(r.opt("trafficLaneAdvised")));
        }
        JSONArray rows=new JSONArray();for(JSONObject r:ordered)rows.put(r);
        return finish(source,rows);
    }
    public static JSONObject link(JSONObject d)throws JSONException{
        String source="amap_link_14";
        int n=integer(d==null?null:d.opt("laneCount"),32);
        if(n==0)return result(source,"withdrawn",null);
        JSONArray b=d==null?null:d.optJSONArray("backLane"),f=d==null?null:d.optJSONArray("frontLane");
        if(n<1||b==null||f==null||b.length()!=n||f.length()!=n)return result(source,"invalid_count",null);
        JSONArray rows=new JSONArray();
        for(int i=0;i<n;i++){
            int back=integer(b.opt(i),255),front=integer(f.opt(i),255);
            if(back<0||front<0)return result(source,"invalid_lane",null);
            rows.put(row(i,back,front,front!=255));
        }
        return finish(source,rows);
    }
}
