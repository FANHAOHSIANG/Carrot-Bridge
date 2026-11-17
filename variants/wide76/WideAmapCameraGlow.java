package com.navipilot.obf;

import android.os.SystemClock;

/** Visual warning only; observes the same validated camera sample queued for the HUD. */
final class WideAmapCameraGlow {
    private static final long MAX_AGE_MS = 2600;
    private static volatile Alert active;

    private static final class Alert {
        final int distance;
        final long time;
        Alert(int distance, long time) { this.distance = distance; this.time = time; }
    }

    // T4: a = normalized camera type, b = metres, c = nullable camera speed limit.
    // Both 10001 navigation updates and 13005 camera broadcasts converge here.
    static void updateCamera(T4 camera) {
        if (camera == null) {
            clear();
            return;
        }
        update(camera.a, camera.b, camera.c == null ? 0 : camera.c.intValue());
    }

    static void update(int type, int distance, int limit) {
        if (WideVariant.navigation() != WideVariant.Navigation.CAR) {
            clear();
            return;
        }
        active = type >= 0 && distance > 0 && limit > 0
            ? new Alert(distance, SystemClock.elapsedRealtime()) : null;
    }

    static void clear() { active = null; }

    static int distance(long now) {
        Alert event = active;
        if (event == null || WideVariant.navigation() != WideVariant.Navigation.CAR
                || now < event.time || now - event.time > MAX_AGE_MS) return 0;
        return event.distance <= 500 ? event.distance : 0;
    }
}
