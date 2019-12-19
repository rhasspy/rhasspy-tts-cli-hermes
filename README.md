# Rhasspy TTS Hermes MQTT Service

Implements `hermes/tts` functionality from [Hermes protocol](https://docs.snips.ai/reference/hermes) using any of the following command-line text to speech systems:

* [eSpeak](http://espeak.sourceforge.net) (text to speech)
    * `espeak --stdout`
* [flite](http://www.festvox.org/flite) (text to speech)
    * `flite -o /dev/stdout -t`
* [PicoTTS](https://en.wikipedia.org/wiki/SVOX) (text to speech)
    * `pico2wave.sh` (in `bin`)
    
Use `--play-command aplay` to play speech locally instead of using `hermes/audioServer<siteId>playBytes`.
