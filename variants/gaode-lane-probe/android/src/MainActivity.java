package tw.carrot.gaodeprobe;
import android.app.Activity;
import android.content.Intent;
import android.os.*;
import android.widget.*;
import java.io.*;
import com.navipilot.obf.WideBridgeLog;
public final class MainActivity extends Activity {
  private final Handler ui=new Handler(Looper.getMainLooper());
  private TextView status;
  private Button start,stop,export;
  private boolean exporting;
  private static final int EXPORT=9;
  private final Runnable refresh=new Runnable(){public void run(){
    boolean running=WideBridgeLog.recording();long last=CaptureService.lastMono;
    status.setText("狀態："+CaptureService.state+"\n"+CaptureService.detail+"\n已授權事件："+CaptureService.callbacks.get()+"\n紀錄筆數："+WideBridgeLog.count()+" / 丟棄："+WideBridgeLog.dropped()+"\n最近事件："+(last<0?"無":Math.max(0,SystemClock.elapsedRealtime()-last)+" ms前")+"\nL2/L4：未開放／未驗證，不啟用\n車道中心線：未驗證\n"+WideBridgeLog.error());
    start.setEnabled(WideBridgeLog.idle()&&!exporting);stop.setEnabled(running);export.setEnabled(WideBridgeLog.idle()&&!exporting&&WideBridgeLog.existing(MainActivity.this).isFile());ui.postDelayed(this,500);
  }};
  @Override public void onCreate(Bundle b){
    super.onCreate(b);LinearLayout l=new LinearLayout(this);l.setOrientation(LinearLayout.VERTICAL);l.setPadding(24,32,24,24);
    TextView title=new TextView(this);title.setText("GaodeProbe 0.1 — Link 觀察版");title.setTextSize(22);l.addView(title);
    TextView note=new TextView(this);note.setText("停車時啟動與停止。以實際高德授權為準。只在本機紀錄，不控制車輛，不取代原高德或 Carrot Bridge。新錄製會覆蓋上一份，請先匯出。");l.addView(note);
    start=new Button(this);start.setText("開始採集");l.addView(start);start.setOnClickListener(v->new android.app.AlertDialog.Builder(this).setTitle("開始本機錄製？").setMessage("將覆蓋上一份紀錄，可能含導航路線與位置。").setNegativeButton("取消",null).setPositiveButton("開始",(d,w)->{start.setEnabled(false);startForegroundService(new Intent(this,CaptureService.class));}).show());
    stop=new Button(this);stop.setText("停止採集");l.addView(stop);stop.setOnClickListener(v->stopService(new Intent(this,CaptureService.class)));
    export=new Button(this);export.setText("匯出 JSONL");l.addView(export);export.setOnClickListener(v->{Intent i=new Intent(Intent.ACTION_CREATE_DOCUMENT).setType("application/octet-stream").addCategory(Intent.CATEGORY_OPENABLE).putExtra(Intent.EXTRA_TITLE,"gaode-events.jsonl");startActivityForResult(i,EXPORT);});
    status=new TextView(this);status.setTextSize(16);l.addView(status);ScrollView sc=new ScrollView(this);sc.addView(l);setContentView(sc);
  }
  @Override protected void onResume(){super.onResume();ui.removeCallbacks(refresh);ui.post(refresh);}
  @Override protected void onPause(){ui.removeCallbacks(refresh);super.onPause();}
  @Override protected void onActivityResult(int request,int result,Intent data){
    super.onActivityResult(request,result,data);if(request!=EXPORT||result!=RESULT_OK||data==null||data.getData()==null||!WideBridgeLog.idle())return;
    exporting=true;final android.net.Uri uri=data.getData();new Thread(()->{String msg="匯出完成";
      try(InputStream in=new FileInputStream(WideBridgeLog.existing(this));OutputStream out=getContentResolver().openOutputStream(uri,"w")){if(out==null)throw new IOException("null_output");byte[] buf=new byte[8192];int n;while((n=in.read(buf))!=-1)out.write(buf,0,n);}catch(IOException e){msg="匯出失敗";}
      final String m=msg;runOnUiThread(()->{exporting=false;Toast.makeText(this,m,Toast.LENGTH_LONG).show();});}).start();
  }
}
