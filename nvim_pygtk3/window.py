from gi.repository import GObject, GLib, Gio, Gdk, Gtk, Vte, Pango
import neovim
from threading import Thread
from functools import partial


class NeovimBufferBar(Gtk.StackSwitcher):
    """Widget that displays open buffers as GtkToggleButtons.

    The buttons also indicate modified buffers through a `document-edit` icon.

    To increase performance, buttons are kept in a cache that is increased as
    needed.

    """

    updating = GObject.Property(type=bool, default=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.btns = []
        self.bids = []

    @GObject.Signal()
    def nvim_switch_buffer(self, id: int):
        """Signal emitted when the current buffer should be switched.

        :id: the buffer number to switch to.

        """
        pass

    def _do_button_toggled(self, btn: Gtk.ToggleButton):
        """Handler for when a button is toggled.

        Emits `nvim-switch-buffer` if the button was toggled ON, and the widget
        isn't in the middle of an update.

        Also avoids toggling off buttons, since the user can't "unswitch" to a
        buffer.

        :btn: the toggled button.

        """
        if not self.props.updating:
            if btn.get_active():
                id = self.bids[self.btns.index(btn)]
                self.emit('nvim-switch-buffer', id)
            else:
                btn.set_active(True)

    def update(self, buflist: list, bufcurr: int):
        """Updates the widget's buttons.

        Increases the internal button cache if needed, then displays the
        appropriate amount of buttons, updating their state.

        :buflist: list of tuples (buffer-number, buffer-name, buffer-modified).
        :bufcurr: the active buffer's number.

        """
        self.props.updating = True
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
        self.props.updating = False


class NeovimTabBar(Gtk.Notebook):
    """Widget that displays tabs.

    Pages added to this widget are dummies, since the actual content is drawn
    elsewhere.

    """

    updating = GObject.Property(type=bool, default=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, show_border=False, **kwargs)
        self.connect('switch-page', self._do_switch_page)

    @GObject.Signal()
    def nvim_switch_tab(self, id: int):
        """Signal emitted when the current tab should be switched.

        :id: the tab number to switch to.

        """
        pass

    def _do_switch_page(self, _, page: Gtk.Widget, num: int):
        """Handler for when a tab page is selected.

        Emits `nvim-switch-tab` if the widget is not in the middle of an
        update.

        :page: the selected tab page.
        :num: the selected tab page number.

        """
        if not self.props.updating:
            self.emit('nvim-switch-tab', num + 1)

    def update(self, tablist: list, tabcurr: int):
        """Updates the widget's tabs.

        :tablist: list of tab names.
        :tabcurr: the active buffer's number.

        """
        self.props.updating = True
        for _ in range(self.get_n_pages()):
            self.remove_page(-1)
        for name in tablist:
            page = Gtk.Box()
            self.append_page(page, Gtk.Label(name))
            self.child_set_property(page, 'tab-expand', True)
        self.show_all()
        self.set_current_page(tabcurr - 1)
        self.set_show_tabs(self.get_n_pages() > 1)
        self.props.updating = False


class NeovimViewport(Gtk.Viewport):
    """Widget that manages scrollbars.

    Typically this should be added to a GtkScrolledWindow, and the widget that
    draws neovim's content should be added to this.

    The internal GtkAdjustment's range is forced between [0, 1] to prevent the
    child widget from looking overscrolled.
    """

    lines = GObject.Property(type=int, default=1)
    updating = GObject.Property(type=bool, default=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        vadj = self.get_vadjustment()
        vadj.connect('value-changed', self._do_vadjustment_value_changed)

    @GObject.Signal()
    def nvim_vscrolled(self, val: int):
        """Signal emitted when the current window should be scrolled.

        :val: the line number to scroll to.

        """
        pass

    def _do_vadjustment_value_changed(self, vadj: Gtk.Adjustment):
        """Handler for when the GtkAdjustment's value is changed.

        Emits `nvim-vscrolled` if the widget is not in the middle of an
        update and the bounds are still valid, i.e. not changed automatically
        by GTK.

        :vadj: the adjustment.

        """
        if not self.props.updating and vadj.get_upper() == 1.0:
            v = vadj.get_value()
            v = v if v == 0.0 else v + vadj.get_page_size()
            self.emit('nvim-vscrolled', int(v * self.props.lines))

    def update(self, a: int, b: int, lines: int):
        """Updates the viewport.

        :a: the first visible line of the current window's buffer.
        :b: the last visible line of the current window's buffer.
        :lines: the current window's buffer's line count.

        """
        self.props.updating = True
        a, b, self.props.lines = map(float, (a, b, lines))
        p = (b - a) / self.props.lines
        v = (a if a == 0.0 else a + 1.0) / self.props.lines
        vadj = self.get_vadjustment()
        vadj.configure(v, 0.0, 1.0, 1.0 / self.props.lines, p, p)
        self.props.updating = False


class NeovimTerminal(Vte.Terminal):
    """Widget that manages the child neovim process and displays its content.

    TODO: use a GtkDrawingArea and `Nvim.ui_attach` instead.

    """

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
        """Signal emitted when successfully attached to neovim's remote API.

        :nvim: the attached `neovim.Nvim` instance.

        """
        pass

    def spawn(self, addr: str, argv: list, rtp: str):
        """Spawns the neovim process.

        Upon success, attaches to it and emits `nvim-attached`.

        :addr: the socket path for neovim to listen on.
        :argv: additional arguments passed to neovim.
        :rtp: additional comma-separated vim runtime paths.

        """

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

    def update_font(self, value: str):
        """Updates the widget's font.

        :value: see vim's `:h guifont`.

        """
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

    def update_color(self, bg_color: str, is_dark: bool):
        """Updates the widget's background color and theme.

        :bg_color: string representing the color, or 'None'.
        :is_dark: whether the background is dark, see `:h background`.

        """
        self.get_settings().props.gtk_application_prefer_dark_theme = is_dark
        if bg_color != 'None':
            rgba = Gdk.RGBA()
            rgba.parse(bg_color)
            self.set_color_background(rgba)
        else:
            GLib.idle_add(self.reset_color)

    def reset_font(self):
        """Sets the widget's font from GSettings, if any. """
        giosss = Gio.SettingsSchemaSource.get_default()
        schema = giosss.lookup('org.gnome.desktop.interface', True)
        if not schema:
            self.set_font(Pango.FontDescription(string='Monospace'))
            return
        settings = Gio.Settings(settings_schema=schema)
        value = settings.get_string('monospace-font-name')
        self.set_font(Pango.FontDescription(string=value))

    def reset_color(self):
        """Sets the widget's backgound color from the GTK theme. """
        sctx = self.get_style_context()
        rgba = sctx.get_background_color(sctx.get_state())
        self.set_color_background(rgba)


class NeovimWindow(Gtk.ApplicationWindow):
    """The main window, which wires neovim and the widgets together. """

    def __init__(self, *args, **kwargs):
        super().__init__(*args,
                         default_width=640,
                         default_height=480,
                         **kwargs)
        self.switcher = NeovimBufferBar()
        self.set_titlebar(Gtk.HeaderBar(show_close_button=True,
                                        custom_title=self.switcher))
        vbox = Gtk.Box(parent=self, orientation=Gtk.Orientation.VERTICAL)
        self.notebook = NeovimTabBar(parent=vbox)
        self.viewport = NeovimViewport(parent=Gtk.ScrolledWindow(parent=vbox))
        self.terminal = NeovimTerminal(parent=self.viewport, expand=True)
        self.terminal.connect('child-exited', lambda *_:
                              self.close())
        self.terminal.connect('nvim-attached', lambda _, nvim:
                              self.emit('nvim-setup', nvim))

    @GObject.Signal(flags=GObject.SignalFlags.RUN_LAST)
    def nvim_setup(self, nvim: object):
        """Signal emitted before neovim's main loop.

        After the emission, widgets which can control neovim are connected to
        the API instance. Then, the main loop's thread is started.

        :nvim: the `neovim.Nvim` instance.

        """
        nvim.vars['gui_channel'] = nvim.channel_id
        nvim.subscribe('Gui')
        nvim.options['showtabline'] = 0
        nvim.options['ruler'] = False
        nvim.async_call(partial(nvim.command, 'ru! ginit.vim'))
        self.terminal.connect('focus-in-event', lambda *_:
                              nvim.async_call(partial(nvim.command,
                                                      f'do FocusGained')))
        self.terminal.connect('focus-out-event', lambda *_:
                              nvim.async_call(partial(nvim.command,
                                                      f'do FocusLost')))
        self.switcher.connect('nvim-switch-buffer', lambda _, num:
                              nvim.async_call(partial(nvim.command,
                                                      f'b {num}')))
        self.notebook.connect('nvim-switch-tab', lambda _, num:
                              nvim.async_call(partial(nvim.command,
                                                      f'{num}tabn')))
        self.viewport.connect('nvim-vscrolled', lambda _, val:
                              nvim.async_call(partial(nvim.command,
                                                      f'norm! {val}gg')))
        Thread(daemon=True, target=nvim.run_loop,
               args=(partial(self.emit, 'nvim-request', nvim),
                     partial(self.emit, 'nvim-notify', nvim))).start()

    @GObject.Signal(flags=GObject.SignalFlags.RUN_LAST)
    def nvim_notify(self, nvim: object, sub: str, args: object):
        """Signal emitted on a notification from neovim.

        This is called on neovim's event loop, so modifications to GTK widgets
        should be done through `GLib.idle_add()`.

        :nvim: the `neovim.Nvim` instance.
        :sub: the event name.
        :args: the event arguments.

        """
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
        """Signal emitted on a request from neovim.

        This is called on neovim's event loop, so modifications to GTK widgets
        should be done through `GLib.idle_add()`.

        After emission, should return an appropriate value expected by the
        request.

        :nvim: the `neovim.Nvim` instance.
        :sub: the request name.
        :args: the request arguments.

        """
        if sub == 'Gui' and args[0] == 'Clipboard':
            return self.update_clipboard(*args[1:])

    def update_clipboard(self, method: str, data: list):
        """Handles a clipboard request.

        This is called on neovim's event loop, so modifications to GTK widgets
        should be done through `GLib.idle_add()`.

        :method: `get` to obtain the clipboard's contents or `set` to update
        them.
        :data: when the method is `set`, contains the lines to add to the
        clipboard, else None.
        :returns: the clipboard's contents when the method is `get`, else None.

        """
        cb = Gtk.Clipboard.get_default(Gdk.Display.get_default())
        if method == 'set':
            text = '\n'.join(data[0])
            return cb.set_text(text, len(text))
        if method == 'get':
            text = cb.wait_for_text()
            return text.split('\n') if text else []

