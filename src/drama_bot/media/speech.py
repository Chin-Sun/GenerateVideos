"""Explicit unavailable capabilities; never synthesize placeholders in production."""

from drama_bot.contracts import UnsupportedCapability


class UnavailableSpeechProvider:
    def synthesize(self, line, destination):
        raise UnsupportedCapability("No real Chinese TTS provider configured")


class UnavailableLipSyncProvider:
    def synchronize(self, video, audio, destination):
        raise UnsupportedCapability("No real lip-sync provider configured; mouth motion unverified")
