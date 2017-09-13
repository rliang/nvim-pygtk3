# nvim-pygtk3

PyGTK3 frontend to Neovim with some visual GUI elements.

* Buffer list on the header bar
* Tab list
* Applies GTK's light/dark themes according to `&bg`
* Applies font from GSettings' `org.gnome.desktop.interface`
  `monospace-font-name`

# Screenshot

![](screenshot.png)

# Installation

## System-wide

```sh
$ PREFIX=/usr sudo make install
```

## Per-user through init.vim

```vim
Plug 'rliang/nvim-pygtk3', {'do': 'make install'}
```

## Custom python interpreter

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
$ PREFIX=/usr sudo make install PYTHON=/usr/bin/python3
```
