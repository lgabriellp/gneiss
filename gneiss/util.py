import os
import pystache
import subprocess
import threading
from contextlib import contextmanager

TEMPLATES_PATH = "/".join(__file__.split("/")[:-1] + ["templates"])

renderer = pystache.Renderer(search_dirs=TEMPLATES_PATH)


def render_text(name, context):
    return renderer.render_name(name, context)


def render(name, path, context):
    rendered = open(path, "w")
    rendered.write(render_text(name, context))
    rendered.close()


def format(sep, command, *args, **kwargs):
    command = sep.join(command.split())
    if len(args) or len(kwargs.keys()):
        command = command.format(*args, **kwargs)
    return command


def run(command, *args, **kwargs):
    command = format(" ", command, *args, **kwargs)
    print command
    return subprocess.call(command, shell=True)


@contextmanager
def solarium(context):
    env = os.environ.copy()
    env["LD_LIBRARY_PATH"] = "/usr/lib/jvm/default-java/jre/lib/i386/client"
    env["DISPLAY"] = ":1"

    subprocess.Popen("Xvfb :1",
                     env=env,
                     shell=True,
                     stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE)
    command = format(" ", """ant solarium
                             -f {c.build_file}
                             -Dconfig.file={c.emulation_file}
                          """, c=context)

    ant = subprocess.Popen(command,
                           shell=True,
                           env=env,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)

    def kill():
        run("killall squawk")
        run("killall java")
        run("killall Xvfb")
        ant.kill()

    timer = threading.Timer(context.duration, kill)
    timer.start()

    try:
        yield ant
    except:
        timer.cancel()
        kill()
        raise
