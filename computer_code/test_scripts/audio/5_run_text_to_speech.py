import torch
from TTS.api import TTS

# export PYTORCH_ENABLE_MPS_FALLBACK=1
# pip install git+https://github.com/coqui-ai/TTS.git@dev
# tts --list_models

# Get device
# mps looks slower or as fast as cpu at best. Probably defaults to cpu.
device = "cpu" # cpu | cuda | mps?

# xtts_v2
# ['Yes, I am alive.'] 1st time (cpu)
#  > Processing time: 4.986134052276611
#  > Real-time factor: 1.4124390525783568

# ['Yes, I am alive.'] 2nd time (cpu)
#  > Processing time: 5.095124006271362
#  > Real-time factor: 1.4245724834941613

# ['Please use our dedicated channels for questions and discussion.', "Help is much more valuable if it's shared publicly so that more people can benefit from it."] 1st time (cpu)
#  > Processing time: 20.508080005645752
#  > Real-time factor: 1.6115120172072386

# ['Please use our dedicated channels for questions and discussion.', "Help is much more valuable if it's shared publicly so that more people can benefit from it."] 2nd time (cpu)
#  > Processing time: 24.856979846954346
#  > Real-time factor: 1.54348136215121

# Output quality: Slow-paced, adds audio from another language at the end of sentences

################
#   your_tts   #
################

# ['Yes, I am alive.'] 1st time (cpu)
#  > Processing time: 0.6283490657806396
#  > Real-time factor: 0.4131157565947664

# ['Yes, I am alive.'] 2nd time (cpu)
#  > Processing time: 0.5443038940429688
#  > Real-time factor: 0.3541339583883987

# ['Please use our dedicated channels for questions and discussion.', "Help is much more valuable if it's shared publicly so that more people can benefit from it."] 1st time (cpu)
#  > Processing time: 0.9728260040283203
#  > Real-time factor: 0.13507720133689535

# ['Please use our dedicated channels for questions and discussion.', "Help is much more valuable if it's shared publicly so that more people can benefit from it."] 2nd time (cpu)
#  > Processing time: 1.0387108325958252
#  > Real-time factor: 0.14454645596936058

# Output quality: Fast-paced, human with a slight robotic touch

################
# tortoise-v2  #
################

# ['Yes, I am alive.'] 1st time (cpu)
#  > Processing time: 81.67530822753906
#  > Real-time factor: 26.146059036254883

# ['Yes, I am alive.'] 2nd time (cpu)
#  > Processing time: 83.08467197418213
#  > Real-time factor: 28.965611830108713

# ['Please use our dedicated channels for questions and discussion.', "Help is much more valuable if it's shared publicly so that more people can benefit from it."] 1st time (cpu)
#  > Processing time: 367.43839716911316
#  > Real-time factor: 31.51848880235803

# ['Please use our dedicated channels for questions and discussion.', "Help is much more valuable if it's shared publicly so that more people can benefit from it."] 2nd time (cpu)
#  > Processing time: 336.19041204452515
#  > Real-time factor: 30.5413587079012

# Output quality: Slow-paced, human, voice changes between sentences

#################
# speedy-speech #
#################

# ['Yes, I am alive.'] 1st time (cpu)
#  > Processing time: 0.12953972816467285
#  > Real-time factor: 0.08200364624572337

# ['Yes, I am alive.'] 2nd time (cpu)
#  > Processing time: 0.1187138557434082
#  > Real-time factor: 0.07515045128451284

# ['Please use our dedicated channels for questions and discussion.', "Help is much more valuable if it's shared publicly so that more people can benefit from it."] 1st time (cpu)
#  > Processing time: 0.6444518566131592
#  > Real-time factor: 0.06299724889310611

# ['Please use our dedicated channels for questions and discussion.', "Help is much more valuable if it's shared publicly so that more people can benefit from it."] 2nd time (cpu)
#  > Processing time: 0.624000072479248
#  > Real-time factor: 0.06099802098776165

# Output quality: asian accent, fast-paced, somewhat robotic?

# Init TTS
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
# tts = TTS("tts_models/multilingual/multi-dataset/your_tts").to(device)
# tts = TTS("tts_models/en/multi-dataset/tortoise-v2").to(device)
# tts = TTS("tts_models/en/ljspeech/speedy-speech").to(device)

# Run TTS
# ❗ Since this model is multi-lingual voice cloning model, we must set the target speaker_wav and language
# Text to speech list of amplitude values as output

# wav = tts.tts(text="If you've spent any time watching YouTube, listening to comedy podcasts, or reading internet comment threads, you've probably come across the phenomenon known as ASMR — or, “autonomous sensory meridian response.” Perhaps you've been mystified by videos of people whispering to the camera, scratching their microphones to produce soft, staticky noises, or just brushing their hair. ", speaker_wav="cloning_voice/short_and_quiet.wav", language="en")
# Text to speech to a file

# xtts_v2
tts.tts_to_file(text="Please use our dedicated channels for questions and discussion. Help is much more valuable if it's shared publicly so that more people can benefit from it.", language="en", speaker_wav="cloning_voice/Untitled.wav", file_path="output.wav")

# your_tts
# tts.tts_to_file(text="Please use our dedicated channels for questions and discussion. Help is much more valuable if it's shared publicly so that more people can benefit from it.", language="en", speaker_wav="cloning_voice/Untitled.wav", file_path="output.wav")

# Tortoise
# tts.tts_to_file(text="Please use our dedicated channels for questions and discussion. Help is much more valuable if it's shared publicly so that more people can benefit from it.", file_path="output.wav")

# speedy-speech
# tts.tts_to_file(text="Please use our dedicated channels for questions and discussion. Help is much more valuable if it's shared publicly so that more people can benefit from it.", file_path="output.wav")
