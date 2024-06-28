import time
from transformers.pipelines.audio_utils import ffmpeg_read
from transformers import WhisperProcessor, WhisperForConditionalGeneration

#################
# Description   #
#################
# This is a test program to use Whisper with the transformers library
# to perform speech-to-text (STT) on an audio file.

# Note FRAME_RATE seems to need to be 16000 for Whisper to work

#################
# venv          #
#################
# Remember to create a virtual environment, install the packages, and activate it.
# In my case: source ./tensorflow-metal-test/bin/activate (from v2 folder)

######################
# Voice or Noise
######################
# Obtaining the number of words in the transcription is a rough
# but quick way to determine whether the audio was noise
# or voice. It the KY-037 was triggered incorrectly, the
# hope is the number of words in the transcription will be
# low enough to indicate the audio was noise and not a voice
# and can be ignored.

######################
# short_and_quiet.wav 
######################
# whisper-tiny:
# Time taken for STT: 0.45424580574035645 seconds
# [' 1, 2, 3, 4, 5, 1, 2, 3, 4, 5,']

# whisper-small:
# Time taken for STT: 1.125535011291504 seconds
# [' one two three four five one two three four five']

# whisper-medium:
# Time taken for STT: 2.8318517208099365 seconds
# [' 1 2 3 4 5 1 2 3 4 5']

# whisper-large-v2:
# Time taken for STT: 6.010629892349243 seconds
# [' 1, 2, 3, 4, 5. 1, 2, 3, 4, 5.']

######################
# long_and_loud.wav
######################
# whisper-tiny:
# Time taken for STT: 0.664097785949707 seconds
# [" By default, OBS Studio is set to capture your desktop audio and microphone. You can verify this by looking at the volume meters and the mixer section of the main OBS Studio window if they aren't moving or you suspect the wrong device is being captured. Click on Settings, Audio, and select the devices"]

# whisper-small:
# Time taken for STT: 2.393407106399536 seconds
# [" by default, OBS Studio is set to capture your desktop audio and microphone. You can verify this by looking at the volume meters in the mixer section of the main OBS Studio window. If they aren't moving or you suspect the wrong device is being captured, click on Settings, Audio, and select the device"]

# whisper-medium:
# Time taken for STT: 6.18572211265564 seconds
# [" By default OBS studio is set to capture your desktop audio and microphone You can verify this by looking at the volume meters in the mixer section of the main OBS studio window If they aren't moving or you suspect The wrong device is being captured click on settings audio and select the devices"]

# whisper-large-v2:
# Time taken for STT: 11.266741037368774 seconds
# [" By default OBS studio is set to capture your desktop audio and microphone you can verify this by looking at the volume meters in the mixer section of the main OBS studio window If they aren't moving or you suspect The wrong device is being captured click on settings audio and select the devices"]

#################
# Configuration #
#################
SHORT_AND_QUIET = True
MODEL = "whisper-tiny"

# Load model and processor from pre-trained
processor = WhisperProcessor.from_pretrained("openai/" + MODEL)
model = WhisperForConditionalGeneration.from_pretrained("openai/" + MODEL)

# Load audio file
if SHORT_AND_QUIET:
    audio_path = "./voice_for_stt/short_and_quiet.wav"
else:
    audio_path = "./voice_for_stt/long_and_loud.wav"
sampling_rate = processor.feature_extractor.sampling_rate

# Start timing
start_time = time.time()

# Load as bytes
with open(audio_path, "rb") as f:
    inputs = f.read()

# Read bytes as array
inputs = ffmpeg_read(inputs, sampling_rate=sampling_rate)

# Pre-process to get the input features
input_features = processor(inputs, sampling_rate=sampling_rate, return_tensors="pt").input_features

# Generate token ids by running model forward sequentially
predicted_ids = model.generate(input_features, max_new_tokens=256)

# Post-process token ids to text
transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)

# End timing
end_time = time.time()

time_taken = end_time - start_time
print(f"Time taken for STT: {time_taken} seconds")

# Retrive the number of words in the transcription (roughly)
num_words = len(transcription[0].split(" "))
print(f"Number of words in transcription: {num_words}")

# Print prediction
print(transcription)
