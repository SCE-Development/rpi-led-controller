from fastapi import FastAPI, Request, HTTPException
import uvicorn
import threading
import logging
import subprocess
from fastapi.staticfiles import StaticFiles
from datetime import datetime, timezone
from dataclasses import dataclass
import argparse

logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
logging.getLogger("uvicorn.error").setLevel(logging.WARNING)

@dataclass
class SignData:
    background_color: str
    text_color: str
    border_color: str
    scroll_speed: int
    text: str
    expiration: datetime

    def to_subprocess_command(self) -> str:
        return ("--set-background-color " + self.background_color +
                " --set-font-color " + self.text_color +
                " --set-border-color " + self.border_color +
                " --set-speed " + str(self.scroll_speed) +
                " --set-text " + self.text +
                " --set-expiration " + self.expiration.isoformat()
                )

app = FastAPI()
cancel_event = threading.Event()

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--port",
        type=int,
        default=10000,
        help="port for server to be hosted on, defaults to 10000"
    )
    parser.add_argument(
        "--development",
        action="store_true",
        help="stores true if passed in"
    )
    return parser.parse_args()

args = get_args()
    
logging.basicConfig( #logging is another way u can logging.info text in the terminal when running python
    level=logging.INFO,
    format='%(asctime)s [%(threadName)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S' #date format
)

sign_data = None
process = None

# when u call replace on a datetime object, the time technically stays the same
# u are just updating the timezone
# when u call astimezone u are updating the timezone and converting the time to be in that timezone

def set_and_reset_event():
    global cancel_event
    cancel_event.set()
    cancel_event = threading.Event()

def reset_sign(seconds):
    if cancel_event.wait(timeout=seconds):
        logging.info("cancelling old sign thread")
        return
    global process
    global sign_data
    sign_data = None
    process.kill()
    ID = process.pid
    process = None
    print("!!!killing process of ", ID, "& expiring")

@app.get("/turn-off") #
def turn_off_process():
    global process
    global sign_data
    set_and_reset_event()
    if process != None:
        sign_data = None
        ID = process.pid
        print("killing process of", str(ID))
        process.kill()
        process = None
        return({"message": "killing old process of " + str(ID) })
    else:
        print("no process to kill")
        return({"message": "no process to kill"})

@app.post("/update-sign")
async def update(request: Request):
    global process
    response = await request.json()
    expiration = None
    global sign_data
    global process
    if(process != None): #if there's older processes
        process.kill()
        ID = process.pid
        process = None
        print("KILLING OLD process", ID)

    if "expiration" in response:
        if not response["expiration"]: # catches the empty values
            print("continuing with no expiration")
        else:
            expiration_string = response["expiration"]
            print("MADE IT ", expiration_string)
            expiration = datetime.fromisoformat(expiration_string.replace("Z", "+00:00"))
            expiration = expiration.astimezone(tz=timezone.utc)
            print(type(expiration))
            now = datetime.now(tz=timezone.utc)
            if expiration != None:
                if expiration <= now:
                    raise HTTPException(status_code=400, detail="Expiration is in the past")
                else:
                    #  create sign_data object if expiration is valid
                    seconds = (expiration - datetime.now(timezone.utc)).total_seconds()
                    print("date expiring ", expiration , " now ", now," seconds to expire ", seconds)
                    signThread = threading.Thread(target=reset_sign, args=(seconds,))
                    logging.info("starting thread, updating sign")
                    set_and_reset_event()
                    signThread.start()
    sign_data = SignData(response["background_color"], response["text_color"], response["border_color"], response["scroll_speed"], response["text"], expiration)
    command = sign_data.to_subprocess_command().split()
    if not args.development:
        process = subprocess.Popen(command)
        print("process id of new ", process.pid)


@app.get("/health-check") # my health check
def status():
    global sign_data
    return({ "sign data": sign_data})
    

app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run("server:app", port=args.port, reload=True)
