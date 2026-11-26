package android.os;
import java.util.HashMap;
public class Bundle {
 private final HashMap<String,Object> values=new HashMap<>();
 public Object get(String key){return values.get(key);}
 public Bundle put(String key,Object value){values.put(key,value);return this;}
}
