if exists('g:GuiLoaded') | fini | en
let g:GuiLoaded = 1

augroup nvim_pygtk3
  au!

  au DirChanged,BufEnter,BufLeave * cal nvim_pygtk3#notify_bufs(0)
  au TermOpen * cal nvim_pygtk3#notify_bufs(0)
  au TextChanged,TextChangedI,BufWritePost * cal nvim_pygtk3#notify_bufs(0)
  cal nvim_pygtk3#notify_bufs(0)

  au DirChanged,BufEnter,BufLeave * cal nvim_pygtk3#notify_tabs(0)
  au TabEnter,TabLeave,TabNew,TabClosed * cal nvim_pygtk3#notify_tabs(0)
  cal nvim_pygtk3#notify_tabs(0)

  au ColorScheme * cal nvim_pygtk3#notify_colors(0)
  cal nvim_pygtk3#notify_colors(0)

  au CursorMoved,CursorMovedI * cal nvim_pygtk3#notify_scroll(0)
  au FocusGained,FocusLost * cal nvim_pygtk3#notify_scroll(1)
  au VimResized * cal nvim_pygtk3#notify_scroll(1)
augroup END

com! -nargs=? -bang GuiFont cal nvim_pygtk3#notify_font('<args>')
