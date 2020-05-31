"""Hermes MQTT server for Rhasspy TTS using external program"""
import asyncio
import logging
import os
import shlex
import subprocess
import tempfile
import typing
from uuid import uuid4

from rhasspyhermes.audioserver import AudioPlayBytes, AudioPlayError, AudioPlayFinished
from rhasspyhermes.base import Message
from rhasspyhermes.client import GeneratorType, HermesClient, TopicArgs
from rhasspyhermes.tts import GetVoices, TtsError, TtsSay, TtsSayFinished, Voice, Voices

from .utils import get_wav_duration

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
        use_temp_wav: bool = False,
        text_on_stdin: bool = False,
        site_ids: typing.Optional[typing.List[str]] = None,
    ):
        super().__init__("rhasspytts_cli_hermes", client, site_ids=site_ids)

        self.subscribe(TtsSay, GetVoices, AudioPlayFinished)

        self.tts_command = tts_command
        self.play_command = play_command
        self.voices_command = voices_command
        self.language = language

        # If True, a temporary file is used for TTS WAV audio
        self.use_temp_wav = use_temp_wav

        # If True, TTS text is provided on stdin instead of as arguments
        self.text_on_stdin = text_on_stdin

        self.play_finished_events: typing.Dict[typing.Optional[str], asyncio.Event] = {}

        # Seconds added to playFinished timeout
        self.finished_timeout_extra: float = 0.25

    # -------------------------------------------------------------------------

    async def handle_say(
        self, say: TtsSay
    ) -> typing.AsyncIterable[
        typing.Union[
            TtsSayFinished,
            typing.Tuple[AudioPlayBytes, TopicArgs],
            TtsError,
            AudioPlayError,
        ]
    ]:
        """Run TTS system and publish WAV data."""
        wav_bytes: typing.Optional[bytes] = None
        temp_wav_path: typing.Optional[str] = None

        try:
            language = say.lang or self.language
            format_args = {"lang": language}

            if self.use_temp_wav:
                # WAV audio will be stored in a temporary file
                temp_wav_path = tempfile.NamedTemporaryFile(
                    suffix=".wav", delete=False
                ).name

                # Path to WAV file
                format_args["file"] = temp_wav_path

            tts_command_str = self.tts_command.format(**format_args)
            say_command = shlex.split(tts_command_str)

            if not self.text_on_stdin:
                # Text as command-line arguments
                say_command += [say.text]

            _LOGGER.debug(say_command)

            # WAV audio on stdout, text as command-line argument
            proc_stdin: typing.Optional[int] = None
            proc_stdout: typing.Optional[int] = subprocess.PIPE
            proc_input: typing.Optional[bytes] = None

            if self.use_temp_wav:
                # WAV audio from file
                proc_stdout = None

            if self.text_on_stdin:
                # Text from standard in
                proc_stdin = subprocess.PIPE
                proc_input = say.text.encode()

            # Run TTS process
            proc = subprocess.Popen(say_command, stdin=proc_stdin, stdout=proc_stdout)
            wav_bytes, _ = proc.communicate(input=proc_input)
            proc.wait()

            assert proc.returncode == 0, f"Non-zero exit code: {proc.returncode}"

            if self.use_temp_wav and temp_wav_path:
                with open(temp_wav_path, "rb") as wav_file:
                    wav_bytes = wav_file.read()

            assert wav_bytes, "No WAV data received"
            _LOGGER.debug("Got %s byte(s) of WAV data", len(wav_bytes))

            if wav_bytes:
                finished_event = asyncio.Event()

                # Play WAV
                if self.play_command:
                    try:
                        # Play locally
                        play_command = shlex.split(
                            self.play_command.format(lang=say.lang)
                        )
                        _LOGGER.debug(play_command)

                        subprocess.run(play_command, input=wav_bytes, check=True)

                        # Don't wait for playFinished
                        finished_event.set()
                    except Exception as e:
                        _LOGGER.exception("play_command")
                        yield AudioPlayError(
                            error=str(e),
                            context=say.id,
                            site_id=say.site_id,
                            session_id=say.session_id,
                        )
                else:
                    # Publish playBytes
                    request_id = say.id or str(uuid4())
                    self.play_finished_events[request_id] = finished_event

                    yield (
                        AudioPlayBytes(wav_bytes=wav_bytes),
                        {"site_id": say.site_id, "request_id": request_id},
                    )

                try:
                    # Wait for audio to finished playing or timeout
                    wav_duration = get_wav_duration(wav_bytes)
                    wav_timeout = wav_duration + self.finished_timeout_extra

                    _LOGGER.debug("Waiting for play finished (timeout=%s)", wav_timeout)
                    await asyncio.wait_for(finished_event.wait(), timeout=wav_timeout)
                except asyncio.TimeoutError:
                    _LOGGER.warning("Did not receive playFinished before timeout")

        except Exception as e:
            _LOGGER.exception("handle_say")
            yield TtsError(
                error=str(e),
                context=say.id,
                site_id=say.site_id,
                session_id=say.session_id,
            )
        finally:
            yield TtsSayFinished(
                id=say.id, site_id=say.site_id, session_id=say.session_id
            )

            if temp_wav_path:
                try:
                    os.unlink(temp_wav_path)
                except Exception:
                    pass

    async def handle_get_voices(
        self, get_voices: GetVoices
    ) -> typing.AsyncIterable[typing.Union[Voices, TtsError]]:
        """Publish list of available voices"""
        voices: typing.List[Voice] = []
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
                    voice = Voice(voice_id=parts[0])
                    if len(parts) > 1:
                        voice.description = parts[1]

                    voices.append(voice)
        except Exception as e:
            _LOGGER.exception("handle_get_voices")
            yield TtsError(
                error=str(e), context=get_voices.id, site_id=get_voices.site_id
            )

        # Publish response
        yield Voices(voices=voices, id=get_voices.id, site_id=get_voices.site_id)

    # -------------------------------------------------------------------------

    async def on_message(
        self,
        message: Message,
        site_id: typing.Optional[str] = None,
        session_id: typing.Optional[str] = None,
        topic: typing.Optional[str] = None,
    ) -> GeneratorType:
        """Received message from MQTT broker."""
        if isinstance(message, TtsSay):
            async for say_result in self.handle_say(message):
                yield say_result
        elif isinstance(message, GetVoices):
            async for voice_result in self.handle_get_voices(message):
                yield voice_result
        elif isinstance(message, AudioPlayFinished):
            # Signal audio play finished
            finished_event = self.play_finished_events.pop(message.id, None)
            if finished_event:
                finished_event.set()
        else:
            _LOGGER.warning("Unexpected message: %s", message)
