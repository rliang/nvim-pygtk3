PREFIX?=${HOME}/.local

EXEC=${PREFIX}/bin/nvim-pygtk3
ICON=${PREFIX}/share/icons/hicolor/256x256/apps/nvim-pygtk3.png
ENTRY=${PREFIX}/share/applications/nvim-pygtk3.desktop

install: ${EXEC} ${ICON} ${ENTRY}

uninstall:
	rm ${EXEC} ${ICON} ${ENTRY}

${EXEC}: nvim-pygtk3
	install -Dm755 $^ $@

${ICON}: neovim.png
	install -Dm644 $^ $@

${ENTRY}: nvim-pygtk3.desktop
	install -Dm644 $^ $@
	sed -i "s|{PREFIX}|${PREFIX}|" $@
