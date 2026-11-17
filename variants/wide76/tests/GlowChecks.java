package com.navipilot.obf;
import android.os.SystemClock;

public class GlowChecks {
    private static int count;
    static void expect(int expected, long now) {
        int actual = WideAmapCameraGlow.distance(now);
        if (actual != expected) throw new AssertionError("expected " + expected + ", got " + actual);
        count++;
    }
    public static void main(String[] args) {
        // Normalized samples from either accepted broadcast use the same consumer.
        WideAmapCameraGlow.updateCamera(new T4(1, 501, 50)); expect(0, 10000);
        WideAmapCameraGlow.updateCamera(new T4(1, 500, 50)); expect(500, 10000);
        WideAmapCameraGlow.updateCamera(new T4(1, 350, 50)); expect(350, 10000);
        expect(350, 12600); expect(0, 12601); expect(0, 9999);
        SystemClock.now = 13000;
        WideAmapCameraGlow.updateCamera(new T4(1, 200, 50)); expect(200, 13000);
        WideAmapCameraGlow.updateCamera(null); expect(0, 13000);
        for (T4 invalid : new T4[] {new T4(-1, 350, 50), new T4(1, 0, 50),
                new T4(1, -1, 50), new T4(1, 350, null), new T4(1, 350, 0)}) {
            WideAmapCameraGlow.updateCamera(new T4(1, 350, 50));
            WideAmapCameraGlow.updateCamera(invalid); expect(0, 13000);
        }
        WideAmapCameraGlow.updateCamera(new T4(1, 350, 50));
        WideVariant.selected = WideVariant.Navigation.GOOGLE; expect(0, 13000);
        WideAmapCameraGlow.updateCamera(new T4(1, 200, 50));
        WideVariant.selected = WideVariant.Navigation.CAR; expect(0, 13000);
        WideAmapCameraGlow.updateCamera(new T4(1, 350, 50));
        WideAmapCameraGlow.clear(); expect(0, 13000);
        System.out.println(count + " camera glow checks passed");
    }
}
