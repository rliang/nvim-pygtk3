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
