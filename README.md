
# ML Project February 2023

This repository contains the code to setup the final evaluation of the course "[Machine Learning: Project](https://onderwijsaanbod.kuleuven.be/syllabi/e/H0T25AE.htm)" (KU Leuven, Faculty of Engineering, Department of Computer Science, [DTAI Section](https://dtai.cs.kuleuven.be)).

## Use on departmental computers

The departmental computers will be used to run a tournament and submit your implementation (see detailed instructions below). You can also use these computers to train your agents. A tutorial to connect remotely via SSH can be found [here](ssh.md) and additional info is available on [the departmental web pages](https://system.cs.kuleuven.be/cs/system/wegwijs/computerklas/index-E.shtml).

You will see a personal directory in:

```
/cw/lvs/NoCsBack/vakken/ac2223/H0T25A/ml-project
```

There is an upper limit of 50MB on the disk space that you can use. Remote (ssh) users are also limited to 2GB of RAM.

OpenSpiel and other packages that you can use are pre-installed in a virtual environment, which can be activated using:

```
source /cw/lvs/NoCsBack/vakken/ac2223/H0T25A/ml-project/venv/bin/activate
```

Since this virtual environment will be used to run the tournament, you should avoid language features that are not compatible with the installed Python version (3.10.6) or use packages that are not installed. All of OpenSpiel's [required](https://gitlab.kuleuven.be/dtai/courses/machine-learning-project/open_spiel/-/blob/dots_and_boxes/requirements.txt) and [optional](https://gitlab.kuleuven.be/dtai/courses/machine-learning-project/open_spiel/-/blob/dots_and_boxes/open_spiel/scripts/python_extra_deps.sh) dependencies are currently installed.

## Local installation

This section describes how get started with using Dots and Boxes in OpenSpiel.

First, download [our custom branch of OpenSpiel](https://gitlab.kuleuven.be/dtai/courses/machine-learning-project/open_spiel/-/tree/dots_and_boxes).

```
git clone -b dots_and_boxes https://gitlab.kuleuven.be/dtai/courses/machine-learning-project/open_spiel.git
```

Next, install from source as described in [OpenSpiel's documentation](https://openspiel.readthedocs.io/en/latest/install.html#installation-from-source). Don't forget to update your `PYTHONPATH`, reload the shell if necessary, and activate the virtual environment.
To make sure everything works, you can try to execute the example script:

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

If you prefer to program in C++, you can also use OpenSpiel's C++ API. Although, you will still have to write a Python wrapper to be able to participate in the tournament. To compile C++ code on the departmental computers you can use the g++ compiler.


## Submission using the Departmental Computers

To submit your agent, a copy of you code and agent needs to be available on the departmental computers in a directory assigned to you (only your own code, openspiel and other libraries are provided). Also the code to train your agent should be included.

The departmental computers have openspiel and its dependencies installed such that you can verify that your agent works. During the semester the tournament script will be run to play games between the (preliminary) agents that are already available. A tentative ranking will be shared.


## FAQ

### Installation cannot find tensorflow

Tensorflow is only compatible with Python 3.7--3.10.

On macOS you can use an older version by running these commands before the install script:

```
brew install python@3.10  # if using homebrew
virtualenv -p /usr/local/opt/python@3.10/bin/python3 venv
. ./venv/bin/activate
```

### Module absl not found

Install the required packages (in the virtual environment).

```
pip install -r requirements.txt
```

### openspiel or pyspiel not found

First, check if the `pyspiel` module is available in `build/python`. If it's absent compilation failed. Try compiling again.

Second, make sure the modules can be found by Python by setting the `PYTHONPATH` environment variable:

```
export PYTHONPATH=.:./build/python:$PYTHONPATH
```

If you encounter this error on the departmental computers, make sure to activate the virtual environment (see above).

### Compilation fails on 'Return statement with no value'

Most compilers will allow an empty return statement, but some do not.

```
open_spiel/open_spiel/higc/referee_test.cc:229:47: error: return-statement with no value, in function returning ‘int’ [-fpermissive]
  229 |   if (absl::GetFlag(FLAGS_run_only_blocking)) return;
```

You can easily fix this by replacing `return;` with `return 0;` in the source code.
