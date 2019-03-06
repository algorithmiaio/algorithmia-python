Algorithmia Common Library (python)
===================================

Python client library for accessing the Algorithmia API
For API documentation, see the [PythonDocs](https://algorithmia.com/docs/lang/python)

[![PyPI](https://img.shields.io/pypi/v/algorithmia.svg?maxAge=2592000)]()

## Install from PyPi

The official Algorithmia python client is [available on PyPi](https://pypi.python.org/pypi/algorithmia).
Install it with pip:

```bash
pip install algorithmia
```

## Install from source

Build algorithmia client wheel:

```bash
python setup.py bdist_wheel
```

Install a wheel manually:

```bash
pip install --user --upgrade dist/algorithmia-*.whl
```

## Authentication

First, create an Algorithmia client and authenticate with your API key:

```python
import Algorithmia

apiKey = '{{Your API key here}}'
client = Algorithmia.client(apiKey)
```

Now you're ready to call algorithms.

## Calling algorithms

The following examples of calling algorithms are organized by type of input/output which vary between algorithms.

Note: a single algorithm may have different input and output types, or accept multiple types of input,
so consult the algorithm's description for usage examples specific to that algorithm.

### Text input/output

Call an algorithm with text input by simply passing a string into its `pipe` method.
If the algorithm output is text, then the `result` field of the response will be a string.

```python
algo = client.algo('demo/Hello/0.1.1')
response = algo.pipe("HAL 9000")
print response.result    # Hello, world!
print response.metadata  # Metadata(content_type='text',duration=0.0002127)
print response.metadata.duration # 0.0002127
```

### JSON input/output

Call an algorithm with JSON input by simply passing in a type that can be serialized to JSON:
most notably python dicts and arrays.
For algorithms that return JSON, the `result` field of the response will be the appropriate
deserialized type.

```python
algo = client.algo('WebPredict/ListAnagrams/0.1.0')
result = algo.pipe(["transformer", "terraforms", "retransform"]).result
# -> ["transformer","retransform"]
```

### Binary input/output

Call an algorithm with Binary input by passing a byte array into the `pipe` method.
Similarly, if the algorithm response is binary data, then the `result` field of the response
will be a byte array.

```python
input = bytearray(open("/path/to/bender.png", "rb").read())
result = client.algo("opencv/SmartThumbnail/0.1").pipe(input).result
# -> [binary byte sequence]
```

### Error handling

API errors and Algorithm exceptions will result in calls to `pipe` throwing an `AlgoException`:

```python
client.algo('util/whoopsWrongAlgo').pipe('Hello, world!')
# Algorithmia.algo_response.AlgoException: algorithm algo://util/whoopsWrongAlgo not found
```

### Request options

The client exposes options that can configure algorithm requests.
This includes support for changing the timeout or indicating that the API should include stdout in the response.

```python
from Algorithmia.algorithm import OutputType
response = client.algo('util/echo').set_options(timeout=60, stdout=False)
print response.metadata.stdout
```

Note: `stdout=True` is only supported if you have access to the algorithm source.


## Working with data
The Algorithmia client also provides a way to manage both Algorithmia hosted data
and data from Dropbox or S3 accounts that you've connected to you Algorithmia account.

### Create directories
Create directories by instantiating a `DataDirectory` object and calling `create()`:

```python
client.dir("data://.my/foo").create()
client.dir("dropbox://somefolder").create()
```

### Upload files to a directory

Upload files by calling `put` on a `DataFile` object,
or by calling `putFile` on a `DataDirectory` object.

```python
foo = client.dir("data://.my/foo")
foo.file("remote_file").putFile("/path/to/myfile")
foo.file("sample.txt").put("sample text contents")
foo.file("binary_file").put(some_binary_data)
```

Note: you can instantiate a `DataFile` by either `client.file(path)` or `client.dir(path).file(filename)`


### Download contents of file

Download files by calling `getString`, `getBytes`, `getJson`, or `getFile` on a `DataFile` object:

```python
foo = client.dir("data://.my/foo")
sampleText = foo.file("sample.txt").getString()  # String object
binaryContent = foo.file("binary_file").getBytes()  # Binary data
tempFile = foo.file("myfile").getFile()   # Open file descriptor
```

### Delete files and directories

Delete files and directories by calling `delete` on their respective `DataFile` or `DataDirectory` object.
DataDirectories take an optional `force` parameter that indicates whether the directory should be deleted
if it contains files or other directories.

```python
foo = client.dir("data://.my/foo")
foo.file("sample.txt").delete()
foo.delete(true) // true implies force deleting the directory and its contents
```


### List directory contents

Iterate over the contents of a directory using the iterated returned by calling `list`, `files`, or `dirs`
on a `DataDirectory` object:

```python
foo = client.dir("data://.my/foo")

# List files in "foo"
for file in foo.files():
    print file.path + " at URL: " + file.url + " last modified " + file.last_modified

# List directories in "foo"
for file in foo.dirs():
    print dir.path + " at URL: " + file.url

# List everything in "foo"
for entry in foo.list():
    print entry.path + " at URL: " + entry.url
```

### Manage directory permissions

Directory permissions may be set when creating a directory, or may be updated on already existing directories.

```python
from Algorithmia.acl import ReadAcl, AclType
foo = client.dir("data://.my/foo")
# ReadAcl.public is a wrapper for Acl(AclType.public) to make things easier
foo.create(ReadAcl.public)

acl = foo.get_permissions()  # Acl object
acl.read_acl == AclType.public  # True

foo.update_permissions(ReadAcl.private)
foo.get_permissions().read_acl == AclType.private # True
```

## Running tests

```bash
export ALGORITHMIA_API_KEY={{Your API key here}}
cd Test
python acl_test.py
python algo_test.py
python datadirectorytest.py
python datafile_test.py
python utiltest.py
```
