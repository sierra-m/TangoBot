package csci455.tangophone;

import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;

public class MainActivity extends AppCompatActivity implements View.OnClickListener {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        Button talkButton = (Button)findViewById(R.id.TalkButton);
        talkButton.setOnClickListener(this);

        Button connectButton = (Button)findViewById(R.id.ConnectButton);
        connectButton.setOnClickListener(this);
    }

    public void onClick(View view) {

        switch(view.getId()) {
            case R.id.TalkButton:
                talk();
                break;

            case R.id.ConnectButton:
                startServer();
                break;
        }
    }

    public void talk() {
        Log.v("**Log**", "Button Pressed");
        Intent talkingRobot = new Intent(this, TalkActivity.class);
        startActivity(talkingRobot);
    }

    public void startServer() {
        Log.v("**Log**", "Starting Server");
        Intent tangoServer = new Intent(this, ServerActivity.class);
        startActivity(tangoServer);
    }
}
