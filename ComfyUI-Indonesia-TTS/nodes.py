import os
import logging
import torch
import comfy.sample as comfy_sample
from transformers import VitsModel, AutoTokenizer
import torchaudio.functional as F
import torchaudio.transforms as T

logger = logging.getLogger(__name__)

# Daftar variant (karakter) berupa repo HF yang mendukung Bahasa Indonesia
VARIANTS = [
    "facebook/mms-tts-ind",                # Default Indonesian
    "Wikidepia/indonesian-tts",            # Indonesian TTS community
    # Tambahkan repo lain yang Anda temukan dengan logat Indonesia
]

# Default cache folder
DEFAULT_CACHE = "models/mms_tts_ind"

class FacebookMMSTTSNode:
    """
    Synthesizes speech waveform from input text using various Indonesian TTS models.
    Menyediakan kontrol speed, pitch, kvalitet, reverb, dan delay.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {
                    "multiline": True,
                    "default": "Halo, bagaimana kabarmu hari ini?",
                    "description": "Teks yang akan disintesis"
                }),
                "variant": ([*VARIANTS], {
                    "default": VARIANTS[0],
                    "description": "Pilih karakter / model HF untuk suara"
                }),
                "cache_dir": ("STRING", {
                    "default": DEFAULT_CACHE,
                    "description": "Folder lokal untuk cache model"
                }),
                "speed": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.5,
                    "max": 2.0,
                    "description": "Kecepatan playback: <1 lambat, >1 cepat"
                }),
                "pitch_shift": ("FLOAT", {
                    "default": 0.0,
                    "min": -12.0,
                    "max": 12.0,
                    "description": "Pitch shift dalam semitone: positif naik, negatif turun"
                }),
                "quality": (["low","medium","high"], {
                    "default": "medium",
                    "description": "Quality level: berpengaruh pada upsampling/resolution"
                }),
                "reverb": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 1.0,
                    "description": "Amount reverb (0-1)"
                }),
                "delay_ms": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 1000,
                    "description": "Delay effect in milliseconds"
                }),
                "delay_feedback": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 0.95,
                    "description": "Delay feedback (0-0.95)"
                }),
            }
        }

    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)
    FUNCTION = "generate"
    CATEGORY = "facebook-tts"

    def __init__(self):
        self._model = None
        self._tokenizer = None
        self._sample_rate = None

    def _load_model(self, repo_id: str, cache_dir: str):
        os.makedirs(cache_dir, exist_ok=True)
        logger.info(f"Loading model {repo_id} into cache {cache_dir}...")
        self._model = VitsModel.from_pretrained(repo_id, cache_dir=cache_dir)
        self._tokenizer = AutoTokenizer.from_pretrained(repo_id, cache_dir=cache_dir)
        self._model.eval()
        # Ambil sample rate dari config, fallback 22050
        self._sample_rate = getattr(self._model.config, "sampling_rate", 22050)
        logger.info(f"Model loaded. Sample rate = {self._sample_rate}")

    def generate(self, text: str, variant: str, cache_dir: str,
                 speed: float, pitch_shift: float, quality: str,
                 reverb: float, delay_ms: int, delay_feedback: float):
        # Lazy-load model sesuai variant
        if self._model is None or self._tokenizer is None or self._current_variant != variant:
            try:
                self._load_model(variant, cache_dir)
                self._current_variant = variant
            except Exception as e:
                logger.error(f"Failed to load model '{variant}': {e}")
                return (None,)

        # Tokenisasi & inferensi
        try:
            inputs = self._tokenizer(text, return_tensors="pt")
            with torch.no_grad():
                outputs = self._model(**inputs)
            waveform = outputs.waveform.cpu().squeeze(0)  # (time,)
        except Exception as e:
            logger.error(f"TTS generation error: {e}")
            return (None,)

        # Time-stretch via resampling untuk speed
        sr = self._sample_rate
        target_sr = int(sr * speed)
        y = F.resample(waveform.unsqueeze(0), sr, target_sr).squeeze(0)

        # Pitch shift (semitone) dengan phase vocoder
        if abs(pitch_shift) > 0.001:
            n_steps = pitch_shift
            # torchaudio pitch shift transform (quality dependent)
            bins_per_octave = 12
            y = T.PitchShift(sample_rate=target_sr,
                             n_steps=n_steps,
                             bins_per_octave=bins_per_octave)(y.unsqueeze(0)).squeeze(0)

        # Basic up/down sampling for quality
        if quality == "low":
            y = F.resample(y.unsqueeze(0), target_sr, target_sr//2).squeeze(0)
            y = F.resample(y.unsqueeze(0), target_sr//2, target_sr).squeeze(0)
        elif quality == "high":
            up = 2
            y = F.resample(y.unsqueeze(0), target_sr, target_sr*up).squeeze(0)
            y = F.resample(y.unsqueeze(0), target_sr*up, target_sr).squeeze(0)

        # Efek reverb sederhana dengan convolution IR (optional: gunakan IR nyata)
        if reverb > 0.001:
            # buat IR sederhana: exponential decay
            ir_length = int(0.03 * target_sr)
            ir = torch.logspace(start=0, end=-3, steps=ir_length)
            ir = ir / ir.sum()
            y = torch.nn.functional.conv1d(y.unsqueeze(0).unsqueeze(0), ir.unsqueeze(0).unsqueeze(0), padding=ir_length//2).squeeze()
            # mix dry/wet
            y = (1-reverb)*y + reverb*y

        # Efek delay
        if delay_ms > 0 and delay_feedback > 0.0:
            delay_samples = int(target_sr * delay_ms / 1000)
            buffer = torch.zeros(y.shape[0] + delay_samples)
            buffer[:y.shape[0]] = y
            for i in range(y.shape[0]):
                buffer[i+delay_samples] += y[i] * delay_feedback
            y = buffer[:y.shape[0]]

        # Bungkus ke format ComfyUI: batch=1, channel=1
        audio_tensor = torch.from_numpy(y.numpy()).unsqueeze(0).unsqueeze(0).float()
        audio_dict = {
            "waveform": audio_tensor,
            "sample_rate": target_sr
        }
        logger.info(f"Generated audio: variant={variant}, speed={speed}, pitch={pitch_shift}, quality={quality}, reverb={reverb}, delay={delay_ms}ms")
        return (audio_dict,)

    @classmethod
    def IS_CHANGED(cls, text, variant, cache_dir, speed, pitch_shift, quality, reverb, delay_ms, delay_feedback):
        # Trigger rerun on any input change
        return hash((text, variant, cache_dir, speed, pitch_shift, quality, reverb, delay_ms, delay_feedback))

# Mapping nama node ke kelasnya agar ComfyUI dapat mendeteksi
NODE_CLASS_MAPPINGS = {
    "Facebook MMS-TTS-IND Variants FX": FacebookMMSTTSNode,
}
