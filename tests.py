import unittest

from peewee import fn

import models
from models import Cycle, MidletClass, Emulation, Round, SampledSpotCycle, Spot


class EmulationTest(unittest.TestCase):
    def setUp(self):
        models.create()
        MidletClass.create(path="br.ufrj.dcc.wsn.main.HeatSensorNode",
                           type="sensor")
        MidletClass.create(path="br.ufrj.dcc.wsn.main.BaseStation",
                           type="basestation")
        self.emulation = Emulation.create(number=1,
                                          duration=90,
                                          interval=250,
                                          density=.3,
                                          basestation_spot_number=1,
                                          sensor_spot_number=10,
                                          max_sensors_in_spot=1,
                                          behavior=0)
        self.emulation.add_spots()
        self.emulation.deploy("/home/lgabriel/Workspace/Rossan/")

    def test_run(self):
        self.emulation.run()

        assert Round.select().count() == 1
        assert Cycle.select().count() > 0

        samples = (SampledSpotCycle
                   .select(SampledSpotCycle.cycle,
                           fn.Count(fn.Distinct(SampledSpotCycle.spot)))
                   .group_by(SampledSpotCycle.cycle)
                   .tuples())
        for cycle, spots in samples:
            assert spots > 0

    def tearDown(self):
        models.drop()
