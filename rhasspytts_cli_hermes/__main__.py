"""Hermes MQTT service for Rhasspy TTS with external program."""
import argparse
import asyncio
import logging

import paho.mqtt.client as mqtt
import rhasspyhermes.cli as hermes_cli

from . import TtsHermesMqtt

_LOGGER = logging.getLogger("rhasspytts_cli_hermes")

# -----------------------------------------------------------------------------


def main():
    """Main method."""
    parser = argparse.ArgumentParser(prog="rhasspy-tts-cli-hermes")
    parser.add_argument(
        "--tts-command",
        required=True,
        help="Text to speech command to execute with text as an argument",
    )
    parser.add_argument(
        "--play-command",
        help="Command to play WAV data from stdin (default: publish playBytes)",
    )
    parser.add_argument(
        "--voices-command", help="Command to list voices (one per line)"
    )
    parser.add_argument(
        "--language", default="", help="Default language passed to command"
    )
    parser.add_argument(
        "--temporary-wav",
        action="store_true",
        help="Pass path to temporary WAV file to TTS command",
    )
    parser.add_argument(
        "--text-on-stdin",
        action="store_true",
        help="Pass input text to TTS command's stdin instead of as arguments",
    )

    hermes_cli.add_hermes_args(parser)
    args = parser.parse_args()

    hermes_cli.setup_logging(args)
    _LOGGER.debug(args)

    # Listen for messages
    client = mqtt.Client()
    hermes = TtsHermesMqtt(
        client,
        args.tts_command,
        play_command=args.play_command,
        voices_command=args.voices_command,
        use_temp_wav=args.temporary_wav,
        text_on_stdin=args.text_on_stdin,
        language=args.language,
        site_ids=args.site_id,
    )

    _LOGGER.debug("Connecting to %s:%s", args.host, args.port)
    hermes_cli.connect(client, args)
    client.loop_start()

    try:
        # Run event loop
        asyncio.run(hermes.handle_messages_async())
    except KeyboardInterrupt:
        pass
    finally:
        _LOGGER.debug("Shutting down")
        client.loop_stop()


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
