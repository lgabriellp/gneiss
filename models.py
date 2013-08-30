import peewee
import datetime
import pystache
import tempfile
import flask
import subprocess


db = peewee.SqliteDatabase("emulation.db")
renderer = pystache.Renderer(search_dirs="templates")


def render(name, path, context):
    rendered = open(path, "w")
    rendered.write(renderer.render_name(name, context))
    rendered.close()


def run(command, *args, **kwargs):
    command = command.format(*args, **kwargs)
    print command
    return subprocess.call(command, shell=True, bufsize=4096)


def start(command, *args, **kwargs):
    command = command.format(*args, **kwargs)
    print command
    return subprocess.Popen(command, shell=True, bufsize=4096,
                            stdout=subprocess.PIPE)


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

    @property
    def name(self):
        return "emulation-{s.number}".format(s=self)

    @property
    def path(self):
        return "/tmp/{s.name}".format(s=self)

    @property
    def emulation_path(self):
        return self.path + "emulation.xml"

    def deploy(self, project):
        run("mkdir {e.path} -p", e=self)
        run("tar -C {e.path} -Pczf {e.path}/repo.tgz --exclude='\.*' --transform='s,{0},repo/,' {0}", project, e=self)
        run("tar -C {e.path} -Pxzf {e.path}/repo.tgz", e=self)
        run("cp {e.path}/repo/build.xml {e.path}", e=self)
        run("cp {e.path}/repo/solarium.sh {e.path}", e=self)
        render("emulation", self.emulation_path, self)
        
        for spot in self.spots:
            run("cp -r {e.path}/repo {e.path}/{s.name}", e=self, s=spot)
            render("manifest", spot.manifest_path, spot)

    
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
    def build_file(self):
        return "{s.name}/build.xml".format(s=self)

    @property
    def manifest_path(self):
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
