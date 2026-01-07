# Supertonic V2 TTS Plugin for Open Voice OS



A lightweight, local TTS plugin for [Open Voice OS (OVOS)](https://www.openvoiceos.org/) using [Supertonic V2](https://github.com/supertone-inc/supertonic) ONNX model.


## Installation

```bash
git clone
cd ovos-tts-plugin-supertonic
pip install .

```

## Configuration

Update your mycroft.conf:
```
  "tts": {
    "module": "supertonic_tts_plugin",
    "supertonic_tts_plugin": {
      "voice": "Sarah",  // Choose: Sarah (F1), Lily (F2), Jessica (F3), Olivia (F4), Emily (F5), Alex (M1), James (M2), Robert (M3), Sam (M4), Daniel (M5)
      "lang": "en", // Change the language to the preferred other language then OVOS interface language, if supported. Fallback is "en"
      "quality": 5, #quality steps range 1 - 15
      "speed": 1.05 #default suggested by Supertonic, speed up to 1.3x supported
    }
}
```

## Auto download
The models are auto downloaded on first use (it takes some time the first time to download ~250mb)
