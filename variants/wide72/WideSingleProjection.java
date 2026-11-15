package com.navipilot.obf;

import android.app.Activity;
import android.content.Context;
import android.content.ContextWrapper;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.PopupMenu;

final class WideSingleProjection {
    static boolean enabled;
    private static final String PREFS = "wide_layout_preferences";
    private static final String KEY = "map_projection_only";

    static void load(Activity activity) {
        enabled = activity.getSharedPreferences(PREFS, 0).getBoolean(KEY, false);
    }

    static void addOption(PopupMenu popup, View anchor) {
        popup.getMenu().add(0, 0x4342, 13, enabled ? "顯示分區二" : "關閉分區二")
            .setOnMenuItemClickListener(item -> {
                Context context = anchor.getContext();
                while (context instanceof ContextWrapper && !(context instanceof Activity)) {
                    context = ((ContextWrapper) context).getBaseContext();
                }
                if (context instanceof Activity activity) {
                    activity.getSharedPreferences(PREFS, 0).edit().putBoolean(KEY, !enabled).apply();
                    activity.recreate();
                }
                return true;
            });
    }

    static void addMapMenu(WideDirect.Pane pane) {
        if (!enabled || pane.shield) return;
        Button button = new Button(pane.getContext());
        button.setText("⋯");
        button.setContentDescription("分區一投屏選項");
        button.setOnClickListener(pane::menu);
        float density = pane.getResources().getDisplayMetrics().density;
        FrameLayout.LayoutParams params = new FrameLayout.LayoutParams(
            Math.round(48 * density), Math.round(48 * density), Gravity.BOTTOM | Gravity.END);
        params.setMarginEnd(Math.round(8 * density));
        params.bottomMargin = Math.round(8 * density);
        pane.body.addView(button, params);
    }
}
