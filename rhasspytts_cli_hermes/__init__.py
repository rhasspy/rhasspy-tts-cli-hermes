"""Hermes MQTT server for Rhasspy TTS using external program"""
import logging
import shlex
import subprocess
import typing
from uuid import uuid4

from rhasspyhermes.audioserver import AudioPlayBytes
from rhasspyhermes.base import Message
from rhasspyhermes.client import GeneratorType, HermesClient, TopicArgs
from rhasspyhermes.tts import GetVoices, TtsSay, TtsSayFinished, Voice, Voices

_LOGGER = logging.getLogger("rhasspytts_cli_hermes")

# -----------------------------------------------------------------------------


class TtsHermesMqtt(HermesClient):
    """Hermes MQTT server for Rhasspy TTS using external program."""

    def __init__(
        self,
        client,
        tts_command: str,
        play_command: typing.Optional[str] = None,
        voices_command: typing.Optional[str] = None,
        language: str = "",
        siteIds: typing.Optional[typing.List[str]] = None,
    ):
        super().__init__("rhasspytts_cli_hermes", client, siteIds=siteIds)

        self.subscribe(TtsSay, GetVoices)

        self.tts_command = tts_command
        self.play_command = play_command
        self.voices_command = voices_command
        self.language = language

    # -------------------------------------------------------------------------

    async def handle_say(
        self, say: TtsSay
    ) -> typing.AsyncIterable[
        typing.Union[TtsSayFinished, typing.Tuple[AudioPlayBytes, TopicArgs]]
    ]:
        """Run TTS system and publish WAV data."""
        wav_bytes: typing.Optional[bytes] = None

        try:
            language = say.lang or self.language
            say_command = shlex.split(self.tts_command.format(lang=language)) + [
                say.text
            ]
            _LOGGER.debug(say_command)

            wav_bytes = subprocess.check_output(say_command)
            assert wav_bytes
            _LOGGER.debug("Got %s byte(s) of WAV data", len(wav_bytes))
        except Exception:
            _LOGGER.exception("tts_command")
        finally:
            yield TtsSayFinished(id=say.id, siteId=say.siteId, sessionId=say.sessionId)

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
                yield (
                    AudioPlayBytes(wav_bytes=wav_bytes),
                    {"siteId": say.siteId, "requestId": request_id},
                )

    async def handle_get_voices(
        self, get_voices: GetVoices
    ) -> typing.AsyncIterable[Voices]:
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
        yield Voices(voices=voices, id=get_voices.id, siteId=get_voices.siteId)

    # -------------------------------------------------------------------------

    async def on_message(
        self,
        message: Message,
        siteId: typing.Optional[str] = None,
        sessionId: typing.Optional[str] = None,
        topic: typing.Optional[str] = None,
    ) -> GeneratorType:
        """Received message from MQTT broker."""
        if isinstance(message, TtsSay):
            async for say_result in self.handle_say(message):
                yield say_result
        elif isinstance(message, GetVoices):
            async for voice_result in self.handle_get_voices(message):
                yield voice_result
        else:
            _LOGGER.warning("Unexpected message: %s", message)
