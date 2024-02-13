
# ML Project February 2024

This repository contains the code to setup the final evaluation of the course "[Machine Learning: Project](https://onderwijsaanbod.kuleuven.be/syllabi/e/H0T25AE.htm)" (KU Leuven, Faculty of Engineering, Department of Computer Science, [DTAI Section](https://dtai.cs.kuleuven.be)).


## Available files

- `dotsandboxes_agent`: Agent code to expand which will run on the departmental servers
- `example_dotsandboxes.ipynb`: Notebook to illustrate how to play the Dots and Boxes game in OpenSpiel
- `minimax_template.py`: Code you can use to implement minimax for Dots and Boxes
- `tournament.py`: Code that is used on the departmental server to play the tournament
- `websocket_player.py`: Code to wrap your agent to play interactively using the web-based interface


## Use on departmental computers

The departmental computers will be used to run a tournament and submit your implementation (see detailed instructions below). You can also use these computers to train your agents. A tutorial to connect remotely via SSH can be found [here](ssh.md) and additional info is available on [the departmental web pages](https://system.cs.kuleuven.be/cs/system/wegwijs/computerklas/index-E.shtml).

You will see a personal directory in:

```
/cw/lvs/NoCsBack/vakken/H0T25A/ml-project
```

There is an upper limit of 50MB on the disk space that you can use. Remote (ssh) users are also limited to 2GB of RAM.

OpenSpiel (v1.4) and other packages that you can use are pre-installed in a virtual environment, which can be activated using:

```
source /cw/lvs/NoCsBack/vakken/H0T25A/ml-project/venv/bin/activate
```

Since this virtual environment will be used to run the tournament, you should avoid language features that are not compatible with the installed Python version (3.10.12) or use packages that are not installed. All of OpenSpiel's [required](https://github.com/google-deepmind/open_spiel/blob/v1.4/requirements.txt) dependencies are currently installed, as well as `torch==2.2.0` and `tensorflow==2.15.0`.

## Local installation

We make use of the public version of OpenSpiel. See the [documentation](https://openspiel.readthedocs.io/en/latest/) for installation options.


If you have a local install of the repository, you can test the Dots and Boxes game with:

```
python3 python/examples/dotsandboxes_example.py
```

This will run two random players in Dots and Boxes. You can also play yourself on the keyboard by passing flags:

```
python3 python/examples/dotsandboxes_example.py \ 
    --player0=random --player1=human
```


## Tournament

The tournament will be played with agents that are available on the departmental computers. This will allow you to try your agent in the identical environment that is used by the tournament script. For this to work, you have to adhere to the following setup:

- Your agent extends the `Agent` class provided in the file `dotsandboxes_agent/dotsandboxes_agent.py`.
- The tournament code will scrape the directory provided for you on the departmental computers for the `dotsandboxes_agent.py` file and call the `get_agent_for_tournament` method. If multiple matching files are found, a random one will be used.
- Your agent should be ready to play in a few seconds, thus use a pre-trained policy. An agent that is not responding after 10 seconds will forfeit the game.

Make sure you **do not use relative paths** in your implementation to load your trained model, as this will fail when running your agent from a different directory. Best practice is to retrieve the absolute path to the module directory:

```python
package_directory = os.path.dirname(os.path.abspath(__file__))
```

Afterwards, you can load your resources based on this `package_directory`:

```python
model_file = os.path.join(package_directory, 'models', 'mymodel.pckl')
```

If you use Tensorflow you must use the V2 api and cannot use `tf.compat` and `tf.compat.v1` namespaces. Otherwise, this will give problems when playing against other agents in the tournament.

If you prefer to program in C++, you can also use OpenSpiel's C++ API. Although, you will still have to write a Python wrapper to be able to participate in the tournament. To compile C++ code on the departmental computers you can use the `usr/bin/g++-11` compiler.


## Submission using the Departmental Computers

To submit your agent, a copy of your code and agent needs to be available on the departmental computers in a directory assigned to you (only your own code, openspiel and other libraries are provided). Also the code to train your agent should be included.

The departmental computers have openspiel and its dependencies installed such that you can verify that your agent works. During the semester the tournament script will be run to play games between the (preliminary) agents that are already available. A tentative ranking will be shared.


## FAQ

### Installation cannot find tensorflow

Tensorflow is only compatible with Python 3.8--3.11.

On macOS you can use an older version by running these commands before the install script:

```
brew install python@3.10  # if using homebrew
virtualenv -p /usr/local/opt/python@3.10/bin/python3 venv
. ./venv/bin/activate
```

### Tensorflow / PyTorch does not work on Apple Silicon

When using macOS on M1/M2 Apple Silicon, you might need to use the custom packages provided by Apple:

- https://developer.apple.com/metal/pytorch/
- https://developer.apple.com/metal/tensorflow-plugin/


### Module absl not found

Install the required packages (in the virtual environment).

```
pip install -r requirements.txt
```

### openspiel or pyspiel not found

If you encounter this error on the departmental computers, make sure to activate the virtual environment (see above).

If you installed openspiel from source:

First, check if the `pyspiel` module is available in `build/python`. If it's absent compilation failed. Try compiling again.

Second, make sure the modules can be found by Python by setting the `PYTHONPATH` environment variable:

```
export PYTHONPATH=.:./build/python:$PYTHONPATH
```

You can also use `pip install -e` (for those who know what development mode in pip is).

If you have install openspiel using pip:

Check that openspiel is installed in the virtual environment you are using.

### Cannot import OpenSpiel: incompatible architecture

Check that your Python version is compiled for the same architecture as you are compile C++ code. You can check this by running `python3 -c "import platform; print(platform.platform())"` and compare the output to running `arch`.

This can occur on M1/M2 Apple computers when you see: `ImportError: dlopen ... (mach-o file, but is an incompatible architecture (have 'arm64', need 'x86_64')`. This is resolved by forcing the architecture (and potentially reinstalling some libraries): `env /usr/bin/arch -arm64  /bin/zsh --login`.

### Compilation fails on 'Return statement with no value'

Most compilers will allow an empty return statement, but some do not.

```
open_spiel/open_spiel/higc/referee_test.cc:229:47: error: return-statement with no value, in function returning ‘int’ [-fpermissive]
  229 |   if (absl::GetFlag(FLAGS_run_only_blocking)) return;
```

You can easily fix this by replacing `return;` with `return 0;` in the source code.

### Tests fail with ValueError: setting an array element with a sequence

If you see one of the following two errors:

```
ValueError: setting an array element with a sequence. The requested array has an inhomogeneous shape after 2 dimensions. The detected shape was (10, 3) + inhomogeneous part.
ValueError: The history as tensor in the same infoset are different:
```

This is because Numpy became more strict. You can downgrade numpy using `pip install "numpy==1.21.6"` to eliminiate the errors (but it will most likely have no effect on the correctness of the project).

### Dots and boxes game not registered in games list

Things to check:

- Did you install an old version of OpenSpiel version? 
- Check where the files are located that you are using. The example files should be in the same directory as the package you are using. If you have multiple installations these can differ based on your path settings. After all import statements, add:

```
import sys
print(sys.path)  # Check which paths are being search for the OpenSpiel package
print(pyspiel)   # Print the location of the used OpenSpiel package
print(__file__)  # Print the location of the current script being executed
```
