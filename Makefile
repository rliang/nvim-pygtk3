PREFIX?=${HOME}/.local

install:
	install -Dm755 nvim-pygtk3 ${PREFIX}/bin/nvim-pygtk3
	install -Dm644 nvim-pygtk3.desktop ${PREFIX}/share/applications/nvim-pygtk3.desktop
	install -Dm644 neovim.png ${PREFIX}/share/icons/hicolor/256x256/apps/nvim-pygtk3.png
	sed -i "s|{PREFIX}|${PREFIX}|" ${PREFIX}/share/applications/nvim-pygtk3.desktop
