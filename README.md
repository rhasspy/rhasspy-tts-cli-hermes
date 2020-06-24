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

## Requirements

* Python 3.7

## Installation

```bash
$ git clone https://github.com/rhasspy/rhasspy-tts-cli-hermes
$ cd rhasspy-tts-cli-hermes
$ ./configure
$ make
$ make install
```

## Running

Run script:

```bash
bin/rhasspy-tts-cli-hermes <ARGS>
```

## Command-Line Options

```
usage: rhasspy-tts-cli-hermes [-h] --tts-command TTS_COMMAND
                              [--play-command PLAY_COMMAND]
                              [--voices-command VOICES_COMMAND]
                              [--language LANGUAGE] [--temporary-wav]
                              [--text-on-stdin] [--host HOST] [--port PORT]
                              [--username USERNAME] [--password PASSWORD]
                              [--tls] [--tls-ca-certs TLS_CA_CERTS]
                              [--tls-certfile TLS_CERTFILE]
                              [--tls-keyfile TLS_KEYFILE]
                              [--tls-cert-reqs {CERT_REQUIRED,CERT_OPTIONAL,CERT_NONE}]
                              [--tls-version TLS_VERSION]
                              [--tls-ciphers TLS_CIPHERS] [--site-id SITE_ID]
                              [--debug] [--log-format LOG_FORMAT]

optional arguments:
  -h, --help            show this help message and exit
  --tts-command TTS_COMMAND
                        Text to speech command to execute with text as an
                        argument
  --play-command PLAY_COMMAND
                        Command to play WAV data from stdin (default: publish
                        playBytes)
  --voices-command VOICES_COMMAND
                        Command to list voices (one per line)
  --language LANGUAGE   Default language passed to command
  --temporary-wav       Pass path to temporary WAV file to TTS command
  --text-on-stdin       Pass input text to TTS command's stdin instead of as
                        arguments
  --host HOST           MQTT host (default: localhost)
  --port PORT           MQTT port (default: 1883)
  --username USERNAME   MQTT username
  --password PASSWORD   MQTT password
  --tls                 Enable MQTT TLS
  --tls-ca-certs TLS_CA_CERTS
                        MQTT TLS Certificate Authority certificate files
  --tls-certfile TLS_CERTFILE
                        MQTT TLS certificate file (PEM)
  --tls-keyfile TLS_KEYFILE
                        MQTT TLS key file (PEM)
  --tls-cert-reqs {CERT_REQUIRED,CERT_OPTIONAL,CERT_NONE}
                        MQTT TLS certificate requirements (default:
                        CERT_REQUIRED)
  --tls-version TLS_VERSION
                        MQTT TLS version (default: highest)
  --tls-ciphers TLS_CIPHERS
                        MQTT TLS ciphers to use
  --site-id SITE_ID     Hermes site id(s) to listen for (default: all)
  --debug               Print DEBUG messages to the console
  --log-format LOG_FORMAT
                        Python logger format
```
