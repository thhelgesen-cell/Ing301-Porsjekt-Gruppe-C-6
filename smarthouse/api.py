import uvicorn

from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.encoders import jsonable_encoder

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from tests.demo_house import DEMO_HOUSE

from smarthouse.domain import Actuator, Sensor, Measurement
from smarthouse.dto import SmartHouseInfo, FloorInfo, RoomInfo, DeviceInfo, ActuatorStateInfo

from pathlib import Path
import os

app = FastAPI()
smarthouse = DEMO_HOUSE


# Static setup
if not (Path.cwd() / "www").exists():
    os.chdir(Path.cwd().parent)

if (Path.cwd() / "www").exists():
    app.mount("/static", StaticFiles(directory="www"), name="static")


@app.get("/")
def root():
    return RedirectResponse("/static/index.html")


@app.get("/hello")
def hello(name: str = "world"):
    return {"hello": name}


# -------------------------
# STRUCTURE ENDPOINTS
# -------------------------

@app.get("/smarthouse")
def get_smarthouse_info() -> SmartHouseInfo:
    return SmartHouseInfo.from_obj(smarthouse)


@app.get("/smarthouse/floor")
def get_floors() -> list[FloorInfo]:
    return [FloorInfo.from_obj(f) for f in smarthouse.get_floors()]


@app.get("/smarthouse/floor/{fid}")
def get_floor(fid: int) -> Response:
    for f in smarthouse.get_floors():
        if f.level == fid:
            return JSONResponse(content=jsonable_encoder(FloorInfo.from_obj(f)))
    return Response(status_code=404)


@app.get("/smarthouse/floor/{fid}/room")
def get_rooms(fid: int) -> list[RoomInfo]:
    for f in smarthouse.get_floors():
        if f.level == fid:
            return [RoomInfo.from_obj(r) for r in f.rooms]
    return []


@app.get("/smarthouse/floor/{fid}/room/{rid}")
def get_room(fid: int, rid: int) -> Response:
    for f in smarthouse.get_floors():
        if f.level == fid:
            for r in f.rooms:
                if r.rid == rid:
                    return JSONResponse(content=jsonable_encoder(RoomInfo.from_obj(r)))
    return Response(status_code=404)


@app.get("/smarthouse/device")
def get_devices() -> list[DeviceInfo]:
    return [DeviceInfo.from_obj(d) for d in smarthouse.get_devices()]


@app.get("/smarthouse/device/{uuid}")
def get_device(uuid: str) -> Response:
    d = smarthouse.get_device_by_id(uuid)
    if d:
        return JSONResponse(content=jsonable_encoder(DeviceInfo.from_obj(d)))
    return Response(status_code=404)


# -------------------------
# SENSOR ENDPOINTS
# -------------------------

@app.get("/smarthouse/sensor/{uuid}/current")
def read_measurement(uuid: str) -> Response:
    d = smarthouse.get_device_by_id(uuid)
    if isinstance(d, Sensor):
        m = d.get_current()
        return JSONResponse(content=jsonable_encoder(m))
    return Response(status_code=404)


@app.put("/smarthouse/sensor/{uuid}/current")
def update_sensor_measurement(uuid: str, measurement: Measurement) -> Response:
    d = smarthouse.get_device_by_id(uuid)
    if d and d.is_sensor():
        d.set_current(measurement)
        return JSONResponse(content=jsonable_encoder(measurement))
    return Response(status_code=404)


@app.delete("/smarthouse/sensor/{uuid}/current")
def delete_measurement(uuid: str) -> Response:
    d = smarthouse.get_device_by_id(uuid)
    if d and d.is_sensor():
        d.set_current(None)
        return JSONResponse(content={})
    return Response(status_code=404)


# -------------------------
# ACTUATOR ENDPOINTS
# -------------------------

@app.get("/smarthouse/actuator/{uuid}/state")
def read_actuator_state(uuid: str) -> Response:
    d = smarthouse.get_device_by_id(uuid)
    if isinstance(d, Actuator):
        return JSONResponse(content=jsonable_encoder(
            ActuatorStateInfo(state=d.state)
        ))
    return Response(status_code=404)


@app.put("/smarthouse/actuator/{uuid}/state")
def update_sensor_state(uuid: str, target_state: ActuatorStateInfo) -> Response:
    d = smarthouse.get_device_by_id(uuid)
    if isinstance(d, Actuator):
        if isinstance(target_state.state, bool):
            if target_state.state:
                d.turn_on()
            else:
                d.turn_off()
        else:
            d.turn_on(target_state.state)
        return Response(status_code=204)
    return Response(status_code=404)


# -------------------------

if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)