package csci455.tangophone;

import androidx.appcompat.app.AppCompatActivity;

import android.os.Bundle;
import android.os.Message;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

public class TalkActivity extends AppCompatActivity implements View.OnClickListener {
    TextView talkText;
    TTS textToSpeech;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_talk);
        talkText = (TextView) findViewById(R.id.talkText);

        Button talkButton = (Button) findViewById(R.id.speakButton);
        talkButton.setOnClickListener(this);

        textToSpeech = new TTS(this);
        textToSpeech.start();
    }

    public void onClick(View view) {
        Toast.makeText(this, "onClick", Toast.LENGTH_SHORT).show();
        switch (view.getId()) {
            case R.id.speakButton:
                String input = talkText.getText().toString();
                Message sendMessage =  textToSpeech.handler.obtainMessage();
                Bundle bundle = new Bundle();
                bundle.putString("TT", input);
                sendMessage.setData(bundle);
                textToSpeech.handler.sendMessage(sendMessage);

                break;
        }
    }
}
