import os

os.environ["INTERPRETER_EXPERIMENTAL_WEB_SEARCH"] = "True"

def start_server(server_host, server_port, interpreter, voice, debug):
    interpreter.server()