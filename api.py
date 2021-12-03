import flask
from flask import Flask
from flask.json import jsonify
import uuid
import os
from ActInt import Amazon
from ActInt import Box
from ActInt import Robot

simulations = {}

app = flask.Flask(__name__)

@app.route("/simulation", methods=["POST"])
def create():
    global simulations
    id = str(uuid.uuid4())
    simulations[id] = Amazon()
    return "ok", 201, {'Location': f"/simulation/{id}", "Items": len(simulations[id].schedule.agents)-5}

@app.route("/simulation/<id>", methods=["GET"])
def queryState(id):
    global model
    model = simulations[id]
    model.step()
    agents = []
    for agent in model.schedule.agents:
        if(agent.pos is not None):
            if isinstance(agent, Robot):
                agents.append({"type": type(agent).__name__, "x": agent.pos[0], "y": agent.pos[1], "z": 1})
            elif isinstance(agent, Box):
                agents.append({"type": type(agent).__name__, "x": agent.pos[0], "y": agent.pos[1], "z": agent.height})
            else:
                agents.append({"type": type(agent).__name__, "x": agent.pos[0], "y": agent.pos[1], "z": 1})
    return jsonify({"Items": agents})

app.run()
