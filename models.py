import peewee
import datetime
import pystache
import tempfile
import flask

db = peewee.SqliteDatabase("emulation.db")
renderer = pystache.Renderer(search_dirs="templates")

def render(name, context):
    rendered = tempfile.TemporaryFile("w+")
    rendered.write(renderer.render_name(name, context))
    rendered.seek(0)
    return rendered

class BaseModel(peewee.Model):
    class Meta:
        database = db

class Emulation(BaseModel):
    number = peewee.IntegerField(primary_key=True)
    duration = peewee.IntegerField()
    interval = peewee.IntegerField()
    density = peewee.IntegerField()
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

    def render_xml(self):
        xml = render("emulation", self) 
        print xml.read()
        xml.close()


class Spot(BaseModel):
    emulation = peewee.ForeignKeyField(Emulation, related_name="spots")
    address = peewee.IntegerField()
    position = peewee.IntegerField()
    
    type = peewee.CharField()
    version = peewee.CharField(default="1.0.0")
    vendor = peewee.CharField(default="DCC-UFRJ")
    
    class Meta:
        indexes = ((("emulation", "address", "position"), True),)
        order_by = ("emulation", "-address")

    @property
    def name(self):
        return "{s.type}-{s.address}".format(s=self)

    @property
    def path(self):
        return self.name

    @property
    def build_file(self):
        return "{s.path}/build.xml".format(s=self)

    @property
    def manifest_file(self):
        return "{s.path}/resources/META-INF/manifest.mf".format(s=self)
    
    @property
    def interval(self):
        return self.emulation.interval

    @property
    def range(self):
        return int(100 * self.emulation.density)

    @property
    def behavior(self):
        return self.emulation.behavior
    
    def render_mf(self):
        manifest = render("manifest", self)
        print manifest.read()
        manifest.close()


class MidletClass(BaseModel):
    path = peewee.CharField(unique=True)
    type = peewee.CharField()


class Midlet(MidletClass):
    spot = peewee.ForeignKeyField(Spot, related_name="midlets")
    number = peewee.IntegerField()

    @property
    def name(self):
        return self.path.split(".")[-1]

class Round(BaseModel):
    emulation = peewee.ForeignKeyField(Emulation, related_name="rounds")
    number = peewee.IntegerField()
    seed = peewee.IntegerField()
    date = peewee.DateTimeField(default=datetime.datetime.now)

    class Meta:
        indexes = ((("emulation", "number", "date"), True),)
        order_by = ("emulation", "-number")


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
