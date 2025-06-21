from src.motor.motorControl import *
from utils.test.database import *
from interface.global_interface import *
from flask import Flask, render_template, jsonify
import pandas as pd
import threading

key = threading.Lock()

class RobotController:
    def __init__(self, lock, host="192.168.1.244", port=5000):
        self.app = Flask(__name__)
        self.host = host
        self.port = port
        self.lock = lock
        self.setup_routes()

    def setup_routes(self):
        @self.app.route("/")
        def index():
            return render_template("index.html")

        @self.app.route("/<cmd>")
        def move(cmd):
            if cmd == "forward":
                forward(40)
            elif cmd == "backward":
                backward(40)
            elif cmd == "left":
                turnLeft(45)
            elif cmd == "right":
                turnRight(45)
            else:
                brake()
            return ("", 204)

        @self.app.route("/shutdown")
        def shutdown():
            brake()
            return "Stopped"

        # @self.app.route("/data")
        # def get_data():
        #     with self.lock:
        #         with open('vo.csv', 'r') as f:
        #             lines = f.readlines()

        #         parsed = []
        #         for line in lines:
        #             line = line.strip().strip('[]')
        #             if line:
        #                 parts = line.split()
        #                 if len(parts) == 3:
        #                     x, y, z = map(float, parts)
        #                     parsed.append({'x': x, 'y': z})  # dùng x, z để vẽ 2D

        #         return jsonify(parsed)

    def run(self):
        self.app.run(host=self.host, port=self.port)

# if __name__ == "__main__":
#     controller = RobotController(key)
#     controller.run()
