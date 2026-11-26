package com.navipilot.obf;

import java.util.Map;
import org.json.JSONObject;

/** Export the native strategy as an expiring advisory, never as a posted limit. */
public final class WideAmapPreAdjust {
    static final String KEY = "_copilot_amap_pre_adjust";
    static final String AT = "_copilot_amap_pre_adjust_at";
    static boolean valid(int value) { return value >= 10 && value <= 200 && value % 10 == 0; }

    public static JSONObject mark(JSONObject value, Integer target, R4 policy) {
        if (value == null) return null;
        try {
            JSONObject copy = new JSONObject(value.toString());
            copy.remove(KEY); copy.remove(AT); copy.remove("pre_adjust");
            if (target != null && valid(target) && policy != null && policy.e != null
                    && copy.optInt("road_limit_kph", -1) == target) {
                copy.put(KEY, target.intValue());
                copy.put(AT, policy.e.longValue());
            }
            return copy;
        } catch (Exception error) { return null; }
    }

    public static JSONObject merge(String stream, JSONObject original, Map times) {
        JSONObject merged = WideBridge.merge(stream, original, times);
        if (!"speed".equals(stream)) return merged;
        return finish(original, merged, System.currentTimeMillis());
    }

    static JSONObject finish(JSONObject original, JSONObject merged, long now) {
        if (merged == null) return null; // Never revive rejected input.
        try {
            JSONObject result = new JSONObject(merged.toString());
            result.remove(KEY); result.remove(AT); result.remove("pre_adjust");
            // The legacy native policy exposes only a target and timestamp.
            // Neither identifies the maneuver or proves that it is still ahead.
            // Do not export this unbound advisory until its lifecycle is verified.
            // The independent shared-navigation permission is untouched.
            // WideOsmLimit continues to replace road_limit_kph using confirmed TDX/OSM.
            return result.length() == 0 ? null : result;
        } catch (Exception error) { return null; }
    }
}
