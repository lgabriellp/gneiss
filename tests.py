import nose
from models import *

@nose.with_setup(create, drop)
def test_render():
    e = Emulation.create(
            number=2,
            duration=60,
            interval=50,
            density=.3,
            basestation_spot_number=1,
            sensor_spot_number=10,
            max_sensors_in_spot=1,
            behavior=0)

    s = Spot.create(
            emulation=e,
            address=1,
            position=0,
            type="sensor")

    Midlet.create(spot=s,
            number=1,
            path="asd.Asd",
            type="sensor")
    m = Midlet.create(spot=s,
            number=2,
            path="qwe.Qwe",
            type="sensor")

    e.deploy("/home/lgabriel/Workspace/Rossan/")


