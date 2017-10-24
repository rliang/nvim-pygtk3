if exists('g:GuiLoaded') | fini | en
let g:GuiLoaded = 1

augroup nvim_pygtk3
  au!
  au BufEnter,DirChanged,TermOpen,TextChanged,TextChangedI,BufWritePost * cal nvim_pygtk3#notify_bufs()
  au BufEnter,DirChanged,TabEnter,TabLeave,TabNew,TabClosed * cal nvim_pygtk3#notify_tabs()
  au ColorScheme * cal nvim_pygtk3#notify_colors()
augroup END

com! -nargs=? -bang GuiFont cal nvim_pygtk3#notify_font('<args>')
