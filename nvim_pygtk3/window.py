from gi.repository import GObject, GLib, Gio, Gdk, Gtk, Vte, Pango
import neovim
from threading import Thread
from functools import partial


class NeovimWindow(Gtk.ApplicationWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.updating = False
        self.switcher = Gtk.StackSwitcher()
        self.set_titlebar(Gtk.HeaderBar(show_close_button=True,
                                        custom_title=self.switcher))
        vbox = Gtk.Box(parent=self, orientation=Gtk.Orientation.VERTICAL)
        self.notebook = Gtk.Notebook(parent=vbox,
                                     show_tabs=False,
                                     show_border=False)
        swin = Gtk.ScrolledWindow(parent=vbox)
        vbox.child_set_property(swin, 'expand', True)
        self.terminal = Vte.Terminal(parent=Gtk.Viewport(parent=swin),
                                     is_focus=True,
                                     has_focus=True,
                                     pointer_autohide=True,
                                     scrollback_lines=0)
        self.terminal.connect('child-exited', lambda *_: self.close())
        self._reset_font()
        self._reset_color()

    def spawn(self, addr, argv, rtp):
        def callback(*_):
            self.terminal.disconnect(once)
            self.emit('nvim-setup', neovim.attach('socket', path=addr))
        once = self.terminal.connect('cursor-moved', callback)
        self.terminal.spawn_sync(Vte.PtyFlags.DEFAULT,
                                 None,
                                 ['nvim', f'+set rtp^={rtp}', *argv],
                                 [f'NVIM_LISTEN_ADDRESS={addr}'],
                                 GLib.SpawnFlags.SEARCH_PATH,
                                 None,
                                 None,
                                 None)

    @GObject.Signal(flags=GObject.SignalFlags.RUN_LAST)
    def nvim_setup(self, nvim: object):
        nvim.subscribe('Gui')
        nvim.options['showtabline'] = 0
        nvim.options['ruler'] = False
        nvim.vars['gui_channel'] = nvim.channel_id
        nvim.command('ru! ginit.vim', async=True)
        self.notebook.connect('switch-page', lambda _, page, num:
                              nvim.command(f'{num + 1}tabn', async=True)
                              if not self.updating else None)
        Thread(daemon=True, target=nvim.run_loop,
               args=(partial(self.emit, 'nvim-request', nvim),
                     partial(self.emit, 'nvim-notify', nvim))).start()

    @GObject.Signal(flags=GObject.SignalFlags.RUN_LAST)
    def nvim_notify(self, nvim: object, sub: str, args: object):
        if sub == 'Gui' and args[0] == 'Bufs':
            return GLib.idle_add(self._update_bufs, nvim, args[1:])
        if sub == 'Gui' and args[0] == 'Tabs':
            return GLib.idle_add(self._update_tabs, nvim, args[1:])
        if sub == 'Gui' and args[0] == 'Font':
            return GLib.idle_add(self._update_font, nvim, args[1:])
        if sub == 'Gui' and args[0] == 'Color':
            return GLib.idle_add(self._update_color, nvim, args[1:])
        if sub == 'Gui' and args[0] == 'Scroll':
            return GLib.idle_add(self._update_scroll, nvim, args[1:])

    @GObject.Signal(flags=GObject.SignalFlags.RUN_LAST)
    def nvim_request(self, nvim: object, sub: str, args: object) -> object:
        if sub == 'Gui' and args[0] == 'Clipboard':
            return self._update_clipboard(nvim, args[1:])

    def _update_bufs(self, nvim, args):
        buflist, bufcurr = args
        for child in self.switcher.get_children():
            self.switcher.remove(child)
        for id, name, modified in buflist:
            ico = (Gtk.Image(icon_name='document-edit-symbolic')
                   if modified else None)
            btn = Gtk.ToggleButton(name,
                                   parent=self.switcher,
                                   active=id == bufcurr,
                                   image=ico,
                                   always_show_image=True)
            btn.connect('clicked',
                        lambda _, id: nvim.command(f'b {id}', async=True),
                        id)
        self.switcher.show_all()
        self.terminal.grab_focus()

    def _update_tabs(self, nvim, args):
        tablist, tabcurr = args
        self.updating = True
        for _ in range(self.notebook.get_n_pages()):
            self.notebook.remove_page(-1)
        for name in tablist:
            page = Gtk.Box()
            self.notebook.append_page(page, Gtk.Label(name))
            self.notebook.child_set_property(page, 'tab-expand', True)
        self.notebook.show_all()
        self.notebook.set_show_tabs(len(tablist) > 1)
        self.notebook.set_current_page(tabcurr - 1)
        self.updating = False

    def _update_font(self, nvim, args):
        family, *attrs = args[0].split(':')
        font = Pango.FontDescription(string=family.replace('_', ' '))
        for a in attrs:
            if a[0] == 'h':
                font.set_size(float(a[1:]) * Pango.SCALE)
            if a[0] == 'b':
                font.set_weight(Pango.Weight.BOLD)
            if a[0] == 'i':
                font.set_style(Pango.Style.ITALIC)
        self.terminal.set_font(font)

    def _reset_font(self):
        giosss = Gio.SettingsSchemaSource.get_default()
        schema = giosss.lookup('org.gnome.desktop.interface', True)
        if not schema:
            return
        settings = Gio.Settings(settings_schema=schema)
        value = settings.get_string('monospace-font-name')
        self.terminal.set_font(Pango.FontDescription(string=value))

    def _update_color(self, nvim, args):
        bg_color, is_dark = args
        if bg_color != 'None':
            rgba = Gdk.RGBA()
            rgba.parse(bg_color)
            self.terminal.set_color_background(rgba)
        else:
            self._reset_color()
        self.get_settings().props.gtk_application_prefer_dark_theme = is_dark

    def _reset_color(self):
        sctx = self.terminal.get_style_context()
        rgba = sctx.get_background_color(sctx.get_state())
        self.terminal.set_color_background(rgba)

    def _update_scroll(self, nvim, args):
        a, b, lines = map(float, args)
        value = (a if a == 0 else a + 1) / lines
        page = (b - a) / lines
        adjustment = self.terminal.get_parent().get_vadjustment()
        adjustment.configure(value, 0.0, 1.0, 1.0 / lines, page, page)

    def _update_clipboard(self, nvim, args):
        method, data = args
        clipboard = Gtk.Clipboard.get_default(Gdk.Display.get_default())
        if method == 'set':
            text = '\n'.join(data[0])
            return clipboard.set_text(text, len(text))
        if method == 'get':
            text = clipboard.wait_for_text()
            return text.split('\n') if text else []
