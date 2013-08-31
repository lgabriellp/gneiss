import os
import pystache
import subprocess
import threading
from contextlib import nested, contextmanager

renderer = pystache.Renderer(search_dirs="templates")

def render(name, path, context):
    rendered = open(path, "w")
    rendered.write(renderer.render_name(name, context))
    rendered.close()


def run(command, *args, **kwargs):
    command = command.format(*args, **kwargs)
    print command
    return subprocess.call(command, shell=True)

@contextmanager
def solarium(context):
    env = os.environ.copy()
    env["LD_LIBRARY_PATH"] = "/usr/lib/jvm/default-java/jre/lib/i386/client"
    env["DISPLAY"] = ":1"

    vfb = subprocess.Popen("Xvfb :1",
                               env=env,
                               shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    ant = subprocess.Popen("ant solarium -f {c.build_file} -Dconfig.file={c.emulation_file}".format(c=context),
                               shell=True,    
                               env=env,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)

    def kill():
        run("killall squawk")
        run("killall java")
        run("killall Xvfb")

    threading.Timer(context.duration, kill).start()

    try:
        yield ant
    except KeyboardInterrupt:
        kill()
    
   
