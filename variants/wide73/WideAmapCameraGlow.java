package com.navipilot.obf;

import android.os.SystemClock;

final class WideAmapCameraGlow {
    private record Alert(int distance, long time) {}
    private static volatile Alert active;
    private static final long MAX_AGE_MS = 2600;

    static void update(int type, int distance, int limit) {
        if (WideVariant.navigation() != WideVariant.Navigation.CAR) return;
        active = type >= 0 && distance > 0 && limit > 0
            ? new Alert(distance, SystemClock.elapsedRealtime()) : null;
    }

    static void clear() {
        active = null;
    }

    static int distance(long now) {
        Alert event = active;
        if (event == null || WideVariant.navigation() != WideVariant.Navigation.CAR
                || now < event.time() || now - event.time() > MAX_AGE_MS) return 0;
        return event.distance() <= 500 ? event.distance() : 0;
    }
}
