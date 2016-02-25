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


# Use
First create an Algorithmia client:
```python
import Algorithmia

apiKey = '{{Your API key here}}'

client = Algorithmia.client(apiKey)
```

Now you can call an algorithm:
```python
result = client.algo('util/echo').pipe('Hello, world!')
```

The result of a call is either an AlgoException (indicating an error) or an AlgoResponse:
```python
print result.result    # Hello, world!
print result.metadata  # Metadata(content_type='text',duration=0.0002127)
print result.metadata.duration # 0.0002127
client.algo('util/whoopsWrongAlgo').pipe('Hello, world!')  # Algorithmia.algo_response.AlgoException: algorithm algo://util/whoopsWrongAlgo not found
```

You can also set options (query paramters in the spec):
```python
from Algorithmia.algorithm import OutputType
client.algo('util/echo').set_options(timeout=60, stdout=False, output=OutputType.raw)
```

# Working with data
After creating a client you can store data within Algorithmia as well
```python
# Create a directory "foo"
foo = client.dir("data://.my/foo")
foo.create();

# You can also set the ACL for the directory on creation or update it
from Algorithmia.acl import ReadAcl, AclType
foo.create(ReadAcl.public)   # ReadAcl.public is a wrapper for Acl(AclType.public) to make things easier

acl = foo.get_permissions()  # Acl object
acl.read_acl == AclType.public  # True

foo.update_permissions(ReadAcl.private)
foo.get_permissions().read_acl == AclType.private # True


# Upload files to "foo" directory
foo.file("sample.txt").put("sample text contents")
foo.file("binary_file").put(some_binary_data)
foo.putFile(open("/path/to/myfile"))

# List files in "foo"
for file in foo.files():
    print file.path " at URL: " + file.url + " last modified " + file.last_modified

# Note nested directories are not currently supported by the API, but there are an analogous .dirs and .list methods

# Get contents of files
sampleText = foo.file("sample.txt").getString()  # String object
binaryContent = foo.file("binary_file").getBytes()  # Binary data
tempFile = foo.file("myfile").getFile()   # Open file descriptor

# Delete files and directories
foo.file("sample.txt").delete()
foo.delete(true) // true implies force deleting the directory and its contents
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
