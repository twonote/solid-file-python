[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT) 
[![pypi](https://img.shields.io/pypi/v/solid-file.svg)](https://pypi.python.org/pypi/solid-file)
[![versions](https://img.shields.io/pypi/pyversions/solid-file.svg)](https://github.com/twonote/solid-file-python)
![PyPI - Downloads](https://img.shields.io/pypi/dm/solid-file) 
![GitHub closed issues](https://img.shields.io/github/issues-closed/twonote/solid-file-python)

# About 
solid-file-python is a Python library for creating and managing files and folders in Solid pods.

Read and try it on [jupiter notebook](https://github.com/twonote/solid-file-python/blob/master/solid-file-python-getting-start.ipynb) now!

# Limitations

Currently the authentication process relies on endpoints and cookies by the node-solid-server. Therefore, at least for now, authentication with other pod providers won't work.

# What is Solid?

Solid is a specification that lets people store their data securely in decentralized data stores called Pods. Learn more about Solid on [solidproject.org](https://solidproject.org/).

# Test setting
If you run the tests on terminal using VS Code as the editor, you need to add this line `"terminal.integrated.env.osx": {"PYTHONPATH": "${workspaceFolder}"}` to `/.vscode/setting.json` to make it work.

# Credit
This project is inspired by (and porting from) [jeff-zucker/solid-file-client](https://github.com/jeff-zucker/solid-file-client)
I want to thank the original authors and the community who worked to build that lovely project for Solid ecosystem.
