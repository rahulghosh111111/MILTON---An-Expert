"""Offline text-to-speech via the system's SAPI5 voices (pyttsx3). No network
call, no API key. Note: quality/availability of Hindi/Bengali voices depends
on what's installed in Windows Settings > Time & Language > Speech.
"""

_engine = None


def _get_engine():
    global _engine
    if _engine is None:
        import pyttsx3

        _engine = pyttsx3.init()
    return _engine


def speak(text: str):
    if not text:
        return
    engine = _get_engine()
    engine.say(text)
    engine.runAndWait()
