package com.navipilot.obf;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;

final class HudMapPacket {
    private HudMapPacket() {}

    static byte[] jpeg(int handle, int revision, long seq, long time, int width, int height, byte[] image) {
        if (width < 1 || width > 640 || height < 1 || height > 360 || image.length == 0 || image.length > 188000)
            throw new IllegalArgumentException("Unsupported HUD image");
        return packet(handle, revision, seq, time, 1, 2, 1, width, height, image);
    }

    static byte[] clear(int handle, int revision, long seq, long time) {
        return packet(handle, revision, seq, time, 4, 2, 0, 0, 0, new byte[0]);
    }

    private static byte[] packet(int handle, int revision, long seq, long time,
                                 int kind, int format, int flags, int width, int height, byte[] bytes) {
        if (handle <= 0 || revision <= 0 || seq <= 0 || time <= 0)
            throw new IllegalArgumentException("Invalid HUD map stream identity");
        return ByteBuffer.allocate(40 + bytes.length).order(ByteOrder.BIG_ENDIAN)
            .putInt(0x434e5632).put((byte) 2).put((byte) kind).put((byte) format).put((byte) flags)
            .putInt(handle).putInt(revision).putLong(seq).putLong(time).putInt(bytes.length)
            .putShort((short) width).putShort((short) height).put(bytes).array();
    }
}
