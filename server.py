import argparse
import logging
from flask import Flask, request, jsonify, render_template # type: ignore
from os import sep, path
from prometheus_client import Gauge, generate_latest # type: ignore
import random
import subprocess
import threading
import time
from datetime import datetime
from zoneinfo import ZoneInfo

from threading import Timer

from subprocess import Popen, PIPE, STDOUT

tied = False
threadExists = False
cancel_event = threading.Event()


app = Flask(__name__)




# def maybe_reopen_ssh_tunnel():
    # """
    # if we havent recieved a health check ping in over 1 min then
    # we rerun the script to open the ssh tunnel.
    # """
    # while 1:
    #     time.sleep(60)
    #     now_epoch_seconds = int(time.time())
    #     # skip reopening the tunnel if the value is 0 or falsy
    #     if not last_health_check_request._value.get():
    #         continue
    #     if now_epoch_seconds - last_health_check_request._value.get() > 120:
    #         ssh_tunnel_last_opened.set(now_epoch_seconds)
    #         subprocess.Popen(
    #             './tun.sh tunnel-only',
    #             shell=True,
    #             stderr=subprocess.DEVNULL,
    #             stdout=subprocess.DEVNULL,
    #         )



@app.route("/tie", methods=["GET"])
def tieShoes():
    print("TIE CALLED AND ORIENTATION IS TOMORROW!!!!!", flush=True)
    global tied
    global threadExists
    global cancel_event

    format_code = "%Y-%m-%dT%H:%M"
    endTime = datetime.strptime(request.args.get("endTime"), format_code)
    endTime = endTime.replace(tzinfo=ZoneInfo("America/Los_Angeles"))
    tied = True
    currDate = datetime.now(ZoneInfo("America/Los_Angeles"))
    print(currDate)
    print(endTime)

    ts = abs((endTime - currDate).total_seconds())

    if threadExists:
         print("canceleddd", flush=True)
         cancel_event.set()
         cancel_event = threading.Event()

    currThread = threading.Thread(target=expire, args=(ts,))
    
    currThread.start()
    threadExists = True

    return jsonify({
        "endTime": endTime,
        "today": currDate,
        "time": ts
    })
def expire(exp):
    print("expire called with a timeout of", exp, flush=True)
    global tied
    # if the time is being changed, it means this current expire is no longer valid -> just exit function
    if cancel_event.wait(timeout=exp):
        print("forget it lol", flush=True)
        return
    print("untied lmao", flush=True)
    tied = False


@app.route("/status", methods=["GET"])
def status_check():
    global tied
    if tied:
        tied = 'tied'
        return jsonify({
        "isTied": "Shoes Tied!"
        })
    else:
        return jsonify({
        "isTied": "No!"
        })



@app.route('/', methods=["GET", "POST"])
def home():     
    return render_template('index.html', tied = tied)


if __name__ == "__main__":
    # give the last opened an initial value of now,
    # since upon starting the led sign the tunnel should
    # be open
    # ssh_tunnel_last_opened.set(int(time.time()))
    # if not args.development:
    #     t = threading.Thread(
    #         target=maybe_reopen_ssh_tunnel,
    #         daemon=True,
    #     )
    #     t.start()
    app.run(host="0.0.0.0", port=7000, debug=True, threaded=True)