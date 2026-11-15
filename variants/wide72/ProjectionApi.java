package com.navipilot.obf;

import android.content.Context;
import android.view.View;
import android.widget.FrameLayout;
import android.widget.LinearLayout;

final class WideDirect {
    static final class Pane extends LinearLayout {
        boolean shield;
        FrameLayout body;
        Pane(Context context) { super(context); }
        native void menu(View anchor);
    }
}
