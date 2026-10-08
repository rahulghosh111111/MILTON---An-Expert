"""Speech-to-text input. This is a minimal, swappable placeholder for the
"already built, upstream" ASR the system prompt assumes — good enough for
English via the free Google Web Speech API, but not genuinely multilingual
code-switch recognition. For real Hindi/Bengali/English mixing, swap
listen_from_mic's internals for a local multilingual model (e.g.
faster-whisper) and keep the same return signature (str transcript).
"""

from . import config

_recognizer = None


def _get_recognizer():
    global _recognizer
    if _recognizer is None:
        import speech_recognition as sr

        _recognizer = sr.Recognizer()
    return _recognizer


def listen_from_mic(timeout=5, phrase_time_limit=10):
    import speech_recognition as sr

    recognizer = _get_recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.3)
        audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)

    try:
        return recognizer.recognize_google(audio, language=config.ASR_LANGUAGE)
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        return ""


def listen_from_console(prompt="You: "):
    return input(prompt)
