import sys
import time
import flask
import peewee
import random
import datetime
import threading

import util

db = peewee.SqliteDatabase("emulation.db")

class BaseModel(peewee.Model):
    class Meta:
        database = db


class Emulation(BaseModel):
    number = peewee.IntegerField(primary_key=True)
    duration = peewee.IntegerField()
    interval = peewee.IntegerField()
    density = peewee.FloatField()
    basestation_spot_number = peewee.IntegerField()
    sensor_spot_number = peewee.IntegerField()
    max_sensors_in_spot = peewee.IntegerField()
    behavior = peewee.IntegerField(choices=(
       (0, "Exponential"),
       (1, "NodeDensity"),
       (2, "Dummy"      )
    ))
    
    class Meta:
        indexes = ((("number", 
                     "density",
                     "basestation_spot_number",
                     "sensor_spot_number",
                     "max_sensors_in_spot",
                     "behavior"), True),)

    @property
    def name(self):
        return "emulation-{s.number}".format(s=self)

    @property
    def path(self):
        return "/tmp/{s.name}".format(s=self)
    
    @property
    def build_file(self):
        return "{e.path}/build.xml".format(e=self)

    @property
    def emulation_file(self):
        return "{e.path}/emulation.xml".format(e=self)
    
    def add_spots(self):
        base_address = 1
        for i in xrange(self.sensor_spot_number):
            spot = Spot.create(emulation=self,
                               address=base_address+i,
                               position=random.randint(0, 100))
            spot.add_midlets(MidletClass.type=="sensor")

        base_address += self.sensor_spot_number
        for i in xrange(self.basestation_spot_number):
            spot = Spot.create(emulation=self,
                               address=base_address+i,
                               position=0)
            spot.add_midlets(MidletClass.type=="basestation")

    def cleanup(self):
        util.run("rm -rf {e.path}", e=self)

    def deploy(self, project):
        self.cleanup()

        util.run("mkdir {e.path} -p", e=self)
        util.run("tar -C {e.path} -Pczf {e.path}/repo.tgz --exclude='\.*' --transform='s,{0},repo/,' {0}", project, e=self)
        util.run("tar -C {e.path} -Pxzf {e.path}/repo.tgz", e=self)
        util.run("cp {e.path}/repo/build.xml {e.path}", e=self)
        util.render("emulation", self.emulation_file, self)
        
        for spot in self.spots:
            util.run("cp -r {e.path}/repo {e.path}/{s.name}", e=self, s=spot)
            util.render("manifest", spot.manifest_file, spot)

    def run(self):
        round = Round.create(emulation=self, number=1)
        round.run()
    
class Spot(BaseModel):
    emulation = peewee.ForeignKeyField(Emulation, related_name="spots")
    address = peewee.IntegerField()
    position = peewee.IntegerField()
    
    version = peewee.CharField(default="1.0.0")
    vendor = peewee.CharField(default="DCC-UFRJ")
    
    class Meta:
        indexes = ((("emulation", "address", "position"), True),)
        order_by = ("emulation", "address")

    @property
    def name(self):
        return "spot-{s.address}".format(s=self)

    @property
    def build_file(self):
        return "{s.name}/build.xml".format(s=self)

    @property
    def manifest_file(self):
        return "{s.emulation.path}/{s.name}/resources/META-INF/manifest.mf".format(s=self)
    
    @property
    def interval(self):
        return self.emulation.interval

    @property
    def range(self):
        return int(100 * self.emulation.density)

    @property
    def behavior(self):
        return self.emulation.behavior

    def add_midlets(self, *filters):
        number = random.randint(1, self.emulation.max_sensors_in_spot)
        classes = random.sample(list(MidletClass.select().where(*filters)), number)

        for i in xrange(number):
            Midlet.create(clas=classes[i], spot=self, number=i+1)

class MidletClass(BaseModel):
    id = peewee.PrimaryKeyField()
    path = peewee.CharField(unique=True)
    type = peewee.CharField()


class Midlet(BaseModel):
    clas = peewee.ForeignKeyField(MidletClass)
    spot = peewee.ForeignKeyField(Spot, related_name="midlets")
    number = peewee.IntegerField()
    
    class Meta:
        indexes = ((("spot", "number"), True),)
        order_by = ("spot", "number")
    
    @property
    def path(self):
        return self.clas.path

    @property
    def name(self):
        return self.clas.path.split(".")[-1]


class Round(BaseModel):
    emulation = peewee.ForeignKeyField(Emulation, related_name="rounds")
    seed = peewee.IntegerField(default=lambda:random.randint(0, sys.maxint))
    date = peewee.DateTimeField(default=datetime.datetime.now)
    number = peewee.IntegerField()

    class Meta:
        indexes = ((("emulation", "number", "date"), True),)
        order_by = ("emulation", "-number")

    def parse(self, output):
        while True:
            line = output.readline()
            if line: print line,
            else: break
            
            if "Failed" in line:
                print output.read()
                break

    def run(self):
        random.seed(self.seed)

        with util.solarium(self.emulation) as solarium:
            self.parse(solarium.stdout)


class Cycle(BaseModel):
    round = peewee.ForeignKeyField(Round, related_name="cycles")
    number = peewee.IntegerField()
    energy = peewee.IntegerField()
    time = peewee.IntegerField()
    hops = peewee.IntegerField()

    class Meta:
        indexes = ((("round", "number"), True),)
        order_by = ("round", "-number")


db.connect()


def create():
    with db.transaction():
        Emulation.create_table()
        MidletClass.create_table()
        Midlet.create_table()
        Spot.create_table()
        Round.create_table()
        Cycle.create_table()


def drop():
    with db.transaction():
        Cycle.drop_table()
        Round.drop_table()
        Spot.drop_table()
        Midlet.drop_table()
        MidletClass.drop_table()
        Emulation.drop_table()


if __name__ == "__main__":
    create()
