"""Hume -- A Cli

Usage:
  hume [options] <command> [<args>...]
  hume --version

Commands:
  build   Build the ml model
  fit     Fit the model
  pedict  Predict with the model
  params  View and set model parameters

Options:
  -h, --help  Print this help message and exit.
  --version   Show version and exit.

"""
from __future__ import print_function
import json
import yaml
import csv
import os
import sys
from textwrap import dedent
from .hume import Hume
from docopt import docopt
from pkg_resources import get_distribution

__version__ = get_distribution('hume').version


def build(argv):
    """
    Usage: hume build [options] (-t tag | <tag>) <path>

    Options:
      -h, --help        Print this help message and exit.
      -f, --dockerfile  The Dockerfile to use.
      -t, --tag         The tag to use.
      -q, --quiet       Build quietly.
    """
    options = docopt(dedent(build.__doc__), argv=argv)
    path, dockerfile = options['<path>'], options.get('<dockerfile>')
    tag = options['<tag>']
    verbose = not bool(options['--quiet'])
    Hume.build(path=path, dockerfile=dockerfile, tag=tag, verbose=verbose)

def fit(argv):
    """
    Usage: hume fit [options] <image> <data>

    Options:
      -h, --help                    Print this help message and exit.
      -T <label>, --target <label>  The target label to train with.
      -p, --params                  Path to yaml file with parameters.
    """
    options = docopt(dedent(fit.__doc__), argv=argv)
    image, data = options['<image>'], options['<data>']
    if data == "-":
        data = sys.stdin

    params = options['--params']
    if not params:
        with open("./params.yml") as f:
            params = yaml.load(f)
    else:
        with open(params) as f:
            params = yaml.load(f)
    Hume(image, params=params).fit(data, target=options['--target'])

#TODO: Pass filelike to hume.predict (stdin or file)
def predict(argv):
    """
    Usage: hume predict [options] <image> [<input>]

    Options:
      -h, --help  Print this help message and exit.

    Predict using a model image on data from a file or stdin.
    """
    options = docopt(dedent(predict.__doc__), argv=argv)
    image, input = options['<image>'], options['<input>']
    if input == "-":
        file_ = sys.stdin
    else:
        file_ = open(input)
    print(Hume(image).predict(file_))

def params(argv):
    """
    Usage: hume params [options] <image>

    Options:
      -h, --help  Print this help message.

    Return the parameters used to fit the model. By default returns parameters
    as JSON.
    """
    options = docopt(dedent(params.__doc__), argv=argv)
    image = options['<image>']
    print(json.dumps(Hume(image).params(), indent=4, sort_keys=True))

def main():
    args = docopt(__doc__, options_first=True)
    cmd, cmd_args = args['<command>'], args['<args>']
    if args['--version']:
        print(__version__)

    argv = [cmd] + cmd_args

    if cmd == "build":
        build(argv)
    elif cmd == "fit":
        fit(argv)
    elif cmd == "predict":
        predict(argv)
    elif cmd == "params":
        params(argv)
    else:
        pass

if __name__ == "__main__":
    main()
