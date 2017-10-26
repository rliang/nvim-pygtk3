if exists('g:GuiLoaded') | fini | en
let g:GuiLoaded = 1

augroup nvim_pygtk3
  au!

  au DirChanged,BufEnter,BufLeave * cal nvim_pygtk3#notify_bufs()
  au TermOpen * cal nvim_pygtk3#notify_bufs()
  au TextChanged,TextChangedI,BufWritePost * cal nvim_pygtk3#notify_bufs()

  au DirChanged,BufEnter,BufLeave * cal nvim_pygtk3#notify_tabs()
  au TabEnter,TabLeave,TabNew,TabClosed * cal nvim_pygtk3#notify_tabs()

  au ColorScheme * cal nvim_pygtk3#notify_colors()
  do ColorScheme

  au CursorMoved,CursorMovedI * cal nvim_pygtk3#notify_scroll()
  au VimResized * cal nvim_pygtk3#notify_scroll()
augroup END

com! -nargs=? -bang GuiFont cal nvim_pygtk3#notify_font('<args>')
