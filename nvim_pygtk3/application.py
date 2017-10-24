from gi.repository import GLib, Gio, Gtk
import os
from glob import glob
from uuid import uuid4
from .window import NeovimWindow


class NeovimApplication(Gtk.Application):

    def __init__(self, name, runtime, *args, **kwargs):
        super().__init__(*args,
                         application_id=f'org.{name}',
                         flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
                         **kwargs)
        self.runtime = os.path.join(os.path.dirname(runtime), 'runtime')
        self.scripts = os.path.join(GLib.get_user_config_dir(), name, '*.py')
        self.scripts = [compile(open(script).read(), script, 'exec')
                        for script in glob(self.scripts)]

    def do_command_line(self, command_line):
        window = NeovimWindow(application=self)
        self._configure(window)
        window.show_all()
        window.present()
        window.spawn(os.path.join(GLib.get_tmp_dir(), f'nvim-{uuid4()}'),
                     command_line.get_arguments(),
                     self.runtime)

    def _configure(self, window):
        def connect(obj, sig):
            return lambda fun: obj.connect(sig, lambda obj, *args: fun(*args))
        for script in self.scripts:
            exec(script, {'window': window, 'connect': connect})
