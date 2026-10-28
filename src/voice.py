from gnani.stt import GnaniSTTClient
from gnani.tts import GnaniTTSClient
from src.config import TTS_MODEL, TTS_VOICE, DEFAULT_LANGUAGE

stt = GnaniSTTClient()
tts = GnaniTTSClient()

def voice_turn(audio_path: str, agent):
    heard_res = stt.transcribe(audio_path, language_code=DEFAULT_LANGUAGE)
    heard = heard_res.get("transcript", "").strip()
    
    if not heard:
        reply = "Sorry, I didn't catch that. Could you please repeat?"
        sources = []
    else:
        reply, sources = agent.respond(heard)
        
    return heard, reply, sources

def synthesize_response(text: str, output_path: str):
    tts.synthesize(
        text,
        voice=TTS_VOICE,
        model=TTS_MODEL,
        language=DEFAULT_LANGUAGE,
        output_file=output_path
    )