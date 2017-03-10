PREFIX?=${HOME}/.local

BIN=${PREFIX}/bin/nvim-pygtk3
ICON=${PREFIX}/share/icons/hicolor/scalable/apps/nvim-pygtk3.svg
ENTRY=${PREFIX}/share/applications/nvim-pygtk3.desktop

install: ${BIN} ${ICON} ${ENTRY}

uninstall:
	rm ${BIN} ${ICON} ${ENTRY}

${BIN}: nvim-pygtk3
	install -Dm755 $^ $@

${ICON}: neovim.svg
	install -Dm644 $^ $@

${ENTRY}: nvim-pygtk3.desktop
	install -Dm644 $^ $@
	sed -i "s|{PREFIX}|${PREFIX}|" $@
