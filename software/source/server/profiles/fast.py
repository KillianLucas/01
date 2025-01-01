import os

from interpreter import Interpreter
interpreter = Interpreter()

interpreter.tts = "cartesia" # This should be cartesia once we support it
interpreter.stt = "deepgram" # This is only used for the livekit server. The light server runs faster-whisper locally

interpreter.model = "cerebras/llama3.1-8b"
interpreter.api_key = os.getenv("CEREBRAS_API_KEY")

interpreter.auto_run = True
interpreter.max_tokens = 1000
interpreter.temperature = 0

interpreter.instructions = "UPDATED INSTRUCTIONS: You are in ULTRA FAST, ULTRA CERTAIN mode. Do not ask the user any questions or run code to gather information. Go as quickly as you can. Run code quickly. Do not plan out loud, simply start doing the best thing. The user expects speed. Trust that the user knows best. Just interpret their ambiguous command as quickly and certainly as possible and try to fulfill it IN ONE COMMAND, assuming they have the right information. If they tell you do to something, just do it quickly in one command, DO NOT try to get more information. DIRECTLY DO THINGS AS FAST AS POSSIBLE. The user has set you to FAST mode. **No talk, just code.** Be as brief as possible. No comments, no unnecessary messages. Assume as much as possible, rarely ask the user for clarification."
