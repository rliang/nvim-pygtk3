from gi.repository import GObject, GLib, Gio, Gdk, Gtk, Vte, Pango
import neovim
from threading import Thread
from functools import partial


class NeovimBufferBar(Gtk.StackSwitcher):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lock = False
        self.btns = []
        self.bids = []

    @GObject.Signal()
    def nvim_switch_buffer(self, id: int):
        pass

    def _do_button_toggled(self, btn):
        if not self.lock:
            if btn.get_active():
                id = self.bids[self.btns.index(btn)]
                self.emit('nvim-switch-buffer', id)
            else:
                btn.set_active(True)

    def update(self, buflist, bufcurr):
        self.lock = True
        self.bids = [id for id, *_ in buflist]
        for _ in range(len(buflist) - len(self.btns)):
            ico = Gtk.Image(icon_name='document-edit-symbolic')
            btn = Gtk.ToggleButton(None, can_focus=False, image=ico)
            btn.connect('toggled', self._do_button_toggled)
            self.btns.append(btn)
        for btn in self.get_children():
            self.remove(btn)
        for btn, (id, name, modified) in zip(self.btns, buflist):
            btn.set_label(name)
            btn.set_active(id == bufcurr)
            btn.set_always_show_image(modified)
            self.add(btn)
        self.show_all()
        self.lock = False


class NeovimTabBar(Gtk.Notebook):

    def __init__(self, *args, **kwargs):
        super().__init__(*args,
                         can_focus=False,
                         show_tabs=False,
                         show_border=False,
                         **kwargs)
        self.lock = False

    @GObject.Signal()
    def nvim_switch_tab(self, id: int):
        pass

    def do_switch_page(self, page, num):
        if not self.lock:
            self.emit('nvim-switch-tab', num + 1)

    def update(self, tablist, tabcurr):
        self.lock = True
        for _ in range(self.get_n_pages()):
            self.remove_page(-1)
        for name in tablist:
            page = Gtk.Box()
            self.append_page(page, Gtk.Label(name))
            self.child_set_property(page, 'tab-expand', True)
        self.show_all()
        self.props.show_tabs = len(tablist) > 1
        self.props.page = tabcurr - 1
        self.lock = False


class NeovimViewport(Gtk.Viewport):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lock = False
        self.size = 1
        vadj = self.get_vadjustment()
        vadj.connect('value-changed', self._do_vadjustment_value_changed)

    @GObject.Signal()
    def nvim_vscrolled(self, val: int):
        pass

    def _do_vadjustment_value_changed(self, vadjustment):
        if not self.lock:
            val = vadjustment.get_value()
            val = val if val == 0 else val + vadjustment.get_page_size()
            self.emit('nvim-vscrolled', int(val * self.size))

    def update(self, a, b, size):
        self.lock = True
        a, b, self.size = map(float, (a, b, size))
        page = (b - a) / self.size
        val = (a if a == 0 else a + 1) / self.size
        vadj = self.get_vadjustment()
        vadj.configure(val, 0.0, 1.0, 1.0 / self.size, page, page)
        self.lock = False


class NeovimTerminal(Vte.Terminal):

    def __init__(self, *args, **kwargs):
        super().__init__(*args,
                         is_focus=True,
                         has_focus=True,
                         pointer_autohide=True,
                         scrollback_lines=0,
                         **kwargs)
        self.reset_font()
        self.reset_color()

    @GObject.Signal()
    def nvim_attached(self, nvim: object):
        pass

    def spawn(self, addr, argv, rtp):
        def callback(self):
            self.disconnect(once)
            self.emit('nvim-attached', neovim.attach('socket', path=addr))
        once = self.connect('cursor-moved', callback)
        self.spawn_sync(Vte.PtyFlags.DEFAULT,
                        None,
                        ['nvim', f'+set rtp^={rtp}', *argv],
                        [f'NVIM_LISTEN_ADDRESS={addr}'],
                        GLib.SpawnFlags.SEARCH_PATH,
                        None,
                        None,
                        None)

    def update_font(self, value):
        family, *attrs = value.split(':')
        font = Pango.FontDescription(string=family.replace('_', ' '))
        for a in attrs:
            if a[0] == 'h':
                font.set_size(float(a[1:]) * Pango.SCALE)
            if a[0] == 'b':
                font.set_weight(Pango.Weight.BOLD)
            if a[0] == 'i':
                font.set_style(Pango.Style.ITALIC)
        self.set_font(font)

    def update_color(self, bg_color, is_dark):
        self.get_settings().props.gtk_application_prefer_dark_theme = is_dark
        if bg_color != 'None':
            rgba = Gdk.RGBA()
            rgba.parse(bg_color)
            self.set_color_background(rgba)
        else:
            GLib.idle_add(self.reset_color)

    def reset_font(self):
        giosss = Gio.SettingsSchemaSource.get_default()
        schema = giosss.lookup('org.gnome.desktop.interface', True)
        if not schema:
            self.set_font(Pango.FontDescription(string='Monospace'))
            return
        settings = Gio.Settings(settings_schema=schema)
        value = settings.get_string('monospace-font-name')
        self.set_font(Pango.FontDescription(string=value))

    def reset_color(self):
        sctx = self.get_style_context()
        rgba = sctx.get_background_color(sctx.get_state())
        self.set_color_background(rgba)


class NeovimWindow(Gtk.ApplicationWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.switcher = NeovimBufferBar()
        self.set_titlebar(Gtk.HeaderBar(show_close_button=True,
                                        custom_title=self.switcher))
        vbox = Gtk.Box(parent=self, orientation=Gtk.Orientation.VERTICAL)
        self.notebook = NeovimTabBar(parent=vbox)
        swin = Gtk.ScrolledWindow(parent=vbox)
        vbox.child_set_property(swin, 'expand', True)
        self.viewport = NeovimViewport(parent=swin)
        self.terminal = NeovimTerminal(parent=self.viewport)
        self.terminal.connect('child-exited', lambda *_:
                              self.close())
        self.terminal.connect('nvim-attached', lambda _, nvim:
                              self.emit('nvim-setup', nvim))

    @GObject.Signal(flags=GObject.SignalFlags.RUN_LAST)
    def nvim_setup(self, nvim: object):
        nvim.vars['gui_channel'] = nvim.channel_id
        nvim.subscribe('Gui')
        nvim.options['showtabline'] = 0
        nvim.options['ruler'] = False
        nvim.command('ru! ginit.vim', async=True)
        self.switcher.connect('nvim-switch-buffer', lambda _, num:
                              nvim.command(f'b {num}', async=True))
        self.notebook.connect('nvim-switch-tab', lambda _, num:
                              nvim.command(f'{num}tabn', async=True))
        self.viewport.connect('nvim-vscrolled', lambda _, val:
                              nvim.command(f'norm! {val}gg', async=True))
        Thread(daemon=True, target=nvim.run_loop,
               args=(partial(self.emit, 'nvim-request', nvim),
                     partial(self.emit, 'nvim-notify', nvim))).start()

    @GObject.Signal(flags=GObject.SignalFlags.RUN_LAST)
    def nvim_notify(self, nvim: object, sub: str, args: object):
        if sub == 'Gui' and args[0] == 'Bufs':
            return GLib.idle_add(self.switcher.update, *args[1:])
        if sub == 'Gui' and args[0] == 'Tabs':
            return GLib.idle_add(self.notebook.update, *args[1:])
        if sub == 'Gui' and args[0] == 'Font':
            return GLib.idle_add(self.terminal.update_font, *args[1:])
        if sub == 'Gui' and args[0] == 'Color':
            return GLib.idle_add(self.terminal.update_color, *args[1:])
        if sub == 'Gui' and args[0] == 'Scroll':
            return GLib.idle_add(self.viewport.update, *args[1:])

    @GObject.Signal(flags=GObject.SignalFlags.RUN_LAST)
    def nvim_request(self, nvim: object, sub: str, args: object) -> object:
        if sub == 'Gui' and args[0] == 'Clipboard':
            return self.update_clipboard(*args[1:])

    def update_clipboard(self, method, data):
        cb = Gtk.Clipboard.get_default(Gdk.Display.get_default())
        if method == 'set':
            text = '\n'.join(data[0])
            return cb.set_text(text, len(text))
        if method == 'get':
            text = cb.wait_for_text()
            return text.split('\n') if text else []
