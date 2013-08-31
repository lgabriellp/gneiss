import nose
from models import *

@nose.with_setup(create, drop)
def test_render():
    MidletClass.create(path="br.ufrj.dcc.wsn.main.HeatSensorNode", type="sensor")
    MidletClass.create(path="br.ufrj.dcc.wsn.main.BaseStation", type="basestation")

    e = Emulation.create(
            number=2,
            duration=5,
            interval=250,
            density=.3,
            basestation_spot_number=1,
            sensor_spot_number=10,
            max_sensors_in_spot=1,
            behavior=0)
    e.add_spots()
    e.deploy("/home/lgabriel/Workspace/Rossan/")
    e.run()


