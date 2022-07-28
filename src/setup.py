from setuptools import setup

APP=['game.py']
OPTIONS = {
    "iconfile":"airforce.png",
    'argv_emulation': True,
}

setup(
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app']
)