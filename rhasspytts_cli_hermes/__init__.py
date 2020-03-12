"""Hermes MQTT server for Rhasspy TTS using external program"""
import json
import logging
import shlex
import subprocess
import typing
from uuid import uuid4

import attr
from rhasspyhermes.audioserver import AudioPlayBytes
from rhasspyhermes.base import Message
from rhasspyhermes.tts import GetVoices, TtsSay, TtsSayFinished, Voice, Voices

_LOGGER = logging.getLogger("rhasspytts_cli_hermes")

# -----------------------------------------------------------------------------


class TtsHermesMqtt:
    """Hermes MQTT server for Rhasspy TTS using external program."""

    def __init__(
        self,
        client,
        tts_command: str,
        play_command: typing.Optional[str] = None,
        voices_command: typing.Optional[str] = None,
        siteIds: typing.Optional[typing.List[str]] = None,
    ):
        self.client = client
        self.tts_command = tts_command
        self.play_command = play_command
        self.voices_command = voices_command
        self.siteIds = siteIds or []

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
            assert wav_bytes
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
                self.publish(
                    AudioPlayBytes(wav_bytes=wav_bytes),
                    siteId=say.siteId,
                    requestId=request_id,
                )

    def handle_get_voices(self, get_voices: GetVoices):
        """Publish list of available voices"""
        voices: typing.Dict[str, Voice] = {}
        try:
            assert self.voices_command, "No voices command"
            _LOGGER.debug(self.voices_command)

            lines = (
                subprocess.check_output(self.voices_command, shell=True)
                .decode()
                .splitlines()
            )

            # Read a voice on each line.
            # The line must start with a voice ID, optionally follow by
            # whitespace and a description.
            for line in lines:
                line = line.strip()
                if line:
                    # ID description with whitespace
                    parts = line.split(maxsplit=1)
                    voice = Voice(voiceId=parts[0])
                    if len(parts) > 1:
                        voice.description = parts[1]

                    voices[voice.voiceId] = voice
        except Exception:
            _LOGGER.exception("handle_get_voices")

        # Publish response
        self.publish(Voices(voices=voices, id=get_voices.id, siteId=get_voices.siteId))

    # -------------------------------------------------------------------------

    def on_connect(self, client, userdata, flags, rc):
        """Connected to MQTT broker."""
        try:
            topics = [TtsSay.topic(), GetVoices.topic()]
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

                self.handle_say(TtsSay.from_dict(json_payload))
            elif msg.topic == GetVoices.topic():
                json_payload = json.loads(msg.payload or "{}")
                if not self._check_siteId(json_payload):
                    return

                self.handle_get_voices(GetVoices.from_dict(json_payload))

        except Exception:
            _LOGGER.exception("on_message")

    def publish(self, message: Message, **topic_args):
        """Publish a Hermes message to MQTT."""
        try:
            if isinstance(message, AudioPlayBytes):
                _LOGGER.debug(
                    "-> %s(%s byte(s))",
                    message.__class__.__name__,
                    len(message.wav_bytes),
                )
                payload = message.wav_bytes
            else:
                _LOGGER.debug("-> %s", message)
                payload = json.dumps(attr.asdict(message)).encode()

            topic = message.topic(**topic_args)
            _LOGGER.debug("Publishing %s bytes(s) to %s", len(payload), topic)
            self.client.publish(topic, payload)
        except Exception:
            _LOGGER.exception("on_message")

    def _check_siteId(self, json_payload: typing.Dict[str, typing.Any]) -> bool:
        if self.siteIds:
            return json_payload.get("siteId", "default") in self.siteIds

        # All sites
        return True
