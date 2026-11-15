package com.navipilot.obf;

import android.content.Context;
import android.graphics.Bitmap;
import android.os.SystemClock;
import android.util.Log;
import android.view.Menu;
import android.view.TextureView;
import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

final class HudMapVideo {
    private static final String TAG = "CarrotHudMap";
    private static final int MENU_ID = 90;
    private static final long INTERVAL_MS = 200;
    private static final long RETRY_MS = 2000;
    private static final ExecutorService ENCODE = Executors.newSingleThreadExecutor();
    private static RenderStream stream;
    private static WideDirect.Pane active;
    private static boolean enabled, loaded, busy, navigationStopped;
    private static long epoch, lastCapture;

    private HudMapVideo() {}

    static synchronized void addMenu(WideDirect.Pane pane, Menu menu) {
        if (pane.shield || !isAmap(WideVariant.packageName())) return;
        loadPreference(pane.getContext());
        menu.add(0, MENU_ID, 25, "HUD 地圖影像（測試）").setCheckable(true).setChecked(enabled);
    }

    static synchronized boolean menuClick(WideDirect.Pane pane, int id) {
        if (id != MENU_ID || pane.shield || !isAmap(WideVariant.packageName())) return false;
        loadPreference(pane.getContext());
        enabled = !enabled;
        pane.getContext().getSharedPreferences("hud_map_video", Context.MODE_PRIVATE)
            .edit().putBoolean("enabled", enabled).apply();
        if (!enabled) clear(pane);
        return true;
    }

    private static void loadPreference(Context context) {
        if (!loaded) {
            enabled = context.getSharedPreferences("hud_map_video", Context.MODE_PRIVATE)
                .getBoolean("enabled", false);
            loaded = true;
        }
    }

    private static boolean isAmap(String name) {
        return "com.autonavi.amapauto".equals(name) || "com.autonavi.minimap".equals(name);
    }

    static boolean handles(String kind, String name) {
        return "json".equals(kind) || ("render".equals(kind) && "map_main".equals(name));
    }

    static synchronized void prepareManifest(QG manifest) {
        NW config = manifest.c.get("render:map_main");
        if (config != null && config.e) {
            config.f.put("codec", "jpeg");
            config.f.put("width", 640);
            config.f.put("height", 360);
            config.f.put("fps", 5);
            config.f.put("jpeg_quality", 72);
        }
    }

    static synchronized void useManifest(XG owner, QG manifest) {
        if (stream != null) stream.close();
        stream = null;
        epoch++;
        NW config = manifest.c.get("render:map_main");
        if (config == null || !config.e || config.d <= 0 || manifest.b <= 0 ||
                manifest.a == null || !manifest.a.matches("[A-Za-z0-9_-]{8,64}")) return;
        if (owner.e == null || owner.f < 1 || owner.f > 65535) return;
        final String authority = owner.e.indexOf(':') >= 0 && !owner.e.startsWith("[")
            ? "[" + owner.e + "]" : owner.e;
        navigationStopped = false;
        stream = new RenderStream(owner, "ws://" + authority + ":" + owner.f
            + "/api/navi/ws/v2/render/" + manifest.a + "/map_main", config.d, manifest.b);
    }

    static synchronized void observeStatus(XG owner, String name, boolean present, JSONObject value) {
        if (!"navigation_status".equals(name) || stream == null || stream.owner != owner) return;
        if (!present || value == null || value.optBoolean("off_route", false)
                || "idle".equals(value.optString("mode"))) {
            navigationStopped = true;
            if (active != null) clear(active);
        } else if (value.optBoolean("guidance_active", false) || "guiding".equals(value.optString("mode"))) {
            navigationStopped = false;
        }
    }

    static synchronized void reset(XG owner) {
        if (stream == null || stream.owner != owner) return;
        stream.close();
        stream = null;
        epoch++;
    }

    static synchronized void clear(WideDirect.Pane pane) {
        if (active != pane) return;
        active = null;
        epoch++;
        if (stream != null) stream.clear();
    }

    static void onFrame(WideDirect.Pane pane) {
        if (pane.shield) return;
        final long captureTime = System.currentTimeMillis();
        final long now = SystemClock.elapsedRealtime();
        final long token;
        final RenderStream target;
        TextureView view = pane.texture;
        synchronized (HudMapVideo.class) {
            loadPreference(pane.getContext());
            String source = pane.session == null ? null : pane.session.hudMapPackage;
            if (!enabled || navigationStopped || !pane.frameShown || pane.session == null || pane.session.closed ||
                    !isAmap(source) || !source.equals(WideVariant.packageName()) || !view.isAvailable()) {
                clear(pane);
                return;
            }
            if (active != pane) {
                if (active != null) clear(active);
                active = pane;
                epoch++;
            }
            target = stream;
            if (target == null || busy || now - lastCapture < INTERVAL_MS || !target.ready(now)) return;
            token = epoch;
            lastCapture = now;
            busy = true;
        }
        Bitmap capture = null;
        try {
            int w = view.getWidth(), h = view.getHeight();
            if (w > 0 && h > 0) {
                float ratio = Math.min(1f, Math.min(640f / w, 360f / h));
                capture = view.getBitmap(Math.max(1, Math.round(w * ratio)), Math.max(1, Math.round(h * ratio)));
            }
        } catch (RuntimeException e) {
            Log.w(TAG, "Projection frame unavailable", e);
        }
        if (capture == null) {
            synchronized (HudMapVideo.class) { busy = false; }
            return;
        }
        final Bitmap frame = capture;
        ENCODE.execute(() -> {
            try {
                ByteArrayOutputStream jpeg = new ByteArrayOutputStream();
                if (!frame.compress(Bitmap.CompressFormat.JPEG, 72, jpeg) ||
                        jpeg.size() == 0 || jpeg.size() > 188000) return;
                byte[] image = jpeg.toByteArray();
                synchronized (HudMapVideo.class) {
                    if (epoch != token || stream != target || active != pane || !enabled ||
                            pane.session == null || !java.util.Objects.equals(WideVariant.packageName(), pane.session.hudMapPackage) ||
                            SystemClock.elapsedRealtime() - now > 600) return;
                    target.send(image, frame.getWidth(), frame.getHeight(), captureTime);
                }
            } catch (RuntimeException e) {
                Log.w(TAG, "Unable to supply HUD map frame", e);
            } finally {
                frame.recycle();
                synchronized (HudMapVideo.class) { busy = false; }
            }
        });
    }

    // All state is guarded by HudMapVideo.class. Existing navigation transport owns its control socket.
    private static final class RenderStream {
        final XG owner;
        final String url;
        final int handle, revision;
        long sequence, nextConnect;
        mO socket;
        Listener listener;
        boolean opened, sent, pendingClear;

        RenderStream(XG owner, String url, int handle, int revision) {
            this.owner = owner; this.url = url; this.handle = handle; this.revision = revision;
        }

        boolean ready(long now) {
            if (socket == null && now >= nextConnect) {
                nextConnect = now + RETRY_MS;
                try {
                    Wx request = new Wx();
                    request.n(url);
                    listener = new Listener(this);
                    socket = owner.b.a(request.e(), listener);
                } catch (RuntimeException e) {
                    Log.w(TAG, "Unable to open HUD map stream", e);
                }
            }
            if (opened && pendingClear) clear();
            return opened && !pendingClear;
        }

        void send(byte[] bytes, int w, int h, long time) {
            if (opened && enqueue(HudMapPacket.jpeg(handle, revision, sequence + 1, time, w, h, bytes), false)) {
                sequence++;
                sent = true;
            }
        }

        void clear() {
            if (!sent) return;
            pendingClear = !enqueue(HudMapPacket.clear(handle, revision, sequence + 1,
                System.currentTimeMillis()), true);
            if (!pendingClear) {
                sequence++;
                sent = false;
            }
        }

        private boolean enqueue(byte[] packet, boolean clearPacket) {
            mO ws = socket;
            if (ws == null || !opened) return false;
            synchronized (ws) {
                if (ws.q || ws.t || (!clearPacket && ws.p != 0) || ws.p + packet.length > 380000) return false;
                ws.o.add(new kO(new uc(packet), 2));
                ws.p += packet.length;
                ws.g();
                return true;
            }
        }

        void lost(mO ws) {
            if (socket != ws) return;
            opened = false;
            socket = null;
            listener = null;
            nextConnect = SystemClock.elapsedRealtime() + RETRY_MS;
        }

        void close() {
            clear();
            if (socket != null) {
                if (opened) socket.c("map stream ended", 1000);
                else socket.a();
            }
            socket = null;
            listener = null;
            opened = false;
        }
    }

    private static final class Listener extends VQ {
        private final RenderStream target;
        Listener(RenderStream target) { this.target = target; }
        @Override public void r(s30 websocket) {
            mO ws = (mO) websocket;
            synchronized (HudMapVideo.class) {
                if (stream == target && target.listener == this && target.socket == ws) target.opened = true;
                else ws.a();
            }
        }
        @Override public void n(mO ws, int code, String reason) {
            synchronized (HudMapVideo.class) { target.lost(ws); }
            ws.c("map stream closed", 1000);
        }
        @Override public void o(Exception ex, IP response) {
            synchronized (HudMapVideo.class) {
                if (stream == target && target.listener == this && target.socket != null) target.lost(target.socket);
            }
        }
        @Override public void q(mO ws, String text) {}
        @Override public void m(String reason, int code) {}
        @Override public String j(byte[] b, int start, int end) { return ""; }
        @Override public int k(String s, byte[] b, int start, int end) { return 0; }
        @Override public int s(byte[] b, int start, int end) { return 0; }
    }
}
