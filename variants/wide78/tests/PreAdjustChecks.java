package com.navipilot.obf;
import org.json.JSONObject;

public class PreAdjustChecks {
    static int checks;
    static void check(boolean ok) { checks++; if (!ok) throw new AssertionError("check " + checks); }
    static JSONObject input(int target, long at) {
        return WideAmapPreAdjust.mark(new JSONObject().put("road_limit_kph", target)
                .put("sdi", new JSONObject().put("distance_m", 350)), target, new R4(at));
    }
    public static void main(String[] args) {
        JSONObject original = input(60, 10000);
        JSONObject result = WideAmapPreAdjust.finish(original, original, 10500);
        check(!result.has("pre_adjust"));
        check(result.getInt("road_limit_kph") == 60);
        check(!result.has(WideAmapPreAdjust.KEY) && !result.has(WideAmapPreAdjust.AT));
        check(result.getJSONObject("sdi").getInt("distance_m") == 350);
        check(original.has(WideAmapPreAdjust.KEY)); // No mutation of pending/native input.
        for (long now : new long[]{9999, 12000, 100000})
            check(!WideAmapPreAdjust.finish(original, original, now).has("pre_adjust"));
        check(WideAmapPreAdjust.finish(original, null, 10500) == null);
        for (int target : new int[]{0, 5, 65, 210}) {
            JSONObject bad = input(target, 10000);
            check(!WideAmapPreAdjust.finish(bad, bad, 10500).has("pre_adjust"));
        }
        WideAmapSource.allowed = false;
        check(!WideAmapPreAdjust.finish(original, original, 10500).has("pre_adjust"));
        WideAmapSource.allowed = true; WideAmapSource.selectedSince = 10001;
        check(!WideAmapPreAdjust.finish(original, original, 10500).has("pre_adjust"));
        WideAmapSource.selectedSince = 1;
        JSONObject disabled = WideAmapPreAdjust.mark(original, null, new R4(10000));
        check(!WideAmapPreAdjust.finish(disabled, disabled, 10500).has("pre_adjust"));
        JSONObject noStamp = WideAmapPreAdjust.mark(original, 60, null);
        check(!WideAmapPreAdjust.finish(noStamp, noStamp, 10500).has("pre_adjust"));
        JSONObject merged = new JSONObject(original.toString()).put("road_limit_kph", 100);
        result = WideAmapPreAdjust.finish(original, merged, 10500);
        check(result.getInt("road_limit_kph") == 100); // Advisory cannot relabel posted limit.
        check(!result.has("pre_adjust"));
        for (long at = 10000; at < 30000; at += 1000) {
            JSONObject fresh = input(60, at);
            check(!WideAmapPreAdjust.finish(fresh, new JSONObject(fresh.toString()).put("road_limit_kph", 100), at).has("pre_adjust"));
        }
        System.out.println(checks + " pre-adjust checks passed");
    }
}
