package android.content;
import android.os.Bundle;
public class Intent {
 private final Bundle extras;
 public Intent(Bundle extras) { this.extras=extras; }
 public Bundle getExtras() { return extras; }
}
