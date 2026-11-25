from shared import AmpSetting
import pedalboard
import numpy as np

plugin = pedalboard.load_plugin("/Library/Audio/Plug-Ins/VST3/Guitar Rig 7.vst3")
plugin.show_editor()
FIXED_PARAMS = {
    "fire_seeker_on_off": True,
    "matched_cabinet_pro_on_off": True,
    "fire_seeker_master": 0.05,
    "matched_cabinet_pro_x_fade": '100% Cabinet / 0% Room',
    "matched_cabinet_pro_volume": 0.05
}

for name, value in FIXED_PARAMS.items():
    setattr(plugin, name, value)
base_state = plugin.raw_state

def process_audio(setting: AmpSetting, x:np.ndarray, sr:int)->np.ndarray:
    plugin.raw_state = base_state

    for key, value in setting.items():
            name = f"fire_seeker_{key}"
            plugin.parameters[name].raw_value = float(value)


    silence = np.zeros((2, 2 * sr), dtype=np.float32)
    plugin.process(silence, sr, reset=False)

    processed = plugin.process(x, sr, reset=False)

    return processed