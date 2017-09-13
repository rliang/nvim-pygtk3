PREFIX?=${HOME}/.local
PYTHON?=python

BIN=${PREFIX}/bin/nvim-pygtk3
ICON=${PREFIX}/share/icons/hicolor/scalable/apps/neovim.svg
APP=${PREFIX}/share/applications/nvim-pygtk3.desktop
TERM=${PREFIX}/share/applications/nvim-pygtk3-term.desktop

PYTHON_COMMAND=import sys, gi, neovim; sys.exit(0)
INVALID_PYTHON_MESSAGE=python executable \'${PYTHON}\' doesnot satisfies dependencies 'gi' and/or 'neovim'


install: ${BIN} ${ICON} ${APP} ${TERM}

uninstall:
	rm ${BIN} ${ICON} ${APP} ${TERM}

${BIN}: nvim-pygtk3.out
	install -Dm755 $^ $@

${ICON}: neovim.svg
	install -Dm644 $^ $@

${APP}: nvim-pygtk3.desktop
	install -Dm644 $^ $@

${TERM}: nvim-pygtk3-term.desktop
	install -Dm644 $^ $@

clean:
	rm -f nvim-pygtk3.out

nvim-pygtk3.out: nvim-pygtk3
	@$(SHELL) -c "${PYTHON} -c'${PYTHON_COMMAND}' && exit 0; echo ${INVALID_PYTHON_MESSAGE} && exit 1"
	@$(SHELL) -c "sed -n '1s| python$$| `command -v ${PYTHON}`|;w $^.out' $^"

.PHONY: nvim-pygtk3.out clean
