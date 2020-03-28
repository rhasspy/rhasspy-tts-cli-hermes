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

    hermes_cli.add_hermes_args(parser)
    args = parser.parse_args()

    hermes_cli.setup_logging(args)
    _LOGGER.debug(args)

    try:
        loop = asyncio.get_event_loop()

        # Listen for messages
        client = mqtt.Client()
        hermes = TtsHermesMqtt(
            client,
            args.tts_command,
            play_command=args.play_command,
            voices_command=args.voices_command,
            language=args.language,
            siteIds=args.siteId,
            loop=loop,
        )

        _LOGGER.debug("Connecting to %s:%s", args.host, args.port)
        hermes_cli.connect(client, args)
        client.loop_start()

        # Run event loop
        hermes.loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        _LOGGER.debug("Shutting down")


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
