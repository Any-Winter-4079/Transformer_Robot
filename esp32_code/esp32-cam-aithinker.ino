#include <WiFi.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include <esp_camera.h>

// ###########################################
// Code upload
// ###########################################
// This ESP32-CAM doesn't have a USB C port so we need to upload code
// via a USB-to-serial adapter. The adapter is connected to the ESP32-CAM
// as follows:
// FTDI 5V -> ESP32-CAM 5V (but FTDI set at 3.3V)
// FTDI GND -> ESP32-CAM GND
// FTDI TXD -> ESP32-CAM U0R
// FTDI RXD -> ESP32-CAM U0T
// ESP32-CAM GND -> ESP32-CAM IO0 (to ground)
// And of course, the USB of the USB-to-serial adapter is connected to the computer.

// Note that the ESP32-CAM must be in flash mode (IO0 to ground) when uploading code.
// After uploading code, disconnect IO0 from ground to run the code.

// ###########################################
// sendJpg() function and ESPAsyncWebServer
// ###########################################
// AsyncWebServer increases the fps rate in the best case scenario
// from 1 to 37 fps (with 320x240 resolution and quality 63).
// Still, I had to take sendJpg() from the the following gist
// (together with AsyncBufferResponse and AsyncFrameResponse)
// in order to overcome stability issues (like frames reconstructed
// out of order, and so on, especially at the bottom of the image).

// https://gist.github.com/me-no-dev/d34fba51a8f059ac559bf62002e61aa3

// ###########################################
// Libraries outside of Arduino IDE
// ###########################################
// Place the following libraries:
// https://github.com/espressif/esp32-camera
// https://github.com/me-no-dev/AsyncTCP
// https://github.com/me-no-dev/ESPAsyncWebServer

// In the following -or equivalent- folders:
// Users/me/Documents/Arduino/libraries/esp32-camera-master
// Users/me/Documents/Arduino/libraries/AsyncTCP
// Users/me/Documents/Arduino/libraries/ESPAsyncWebServer-master

// ###########################################
// Connectivity
// ###########################################
// Since uploading code to the ESP32 can be a bit of a hassle,
// we add a fallback network in case the primary network is not available.
// The networks are the home WiFi and the iPhone hotspot. More networks can be added.
// The home WiFi may provide a faster speed than the iPhone hotspot.

// If you want to connect computer, iPhone, and robot to same network (instead of using the home WiFi):
// 1. Turn the iPhone hotspot on
// 2. Turn Maximize compatibility on
// 3. Turn the robot on (wait for it to connect to hotspot)
// 4. Connect computer to hotspot
// 5. (If the cameras still work) Turn Maximize compatibility off (for a potentially faster frame rate)

// ###########################################
// If you face issues
// ###########################################
// Lots of issues and threads point to the clock being exposed on some pin,
// antenna issues where the signal is too weak or experiences interference,
// problems if the average compression rate (e.g. with a complex scene)
// cannot be met, and so on.
// For example, on the FreeNove camera I have tested how covering it with
// the plastic bag it came in increased the fps (as others reported).
// In the end, I ended up using the Ai-Thinker and the M5Stack Wide cameras
// and left the FreeNove camera to handle mostly audio.
// For the Ai-Thinker, leaving the antenna unosbstructed seemed to increase
// the frame rate by quite a bit. So playing with the position is advised.

// Lowering the clock frequency for the camera might help too, as others have
// suggested. It'll update a bit slower, but the clock signal may be more robust.

// https://www.youtube.com/watch?v=NvmyCBbTGPs
// https://github.com/espressif/esp32-camera/issues/150

// ###########################################
// Frames rates for different configurations
// ###########################################
// Performing a synchronous fetch of 1k images for each of the following 30
// (FRAME_SIZE, JPEG_QUALITY) combinations (using update_camera_config.py
// as test script), we observe latencies from 0.027 (s) to 0.503 (s):

// # | FRAME_SIZE      | JPEG_QUALITY 4 | JPEG_QUALITY 8 | JPEG_QUALITY 16 | JPEG_QUALITY 32 | JPEG_QUALITY 63 |
// # |-----------------|----------------|----------------|-----------------|-----------------|-----------------|
// # | QVGA (320x240)  | Err            | 0.039          | 0.029           | 0.030           | 0.027           |
// # | VGA (640x480)   | 0.139          | 0.118          | 0.074           | 0.075           | 0.068           |
// # | SVGA (800x600)  | 0.143          | 0.111          | 0.107           | 0.067           | 0.067           |
// # | XGA (1024x768)  | 0.286          | 0.269          | 0.182           | 0.148           | 0.150           |
// # | SXGA (1280x1024)| 0.374          | 0.258          | 0.212           | 0.173           | 0.155           |
// # | UXGA (1600x1200)| 0.503          | 0.307          | 0.218           | 0.221           | 0.194           |

// ###########################################
// Observations
// ###########################################
// As quality, buffer count, frequency and grab mode change, image changes a bit too
// (in noise, clarity, and so on). Not very dramatically, but it is noticeable.
// Lower clock rates seem to provide a clearer image, as if there was more natural light.

// ###########################################
// ESP32-CAM configuration from computer
// ###########################################
// To allow for different configurations, given the different possible tasks the computer
// may want to perform (object detection, face-tracking, etc.), we add a handler for
// /camera_config that allows the computer to send the camera configuration to the ESP32-CAM.
// This allows us to change the frame_size and quality without re-uploading the code.
// Other configurations changes can be added.

// WiFi credentials and IP configurations
const char* ssid1 = "***";  //                                                          ** Replace **
const char* password1 = "***";;  //                                                     ** Replace **
IPAddress staticIP1(*, *, *, *); // Static IP for Home WiFi, e.g. (192, 168, 1, 181).   ** Replace **
IPAddress gateway1(*, *, *, *);   // Gateway for Home WiFi, e.g. (192, 168, 1, 1).      ** Replace **
IPAddress subnet1(255, 255, 255, 0);

const char* ssid2 = "***";  //                                                          ** Replace **
const char* password2 = "***";  //                                                      ** Replace **
IPAddress staticIP2(*, *, *, *); // Static IP for iPhone Hotspot.                       ** Replace **
IPAddress gateway2(*, *, *, *);   // Gateway for iPhone Hotspot.                        ** Replace **
IPAddress subnet2(255, 255, 255, 0);

AsyncWebServer server(80);

static const char * JPG_CONTENT_TYPE = "image/jpeg";

class AsyncBufferResponse: public AsyncAbstractResponse {
    private:
        uint8_t * _buf;
        size_t _len;
        size_t _index;
    public:
        AsyncBufferResponse(uint8_t * buf, size_t len, const char * contentType){
            _buf = buf;
            _len = len;
            _callback = nullptr;
            _code = 200;
            _contentLength = _len;
            _contentType = contentType;
            _index = 0;
        }
        ~AsyncBufferResponse(){
            if(_buf != nullptr){
                free(_buf);
            }
        }
        bool _sourceValid() const { return _buf != nullptr; }
        virtual size_t _fillBuffer(uint8_t *buf, size_t maxLen) override{
            size_t ret = _content(buf, maxLen, _index);
            if(ret != RESPONSE_TRY_AGAIN){
                _index += ret;
            }
            return ret;
        }
        size_t _content(uint8_t *buffer, size_t maxLen, size_t index){
            memcpy(buffer, _buf+index, maxLen);
            if((index+maxLen) == _len){
                free(_buf);
                _buf = nullptr;
            }
            return maxLen;
        }
};

class AsyncFrameResponse: public AsyncAbstractResponse {
    private:
        camera_fb_t * fb;
        size_t _index;
    public:
        AsyncFrameResponse(camera_fb_t * frame, const char * contentType){
            _callback = nullptr;
            _code = 200;
            _contentLength = frame->len;
            _contentType = contentType;
            _index = 0;
            fb = frame;
        }
        ~AsyncFrameResponse(){
            if(fb != nullptr){
                esp_camera_fb_return(fb);
            }
        }
        bool _sourceValid() const { return fb != nullptr; }
        virtual size_t _fillBuffer(uint8_t *buf, size_t maxLen) override{
            size_t ret = _content(buf, maxLen, _index);
            if(ret != RESPONSE_TRY_AGAIN){
                _index += ret;
            }
            return ret;
        }
        size_t _content(uint8_t *buffer, size_t maxLen, size_t index){
            memcpy(buffer, fb->buf+index, maxLen);
            if((index+maxLen) == fb->len){
                esp_camera_fb_return(fb);
                fb = nullptr;
            }
            return maxLen;
        }
};

void sendJpg(AsyncWebServerRequest *request){
    camera_fb_t * fb = esp_camera_fb_get();
    if (fb == NULL) {
        log_e("Camera frame failed");
        request->send(501);
        return;
    }

    if(fb->format == PIXFORMAT_JPEG){
        AsyncFrameResponse * response = new AsyncFrameResponse(fb, JPG_CONTENT_TYPE);
        if (response == NULL) {
            log_e("Response alloc failed");
            request->send(501);
            return;
        }
        response->addHeader("Access-Control-Allow-Origin", "*");
        request->send(response);
        return;
    }

    size_t jpg_buf_len = 0;
    uint8_t * jpg_buf = NULL;
    unsigned long st = millis();
    bool jpeg_converted = frame2jpg(fb, 80, &jpg_buf, &jpg_buf_len);
    esp_camera_fb_return(fb);
    if(!jpeg_converted){
        log_e("JPEG compression failed: %lu", millis());
        request->send(501);
        return;
    }
    log_i("JPEG: %lums, %uB", millis() - st, jpg_buf_len);

    AsyncBufferResponse * response = new AsyncBufferResponse(jpg_buf, jpg_buf_len, JPG_CONTENT_TYPE);
    if (response == NULL) {
        log_e("Response alloc failed");
        request->send(501);
        return;
    }
    response->addHeader("Access-Control-Allow-Origin", "*");
    request->send(response);
}

// Receive camera config from computer and update camera
void handleCameraConfig(AsyncWebServerRequest *request) {

    camera_config_t config;

    if (request->method() == HTTP_POST) {
        if (request->hasParam("jpeg_quality", true)) {
            String jpegQuality = request->getParam("jpeg_quality", true)->value();
            int jpegQualityInt = jpegQuality.toInt();
            if (jpegQualityInt < 0 || jpegQualityInt > 63) {
                request->send(400, "text/plain", "Parameter 'jpeg_quality' is invalid");
                return;
            }
            else {
                config.jpeg_quality = jpegQualityInt;
            }
        } else {
            request->send(400, "text/plain", "Parameter 'jpeg_quality' is missing");
            return;
        }
        if (request->hasParam("frame_size", true)) {
            String frameSize = request->getParam("frame_size", true)->value();
            if (strcmp(frameSize.c_str(), "FRAMESIZE_QVGA") == 0) {
                config.frame_size = FRAMESIZE_QVGA;
            }
            else if (strcmp(frameSize.c_str(), "FRAMESIZE_VGA") == 0) {
                config.frame_size = FRAMESIZE_VGA;
            }
            else if (strcmp(frameSize.c_str(), "FRAMESIZE_SVGA") == 0) {
                config.frame_size = FRAMESIZE_SVGA;
            }
            else if (strcmp(frameSize.c_str(), "FRAMESIZE_XGA") == 0) {
                config.frame_size = FRAMESIZE_XGA;
            }
            else if (strcmp(frameSize.c_str(), "FRAMESIZE_SXGA") == 0) {
                config.frame_size = FRAMESIZE_SXGA;
            }
            else if (strcmp(frameSize.c_str(), "FRAMESIZE_UXGA") == 0) {
                config.frame_size = FRAMESIZE_UXGA;
            }
            else {
                request->send(400, "text/plain", "Parameter 'frame_size' is invalid");
                return;
            }
        } else {
            request->send(400, "text/plain", "Parameter 'frame_size' is missing");
            return;
        }

        config.ledc_channel = LEDC_CHANNEL_0;
        config.ledc_timer = LEDC_TIMER_0;
        config.pixel_format = PIXFORMAT_JPEG; // PIXFORMAT_JPEG seems recommended

        config.fb_count = 1;
        config.xclk_freq_hz = 20000000; //16 MHz for experimental mode. 20 MHz seems fine too
        config.grab_mode = CAMERA_GRAB_LATEST; //CAMERA_GRAB_WHEN_EMPTY or CAMERA_GRAB_LATEST
        config.fb_location = CAMERA_FB_IN_PSRAM;

        config.pin_d0 = 5;
        config.pin_d1 = 18;
        config.pin_d2 = 19;
        config.pin_d3 = 21;
        config.pin_d4 = 36;
        config.pin_d5 = 39;
        config.pin_d6 = 34;
        config.pin_d7 = 35;
        config.pin_xclk = 0;
        config.pin_pclk = 22;
        config.pin_vsync = 25;
        config.pin_href = 23;
        config.pin_sscb_sda = 26;
        config.pin_sscb_scl = 27;
        config.pin_pwdn = 32;
        config.pin_reset = -1;
        esp_camera_deinit();

        esp_err_t err = esp_camera_init(&config);
        if (err != ESP_OK) {
            request->send(500, "text/plain", "Camera config update failed");
        }
        else {
            request->send(200, "text/plain", "Camera config updated");
        }
    } else {
        request->send(405, "text/plain", "Method Not Allowed");
    }
}

// Connect to WiFi
bool connectToWiFi(const char* ssid, const char* password, IPAddress staticIP, IPAddress gateway, IPAddress subnet) {
    Serial.print("Connecting to ");
    Serial.println(ssid);

    WiFi.config(staticIP, gateway, subnet); // Set static IP, gateway, and subnet
    WiFi.begin(ssid, password);

    for (int i = 0; i < 10; i++) {  // Attempt to connect for 10 seconds
        if (WiFi.status() == WL_CONNECTED) {
        Serial.println("Connected!");
        Serial.print("IP address: ");
        Serial.println(WiFi.localIP());
        return true;
        }
        delay(1000);
        Serial.print(".");
    }
    Serial.println("Connection failed.");
    return false;
}

void setup() {
    // Initialize serial communication at 115200 baud rate
    Serial.begin(115200);

    // Camera configuration for Ai-Thinker
    camera_config_t config;
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer = LEDC_TIMER_0;
    config.pixel_format = PIXFORMAT_JPEG; // PIXFORMAT_JPEG seems recommended
    config.frame_size = FRAMESIZE_VGA;  // FRAMESIZE_QVGA: 320x240, FRAMESIZE_VGA: 640x480, FRAMESIZE_SVGA: 800x600, FRAMESIZE_XGA: 1024x768, FRAMESIZE_SXGA: 1280x1024, FRAMESIZE_UXGA: 1600x1200
    config.jpeg_quality = 12; // 0-63 lower number means higher quality
    config.fb_count = 1;
    config.xclk_freq_hz = 20000000; //16 MHz for experimental mode. 20 MHz seems fine too
    config.grab_mode = CAMERA_GRAB_LATEST; //CAMERA_GRAB_WHEN_EMPTY or CAMERA_GRAB_LATEST
    config.fb_location = CAMERA_FB_IN_PSRAM;
    // >5 fps

    config.pin_d0 = 5;
    config.pin_d1 = 18;
    config.pin_d2 = 19;
    config.pin_d3 = 21;
    config.pin_d4 = 36;
    config.pin_d5 = 39;
    config.pin_d6 = 34;
    config.pin_d7 = 35;
    config.pin_xclk = 0;
    config.pin_pclk = 22;
    config.pin_vsync = 25;
    config.pin_href = 23;
    config.pin_sscb_sda = 26;
    config.pin_sscb_scl = 27;
    config.pin_pwdn = 32;
    config.pin_reset = -1;


    // Initialize camera with the specified configuration
    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        Serial.printf("Camera init failed with error 0x%x", err);
        return;
    }

    // Connect to Wi-Fi
    bool connected = false;
    while (!connected) {
        // Attempt to connect to the primary WiFi network
        connected = connectToWiFi(ssid1, password1, staticIP1, gateway1, subnet1);

        // If connection to the primary network fails, try the secondary network
        if (!connected) {
        connected = connectToWiFi(ssid2, password2, staticIP2, gateway2, subnet2);
        }
    }

    // Start server
    server.on("/image.jpg", HTTP_GET, sendJpg);
    server.on("/camera_config", HTTP_POST, handleCameraConfig);
    server.begin();
}

void loop() {
    // Nothing here
}
