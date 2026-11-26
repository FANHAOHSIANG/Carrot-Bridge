package tw.carrot.gaodeprobe;
import android.app.*;
import android.content.*;
import android.os.*;
import org.json.JSONObject;
import com.navipilot.obf.WideAmapLink;
import com.navipilot.obf.WideBridgeLog;
import java.util.concurrent.atomic.AtomicLong;
public final class CaptureService extends Service implements WideAmapLink.Listener {
  public static volatile String state="IDLE",detail="尚未開始";
  public static final AtomicLong callbacks=new AtomicLong();
  public static volatile long lastMono=-1;
  private WideAmapLink link;
  @Override public IBinder onBind(Intent intent){return null;}
  @Override public int onStartCommand(Intent intent,int flags,int id){
    NotificationManager nm=getSystemService(NotificationManager.class);
    nm.createNotificationChannel(new NotificationChannel("capture","高德資料觀察",NotificationManager.IMPORTANCE_LOW));
    PendingIntent open=PendingIntent.getActivity(this,0,new Intent(this,MainActivity.class),PendingIntent.FLAG_IMMUTABLE);
    PendingIntent stop=PendingIntent.getService(this,1,new Intent(this,CaptureService.class).setAction("STOP"),PendingIntent.FLAG_IMMUTABLE);
    startForeground(101,new Notification.Builder(this,"capture").setSmallIcon(android.R.drawable.ic_menu_compass).setContentTitle("GaodeProbe 資料觀察").setContentText("僅本機記錄，不控制車輛").setContentIntent(open).addAction(android.R.drawable.ic_menu_close_clear_cancel,"停止",stop).setOngoing(true).build());
    if(intent!=null&&"STOP".equals(intent.getAction())){stopSelf();return START_NOT_STICKY;}
    if(link!=null)return START_NOT_STICKY;
    if(!WideBridgeLog.start(this)){state="LOG_ERROR";detail="紀錄尚未準備好";stopSelf();return START_NOT_STICKY;}
    callbacks.set(0);lastMono=-1;link=new WideAmapLink(this,this);link.start();return START_NOT_STICKY;
  }
  @Override public void onState(String s,String d){state=s;detail=d;try{WideBridgeLog.event("amap_link_state",new JSONObject().put("state",s));}catch(Exception ignored){}}
  @Override public void onInvalidated(long e,String why){lastMono=-1;try{WideBridgeLog.event("amap_link_reset",new JSONObject().put("epoch",e).put("reason",why));}catch(Exception ignored){}}
  @Override public void onData(long epoch,int type,JSONObject data,long mono){callbacks.incrementAndGet();lastMono=mono;}
  @Override public void onDestroy(){if(link!=null){link.close();link=null;}WideBridgeLog.stop();state="STOPPED";detail="採集已停止；可匯出本機紀錄";lastMono=-1;stopForeground(STOP_FOREGROUND_REMOVE);super.onDestroy();}
}
