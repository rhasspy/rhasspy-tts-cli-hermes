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

## Running With Docker

```bash
docker run -it rhasspy/rhasspy-tts-cli-hermes:<VERSION> <ARGS>
```

## Building From Source

Clone the repository and create the virtual environment:

```bash
git clone https://github.com/rhasspy/rhasspy-tts-cli-hermes.git
cd rhasspy-tts-cli-hermes
make venv
```

Run the `bin/rhasspy-tts-cli-hermes` script to access the command-line interface:

```bash
bin/rhasspy-tts-cli-hermes --help
```

## Building the Debian Package

Follow the instructions to build from source, then run:

```bash
source .venv/bin/activate
make debian
```

If successful, you'll find a `.deb` file in the `dist` directory that can be installed with `apt`.

## Building the Docker Image

Follow the instructions to build from source, then run:

```bash
source .venv/bin/activate
make docker
```

This will create a Docker image tagged `rhasspy/rhasspy-tts-cli-hermes:<VERSION>` where `VERSION` comes from the file of the same name in the source root directory.

NOTE: If you add things to the Docker image, make sure to whitelist them in `.dockerignore`.

## Command-Line Options

```
usage: rhasspy-tts-cli-hermes [-h] --tts-command TTS_COMMAND
                              [--play-command PLAY_COMMAND] [--host HOST]
                              [--port PORT] [--siteId SITEID] [--debug]

optional arguments:
  -h, --help            show this help message and exit
  --tts-command TTS_COMMAND
                        Text to speech command to execute with text as an
                        argument
  --play-command PLAY_COMMAND
                        Command to play WAV data from stdin (default: publish
                        playBytes)
  --host HOST           MQTT host (default: localhost)
  --port PORT           MQTT port (default: 1883)
  --siteId SITEID       Hermes siteId of this server
  --debug               Print DEBUG messages to the console
```
