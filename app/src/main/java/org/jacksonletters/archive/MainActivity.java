package org.jacksonletters.archive;

import android.app.Activity;
import android.content.Intent;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.webkit.JavascriptInterface;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.webkit.ValueCallback;
import android.widget.Toast;
import java.io.*;
import java.net.*;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicBoolean;

public final class MainActivity extends Activity {
  private final ExecutorService worker = Executors.newSingleThreadExecutor();
  private final AtomicBoolean busy = new AtomicBoolean(false);
  private final AtomicBoolean cancelled = new AtomicBoolean(false);
  private final Object lock = new Object();
  private WebView web;
  private ValueCallback<Uri[]> fileChooser;
  private CountDownLatch volumeLatch;
  private boolean volumeSuccess;
  private File staged;
  private OutputStream stagedStream;
  private String exportName="jackson-letters.json", exportType="application/json";
  private static final int FILE_PICK = 201, FILE_SAVE = 202;

  @Override public void onCreate(Bundle state) {
    super.onCreate(state);
    web=new WebView(this);
    web.setBackgroundColor(Color.rgb(246,247,251));
    WebSettings s=web.getSettings();
    s.setJavaScriptEnabled(true);
    s.setDomStorageEnabled(true);
    s.setDatabaseEnabled(true);
    s.setAllowFileAccess(false);
    s.setAllowContentAccess(true);
    s.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
    web.addJavascriptInterface(new Bridge(),"AndroidBridge");
    web.setWebViewClient(new WebViewClient() {
      @Override public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest req) {
        Uri u=req.getUrl();
        if(!"appassets.androidplatform.net".equals(u.getHost()))return null;
        try {
          String path=u.getPath()==null?"":u.getPath();
          InputStream input;
          String mime="text/plain";
          if(path.equals("/")||path.equals("/index.html")){
            input=getAssets().open("index.html");mime="text/html";
          }else if(path.matches("/archive/volume_[1-6]\\.txt")){
            int v=Integer.parseInt(path.replaceAll("\\D",""));
            File f=bookFile(v);
            if(!f.exists())return new WebResourceResponse("text/plain","UTF-8",404,"Not Found",java.util.Collections.emptyMap(),new ByteArrayInputStream(new byte[0]));
            input=new FileInputStream(f);
          }else return new WebResourceResponse("text/plain","UTF-8",404,"Not Found",java.util.Collections.emptyMap(),new ByteArrayInputStream(new byte[0]));
          return new WebResourceResponse(mime,"UTF-8",input);
        }catch(Exception e){
          return new WebResourceResponse("text/plain","UTF-8",500,"Error",java.util.Collections.emptyMap(),new ByteArrayInputStream(new byte[0]));
        }
      }
      @Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
        Uri uri=request.getUrl();
        if("appassets.androidplatform.net".equals(uri.getHost()))return false;
        if("https".equals(uri.getScheme())) {
          try{startActivity(new Intent(Intent.ACTION_VIEW,uri));}catch(Exception ignored){}
        }
        return true;
      }
    });
    web.setWebChromeClient(new WebChromeClient(){
      @Override public boolean onShowFileChooser(WebView v, ValueCallback<Uri[]> cb, FileChooserParams params){
        if(fileChooser!=null)fileChooser.onReceiveValue(null);
        fileChooser=cb;
        try{
          Intent i=new Intent(Intent.ACTION_OPEN_DOCUMENT);
          i.addCategory(Intent.CATEGORY_OPENABLE);
          i.setType("*/*");
          startActivityForResult(i,FILE_PICK);
        }catch(Exception e){fileChooser.onReceiveValue(null);fileChooser=null;}
        return true;
      }
    });
    setContentView(web);
    web.loadUrl("https://appassets.androidplatform.net/index.html");
  }

  private File bookFile(int v){
    File dir=new File(getFilesDir(),"books");if(!dir.exists())dir.mkdirs();
    return new File(dir,"volume_"+v+".txt");
  }
  private void js(String code){
    runOnUiThread(()->{if(web!=null)web.evaluateJavascript(code,null);});
  }
  private File downloadVolume(int v) throws Exception {
    File dest=bookFile(v);
    if(dest.isFile()&&dest.length()>50000)return dest;
    String id="correspondenceof000"+v+"jack";
    URL u=new URL("https://archive.org/download/"+id+"/"+id+"_djvu.txt");
    HttpURLConnection connection=(HttpURLConnection)u.openConnection();
    connection.setConnectTimeout(20000);
    connection.setReadTimeout(90000);
    connection.setInstanceFollowRedirects(true);
    connection.setRequestProperty("User-Agent","JacksonLettersAndroid/1.0");
    try{
      int status=connection.getResponseCode();
      if(status!=200)throw new IOException("Source returned HTTP "+status);
      File temp=new File(dest.getParentFile(),dest.getName()+".partial");
      try(InputStream in=connection.getInputStream();OutputStream out=new FileOutputStream(temp)){
        byte[] buf=new byte[16384];int n;long count=0;
        while((n=in.read(buf))>=0){
          if(cancelled.get())throw new InterruptedIOException("Cancelled");
          out.write(buf,0,n);count+=n;
          if(count>75_000_000L)throw new IOException("Book exceeds safety limit");
        }
      }catch(Exception e){temp.delete();throw e;}
      if(temp.length()<50000){temp.delete();throw new IOException("Downloaded text is too short");}
      if(dest.exists())dest.delete();
      if(!temp.renameTo(dest))throw new IOException("Could not cache source text");
      return dest;
    }finally{connection.disconnect();}
  }
  private void loadBooks(){
    if(!busy.compareAndSet(false,true))return;
    cancelled.set(false);
    worker.execute(()->{
      boolean stopped=false;
      try{
        for(int v=1;v<=6;v++){
          if(cancelled.get()){stopped=true;break;}
          try{
            js("window.JacksonNative&&JacksonNative.begin("+v+");");
            downloadVolume(v);
            CountDownLatch latch=new CountDownLatch(1);
            synchronized(lock){volumeLatch=latch;volumeSuccess=false;}
            js("window.JacksonNative&&JacksonNative.loadVolume("+v+");");
            if(!latch.await(150,TimeUnit.SECONDS))throw new IOException("Import acknowledgement timed out");
            synchronized(lock){if(!volumeSuccess)throw new IOException("The app could not save this volume");}
          }catch(Exception ex){
            if(cancelled.get()){stopped=true;break;}
            String msg=org.json.JSONObject.quote(ex.getMessage()==null?"Download or import failed":ex.getMessage());
            js("window.JacksonNative&&JacksonNative.error("+v+","+msg+");");
          }
        }
        if(stopped)js("window.JacksonNative&&JacksonNative.cancelled();");
        else js("window.JacksonNative&&JacksonNative.finish();");
      }finally{busy.set(false);}
    });
  }
  private void beginSave(String name,String type){
    synchronized(lock){
      try{
        if(stagedStream!=null)stagedStream.close();
        exportName=name.replaceAll("[^a-zA-Z0-9._-]","_");
        exportType=type;
        staged=File.createTempFile("jackson-export-",".tmp",getCacheDir());
        stagedStream=new FileOutputStream(staged);
      }catch(IOException e){throw new RuntimeException(e);}
    }
  }
  private void saveChunk(String text){
    synchronized(lock){
      try{
        if(stagedStream==null)throw new IOException("No export in progress");
        stagedStream.write(text.getBytes(StandardCharsets.UTF_8));
      }catch(IOException e){throw new RuntimeException(e);}
    }
  }
  private void finishSave(){
    synchronized(lock){
      try{if(stagedStream!=null)stagedStream.close();stagedStream=null;}
      catch(IOException e){throw new RuntimeException(e);}
    }
    runOnUiThread(()->{
      Intent intent=new Intent(Intent.ACTION_CREATE_DOCUMENT);
      intent.addCategory(Intent.CATEGORY_OPENABLE);
      intent.setType(exportType);
      intent.putExtra(Intent.EXTRA_TITLE,exportName);
      try{startActivityForResult(intent,FILE_SAVE);}
      catch(Exception e){Toast.makeText(this,"Cannot open file saver",Toast.LENGTH_LONG).show();}
    });
  }
  public final class Bridge {
    @JavascriptInterface public void startArchive(){loadBooks();}
    @JavascriptInterface public void cancelArchive(){cancelled.set(true);}
    @JavascriptInterface public void volumeFinished(int v,boolean good){
      synchronized(lock){volumeSuccess=good;if(volumeLatch!=null)volumeLatch.countDown();}
    }
    @JavascriptInterface public void beginSave(String name,String type){MainActivity.this.beginSave(name,type);}
    @JavascriptInterface public void saveChunk(String chunk){MainActivity.this.saveChunk(chunk);}
    @JavascriptInterface public void finishSave(){MainActivity.this.finishSave();}
  }
  @Override protected void onActivityResult(int requestCode,int resultCode,Intent data){
    super.onActivityResult(requestCode,resultCode,data);
    if(requestCode==FILE_PICK){
      if(fileChooser!=null){fileChooser.onReceiveValue(resultCode==RESULT_OK&&data!=null&&data.getData()!=null?new Uri[]{data.getData()}:null);fileChooser=null;}
    }else if(requestCode==FILE_SAVE){
      if(resultCode==RESULT_OK&&data!=null&&data.getData()!=null&&staged!=null){
        try(InputStream in=new FileInputStream(staged);OutputStream out=getContentResolver().openOutputStream(data.getData())){
          if(out==null)throw new IOException("Cannot write chosen file");
          byte[] buf=new byte[16384];int n;while((n=in.read(buf))>0)out.write(buf,0,n);
          Toast.makeText(this,"Archive saved",Toast.LENGTH_SHORT).show();
        }catch(Exception e){Toast.makeText(this,"Save failed: "+e.getMessage(),Toast.LENGTH_LONG).show();}
        finally{staged.delete();staged=null;}
      }
    }
  }
  @Override protected void onDestroy(){
    cancelled.set(true);worker.shutdownNow();
    if(web!=null){web.destroy();web=null;}
    super.onDestroy();
  }
}
