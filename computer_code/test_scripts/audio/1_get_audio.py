import io
import asyncio
import datetime
import websockets
from pydub import AudioSegment

#################
# Description   #
#################
# This is a test program to receive audio from the ESP32 (WROVER) (recorded by the INMP441)
# and save it to a file for playback and review.

# Note FRAME_RATE seems to need to be 16000 for Whisper to work

#################
# venv          #
#################
# Remember to create a virtual environment, install the packages, and activate it.
# In my case: source ./tensorflow-metal-test/bin/activate (from v2 folder)

#################
# Configuration #
#################
WS_AUDIO_HOST = '*.*.*.*'        # (Computer's) server IP, e.g. 192.168.1.174          ** Replace **
WS_AUDIO_PORT = 8888             # (Computer's) server port, e.g. 8888                 ** Replace **
FRAME_RATE = 16000
CHANNELS = 1  # Mono
BIT_DEPTH = 2  # 16-bit audio
STORING_FOLDER = "recorded_audio/"
END_OF_AUDIO_SIGNAL = "END_OF_AUDIO"

# Function to receive audio from the ESP32 (WROVER) and save it to a file
async def audio_receiver(websocket, path):
    """Receive audio from the ESP32 (WROVER) and save it to a file."""
    audio_buffer = io.BytesIO()

    async for message in websocket:
        if message == END_OF_AUDIO_SIGNAL:
            audio_buffer.seek(0)
            audio_segment = AudioSegment.from_raw(audio_buffer, sample_width=BIT_DEPTH, frame_rate=FRAME_RATE, channels=CHANNELS)
            wav_bytes = io.BytesIO()
            audio_segment.export(wav_bytes, format="wav")

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{STORING_FOLDER}{timestamp}.wav"

            with open(filename, "wb") as wav_file:
                wav_file.write(wav_bytes.getvalue())
            print(f"Audio saved to {filename}")

            audio_buffer.seek(0)
            audio_buffer.truncate(0)
        else:
            audio_buffer.write(message)

start_server = websockets.serve(audio_receiver, WS_AUDIO_HOST, WS_AUDIO_PORT)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
