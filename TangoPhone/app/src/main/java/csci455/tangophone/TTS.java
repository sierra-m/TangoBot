package csci455.tangophone;

import android.annotation.SuppressLint;
import android.content.Context;
import android.os.Handler;
import android.os.Looper;
import android.os.Message;
import android.speech.tts.TextToSpeech;
import android.widget.Toast;


import java.util.Locale;

public class TTS extends Thread implements TextToSpeech.OnInitListener {

    private TextToSpeech tts;
    private Context context;
    private String lastMessage;
    public Handler handler;

    TTS(Context context) {
        tts = new TextToSpeech(context, this);
        lastMessage = "";
    }

    public void onInit(int status) {
        if (status == TextToSpeech.SUCCESS) ;
        {
            int result = tts.setLanguage(Locale.US);
            tts.setPitch(0);
            tts.setSpeechRate(0);

            if (result == TextToSpeech.LANG_MISSING_DATA || result == TextToSpeech.LANG_NOT_SUPPORTED)
                Toast.makeText(context, "Language or Data Error.", Toast.LENGTH_LONG).show();
        }
    }

    @SuppressLint("HandlerLeak")
    public void run() {
        Looper.prepare();

        handler = new Handler() {
            public void handleMessage(Message message) {
                String response = message.getData().getString("TT");
                speakOut(response);
            }
        };

        Looper.loop();
    }

    public void speakOut(String text) {
        lastMessage = text;

        tts.speak(text, TextToSpeech.QUEUE_FLUSH, null, null);

        while (tts.isSpeaking()) {
            try {
                Thread.sleep(200);
            } catch (Exception ignored) {
            }
        }
    }
}
