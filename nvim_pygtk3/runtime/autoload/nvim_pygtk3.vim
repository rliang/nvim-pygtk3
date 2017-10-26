fu! s:buf_label(nr)
  retu fnamemodify(pathshorten(bufname(a:nr)), ":~:.")
endf

let s:bufs_state=[]
fu! nvim_pygtk3#notify_bufs(force)
  let bufs=range(1, bufnr('$'))
  let bufs=filter(bufs, {k,v -> bufloaded(v) && buflisted(v)})
  let bufs=map(bufs, {k,v -> [v, s:buf_label(v), getbufvar(v, "&mod")]})
  let state=[bufs, bufnr('%')]
  if state != s:bufs_state || a:force
    let s:bufs_state = state
    cal rpcnotify(g:gui_channel, 'Gui', 'Bufs', state[0], state[1])
  en
endf

let s:tabs_state=[]
fu! nvim_pygtk3#notify_tabs(force)
  let tabs=range(1, tabpagenr('$'))
  let tabs=map(tabs, {k,v -> s:buf_label(get(tabpagebuflist(v), 0, 0))})
  let state=[tabs, tabpagenr()]
  if state != s:tabs_state || a:force
    let s:tabs_state = state
    cal rpcnotify(g:gui_channel, 'Gui', 'Tabs', state[0], state[1])
  en
endf

let s:color_state=[]
fu! nvim_pygtk3#notify_colors(force)
  let state=[synIDattr(hlID('Normal'), 'bg'), &bg == 'dark']
  if state != s:color_state || a:force
    let s:color_state = state
    cal rpcnotify(g:gui_channel, 'Gui', 'Color', state[0], state[1])
  en
endf

let s:scroll_state=[]
fu! nvim_pygtk3#notify_scroll(force)
  let state=[line('w0') - 1, line('w$'), line('$')]
  if state != s:scroll_state || a:force
    let s:scroll_state = state
    cal rpcnotify(g:gui_channel, 'Gui', 'Scroll', state[0], state[1], state[2])
  en
endf

fu! nvim_pygtk3#notify_font(font)
  cal rpcnotify(g:gui_channel, 'Gui', 'Font', a:font)
endf
