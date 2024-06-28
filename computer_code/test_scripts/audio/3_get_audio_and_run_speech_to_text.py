import io
import time
import asyncio
import websockets
from pydub import AudioSegment
from transformers.pipelines.audio_utils import ffmpeg_read
from transformers import WhisperProcessor, WhisperForConditionalGeneration

#################
# Description   #
#################
# This is a test program to use Whisper with the transformers library
# to perform speech-to-text (STT) on the audio received from the ESP32.

#################
# venv          #
#################
# Remember to create a virtual environment, install the packages, and activate it.
# In my case: source ./tensorflow-metal-test/bin/activate (from v2 folder)

# Note FRAME_RATE seems to need to be 16000 for Whisper to work

#################
# Configuration #
#################
USE_HOTSPOT = True
WS_AUDIO_HOST = '172.20.10.4' if USE_HOTSPOT else "192.168.1.174"
WS_AUDIO_PORT = 8888
FRAME_RATE = 16000
CHANNELS = 1  # Mono
BIT_DEPTH = 2  # 16-bit audio
END_OF_AUDIO_SIGNAL = "END_OF_AUDIO"
MIN_WORDS_THRESHOLD = 2
MODEL = "whisper-tiny"

# Load model and processor from pre-trained
processor = WhisperProcessor.from_pretrained("openai/" + MODEL)
model = WhisperForConditionalGeneration.from_pretrained("openai/" + MODEL)

async def audio_receiver(websocket, path):
    audio_buffer = io.BytesIO()

    try:
        async for message in websocket:
            if message == END_OF_AUDIO_SIGNAL:
                # Process the audio data
                audio_buffer.seek(0)

                # Convert raw audio to WAV format
                audio_segment = AudioSegment.from_raw(audio_buffer, sample_width=BIT_DEPTH, frame_rate=FRAME_RATE, channels=CHANNELS)
                wav_bytes = io.BytesIO()
                audio_segment.export(wav_bytes, format="wav")
                
                # Read bytes as array
                inputs = ffmpeg_read(wav_bytes.getvalue(), sampling_rate=FRAME_RATE)

                # Start timing
                start_time = time.time()

                # Pre-process to get the input features
                input_features = processor(inputs, sampling_rate=FRAME_RATE, return_tensors="pt").input_features

                # Generate token ids by running model forward sequentially
                predicted_ids = model.generate(input_features, max_new_tokens=256)

                # Post-process token ids to text
                transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)

                # End timing
                end_time = time.time()

                time_taken = end_time - start_time
                print(f"Time taken for STT: {time_taken} seconds")

                # Print transcription
                num_words = len(transcription[0].split(" "))
                if num_words >= MIN_WORDS_THRESHOLD:
                    print(transcription)
                else:
                    # Ignore when the KY-037 is triggered by noise
                    print(f"MIN_WORDS_THRESHOLD not met ({num_words} words)")

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

start_server = websockets.serve(audio_receiver, WS_AUDIO_HOST, WS_AUDIO_PORT)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
