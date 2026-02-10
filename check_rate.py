import sounddevice as sd

device_index = 24  # CABLE Output (VB-Audio Virtual Cable), WASAPI

info = sd.query_devices(device_index)
print(info)
