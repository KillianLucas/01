from interpreter import Interpreter
interpreter = Interpreter()

interpreter.tts = "elevenlabs"
interpreter.stt = "deepgram"

interpreter.model = "gpt-4o"
interpreter.provider = "openai"
interpreter.auto_run = True

interpreter.instructions = "Be very concise in your responses."
