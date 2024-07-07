#include <WiFi.h>
#include <AsyncTCP.h>
#include <HTTPClient.h>
#include <driver/i2s.h>
#include <ESPAsyncWebServer.h>
#include <ArduinoWebsockets.h>

// #########################################
// Tutorials and inspiration
// #########################################

// INMP441 microphone using websockets
// https://www.youtube.com/watch?v=qq2FRv0lCPw
// https://github.com/0015/ThatProject/tree/master/ESP32_MICROPHONE/Broadcasting_Your_Voice

// MAX98357A amplifier [using websockets]
// https://www.youtube.com/watch?v=kw30vLdrGE8
// https://www.youtube.com/watch?v=At8PDQ3g7FQ
// https://github.com/0015/ThatProject/blob/master/ESP32_TTGO/Walkie-Talkie_Project/Client/Client.ino

// ###########################################
// Libraries outside of Arduino IDE
// ###########################################

// Libraries:
// https://github.com/me-no-dev/AsyncTCP
// https://github.com/me-no-dev/ESPAsyncWebServer

// Folders:
// Users/me/Documents/Arduino/libraries/AsyncTCP
// Users/me/Documents/Arduino/libraries/ESPAsyncWebServer-master

// #########################################
// ESP32 to Arduino Uno communication
// #########################################

// Since the ESP32 uses Serial to print logs, which would be sent to the Arduino Uno through Tx,
// and, even if filtered by the Uno to check if they start with angle:, would cause
// an overhead and potentially noise and jittering of the servo,
// HardwareSerial mySerial(2); and pin 13 is used to communicate with the Uno.
// This way normal logs go to Tx and the servo angle goes to pin 13.

// #########################################
// Microphone and Speaker Workflow
// #########################################

// To avoid recording audio continuously, we use a KY-037 sound sensor.
// An interrupt is triggered when the sound sensor detects sound (sends 1 through D0).
// The interrupt handler sets soundDetected to true.
// The microphone task continuously checks if soundDetected is true.
// If soundDetected is true, audio recorded by the INMP441 is sent to the server.

// However, if the robot is speaking, the KY-37 may pick up the sound
// and trigger the interrupt, which would record the robot's voice,
// send it to the server, trying to answer itself, creating a loop.

// To break the loop, we call /ownSpeech and set allowRecording to false
// when the server is going to send its TTS response for the robot to play.
// After the server has sent its audio to be written to the MAX98357A and played,
// we once again call /ownSpeech and set allowRecording to true to allow
// the robot to record audio again when the KY-37 detects a new sound.

// To facilitate processing on the computer, we send END_OF_AUDIO
// after the recording is done. This way, the server knows when to stop
// processing the audio and start processing the transcription.

// Note that whatever noise picked up because of an incorrect KY-37 trigger is discarded
// on the server when the STT transcription does not meet a certain number of words.

// #########################################
// SST (Speech-to-Text)
// #########################################

// The conversion from audio to text is done on the computer.
// Whisper, nevertheless, seems to need a sample rate of 16000 Hz.

// #########################################
// Connectivity
// #########################################

// Since uploading code to the ESP32 can be a bit of a hassle,
// we add a fallback network in case the primary network is not available.
// The networks are the home WiFi and the iPhone hotspot. More networks can be added.
// The home WiFi may provide a faster speed than the iPhone hotspot.

// If you want to connect computer, iPhone, and robot to same network (instead of using the home WiFi):
// 1. Turn on iPhone hotspot
// 2. Turn on Maximize compatibility
// 3. Turn robot on (wait for it to connect to hotspot)
// 4. Connect computer to hotspot
// 5. (If the cameras still work) Turn off Maximize compatibility (faster frame rate)

// UART2
HardwareSerial mySerial(2);

// INMP441 microphone
#define INMP441_SD 26 // Serial Data
#define INMP441_WS 19 // Word Select
#define INMP441_SCK 18 // Serial Clock

#define INMP441_PORT I2S_NUM_0

#define bufferCnt 10
#define bufferLen 1024
int16_t sBuffer[bufferLen];

#define RECORDING_DURATION_MS 5000

// KY-037 sound sensor
#define KY037_PIN 15
volatile bool soundDetected = false;

// MAX98357A amplifier
#define MAX98357A_BCLK 14 // Bit Clock
#define MAX98357A_LRC 12 // Left/Right Clock
#define MAX98357A_DIN 25  // Digital Input
#define MAX98357A_SD 21 // Shutdown

#define MAX98357A_PORT I2S_NUM_1

// WiFi credentials and IP configurations
const char* ssid1 = "MOVISTAR_BC03";
const char* password1 = "****";
IPAddress staticIP1(192, 168, 1, 182); // Requested address
IPAddress gateway1(192, 168, 1, 1); // Gateway for Home WiFi
IPAddress subnet1(255, 255, 255, 0);
const char* websocket_server_host1 = "192.168.1.174"; // Computer IP

const char* ssid2 = "iPhone (2)";
const char* password2 = "****";
IPAddress staticIP2(172, 20, 10, 12); // Requested address
IPAddress gateway2(172, 20, 10, 1); // Gateway for iPhone Hotspot
IPAddress subnet2(255, 255, 255, 0);
const char* websocket_server_host2 = "172.20.10.4"; // Computer IP

// Websocket to send audio data to server
char websocket_server_host[16]; // Computer IP
const uint16_t websocket_server_port = 8888; // Computer port

using namespace websockets;
WebsocketsClient client;
bool isWebSocketConnected;

// Websocket callbacks
void onEventsCallback(WebsocketsEvent event, String data) {
    if (event == WebsocketsEvent::ConnectionOpened) {
        Serial.println("Connnection Opened");
        isWebSocketConnected = true;
    } else if (event == WebsocketsEvent::ConnectionClosed) {
        Serial.println("Connnection Closed");
        isWebSocketConnected = false;
    } else if (event == WebsocketsEvent::GotPing) {
        Serial.println("Got a Ping!");
    } else if (event == WebsocketsEvent::GotPong) {
        Serial.println("Got a Pong!");
    }
}

void onMessageCallback(WebsocketsMessage message) {
    Serial.print("Received audio data!");
    if (message.type() == MessageType::Binary) {
        int msgLength = message.length();
        if (msgLength > 0) {
            Serial.print("Received audio data: ");
            for (int i = 0; i < msgLength; i++) {
                Serial.print(static_cast<uint8_t>(message.c_str()[i]), HEX);
                Serial.print(" ");
            }
            Serial.println();

            size_t bytesOut;
            i2s_write(MAX98357A_PORT, message.c_str(), msgLength, &bytesOut, portMAX_DELAY);
        }
    }
}

// INMP441 microphone
void inmp441_i2s_install() {
    // Set up I2S Processor configuration
    const i2s_config_t i2s_config = {
        .mode = i2s_mode_t(I2S_MODE_MASTER | I2S_MODE_RX), // RX for input
        .sample_rate = 16000, // for Whisper
        .bits_per_sample = i2s_bits_per_sample_t(16),
        .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT, // Mono
        .communication_format = i2s_comm_format_t(I2S_COMM_FORMAT_STAND_I2S),
        .intr_alloc_flags = 0,
        .dma_buf_count = bufferCnt,
        .dma_buf_len = bufferLen,
        .use_apll = false
    };

    i2s_driver_install(INMP441_PORT, &i2s_config, 0, NULL);
}

void inmp441_i2s_setpin() {
    // Set I2S pin configuration
    const i2s_pin_config_t pin_config = {
        .bck_io_num = INMP441_SCK,
        .ws_io_num = INMP441_WS,
        .data_out_num = -1,
        .data_in_num = INMP441_SD
    };

    i2s_set_pin(INMP441_PORT, &pin_config);
}

// MAX98357A amplifier
void max98357a_i2s_install() {
    // Set up I2S Processor configuration for output
    const i2s_config_t i2s_config = {
        .mode = i2s_mode_t(I2S_MODE_MASTER | I2S_MODE_TX), // TX for output
        .sample_rate = 16000, // for Whisper
        .bits_per_sample = i2s_bits_per_sample_t(16),
        .channel_format = I2S_CHANNEL_FMT_RIGHT_LEFT, // Stereo
        .communication_format = i2s_comm_format_t(I2S_COMM_FORMAT_STAND_I2S),
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = bufferCnt,
        .dma_buf_len = bufferLen,
        .use_apll = false
    };

    i2s_driver_install(MAX98357A_PORT, &i2s_config, 0, NULL);
}

void max98357a_i2s_setpin() {
    // Set I2S pin configuration for MAX98357A
    const i2s_pin_config_t pin_config = {
        .bck_io_num = MAX98357A_BCLK,
        .ws_io_num = MAX98357A_LRC,
        .data_out_num = MAX98357A_DIN,
        .data_in_num = I2S_PIN_NO_CHANGE // No input for this configuration
    };

    i2s_set_pin(MAX98357A_PORT, &pin_config);
}

// KY-037 sound sensor
volatile bool allowRecording = true;

void IRAM_ATTR handleSoundDetection() {
    if (allowRecording) {
        soundDetected = true;
    }
}

// AsyncWebServer to receive commands from computer
AsyncWebServer server(80);

// Connect to WiFi
const char* connectToWiFi(const char* ssid, const char* password, IPAddress staticIP, IPAddress gateway, IPAddress subnet) {
    Serial.print("Connecting to ");
    Serial.println(ssid);

    WiFi.config(staticIP, gateway, subnet);
    WiFi.begin(ssid, password);

    for (int i = 0; i < 10; i++) {
        if (WiFi.status() == WL_CONNECTED) {
            Serial.println("Connected!");
            Serial.print("IP address: ");
            Serial.println(WiFi.localIP());

            mySerial.print("SSID:");
            mySerial.println(ssid);
            return ssid;
        }
        delay(1000);
        Serial.print(".");
    }
    Serial.println("Connection failed.");
    return nullptr;
}

// Receive commands from computer
void handleCommand(AsyncWebServerRequest *request) {
    if (request->method() == HTTP_POST) {
        // Check for both vertical and horizontal angle parameters
        if (request->hasParam("angleV", true) && request->hasParam("angleH", true)) {
            String angleVStr = request->getParam("angleV", true)->value();
            String angleHStr = request->getParam("angleH", true)->value();
            
            // Convert angles to integers
            int angleV = angleVStr.toInt();
            int angleH = angleHStr.toInt();
            
            // Forward both angles to Uno, formatted as discussed
            mySerial.print("angleV:" + String(angleV) + ",angleH:" + String(angleH));
            mySerial.println(); // Ensure data is sent as a complete line
            
            // Respond back to the computer
            request->send(200, "text/plain", "Received Angles - V: " + angleVStr + ", H: " + angleHStr);
        } else {
            // Respond with an error if any angle parameter is missing
            request->send(400, "text/plain", "Parameters 'angleV' and/or 'angleH' are missing");
        }
    } else {
        // Handle unsupported methods
        request->send(405, "text/plain", "Method Not Allowed");
    }
}

// Receive sound alerts from computer when the robot has to start / end speaking
// to disable / enable recording when the KY-037 sound sensor detects sound
void handleOwnSpeech(AsyncWebServerRequest *request) {
    if (request->method() == HTTP_POST) {
        if (request->hasParam("allowRecording", true)) {
            String recordingStr = request->getParam("allowRecording", true)->value();
            // Set allowRecording
            allowRecording = (recordingStr.toInt() == 1);
            // Respond back to computer
            request->send(200, "text/plain", allowRecording ? "Recording Enabled" : "Recording Disabled");
        } else {
            request->send(400, "text/plain", "Parameter 'allowRecording' is missing");
        }
    } else {
        request->send(405, "text/plain", "Method Not Allowed");
    }
}

// Connect to computer via websockets
void connectWSServer() {
    client.onEvent(onEventsCallback);
    client.onMessage(onMessageCallback);
    int attempt = 0;
    const int max_attempts = 5;
    while (!client.connect(websocket_server_host, websocket_server_port, "/") && attempt < max_attempts) {
        delay(500);
        Serial.print(".");
        attempt++;
    }
    if (attempt < max_attempts) {
        Serial.println("Websocket Connected!");
    } else {
        Serial.println("Failed to connect to Websocket.");
    }
}

void microphoneTask(void* parameter) {
    size_t bytesIn = 0;
    while (1) {
        // Check and reconnect Wi-Fi if disconnected
        if (WiFi.status() != WL_CONNECTED) {
            connectToWiFi(ssid2, password2, staticIP2, gateway2, subnet2);
            if (WiFi.status() != WL_CONNECTED) {
                connectToWiFi(ssid1, password1, staticIP1, gateway1, subnet1);
            }
        }

        if (soundDetected) {
            Serial.println("Sound detected. Recording...");
            if (!isWebSocketConnected) {
                connectWSServer();
            }

            size_t bytesIn = 0;
            int lastElapsedSecond = -1;
            unsigned long startTime = millis();
            int recordingDurationS = RECORDING_DURATION_MS / 1000;
            
            while (millis() - startTime < RECORDING_DURATION_MS) {
                int elapsedSeconds = (millis() - startTime) / 1000;
                
                if (elapsedSeconds != lastElapsedSecond) {
                    mySerial.print("Listening (");
                    mySerial.print(recordingDurationS - elapsedSeconds);
                    mySerial.println("s)...");
                    lastElapsedSecond = elapsedSeconds;
                }

                esp_err_t result = i2s_read(INMP441_PORT, &sBuffer, bufferLen, &bytesIn, portMAX_DELAY);
                if (result == ESP_OK && isWebSocketConnected) {
                    client.sendBinary((const char*)sBuffer, bytesIn);
                }
            }

            const char* endOfRecordingSignal = "END_OF_AUDIO";
            client.send(endOfRecordingSignal);
            soundDetected = false;
            mySerial.println("Thinking  ...");
        }

        if (client.available()) {
            client.poll();
        }
    }
}

void setup() {
    // Initialize serial communication for Uno at 9600 baud rate
    mySerial.begin(9600, SERIAL_8N1, 12, 13); // 12 (RX), 13 (TX)
    // and for logging at 115200 baud rate
    Serial.begin(115200);

    // Connect to Wi-Fi
    const char* connectedSSID = nullptr;
    while (!connectedSSID) {
        // Attempt to connect to the primary WiFi network
        connectedSSID = connectToWiFi(ssid2, password2, staticIP2, gateway2, subnet2);

        // If connection to the primary network fails, try the secondary network
        if (!connectedSSID) {
            connectedSSID = connectToWiFi(ssid1, password1, staticIP1, gateway1, subnet1);
        }
    }

    // Set websocket_server_host based on the connected network
    if (strcmp(connectedSSID, ssid2) == 0) {
        strcpy(websocket_server_host, websocket_server_host2);
    } else {
        strcpy(websocket_server_host, websocket_server_host1);
    }

    // Setup for KY-037 sound sensor
    pinMode(KY037_PIN, INPUT_PULLUP);

    // Setup for INMP441 microphone
    inmp441_i2s_install();
    inmp441_i2s_setpin();
    i2s_start(INMP441_PORT);

    // Setup for MAX98357A amplifier
    max98357a_i2s_install();
    max98357a_i2s_setpin();
    i2s_start(MAX98357A_PORT);

    // Attach interrupt handler for KY-037 sound sensor
    attachInterrupt(digitalPinToInterrupt(KY037_PIN), handleSoundDetection, RISING);

    // Start microphone task
    xTaskCreatePinnedToCore(microphoneTask, "microphoneTask", 10000, NULL, 1, NULL, 1);

    // Start web server
    server.on("/command", handleCommand);
    server.on("/ownSpeech", handleOwnSpeech);
    server.begin();
}

void loop() {
}
