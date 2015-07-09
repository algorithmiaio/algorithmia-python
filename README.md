Algorithmia Common Library (python)
===================================

Python client library for accessing the Algorithmia API


# Install from PyPi
```bash
pip install algorithmia
```

# Install from source

Build algorithmia client wheel:
```bash
python setup.py bdist_wheel
```

Install a wheel manually:
```bash
pip install --user --upgrade dist/algorithmia-*.whl
```


# Use

```python
import Algorithmia

apiKey = 'XXXXXXXXXX'

print Algorithmia.client(apiKey).algo('util/echo').pipe('echo this string')
```

See full docs at: https://algorithmia.com/docs/clients/python/
