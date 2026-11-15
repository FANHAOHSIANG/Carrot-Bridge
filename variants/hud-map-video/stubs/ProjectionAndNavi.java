package com.navipilot.obf;

import android.view.TextureView;
import android.widget.LinearLayout;
import java.util.ArrayDeque;
import java.util.LinkedHashMap;

// Compile-time declarations pinned to the signed wide.70 APK. Never packaged.
final class WideDirect {
    static final class Session { volatile boolean closed; String hudMapPackage; }
    static final class Pane extends LinearLayout {
        Pane() { super(null); }
        boolean shield;
        boolean frameShown;
        Session session;
        TextureView texture;
    }
}
final class WideVariant { static String packageName() { return null; } }
final class XG { kI b; String e; int f; }
final class QG { String a; int b; LinkedHashMap<String, NW> c; }
final class NW { int d; boolean e; LinkedHashMap<String, Object> f; }
final class kI { mO a(tN r, VQ l) { return null; } }
final class Wx { void n(String url) {} tN e() { return null; } }
final class tN {}
final class uc { uc(byte[] data) {} }
final class kO { kO(uc data, int opcode) {} }
interface s30 {}
final class mO implements s30 {
    ArrayDeque<Object> o;
    long p;
    boolean q, t;
    void g() {}
    boolean c(String reason, int code) { return false; }
    void a() {}
}
final class IP {}
abstract class VQ {
    abstract String j(byte[] b, int start, int end);
    abstract int k(String s, byte[] b, int start, int end);
    abstract void m(String reason, int code);
    abstract void n(mO ws, int code, String reason);
    abstract void o(Exception ex, IP response);
    abstract void q(mO ws, String text);
    abstract void r(s30 ws);
    abstract int s(byte[] b, int start, int end);
}
