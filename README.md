Algorithmia Common Library (python)
===================================

Python client library for accessing the Algorithmia API
For API documentation, see the [PythonDocs](https://algorithmia.com/docs/lang/python)

[![PyPI](https://img.shields.io/pypi/v/algorithmia.svg?maxAge=600)]()

## Algorithm Development Kit
This package contains the [algorithmia-adk](https://github.com/algorithmiaio/algorithmia-adk-python) development kit, simply add `from Algorithmia import ADK` into your workflow to access it.

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
#install locally for testing

from directory containing setup.py and the Algorithmia directory:
```bash
pip3 install ./
```
#add CLI script to PATH

to use the CLI it may be nessesary to add the install location to the PATH enviroment variable
```bash
export PATH = $HOME/.local/bin:$PATH
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
print(response.result)    # Hello, world!
print(response.metadata)  # Metadata(content_type='text',duration=0.0002127)
print(response.metadata.duration) # 0.0002127
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
print(response.metadata.stdout)
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
    print(file.path + " at URL: " + file.url + " last modified " + file.last_modified)

# List directories in "foo"
for file in foo.dirs():
    print(dir.path + " at URL: " + file.url)

# List everything in "foo"
for entry in foo.list():
    print(entry.path + " at URL: " + entry.url)
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

# Algorithmia CLI

Algorithmia CLI is a cross-platform tool for interfacing with algorithms and the Algorithmia Data API.

## Configure Authentication

In order to make calls with the CLI, you'll need to configure the authentication with an API key. If you don't already have an API key, get started by signing up for an account at [Algorithmia.com](https://algorithmia.com). Once you've completed the sign up process, copy the API key from your account dashboard.

Begin the configuration process by running the command `algo auth`.
You will see an interactive prompt to guide you through setting up a default profile:

```
$ algo auth
Configuring authentication for profile: 'default'
Enter API Endpoint [https://api.algorithmia.com]:
Enter API Key:
(optional) enter path to custom CA certificate:
Profile is ready to use. Test with 'algo ls'
```

See [Using multiple profiles](#using-multiple-profiles) for instructions on how to set authenticate and use more than one profile with the Algorithmia CLI tool.

## Usage

To call an algorithm from the CLI, use the command syntax: `algo run`, followed by the algorithm’s username and algorithm name, the data options, and finally the input. Here is a basic example calling the [Factor algorithm](https://algorithmia.com/algorithms/kenny/Factor):

```text
$ algo run kenny/factor -d 19635
[3,5,7,11,17]
```

Run `algo run --help` to see more command options or view the following [Options](#options) section.

### Options

#### Input Data Options
The Algorithmia CLI supports JSON, text, and binary data, as well as an option to auto-detect the data type.

| Option Flag               | Description |
| :------------             | :--------------- |
| -d, --data <data>         | If the data parses as JSON, assume JSON, else if the data is valid UTF-8, assume text, else assume binary |
| -D, --data-file <file>    | Same as --data, but the input data is read from a file |

You may also explictly specify the input type as text (`-t`/`-T`), json (`-j`/`-J`), or binary (`-b`/`-B`) instead of using the auto-detection (`-d`/`-D`).

#### Output Options

The algorithm result is printed to STDOUT by defauft. Additional notices may be printed to STDERR. If you'd like to output the result to a file, use the output option flag followed by a filename:

```text
$ algo run kenny/factor -d 17 --output results.txt
```

| Option Flag     | Description |
| :------------   |:--------------- |
| --debug         | Print algorithm's STDOUT (author-only) |
| -o, --output <file> |  Print result to a file |

#### Other Options

| Option Flag     | Description |
| :------------   |:--------------- |
| --timeout <seconds> | Sets algorithm timeout

#### Examples:

```text
$ algo run kenny/factor/0.1.0 -d '79'                   Run algorithm with specified version & data input
$ algo run anowell/Dijkstra -D routes.json              Run algorithm with file input
$ algo run anowell/Dijkstra -D - < routes.json          Same as above but using STDIN
$ algo run opencv/SmartThumbnail -D in.png -o out.png   Runs algorithm with binary files as input
$ algo run kenny/factor -d 17 --timeout 2               Runs algorithm with a timeout of 2 seconds
```


## The Algorithmia Data API

Use the Algorithmia CLI to interact with the Algorithmia Data API. You can use the CLI to create and manage your data directories.

**Data commands include:**

| Command   | Description |
| :------------   |:--------------- |
| ls |  List contents of a data directory |
| mkdir | Create a data directory |
| rmdir | Delete a data directory |
| rm | Remove a file from a data directory |
| cp | Copy file(s) to or from a data directory |
| cat | Concatenate & print file(s) in a directory |

### Examples of the Algorithmia Data API usage:

Create a data directory:
```text
$ algo mkdir .my/cuteAnimals

Created directory data://.my/cuteAnimals
```

Copy a file from your local directory to the new data directory:

```text
$ algo cp chubby_kittens.jpg data://.my/cuteAnimals

Uploaded data://.my/cuteAnimals/chubby_kittens.jpg
```

## Using multiple profiles

### Add additional profiles

With the Algorithmia CLI, you can configure multiple custom profiles to use. To add a new profile, simply specify a profile to `algo auth` follow the same interactive prompt.

```text
algo auth --profile second_user
Configuring authentication for profile: 'second_user'
Enter API Endpoint [https://api.algorithmia.com]:
Enter API Key:
(optional) enter path to custom CA certificate:
```

Now you may use `algo ls --profile second_user` to list files in your `second_user` account. For more information, see the auth command help with `algo auth --help`.

### Using profiles in commands

When running commands, the Algorithmia CLI will use the default profile unless otherwise specified with the `--profile <profile>` option. See the following example:

```text
$ algo run kenny/factor -d 17 --profile second_user
[17]
```



# Running tests

Make sure you have `numpy` installed before running `datafile_test.py`
```bash
export ALGORITHMIA_API_KEY={{Your API key here}}
cd Test
python acl_test.py
python algo_test.py
python datadirectorytest.py
python datafile_test.py
python utiltest.py
```
