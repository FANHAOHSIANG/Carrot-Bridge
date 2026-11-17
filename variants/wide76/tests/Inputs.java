package com.navipilot.obf;

class T4 {
    public final int a, b;
    public final Integer c;
    T4(int type, int distance, Integer limit) { a = type; b = distance; c = limit; }
}
class WideVariant {
    enum Navigation { CAR, PHONE, GOOGLE }
    static Navigation selected = Navigation.CAR;
    static Navigation navigation() { return selected; }
}
