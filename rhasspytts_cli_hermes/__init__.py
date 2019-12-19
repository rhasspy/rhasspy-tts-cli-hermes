"""Hermes MQTT server for Rhasspy TTS using external program"""
import json
import logging
import shlex
import typing
import subprocess
from uuid import uuid4

import attr

from rhasspyhermes.base import Message
from rhasspyhermes.tts import TtsSay, TtsSayFinished
from rhasspyhermes.audioserver import AudioPlayBytes

_LOGGER = logging.getLogger(__name__)


class TtsHermesMqtt:
    """Hermes MQTT server for Rhasspy TTS using external program."""

    def __init__(
        self,
        client,
        tts_command: str,
        play_command: typing.Optional[str] = None,
        siteId: str = "default",
    ):
        self.client = client
        self.tts_command = tts_command
        self.play_command = play_command
        self.siteId = siteId

    # -------------------------------------------------------------------------

    def handle_say(self, say: TtsSay):
        """Run TTS system and publish WAV data."""
        wav_bytes: typing.Optional[bytes] = None

        try:
            say_command = shlex.split(self.tts_command.format(lang=say.lang)) + [
                say.text
            ]
            _LOGGER.debug(say_command)

            wav_bytes = subprocess.check_output(say_command)
            _LOGGER.debug("Got %s byte(s) of WAV data", len(wav_bytes))
        except Exception:
            _LOGGER.exception("tts_command")
        finally:
            self.publish(TtsSayFinished(id=say.id, sessionId=say.sessionId))

        if wav_bytes:
            # Play WAV
            if self.play_command:
                try:
                    # Play locally
                    play_command = shlex.split(self.play_command.format(lang=say.lang))
                    _LOGGER.debug(play_command)

                    subprocess.run(play_command, input=wav_bytes, check=True)
                except Exception:
                    _LOGGER.exception("play_command")
            else:
                # Publish playBytes
                request_id = say.id or str(uuid4())
                self.client.publish(
                    AudioPlayBytes.topic(site_id=self.siteId, request_id=request_id),
                    wav_bytes,
                )

    # -------------------------------------------------------------------------

    def on_connect(self, client, userdata, flags, rc):
        """Connected to MQTT broker."""
        try:
            topics = [TtsSay.topic()]
            for topic in topics:
                self.client.subscribe(topic)
                _LOGGER.debug("Subscribed to %s", topic)
        except Exception:
            _LOGGER.exception("on_connect")

    def on_message(self, client, userdata, msg):
        """Received message from MQTT broker."""
        try:
            _LOGGER.debug("Received %s byte(s) on %s", len(msg.payload), msg.topic)

            if msg.topic == TtsSay.topic():
                json_payload = json.loads(msg.payload or "{}")

                if not self._check_siteId(json_payload):
                    return

                say = TtsSay(**json_payload)
                self.handle_say(say)
        except Exception:
            _LOGGER.exception("on_message")

    def publish(self, message: Message, **topic_args):
        """Publish a Hermes message to MQTT."""
        try:
            _LOGGER.debug("-> %s", message)
            topic = message.topic(**topic_args)
            payload = json.dumps(attr.asdict(message))
            _LOGGER.debug("Publishing %s char(s) to %s", len(payload), topic)
            self.client.publish(topic, payload)
        except Exception:
            _LOGGER.exception("on_message")

    def _check_siteId(self, json_payload: typing.Dict[str, typing.Any]) -> bool:
        return json_payload.get("siteId", "default") == self.siteId
