# lightfx
`lightfx` is a rgb light strip controller for raspberry pi (mainly), made to be extensible and hackable. 
This is achieved by providing a way to load effects as python modules and by offering a limited python shell to set ad-hoc effects.

## How to setup
The easiest way to setup `lightfx` on an raspberry pi with a raspberry pi os image is by cloning the project in `/opt`:
```sh
sudo git clone https://github.com/alexge50/lightfx /opt/lightfx
sudo chown -R pi /opt/lightfx
sudo pip3 install -r /opt/lightfx/requirements.txt
```

The only system requirement is `pigpio`, which needs to be installed and enabled.
Afterwards, the service file can be loaded:
```sh
sudo systemctl enable --now pigpiod # enabling pigpio daemon
sudo systemctl link /opt/lightfx/systemd/lightfxd.service
sudo systemctl enable --now lightfxd
```

The config file that will be used is placed under `config/config.py`, and the path to the file is supplied via cli arguments. In order to change the config file, the service file must be changed or another one must be made (to make pulling changes easier).

## The config file
The config file is a python file which is imported and executed:
```python
from sinks.pigpio import PiSink
from controllers.shellsocket import ShellSocket


EFFECTS = [ # additional paths to .py files that contain effects
]


SINKS = [ # sinks are the outputs
    PiSink((23, 24, 25)) 
]

CONTROLLERS = [ # controllers are the ones that expose an interface to control the lightfx daemon
    ShellSocket() # ShellSocket is the default controller that exposes a socket which the cli tool use to provide the functionality to change the effects and the option, but also a limited python shell
]

DEFAULT_EFFECT = 'Solid'

FRAME_TIME = 10  # the time slept per frame, in MS - to allow the controllers to do their job
```

## The cli tool
The cli tool `lightfx.py` is the main way to control the daemon, as of now. 
```sh
$ python3 lightfx.py effects # outputs the current effect
$ python3 lightfx.py effects --list # outputs a list of available effects
$ python3 lightfx.py effects Name # changes the effect to `Name`
```

The effects have two ways of taking options - either they take a standard python type (lists, dicts, ints, strings), 
or they take a namedtuple type. 

```sh
$ python3 lightfx.py options # prints the current options value
$ python3 lightfx.py options "(0, 0, 0)" # changes the effects options to `(0, 0, 0)`
```

If the required effect options is a namedtuple type, the options are changed per field:
```sh
$ python3 lightfx.py options field1 "(0, 0, 0)" field2 "(0, 0, 0)"
```

The tool provides a limited python shell, which can be used for ad-hoc control, and this tool is invoked with `python3 lightfx.py shell`:
```python
$ python3 lightfx.py shell
>>> await context.state()
State(options=SolidOptions(color=(255, 0, 255)), current_effect=<solid.Solid object at 0x75f1ddd0>, delta_time=17.708251953125, effects=['Blink', 'Lerp', 'Solid', 'BlinkRandom'])

>>> a = 1

>>> a
1

>>>
```