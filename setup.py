from setuptools import setup
import gi
gi.require_version('Gtk', '3.0')

setup(name='nvim-pygtk3',
      version='0.1.0',
      description='PyGTK3 frontend to Neovim with some visual GUI elements.',
      long_description=open('README.md').read(),
      author='R. Liang',
      author_email='ricardoliang@gmail.com',
      url='https://github.com/rliang/nvim-pygtk3',
      license='MIT',
      keywords='neovim pygtk3 gtk3',
      install_requires=['neovim>=0.1.10'],
      packages=['nvim_pygtk3'],
      package_data={'nvim_pygtk3': ['runtime/*.vim',
                                    'runtime/**/*.vim',
                                    'runtime/**/**/*.vim']},
      entry_points={'gui_scripts': ['nvim-pygtk3=nvim_pygtk3:main']},
      data_files=[('share/applications',
                   ['share/applications/nvim-pygtk3.desktop',
                    'share/applications/nvim-pygtk3-term.desktop']),
                  ('share/icons/hicolor/scalable/apps',
                   ['share/icons/hicolor/scalable/apps/neovim.svg'])])
