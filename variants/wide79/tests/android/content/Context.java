package android.content;
public abstract class Context {
 public abstract Context getApplicationContext();
 public abstract SharedPreferences getSharedPreferences(String key,int mode);
}
