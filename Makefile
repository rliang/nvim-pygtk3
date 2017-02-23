PREFIX?=${HOME}/.local

install:
	install -Dm755 nvim-pygtk3 ${PREFIX}/bin/nvim-pygtk3
	install -Dm644 nvim-pygtk3.desktop ${PREFIX}/share/applications/nvim-pygtk3.desktop
	echo "Exec=${PREFIX}/bin/nvim-pygtk3 %F" >> ${PREFIX}/share/applications/nvim-pygtk3.desktop
