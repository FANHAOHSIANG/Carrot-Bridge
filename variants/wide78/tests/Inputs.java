package com.navipilot.obf;
import java.util.Map;
import org.json.JSONObject;
class R4 { public Long e; R4(long at) { e = at; } }
class WideBridge { static JSONObject merge(String s, JSONObject o, Map t) { return o; } }
class WideAmapSource {
    static boolean allowed = true;
    static long selectedSince = 1;
    static boolean preAdjustAllowed(long at) { return allowed && at >= selectedSince; }
}
