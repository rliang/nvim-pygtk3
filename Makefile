PREFIX?=${HOME}/.local

BIN=${PREFIX}/bin/nvim-pygtk3
ICON=${PREFIX}/share/icons/hicolor/scalable/apps/nvim-pygtk3.svg
APP=${PREFIX}/share/applications/nvim-pygtk3.desktop
TERM=${PREFIX}/share/applications/nvim-pygtk3-term.desktop

install: ${BIN} ${ICON} ${APP} ${TERM}

uninstall:
	rm ${BIN} ${ICON} ${APP} ${TERM}

${BIN}: nvim-pygtk3
	install -Dm755 $^ $@

${ICON}: neovim.svg
	install -Dm644 $^ $@

${APP}: nvim-pygtk3.desktop
	install -Dm644 $^ $@

${TERM}: nvim-pygtk3-term.desktop
	install -Dm644 $^ $@
