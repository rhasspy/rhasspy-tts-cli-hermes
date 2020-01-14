# Rhasspy TTS Hermes MQTT Service

[![Continous Integration](https://github.com/rhasspy/rhasspy-tts-cli-hermes/workflows/Tests/badge.svg)](https://github.com/rhasspy/rhasspy-tts-cli-hermes/actions)
[![GitHub license](https://img.shields.io/github/license/rhasspy/rhasspy-tts-cli-hermes.svg)](https://github.com/rhasspy/rhasspy-tts-cli-hermes/blob/master/LICENSE)

Implements `hermes/tts` functionality from [Hermes protocol](https://docs.snips.ai/reference/hermes) using any of the following command-line text to speech systems:

* [eSpeak](http://espeak.sourceforge.net)
    * `espeak --stdout`
* [flite](http://www.festvox.org/flite)
    * `flite -o /dev/stdout -t`
* [PicoTTS](https://en.wikipedia.org/wiki/SVOX)
    * `pico2wave.sh` (in `bin`)
* [MaryTTS](http://mary.dfki.de)
    * `marytts.sh 'http://localhost:59125/process' {lang}` (in `bin`)

Use `--play-command aplay` to play speech locally instead of using `hermes/audioServer<siteId>/playBytes`.
