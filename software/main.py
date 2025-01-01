import subprocess
import time
import os
import typer
import platform
import webbrowser
import psutil
import ngrok
import segno
import json

from pathlib import Path
from livekit import api
from source.server.livekit.worker import main as worker_main
from source.server.livekit.multimodal import main as multimodal_main

from dotenv import load_dotenv



load_dotenv()
system_type = platform.system()
app = typer.Typer()



ROOM_NAME = "my-room"


def pre_clean_process(port):
    """Find and kill process running on specified port"""
    for proc in psutil.process_iter(['pid', 'name', 'connections']):
        try:
            for conn in proc.connections():
                if conn.laddr.port == port:
                    print(f"Killing process {proc.pid} ({proc.name()}) on port {port}")
                    proc.terminate()
                    proc.wait()
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return False


def cleanup_processes(processes):
    for process in processes:
        if process.poll() is None:  # if process is still running
            process.terminate()
            process.wait()  # wait for process to terminate


@app.command()
def run(
    lk_host: str = typer.Option(
        "0.0.0.0",
        "--lk-host",
        help="Specify the server host where the livekit server will deploy. For other devices on your network to connect to it, keep it on default `0.0.0.0`",
    ),
    lk_port: int = typer.Option(
        10101,
        "--lk-port",
        help="Specify the server port where the livekit server will deploy",
    ),
    domain: str = typer.Option(None, "--domain", help="Pass in a custom ngrok domain to expose the livekit server over the internet"),
    client: str = typer.Option(None, "--client", help="Run client of a particular type. Accepts `meet` or `mobile`, defaults to `meet`"),
    profiles: bool = typer.Option(
        False,
        "--profiles",
        help="Opens the folder where profiles are contained",
    ),
    profile: str = typer.Option(
        "default.py",
        "--profile",
        help="Specify the path to the profile, or the name of the file if it's in the `profiles` directory (run `--profiles` to open the profiles directory)",
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        help="Print latency measurements and save microphone recordings locally for manual playback",
    ),
    multimodal: bool = typer.Option(
        False,
        "--multimodal",
        help="Run the multimodal agent",
    )
):  
    # preprocess ports
    ports = [10101, 8000, 3000]
    for port in ports:
        pre_clean_process(port)

    if profiles:
        if platform.system() == "Windows":
            subprocess.Popen(['explorer', profiles_dir])
        elif platform.system() == "Darwin":
            subprocess.Popen(['open', profiles_dir])
        elif platform.system() == "Linux":
            subprocess.Popen(['xdg-open', profiles_dir])
        else:
            subprocess.Popen(['open', profiles_dir])
        exit(0)

    profiles_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "source", "server", "profiles")

    if profile:
        if not os.path.isfile(profile):
            profile = os.path.join(profiles_dir, profile)
            if not os.path.isfile(profile):
                profile += ".py"
                if not os.path.isfile(profile):
                    print(f"Invalid profile path: {profile}")
                    exit(1)


    OI_CMD = f"interpreter --serve --profile {profile}"
    oi_server = subprocess.Popen(OI_CMD, shell=True)
    print("Interpreter server started")
    

    print("Starting livekit server...")
    if debug: 
        LK_CMD = f"livekit-server --dev --bind {lk_host} --port {lk_port}"
    else:
        LK_CMD = f"livekit-server --dev --bind {lk_host} --port {lk_port} > /dev/null 2>&1"
    
    lk_server = subprocess.Popen(LK_CMD, shell=True)
    print("Livekit server started")
    time.sleep(2)

    lk_url = f"http://{lk_host}:{lk_port}"
    participant_token = str(api.AccessToken('devkey', 'secret') \
                .with_identity("Participant") \
                .with_name("You") \
                .with_grants(api.VideoGrants(
                    room_join=True,
                    room=ROOM_NAME,))
                .to_jwt())

    processes = [lk_server, oi_server]

    if client == 'mobile':
        listener =  ngrok.forward(f"{lk_host}:{lk_port}", authtoken_from_env=True, domain=domain)
        lk_url = listener.url()
        print(f"Livekit server forwarded to: {lk_url}")

        print("Scan the QR code below with your mobile app to connect to the livekit server.")
        content = json.dumps({"livekit_server": lk_url, "token": participant_token})
        qr_code = segno.make(content)
        qr_code.terminal(compact=True)
    else: # meet client
        # Get the path to the meet client directory
        meet_client_path = Path(__file__).parent / "source" / "clients" / "meet"

        print("Starting Next.js dev server...")
        next_server = subprocess.Popen(["pnpm", "dev"], cwd=meet_client_path,)
        print("Next.js dev server started")

        time.sleep(2)
        meet_url = f'http://localhost:3000/custom?liveKitUrl={lk_url.replace("http", "ws")}&token={participant_token}'
        print(f"\nOpening meet interface at: {meet_url}")
        webbrowser.open(meet_url)

        processes.append(next_server)
    
    try:
        print("Starting worker...")
        if multimodal:
            multimodal_main(lk_url)
        else:
            worker_main(lk_url)
        print("Worker started")
    except KeyboardInterrupt:
        print("\nReceived interrupt signal, shutting down...")
    finally:
        print("Cleaning up processes...")
        cleanup_processes(processes)