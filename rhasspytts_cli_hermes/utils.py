"""Utility methods"""
import io
import wave


def get_wav_duration(wav_bytes: bytes) -> float:
    """Return the real-time duration of a WAV file"""
    with io.BytesIO(wav_bytes) as wav_buffer:
        wav_file: wave.Wave_read = wave.open(wav_buffer, "rb")
        with wav_file:
            width = wav_file.getsampwidth()
            rate = wav_file.getframerate()

            # getnframes is not reliable.
            # espeak inserts crazy large numbers.
            guess_frames = (len(wav_bytes) - 44) / width

            return guess_frames / float(rate)
