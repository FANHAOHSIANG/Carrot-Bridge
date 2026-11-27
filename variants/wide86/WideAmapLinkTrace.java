package com.navipilot.obf;
import java.net.URLDecoder;
import java.util.Iterator;
import java.util.Locale;
import org.json.JSONArray;
import org.json.JSONObject;
import org.json.JSONTokener;

/** Bounded copy of authorized navigation JSON for opt-in local analysis, never control. */
public final class WideAmapLinkTrace {
    private static final int MAX_INPUT = 4 * 1024 * 1024;
    private static final int MAX_NODES = 64000, MAX_CHARS = 1500000, MAX_ARRAY = 16384;
    private int nodes, chars, redacted;
    private int nodeLimit = 12000, charLimit = 180000, arrayLimit = 4096;
    private boolean truncated;
    private WideAmapLinkTrace() { }
    public static JSONObject capture(String text) {
        WideAmapLinkTrace copier = new WideAmapLinkTrace();
        JSONObject out = new JSONObject();
        try {
            out.put("schema", 2).put("control_input", false).put("raw_bytes_preserved", false)
                    .put("input_chars", text == null ? 0 : text.length());
            if (text == null || text.length() > MAX_INPUT) {
                out.put("parse_status", "missing_or_oversize");
                copier.truncated = true;
            } else {
                Object value = parse(text);
                if (!(value instanceof JSONObject) && !(value instanceof JSONArray))
                    throw new IllegalArgumentException("structured_value_required");
                // Only route packets get a larger diagnostic budget. Other events keep
                // their previous limits to protect the callback worker.
                if (hasRoute(value)) {
                    copier.nodeLimit = MAX_NODES;
                    copier.charLimit = MAX_CHARS;
                    copier.arrayLimit = MAX_ARRAY;
                }
                Object payload = copier.copy(value, "", 0);
                out.put("payload", payload).put("parse_status", "decoded");
                out.put("observation", observe(payload, copier.truncated));
            }
        } catch (Exception invalid) {
            try { out.put("parse_status", "unparsed"); } catch (Exception ignored) { }
        }
        try { out.put("truncated", copier.truncated).put("redacted_fields", copier.redacted)
                .put("visited_nodes", copier.nodes); } catch (Exception ignored) { }
        return out;
    }
    private static boolean hasRoute(Object value) {
        if (!(value instanceof JSONObject)) return false;
        JSONArray items = ((JSONObject)value).optJSONArray("datas");
        if (items == null) return false;
        for (int i=0; i<Math.min(items.length(),256); i++) {
            JSONObject item = items.optJSONObject(i);
            if (item != null && item.optInt("type",-1)==2) return true;
        }
        return false;
    }
    private static JSONObject observe(Object payload, boolean truncated) throws Exception {
        JSONObject result = new JSONObject().put("control_input",false)
            .put("route_truncated",truncated).put("coordinate_reference","unverified");
        JSONArray observations = new JSONArray();
        if (!(payload instanceof JSONObject)) return result.put("items",observations);
        JSONArray items = ((JSONObject)payload).optJSONArray("datas");
        if (items == null) return result.put("items",observations);
        for (int i=0; i<Math.min(items.length(),256); i++) {
            JSONObject item = items.optJSONObject(i);
            if (item == null) continue;
            int type = item.optInt("type",-1);
            JSONObject d = item.optJSONObject("data");
            if (d == null || (type!=2 && type!=4 && type!=14 && type!=16)) continue;
            JSONObject o = new JSONObject().put("type",type);
            if (type==14) {
                o.put("kind","lane_guidance_raw").put("code_semantics","unverified");
                for (String k : new String[]{"laneCount","eventType"}) copyNumber(d,o,k);
                for (String k : new String[]{"backLane","frontLane","optimalLane","backLaneType","frontLaneType","extensionLane"}) {
                    JSONArray a=d.optJSONArray(k);
                    if(a!=null && a.length()<=64) {
                        boolean numeric=true;
                        for(int j=0;j<a.length();j++) if(!(a.opt(j) instanceof Number)) numeric=false;
                        if(numeric)o.put(k,a);
                    }
                }
            } else if (type==4) {
                o.put("kind","route_progress_raw");
                for (String k:new String[]{"pathID","curManeuverID","curSegIdx","routeRemainDist","segmentRemainDist","split"}) copyNumber(d,o,k);
                JSONObject lane=d.optJSONObject("laneMatchResult");
                if(lane!=null){
                    JSONObject l=new JSONObject();
                    for(String k:new String[]{"laneNum","laneCnt","roadClass"})copyNumber(lane,l,k);
                    l.put("positive_count_reported",lane.optInt("laneCnt",0)>0);
                    o.put("laneMatchResult",l);
                }
            } else if (type==16) {
                o.put("kind","location_raw");
                for(String k:new String[]{"accuracy","heading","speed","currentSegmentIndex","currentLinkIndex","currentPointIndex"})copyNumber(d,o,k);
                JSONObject coords=d.optJSONObject("coords");
                if(coords!=null){
                    JSONObject c=new JSONObject();
                    copyNumber(coords,c,"lat");copyNumber(coords,c,"lon");o.put("coords",c);
                }
            } else {
                o.put("kind","road_route_raw").put("native_lane_centerline",false);
                copyNumber(d,o,"highlightRoute");
            }
            observations.put(o);
        }
        return result.put("items",observations);
    }
    private static void copyNumber(JSONObject from,JSONObject to,String key)throws Exception{
        Object v=from.opt(key);
        if(v instanceof Number && Double.isFinite(((Number)v).doubleValue()))to.put(key,v);
    }
    private Object copy(Object value, String key, int depth) throws Exception {
        if (++nodes > nodeLimit || chars >= charLimit || depth > 20) {
            truncated = true; return "[capture_limit]";
        }
        String k = key.toLowerCase(Locale.ROOT).replace("_", "").replace("-", "");
        if (k.matches(".*(token|secret|password|signature|cookie|authorization|apikey|aeskey|sessionid).*")
                || k.matches("key|nonce|iv|uid|userid|accountid|email|phone|phonenumber")) {
            redacted++; return "[redacted]";
        }
        if (value == null || value == JSONObject.NULL) return JSONObject.NULL;
        if (value instanceof JSONObject) {
            JSONObject input = (JSONObject) value, result = new JSONObject();
            Iterator<String> keys = input.keys(); int count = 0;
            while (keys.hasNext()) {
                String name = keys.next();
                if (++count > 256 || name.length() > 128 || nodes >= nodeLimit || chars >= charLimit) {
                    truncated = true; break;
                }
                chars += name.length();
                result.put(name, copy(input.opt(name), name, depth + 1));
            }
            return result;
        }
        if (value instanceof JSONArray) {
            JSONArray input = (JSONArray) value, result = new JSONArray();
            for (int i = 0; i < input.length(); i++) {
                if (i >= arrayLimit || nodes >= nodeLimit || chars >= charLimit) { truncated = true; break; }
                result.put(copy(input.opt(i), key, depth + 1));
            }
            return result;
        }
        if (value instanceof Number || value instanceof Boolean) { chars += 24; return value; }
        if (!(value instanceof String)) { redacted++; return "[unsupported_value]"; }
        String text = ((String) value).trim(), lower = text.toLowerCase(Locale.ROOT);
        boolean encoded = lower.startsWith("%7b") || lower.startsWith("%5b") || lower.startsWith("%22");
        if (encoded || text.startsWith("{") || text.startsWith("[") || text.startsWith("\"")) {
            if (text.length() <= MAX_INPUT && depth < 20) {
                try {
                    if (encoded) text = URLDecoder.decode(text.replace("+", "%2B"), "UTF-8");
                    return copy(parse(text), key, depth + 1);
                } catch (Exception invalid) { }
            } else truncated = true;
        }
        if (k.matches("nextroadname|nextroutename|curroadname|roadname")) {
            if (text.length() > 200) { text = text.substring(0, 200); truncated = true; }
            chars += text.length(); return text.replaceAll("[\\p{Cntrl}]", " ");
        }
        if (k.equals("status") && (text.equals("success") || text.equals("error"))) {
            chars += text.length(); return text;
        }
        redacted++; chars += 32;
        return new JSONObject().put("_string_chars", text.length());
    }
    private static Object parse(String text) throws Exception {
        int depth = 0; char quote = 0; boolean escaped = false;
        for (int i = 0; i < text.length(); i++) {
            char ch = text.charAt(i);
            if (quote != 0) {
                if (escaped) escaped = false;
                else if (ch == '\\') escaped = true;
                else if (ch == quote) quote = 0;
            } else if (ch == '"' || ch == '\'') quote = ch;
            else if (ch == '{' || ch == '[') {
                if (++depth > 64) throw new IllegalArgumentException("depth");
            } else if (ch == '}' || ch == ']') depth--;
        }
        JSONTokener parser = new JSONTokener(text);
        Object result = parser.nextValue();
        if (parser.nextClean() != 0) throw new IllegalArgumentException("trailing");
        return result;
    }
}

