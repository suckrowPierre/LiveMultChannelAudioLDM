from enum import Enum
import torch
from diffusers import AudioLDM2Pipeline


class Models(Enum):
    # S = "audioldm-s-full"
    ALDM_SV2 = "audioldm-s-full-v2"
    ALDM_M = "audioldm-m-full"
    ALDM_L = "audioldm-l-full"
    ALDM_2 = "audioldm2"
    ALDM_2_L = "audioldm2-large"
    ALDM_2_MUSIC = "audioldm2-music"


class Devices(Enum):
    CPU = "cpu"
    CUDA = "cuda"
    MPS = "mps"


SAMPLE_RATE = 16000
DEVICE = Devices.MPS.value
MODEL = Models.ALDM_2.value


def setup_pipeline():
    dtype = torch.float32 if DEVICE != Devices.CUDA.value else torch.float16
    repo_id = "cvssp/" + MODEL
    pipe = AudioLDM2Pipeline.from_pretrained(repo_id, torch_dtype=dtype).to(DEVICE)
    if DEVICE == "mps":
        pipe.enable_attention_slicing()
    return pipe


def validate_params(params: dict):
    required_params = [
        "prompt",
        "audio_length_in_s",
        "guidance_scale",
        "num_inference_steps",
        "negative_prompt",
        "num_waveforms_per_prompt",
    ]
    for param in required_params:
        if params.get(param) is None:
            raise ValueError(f"{param} must be specified")

    for key in params:
        if key not in required_params:
            raise ValueError(f"Parameter {key} is not a valid parameter")


def generate_params(prompt):
    return {
        "prompt": prompt,
        "audio_length_in_s": 10,
        "guidance_scale": 3,
        "num_inference_steps": 10,
        "negative_prompt": "low quality, average quality, noise, high pitch, artefacts",
        "num_waveforms_per_prompt": 1,
    }


def text2audio(pipe, parameters):
    validate_params(parameters)
    print(f"Generating audio for prompt: {parameters.get('prompt')}")
    waveforms = pipe(**parameters)["audios"]
    return waveforms[0]
