# nvim-pygtk3

PyGTK3 frontend to Neovim with some visual GUI elements.

* Buffer list on header bar
* Tab list
* Applies GTK's light/dark themes according to `&bg`
* Applies font from `:GuiFont`, or from GSettings'
  `org.gnome.desktop.interface:monospace-font-name`
* Customizable with Python scripts

## Preview

![](screenshot.png)

## Installation

Requirements:

* `python-neovim`
* `python-gobject`
* `vte3`

```sh
$ PREFIX=/usr sudo make install
```

If you see a message like...

```
Traceback (most recent call last):
  File "<string>", line 1, in <module>
ImportError: No module named 'gi'
python executable 'python' doesnot satisfies dependencies gi and/or neovim
Makefile:34: recipe for target 'nvim-pygtk3.out' failed
make: *** [nvim-pygtk3.out] Error 1
```

... you can tell make another python location that met the needed dependencies

```sh
$ PREFIX=/usr PYTHON=/usr/bin/python3 sudo make install
```

## Python scripts

Scripts in `$XDG_CONFIG_HOME/nvim-pygtk3/*.py` are `exec`'d at startup,
exposing the following globals:

* `connect`: Utility wrapper to connect GObject signals.
* `window`: The GTK top-level window.
  [Docs](https://developer.gnome.org/gtk3/unstable/GtkApplicationWindow.html)
  * `window.terminal`: The VTE terminal that hosts neovim.
    [Docs](https://developer.gnome.org/vte/unstable/VteTerminal.html)
  * `window.switcher`: The GtkStackSwitcher that displays buffers.
    [Docs](https://developer.gnome.org/gtk3/unstable/GtkStackSwitcher.html)
  * `window.notebook`: The GtkNotebook that displays tabs and hosts the
    terminal.
    [Docs](https://developer.gnome.org/gtk3/unstable/GtkNotebook.html)

The `window` object has the following additional signals:

* `nvim-setup`: Emitted when neovim has started.
* `nvim-notify`: Emitted when neovim has notified the GUI.

Example script `~/.config/nvim-pygtk3/a.py`:

```python
@connect(window, 'nvim-setup')
def a(nvim):
    nvim.command(f'call rpcnotify({nvim.channel_id}, "hello", "world")')

@connect(window, 'nvim-notify')
def b(nvim, event, args):
    if event == 'hello':
        print('hello', args)

@connect(window.terminal, 'cursor-moved')
def c():
    print('cursor moved!')
```
