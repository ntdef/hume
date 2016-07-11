import json
import sys
import os
import contextlib
from subprocess import Popen
from subprocess import check_output
from subprocess import PIPE
from toolz import first, filter, last

from .container import Container
from .utils import indent
from .utils import TemporaryDirectory

@contextlib.contextmanager
def cd(path):
    """A context manager which changes the working directory to the given
    path, and then changes it back to its previous value on exit.
    """
    prev_cwd = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(prev_cwd)


class Hume:
    def __init__(self, image, params=None):
        self._params = params
        self.set_container(image)

    def set_container(self, image):
        self.image = image
        self._container = Container(image)

    @classmethod
    def build(cls, tag, path=".", dockerfile=None, verbose=False):
        """Transform a plain dockerfile into a Humefile, with
        on-build instructions which will create a model.
        """
        with cd(path):
            dockerfile = dockerfile or "./Dockerfile"
            try:
                with open(dockerfile, "r") as f:
                        dockerfile_str = f.read()
            except Exception as e:
                dockerfile_str = dockerfile
            humefile = to_humefile(dockerfile_str)
            if verbose:
                print("New Humefile:")
                print(indent(humefile, "@@ "))
            with open("./Humefile", "w+") as f:
                f.write(humefile)
            cmd = ["docker", "build", "-t", tag, "-f", "Humefile", "."]
            out = check_output(cmd).decode("utf-8")
            if verbose:
                print("Sending to `docker build`...")
                print(indent(out, "  "))
        return Hume(tag)

    def _fit_docker_cmd(self, image, build_args={}, path="."):
        cmd = ["docker", "build", "-t", image]
        for i,j in build_args.iteritems():
            cmd += ["--build-arg", "{}={}".format(i,j)]
        cmd += [path]
        return cmd

    def fit(self, data, target=None, params=None, image=None, tag="fitted", inplace=True, verbose=True):
        """
        Parameters
        ----------
        data : file-like object or str
            Either a file object or a url string that will provide the data for
            fitting in a csv format.
        target : str
            The label of the target to fit with.
        params : dict
            A dictionary of model parameters.
        image : str
            Override the image to fit with.
        tag : str
            Set the output tag. Defaults to `<image>:fitted`
        inplace : bool
            Swap out underlying image with fitted version. By default `True`,
            mirroring `sklearn`'s behavior.
        verbose : bool
            Show verbose output (default: True)

        Return
        ------
        self
        """
        image       = image or self.image
        new_image   = "{}:{}".format(image, tag)
        params      = params if params else self._params
        params_dump = json.dumps(params or "{}")
        build_args  = {"TRAIN_PARAMS": params_dump}
        csv_        = data.read()
        if target:
            build_args['TARGET_LABEL'] = target
        with TemporaryDirectory() as tempdir:
            if verbose:
                print("Creating build context for Docker image at {}".format(tempdir))
            with open("traindata.csv", "w+") as f:
                f.write(csv_)
                build_args["TRAIN_WITH"] = f.name
            with open("Dockerfile", "w+") as dckr:
                dckr.write("FROM {}".format(self.image))
            p = Popen(self._fit_docker_cmd(new_image, build_args), stdout=PIPE, stderr=PIPE)
            out, err = p.communicate()
            p.wait()
        if inplace:
            self.set_container(new_image)
        if verbose:
            print(out)
            print(err)
        return self

    def params(self):
        cmd = ["docker", "run", "--entrypoint", "/bin/sh", self.image, "-c", 'echo "$TRAIN_PARAMS"']
        return json.loads(check_output(cmd).strip() or "{}")

    #TODO: This is going to be tricky...
    def set_param(self, param, value):
        raise NotImplementedError

    def get_param(self, param):
        return self.params()[param]

    def predict(self, sample):
        "Predict with the container"
        cmd = ["docker", "run", "-i", self.image, "predict"]
        if hasattr(sample, "read"):
            return check_output(cmd, stdin=sample)
        elif isinstance(sample, basestring):
            p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            out, err = p.communicate(input=bytes(sample))
            if err:
                raise Exception(err)
            p.wait()
            return out
        else:
            raise NotImplementedError
        #TODO: Delegate the above code to self._container / a docker module
        # return self._container.run(["predict", out])


def entrypoint(dockerfile):
    "Return the entrypoint, if declared"
    f = dockerfile.split("\n")[::-1]  # reverse the lines
    try:
        entry_line = first(filter(lambda x: "ENTRYPOINT" in x, f))
    except StopIteration as e:
        # No ENTRYPOINT line was found
        return None
    else:
        res = last(entry_line.partition("ENTRYPOINT")).strip()
        try:
            return json.loads(res)
        except:
            return res.split()
        return None

def fitline(entry, fit_cmd):
    entry += [fit_cmd]
    run_args = ['{}'.format(arg) for arg in entry]
    return "ONBUILD RUN {}".format(" ".join(run_args))

def to_humefile(dockerfile, entry=None):
    # Get the entrypoint (if any) to know what we need to pass
    # to the ONBUILD RUN line.
    entry = entry or entrypoint(dockerfile)
    if not entry:
        raise Exception("You must provide an entrypoint.")
    out = dockerfile.split("\n")
    out += [
        "#<<<HUMEDOC",
        "ONBUILD RUN mkdir /opt/hume",

        # Data
        "ONBUILD ARG TRAIN_WITH",
        "ONBUILD ENV TRAIN_WITH ${TRAIN_WITH}",
        "ONBUILD ENV HUME_TRAIN_DATA /opt/hume/data",
        "ONBUILD COPY ${TRAIN_WITH} $HUME_TRAIN_DATA",

        # Parameters
        "ONBUILD ARG TRAIN_PARAMS=",
        'ONBUILD ENV TRAIN_PARAMS "${TRAIN_PARAMS}"',
        "ONBUILD ENV HUME_PARAMS_FILE /opt/hume/params",
        "ONBUILD RUN echo $TRAIN_PARAMS",
        'ONBUILD RUN echo $TRAIN_PARAMS > $HUME_PARAMS_FILE',

        # Target label
        "ONBUILD ARG TARGET_LABEL=target",
        "ONBUILD ENV HUME_TARGET_LABEL ${TARGET_LABEL}",
        fitline(entry, 'fit'),
        "#HUMEDOC\n"
    ]
    return "\n".join(out)

if __name__ == "__main__":
    main()

