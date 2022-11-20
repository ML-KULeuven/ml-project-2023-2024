
# Using the departmental machines remotely

This document is a guide for using the departmental machines remotely.
You can access the machines with a secure connection through SSH. This
connection can be used for executing commands on the remote machine,
tunneling through a firewall, and transfering files to and from a remote
machine.

## Installing the SSH client

### Unix

Linux, MacOS and other Unix systems usually come with OpenSSH pre-installed.
You can run `ssh -V` in a terminal window to verify this. If OpenSSH is not
installed, you should be able to use your distribution's package manager to
install the `openssh-client` package.

### Windows

On Windows, we recommend [Windows Subsystem for Linux, version
2 (WSL2)](https://docs.microsoft.com/en-us/windows/wsl/) or PuTTy.
[Cygwin](https://www.cygwin.com/) and [MobaXterm3](https://www.mobatek.net/)
are two other options, but they are not covered in this guide.

**WSL2** lets you run a Linux environment (i.e., a Linux terminal) in Windows.
To install WSL on your Windows machine, follow the instructions on
[Microsoft’s pages](https://docs.microsoft.com/en-us/windows/wsl/install).
We recommend using the Ubuntu Linux distribution. Once WSL is installed, you
will have access to a Bash terminal, and the `ssh` and other Linux commands. If
you choose this option, you can follow the Unix instructions in the remainder
of this guide. Instructions on how to access Windows files from the Linux
terminal are available on
[Microsoft’s pages](https://docs.microsoft.com/en-us/windows/wsl/faq#how-do-i-access-my-c--drive-).
You can edit files from the terminal using `nano` or `vim`.

**PuTTY** can be can be downloaded from
<https://www.chiark.greenend.org.uk/∼sgtatham/putty/latest.html>. The PuTTY
package consists of several binaries. We will use PuTTY (the SSH client),
PuTTYgen (the key generator/reformatter), Pageant (the key manager), Plink (the
command line interface to the PuTTY back-end), and PSCP (the scp client for
copying files over the secure network). You can download all the binaries
separately, or get them all in one package. To be able to invoke all the
binaries from the terminal, ensure that the PuTTY installation folder is in
your `$PATH` variable.

## Obtaining a SSH key pair

To connect to the departmental computers, you need a SSH key pair. Password-based
login is disabled. The pair consists of a private key and a public key. The
private key is kept on your computer and should stay secret. The computer that
you want to connect to has a list of authorized public keys. The remote
computer will allow you to connect if it has your public key. You can generate
an SSH key pair through the website
<https://www.cs.kuleuven.be/restricted/ssh/>. Public keys that are generated
this way are automatically distributed on the departmental machines, allowing
you to access them remotely. If this page indicates your account is **not
active**, please send us an email.

After having generated an SSH key pair, download the `id_rsa` private key from
the same web page and store it somewhere safe on your own device (usually
`$HOME/.ssh`). The public `id_rsa.pub` key of the key pair is automatically
distributed on the departmental machines (including `st.cs.kuleuven.be`),
allowing you to access them securely. Note that this might take a day, so **do
this well before the deadline**!

PuTTY needs the private key to be in `.ppk` format. PuTTYgen can
transform your key to the right format by first loading the existing key
and then saving it.

## Configuring SSH and running remote commands

### A simple connection

We can make a connection to a remote machine by opening a terminal and running:

- on Unix:

    ```sh
     # ssh <username>@<remoteMachine> -i <pathToPrivateKey>
     % ssh r0123456@st.cs.kuleuven.be -i path/to/id_rsa
     ```

- on Windows:

    ```sh
     # plink <username>@<remoteMachine> -i <pathToPrivateKey.pkk>
     % plink r0123456@st.cs.kuleuven.be -i path/to/id_rsa.pkk
     ```

If it found your SSH keys, the session will ask you to enter your
**passphrase**. This is the passphrase you entered while creating your keys.
Note that this is not the same as your r-number password. If the session asks
you to enter a **password**, it did not find your ssh key. Logging in with
a password will not work. When in doubt and things do not work as expected, try
using the verbose mode when connecting (`ssh -vvv`).

To avoid typing the key location every time, you can make sure that the
ssh client finds it automatically. On Unix systems, you do this by
placing the public key in the `$HOME/.ssh` directory.

### Using a SSH agent

To avoid having to type the passphrase every time, you can use an SSH agent.
Many Linux distributions (e.g. Ubuntu, Fedora Workstation), and Macs already
have an SSH agent set up, and you can skip this step. However, if you do not
have an SSH agent, you can use `ssh-agent`:

```sh
% eval `ssh - agent -s`
% ssh-add ~/.ssh/id_rsa
```

On Windows, you run:

```sh
% pageant d:path/to/id_rsa.pkk
```

### Configuration

You can avoid typing the whole command all together by making a
configuration. On **Unix** systems, this is the file `.ssh/config` with the
following text:

```
Host pcroom
    User       r0123456
    HostName   st.cs.kuleuven.be
```

You can now connect with

```sh
 % ssh pcroom
```

On **Windows**, you use the graphical interface of PuTTY. You first complete
the configuration by setting:

- Session → Host Name (or IP address) = st.cs.kuleuven.be
- Session → Port = 22
- Connection → Data → Auto-login username = r0123456

Then you save it in the *Session* tab by writing *pcroom* in *Saved
Sessions* and hitting *Save*.

You can now connect with

```sh
 % plink pcroom
 ```

### Getting passed the login node

The `st.cs.kuleuven.be` server is a login node, it is not meant to run
experiments. The machines that you can run experiments on have the
addres `<pcname>.cs.kotnet.kuleuven.be`. The next section points to a
list of available machines. These machines are not immediately reachable
outside the KU Leuven network, you need to go through the login node
first. From the login node, you can reach any other machine again
through ssh. For example:

```sh
 % ssh st.cs.kuleuven.be
 ...
 (st) % ssh aalst.cs.kotnet.kuleuven.be
```

This is possible because your private keys were stored automatically in
`~/.ssh/` on the departmental machines. You can configure the key
agent and configuration file here the same way as on your personal
computer.

#### Proxy

You can immediately get to a departmental machine by setting up a proxy.

On **Unix** systems, this can be done by adding

```
ProxyJump st.cs.kuleuven.be
```

to the configuration file. Here is a complete example:

```
Host aalst
    User           r0123456
    IdentityFile   ~/.ssh/id_rsa
    HostName       aalst.cs.kotnet.kuleuven.be
    ProxyJump      st.cs.kuleuven.be
```

You can now connect with

```sh
 % ssh aalst
 ```

In **Windows** a proxy can be setup through PuTTY as follows:

- Session → Host Name (or IP address) = aalst.cs.kotnet.kuleuven.be
- Session → Port = 22
- Connection → Data → Auto-login username = r0123456
- Connection → Proxy → Proxy type = local
- Connection → Proxy → Proxy hostname = st.cs.kuleuven.be
- Connection → Proxy → Port = 22
- Connection → Proxy → Username = r0123456
- Connection → Proxy → Telnet command, or local
    proxy command = plink %user@%proxyhost nc %host %port

Then you save it in the *Session* tab by writing *aalst* in *Saved
Sessions* and hitting *Save*.

You can now connect with

```sh
% plink aalst
```

## List of available machines

The page <http://mysql.cs.kotnet.kuleuven.be/> gives an overview of the
available departmental machines and their current load. Avoid using a machine
with high-load; it will improve your and the other user's experience.

This page is only accessible from within the KU Leuven network. You can always
use SSH to reach it using an SSH tunnel to the server
`mysql.cs.kotnet.kuleuven.be` at port 80. Set up the tunnel by entering:

- on Unix:

    ```sh
    % ssh -L 8080:mysql.cs.kotnet.kuleuven.be:80 st.cs.kuleuven.be
    ```

- on Windows:

    ```sh
    % plink -L 8080:mysql.cs.kotnet.kuleuven.be:80 st.cs.kuleuven.be
    ```

Now you can reach the website at <http://localhost:8080/>

## Remote copying

Making a remote copy is similar to making a local copy in the Unix
terminal. The command for a local copy is:

```sh
% cp [-r] <source> <destination>
```

where source and destination are paths. The `-r` is an optional flag to
indicate that you also want to copy directories. A remote copy uses
"secure copy" (`scp`) and needs the ssh configuration of the remote
computer. For copying to the remote machine we use

- on Unix:

    ```sh
     % scp [-r] <source> pcroom:<destination>
     ```

- on Windows:

    ```sh
     % pscp [-r] <source> pcroom:<destination>
    ```

For copying from the remote machine we use

- on Unix:

    ```sh
     % scp [-r] pcroom:<source> <destination>
     ```

- on Windows:

    ```sh
    % pscp [-r] pcroom:<source> <destination>
    ```

If you have a proxy configured, you can directly copy to and from the
departmental machines. If not, you need to make an intermediate copy on
the login node.

On Unix machines, you can also use `rsync` instead of `scp`. The usage
is the same, but this command will analyze the difference between the
source and destination and only copy what is necessary, thus being more
efficient.

## Safely running experiments with "screen"

Screen is a useful application for running experiments remotely because
it allows you to:

- Use multiple shell windows from a single SSH session.
- Keep a shell active even through network disruptions.
- Disconnect and re-connect to a shell sessions from multiple locations.
- Run a long running process without maintaining an active shell session.

Starting screen is done by typing:

```sh
% screen
```

This opens a new screen terminal. After hitting Enter, you can start
working like you would in a normal terminal.

There are two ways to leave a screen terminal: terminating and
detaching. The former kills the screen, including processes that it is
running. The latter lets the screen run in the background while you
leave, it can be recovered later. A session can be terminated with
`<Ctrl>-d` or writing `exit`. It becomes detached with `<Ctrl>-a d` or
by disrupting the connection, for example a network failure or shutting
down the computer. Your experiments will thus keep on running, even when
you lose your internet connection.

All the screen commands start with `<Ctrl>-a` and are followed by
another key. These are the most common ones:

- `d` : detach the screen
- `c` : create a new terminal within screen
- `n` : go to the next terminal
- `p` : go to the previous terminal
- `?` : help page about screen commands

You can reattach to a detached screen by running `screen -r`

## Useful directories

**Home directory**: `/home/r0123456/`

In your home directory you can store your personal files. The home
directory is accessible from all the departmental machines but not from
the login node. There is an upper limit on the space that you can use. To
know the limit and your current usage run:

```sh
% quota
```

**Local space**: `/tmp/`

Every machine has local space that you can use. This folder is cleaned
regularly, so do not store anything important here. It is the perfect
place for heavy output of experiments, just make sure to copy it to a
safe place if you need to keep it.

**Course directory**: `/cw/lvs/NoCsBack/vakken/ac2021/H0T25A/ml-project/r0123456`

This folder is your personal space for submitting your implementation. The
folder is accessible from all the departmental machines but not from the login
node. There is an upper limit of 50MB.
