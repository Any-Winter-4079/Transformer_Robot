import io
import asyncio
import datetime
import websockets
from pydub import AudioSegment

#################
# Description   #
#################
# This is a test program to receive audio from the ESP32 (recorded by the INMP441),
# save it to a file, and send the audio back to the ESP32 to be passed to the
# MAX98357A amplifier and played through the speaker

#################
# venv          #
#################
# Remember to create a virtual environment, install the packages, and activate it.
# In my case: source ./tensorflow-metal-test/bin/activate (from v2 folder)

#################
# Configuration #
#################
USE_HOTSPOT = True
WS_AUDIO_HOST = '172.20.10.4' if USE_HOTSPOT else "192.168.1.174"
WS_AUDIO_PORT = 8888
FRAME_RATE = 16000
CHANNELS = 1  # Mono
BIT_DEPTH = 2  # 16-bit audio
STORING_FOLDER = "recorded_audio/"
RESPONSE_AUDIO_PATH = "recorded_audio/4.wav"
END_OF_AUDIO_SIGNAL = "END_OF_AUDIO"

# Function to receive audio from the ESP32 and save it to a file
async def audio_receiver(websocket, path):
    audio_buffer = io.BytesIO()

    try:
        async for message in websocket:
            if message == END_OF_AUDIO_SIGNAL:
                # Process the audio data
                audio_buffer.seek(0)
                audio_segment = AudioSegment.from_raw(audio_buffer, sample_width=BIT_DEPTH, frame_rate=FRAME_RATE, channels=CHANNELS)
                wav_bytes = io.BytesIO()
                audio_segment.export(wav_bytes, format="wav")

                # Generate a timestamped filename
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{STORING_FOLDER}{timestamp}.wav"

                # Save the received audio to a file
                with open(filename, "wb") as wav_file:
                    wav_file.write(wav_bytes.getvalue())
                print(f"Saved audio to '{filename}'")

                # After saving the received audio, send the response audio file
                await send_response_audio(websocket)

                # Reset audio_buffer for the next audio segment
                audio_buffer.seek(0)
                audio_buffer.truncate(0)
            else:
                # Write message to audio buffer
                audio_buffer.write(message)
    except websockets.exceptions.ConnectionClosedError:
        print("Websocket connection closed unexpectedly.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the audio buffer
        audio_buffer.close()

# Function to send a specific audio file back to the ESP32
async def send_response_audio(websocket):
    print(f"Sending response audio file: {RESPONSE_AUDIO_PATH}")
    with open(RESPONSE_AUDIO_PATH, 'rb') as audio_file:
        audio_data = audio_file.read()
        await websocket.send(audio_data)
    await websocket.send(END_OF_AUDIO_SIGNAL)
    print("Response audio file sent successfully.")

start_server = websockets.serve(audio_receiver, WS_AUDIO_HOST, WS_AUDIO_PORT)
asyncio.get_event_loop().run_until_complete(start_server)
print(f"Server started. Listening on {WS_AUDIO_HOST}:{WS_AUDIO_PORT}")
asyncio.get_event_loop().run_forever()
