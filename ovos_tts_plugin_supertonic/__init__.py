import os
import requests
import soundfile as sf
from ovos_plugin_manager.templates.tts import TTS as OVOS_TTS
from ovos_utils.lang import standardize_lang_tag
from ovos_utils.log import LOG
from ovos_utils.xdg_utils import xdg_data_home
from .helper import load_text_to_speech, load_voice_style

class SupertonicTTSPlugin(OVOS_TTS):
    # Mapping for hybrid support (Names and IDs)
    NAME_TO_ID = {
        "alex": "M1", "james": "M2", "robert": "M3", "sam": "M4", "daniel": "M5",
        "sarah": "F1", "lily": "F2", "jessica": "F3", "olivia": "F4", "emily": "F5"
    }
    
    SUPPORTED_LANGS = {"en", "ko", "es", "pt", "fr"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, audio_ext="wav")
        
        # Gebruik xdg_data_home() omdat get_xdg_data_save_path ontbreekt
        self.model_root = self.config.get("model_path") or \
                          os.path.join(str(xdg_data_home()), "ovos", "tts", "supertonic")
        
        self.onnx_dir = os.path.join(self.model_root, "onnx")
        self.voices_dir = os.path.join(self.model_root, "voice_styles")

        # Automatically download models if they are missing
        self._maybe_download_models()

        # Initialize the ONNX engine
        self.engine = load_text_to_speech(self.onnx_dir, use_gpu=False)
        
        # 1. Determine default language from config or system, fallback to 'en'
        conf_lang = self.config.get("lang") or self.lang or "en"
        self.default_lang = standardize_lang_tag(conf_lang).split("-")[0]
        if self.default_lang not in self.SUPPORTED_LANGS:
            LOG.warning(f"Supertonic: Configured lang '{self.default_lang}' not supported. Falling back to 'en'.")
            self.default_lang = "en"

        self.default_voice = self.config.get("voice", "sarah").lower()
        self.speed = self.config.get("speed", 1.05)
        self.steps = int(self.config.get("quality", 5))

    def _maybe_download_models(self):
        """Downloads V2 models from HuggingFace if not found locally."""
        repo_url = "https://huggingface.co/Supertone/supertonic-2/resolve/main"
        
        files_to_download = [
            "onnx/tts.json", "onnx/unicode_indexer.json",
            "onnx/duration_predictor.onnx", "onnx/text_encoder.onnx", 
            "onnx/vector_estimator.onnx", "onnx/vocoder.onnx"
        ]
        for i in range(1, 6):
            files_to_download.append(f"voice_styles/F{i}.json")
            files_to_download.append(f"voice_styles/M{i}.json")

        headers = {"User-Agent": "Mozilla/5.0"}
        
        for f_path in files_to_download:
            target = os.path.join(self.model_root, f_path)
            if not os.path.exists(target):
                os.makedirs(os.path.dirname(target), exist_ok=True)
                LOG.info(f"Supertonic: Downloading {f_path}...")
                try:
                    r = requests.get(f"{repo_url}/{f_path}", headers=headers, stream=True, timeout=30)
                    r.raise_for_status()
                    with open(target, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=1024*1024):
                            if chunk: f.write(chunk)
                except Exception as e:
                    LOG.error(f"Supertonic: Failed to download {f_path}: {e}")

    def get_tts(self, sentence, wav_file, lang=None, voice=None):
        request_lang = lang or self.default_lang
        lang_code = standardize_lang_tag(request_lang).split("-")[0]
        
        if lang_code not in self.SUPPORTED_LANGS:
            lang_code = "en"

        input_voice = (voice or self.default_voice).lower()
        voice_id = self.NAME_TO_ID.get(input_voice, "F1") if input_voice in self.NAME_TO_ID \
                   else input_voice.upper() if input_voice.upper() in self.NAME_TO_ID.values() \
                   else "F1"

        style_path = os.path.join(self.voices_dir, f"{voice_id}.json")
        style = load_voice_style([style_path])
        
        wav, _ = self.engine(sentence, lang_code, style, self.steps, self.speed)
        sf.write(wav_file, wav[0], 44100)
        
        return (wav_file, None)

    @property
    def available_languages(self) -> set:
        return self.SUPPORTED_LANGS


