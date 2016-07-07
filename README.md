Algorithmia Common Library (python)
===================================

Python client library for accessing the Algorithmia API
For API documentation, see the [PythonDocs](https://algorithmia.com/docs/lang/python)


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


# Getting started
First create an Algorithmia client:
```python
import Algorithmia

apiKey = '{{Your API key here}}'
client = Algorithmia.client(apiKey)
```

Now you can call an algorithm:
```python
algo = client.algo('demo/Hello/0.1.1')
response = algo.pipe("HAL 9000")
print response.result    # Hello, world!
print response.metadata  # Metadata(content_type='text',duration=0.0002127)
print response.metadata.duration # 0.0002127
```

In addition to string input and output, algorithms can receive and return JSON or binary data.
For JSON input/output, you can simply work with native python types like arrays and dicts:

```python
algo = client.algo('WebPredict/ListAnagrams/0.1.0')
result = algo.pipe(["transformer", "terraforms", "retransform"]).result
# -> ["transformer","retransform"]
```

For binary input/output, you can work directly with byte arrays:

```python
input = bytearray(open("/path/to/bender.png", "rb").read())
result = client.algo("opencv/SmartThumbnail/0.1").pipe(input).result
# -> [binary byte sequence]
```

This client also provides w
```
client.algo('util/whoopsWrongAlgo').pipe('Hello, world!')  
# Algorithmia.algo_response.AlgoException: algorithm algo://util/whoopsWrongAlgo not found
```

You can configure the request with options defined in the API spec:
```python
from Algorithmia.algorithm import OutputType
client.algo('util/echo').set_options(timeout=60, stdout=False)
```
(note: `stdout=True` is only supported if you have access to the algorithm source)


# Working with data
The Algorithmia client also provides a way to manage both Algorithmia hosted data
and data from Dropbox or S3 accounts that you've connected to you Algorithmia account.

### Create directories:
Create directories by instantiating a `DataDirectory` object and calling `create()`:
```python
client.dir("data://.my/foo").create()
client.dir("dropbox://somefolder").create()
```

### Upload files to a directory:
Upload files by calling `put` on a `DataFile` object, 
or by calling `putFile` on a `DataDirectory` object.
```
foo = client.dir("data://.my/foo")
foo.putFile(open("/path/to/myfile"))
foo.file("sample.txt").put("sample text contents")
foo.file("binary_file").put(some_binary_data)
```
Note: you can instantiate a `DataFile` by either `client.file(path)` or `client.dir(path).file(filename)`


### Download contents of files
Download files by calling `getString`, `getBytes`, `getJson`, or `getFile` on a `DataFile` object:
```
foo = client.dir("data://.my/foo")
sampleText = foo.file("sample.txt").getString()  # String object
binaryContent = foo.file("binary_file").getBytes()  # Binary data
tempFile = foo.file("myfile").getFile()   # Open file descriptor
```

### Delete files and directories
Delete files and directories by calling `delete` on their respective `DataFile` or `DataDirectory` object.
DataDirectories take an optional `force` parameter that indicates whether the directory should be deleted
if it contains files or other directories.
```
foo = client.dir("data://.my/foo")
foo.file("sample.txt").delete()
foo.delete(true) // true implies force deleting the directory and its contents
```


### List directory contents
Iterate over the contents of a directory using the iterated returned by calling `list`, `files`, or `dirs` 
on a `DataDirectory` object:
```
foo = client.dir("data://.my/foo")

# List files in "foo"
for file in foo.files():
    print file.path " at URL: " + file.url + " last modified " + file.last_modified

# List directories in "foo"
for file in foo.dirs():
    print dir.path " at URL: " + file.url

# List everything in "foo"
for entry in foo.list():
    print entry.path " at URL: " + entry.url
```

### Manage directory permissions
Directory permissions may be set when creating a directory, or may be updated on already existing directories.
```
from Algorithmia.acl import ReadAcl, AclType
foo = client.dir("data://.my/foo")
# ReadAcl.public is a wrapper for Acl(AclType.public) to make things easier
foo.create(ReadAcl.public)   

acl = foo.get_permissions()  # Acl object
acl.read_acl == AclType.public  # True

foo.update_permissions(ReadAcl.private)
foo.get_permissions().read_acl == AclType.private # True
```

# Upgrading from 0.9.x
The main backwards incompatibility between 0.9.x and 1.0.0 is the result of an algorithm call.
In 0.9.x the result of an algorithm call is just the algorithm's output (which is not the full spec returned by the API)
```python
result = client.algo('util/echo').pipe('Hello, world!')
print result   # Hello, world!
```
In 1.0.x the result of an algorithm matches the API specification.  The algorithm's output is nested in an attribute 'result', and metadata can be accessed via the 'metadata' attribute.
```python
result = client.algo('util/echo').pipe('Hello, world!')
print result.result     # Hello, world!
print result.metadata   # content_type, duration etc
```

Aside from that you should be able to drop in the newest version of the client.  Another advantage of using the newest client is full access to the entire Data API specification.

# Running tests

```bash
export ALGORITHMIA_API_KEY={{Your API key here}}
cd Test
python datadirectorytest.py
python util.py
```
