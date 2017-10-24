fu! s:buf_label(nr)
  retu fnamemodify(pathshorten(bufname(a:nr)), ":~:.")
endf

fu! nvim_pygtk3#notify_bufs()
  let bufs=range(1, bufnr('$'))
  let bufs=filter(bufs, {k,v -> bufloaded(v) && buflisted(v)})
  let bufs=map(bufs, {k,v -> [v, s:buf_label(v), getbufvar(v, "&mod")]})
  cal rpcnotify(g:gui_channel, 'Gui', 'Bufs', bufs, bufnr('%'))
endf

fu! nvim_pygtk3#notify_tabs()
  let tabs=range(1, tabpagenr('$'))
  let tabs=map(tabs, {k,v -> [v, s:buf_label(get(tabpagebuflist(v), 0, 0))]})
  cal rpcnotify(g:gui_channel, 'Gui', 'Tabs', tabs, tabpagenr())
endf

fu! nvim_pygtk3#notify_font(font)
  cal rpcnotify(g:gui_channel, 'Gui', 'Font', a:font)
endf

fu! nvim_pygtk3#notify_colors()
  cal rpcnotify(g:gui_channel, 'Gui', 'Color', synIDattr(hlID('Normal'), 'bg'), &bg == 'dark')
endf
