import os
import shutil
from tempfile import mkdtemp


def indent(text, prefix, predicate=None):
    """Adds 'prefix' to the beginning of selected lines in 'text'.

    If 'predicate' is provided, 'prefix' will only be added to the lines
    where 'predicate(line)' is True. If 'predicate' is not provided,
    it will default to adding 'prefix' to all non-empty lines that do not
    consist solely of whitespace characters.
    """
    if predicate is None:
        def predicate(line):
            # return line.strip()
            return True

    def prefixed_lines():
        for line in text.splitlines(True):
            yield (prefix + line if predicate(line) else line)
    return "".join(prefixed_lines())


class TemporaryDirectory:
    def __init__(self, debug=False):
        self._debug = debug

    def __enter__(self):
        self.name = mkdtemp()
        self._prevdir = os.getcwd()
        if self._debug:
            print("Created directory at {}".format(self.name))
        os.chdir(self.name)
        return self.name

    def __exit__(self, type, value, traceback):
        if self._debug:
            print("Cleaning up directory at {}".format(self.name))
        try:
            os.chdir(self._prevdir)
            shutil.rmtree(self.name)
        except Exception:
            raise
