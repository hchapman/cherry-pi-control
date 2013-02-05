#!python
import os.path
current_dir = os.path.dirname(os.path.abspath(__file__))

import cherrypy
import subprocess
import json

userpassdict = {'admin' : 'secretpassword'}
checkpassword = cherrypy.lib.auth_basic.checkpassword_dict(userpassdict)

class WebControl(object):
    @cherrypy.expose
    def index(self):
        index_file = open(os.path.join(
            os.path.dirname(__file__),
            "index.html"))
        out = subprocess.check_output(["ls", "-l"])
        return index_file.read()

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def stopMPD(self):
        out = subprocess.check_output(["mpc", "stop"],
                                      stderr=subprocess.STDOUT)
        return {"error": False, "output": out}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def ejectHDD(self):
        try:
            out = subprocess.check_output(["eject", "/mnt/hd1"],
                                          stderr=subprocess.STDOUT)
            return {"error": False, "output": out}
        except subprocess.CalledProcessError as e:
            out = e.output
            if "unable to find" in out:
                err_type = "The hard drive has already been ejected."
            elif "device is busy" in out:
                err_type = "The device is busy. Are you sure you stopped MPD?"
            else:
                err_type = "Something happened, but we're not sure what'"
            return {"error": True, "output": out, "err_type": err_type}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def checkMPD(self):
        out = subprocess.check_output(["mpc", "status"],
                                      stderr=subprocess.STDOUT)
        return {"error": False, "output": out}

if __name__ == "__main__":
    config = os.path.join(current_dir, "prod.conf")
    cherrypy.tree.mount(WebControl(), "/", config=config)
    cherrypy.server.socket_host = "0.0.0.0"
    cherrypy.engine.start()
    cherrypy.engine.block()