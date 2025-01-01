from interpreter import Interpreter
interpreter = Interpreter()

interpreter.tts = "local"
interpreter.stt = "local"

# LLM settings
interpreter.model = "ollama/codestral"
interpreter.auto_run = True