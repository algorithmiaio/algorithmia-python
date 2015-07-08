Algorithmia Common Library (python)
===================================

This is a python client library for accessing the Algorithmia API


# Package

To build algorithmia client wheel:

```bash
python setup.py bdist_wheel
```


# Install

To install a wheel manually:

```bash
pip install --user --upgrade dist/algorithmia-*.whl
```


# Use

```python
import Algorithmia

apiKey = 'XXXXXXXXXX'

print Algorithmia.client(apiKey)algo('util/echo').pipe('echo this string')
```
