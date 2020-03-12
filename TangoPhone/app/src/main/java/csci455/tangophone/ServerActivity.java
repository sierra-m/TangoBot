package csci455.tangophone;
import android.annotation.SuppressLint;
import android.net.wifi.WifiInfo;
import android.net.wifi.WifiManager;
import android.os.Bundle;

import android.os.Message;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.InetAddress;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.UnknownHostException;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;

@SuppressLint("SetTextI18n")
public class ServerActivity extends AppCompatActivity implements View.OnClickListener {
    ServerSocket serverSocket;
    Thread ServerThread = null;
    TextView tvIP, tvPort;
    TextView tvMessages;

    public static String SERVER_IP = "";
    public static final int SERVER_PORT = 9090;

    TTS textToSpeech;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_server);

        tvIP = findViewById(R.id.tvIP);
        tvPort = findViewById(R.id.tvPort);
        tvMessages = findViewById(R.id.tvMessages);

        textToSpeech = new TTS(this);
        textToSpeech.start();

        try {
            SERVER_IP = getLocalIpAddress();
        } catch (UnknownHostException e) {
            e.printStackTrace();
        }

        ServerThread = new Thread(new ServerThread());
        ServerThread.start();

        Button forwardButton = (Button)findViewById(R.id.ForwardButton);
        forwardButton.setOnClickListener(this);

        Button stopButton = (Button)findViewById(R.id.StopButton);
        stopButton.setOnClickListener(this);

        Button backwardButton = (Button)findViewById(R.id.BackwardButton);
        backwardButton.setOnClickListener(this);

        Button turnRightButton = (Button)findViewById(R.id.TurnRightButton);
        turnRightButton.setOnClickListener(this);

        Button turnLeftButton = (Button)findViewById(R.id.TurnLeftButton);
        turnLeftButton.setOnClickListener(this);

        Button headUpButton = (Button)findViewById(R.id.HeadUpButton);
        headUpButton.setOnClickListener(this);

        Button headDownButton = (Button)findViewById(R.id.HeadDownButton);
        headDownButton.setOnClickListener(this);

        Button headLeftButton = (Button)findViewById(R.id.HeadLeftButton);
        headLeftButton.setOnClickListener(this);

        Button headRightButton = (Button)findViewById(R.id.HeadRightButton);
        headRightButton.setOnClickListener(this);

        Button waistLeftButton = (Button)findViewById(R.id.WaistLeftButton);
        waistLeftButton.setOnClickListener(this);

        Button waistRightButton = (Button)findViewById(R.id.WaistRightButton);
        waistRightButton.setOnClickListener(this);
    }

    private PrintWriter output;
    private BufferedReader input;
    class ServerThread implements Runnable {

        @Override
        public void run() {
            Socket socket;

            try {
                serverSocket = new ServerSocket(SERVER_PORT);
                runOnUiThread(() -> {
                    tvMessages.setText("Not connected");
                    tvIP.setText("IP: " + SERVER_IP);
                    tvPort.setText("Port: " + SERVER_PORT);
                });

                try {
                    socket = serverSocket.accept();
                    output = new PrintWriter(socket.getOutputStream());
                    input = new BufferedReader(new InputStreamReader(socket.getInputStream()));

                    runOnUiThread(() -> tvMessages.setText("Connected\n"));

                    new Thread(new ListenThread()).start();

                } catch (IOException e) {
                    e.printStackTrace();
                }
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }
    private class ListenThread implements Runnable {
        @Override
        public void run() {
            while (true) {
                try {
                    final String message = input.readLine();
                    if (message != null) {
                        runOnUiThread(() -> {
                            tvMessages.append("client:" + message + "\n");
                            Message sendMessage =  textToSpeech.handler.obtainMessage();
                            Bundle bundle = new Bundle();
                            bundle.putString("TT", message);
                            sendMessage.setData(bundle);
                            textToSpeech.handler.sendMessage(sendMessage);
                        });
                    } else {
                        ServerThread = new Thread(new ServerThread());
                        ServerThread.start();
                        return;
                    }
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }
    }

    class SendThread implements Runnable {
        private String command;

        SendThread(String message) {
            this.command = message;
        }

        @Override
        public void run() {
            output.write(command);
            output.flush();
            runOnUiThread(() -> {
                tvMessages.setText("server: " + command + "\n");
            });
        }
    }

    public void onClick(View view) {
        String command = "";

        switch(view.getId()) {
            case R.id.ForwardButton:
                command = "DF";
                break;
            case R.id.BackwardButton:
                command = "DB";
                break;
            case R.id.StopButton:
                command = "DS";
                break;
            case R.id.TurnLeftButton:
                command = "SL";
                break;
            case R.id.TurnRightButton:
                command = "SR";
                break;
            case R.id.HeadUpButton:
                command = "HU";
                break;
            case R.id.HeadDownButton:
                command = "HD";
                break;
            case R.id.HeadLeftButton:
                command = "HL";
                break;
            case R.id.HeadRightButton:
                command = "HR";
                break;
            case R.id.WaistLeftButton:
                command = "WL";
                break;
            case R.id.WaistRightButton:
                command = "WR";
                break;
        }

        new Thread(new SendThread(command)).start();
    }

    private String getLocalIpAddress() throws UnknownHostException {
        WifiManager wifiManager = (WifiManager) getApplicationContext().getSystemService(WIFI_SERVICE);
        assert wifiManager != null;
        WifiInfo wifiInfo = wifiManager.getConnectionInfo();
        int ipInt = wifiInfo.getIpAddress();
        return InetAddress.getByAddress(ByteBuffer.allocate(4).order(ByteOrder.LITTLE_ENDIAN).putInt(ipInt).array()).getHostAddress();
    }
}
