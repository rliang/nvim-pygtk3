# nvim-pygtk3

PyGTK3 frontend to Neovim with some visual GUI elements.

* Buffer list on the header bar
* Tab list
* Automatically switches to GTK dark theme variant according to `&bg`

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
