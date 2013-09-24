from unittest import TestCase

from peewee import fn

from gneiss import App
from gneiss import models
from gneiss.models import Cycle, MidletClass, Emulation, Round
from gneiss.models import SampledSpotCycle, Spot


class EmulationTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = App("gneiss.config.PersistentTesting")
        if cls.app.config["CREATE_SCHEMA"]:
            models.create()

    def setUp(self):
        self.emulation = Emulation.create(
            duration=60,
            interval=500,
            density=.5,
            basestation_spot_number=1,
            sensor_spot_number=10,
            max_sensors_in_spot=1,
            behavior=0)
        self.emulation.add_spots()
        self.emulation.deploy("/home/lgabriel/Workspace/Rossan/")

    def test_run(self):
        self.emulation.run()

#    def tearDown(self):
#        models.drop()
