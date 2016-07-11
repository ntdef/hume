"""
TODO: Potentially use ONBUILD directive for training?
http://container42.com/2014/02/06/docker-quicktip-3-onbuild/
"""
import json
from subprocess import Popen
from subprocess import check_output
from subprocess import check_call
from subprocess import PIPE


class Container:
    def __init__(self, image, memory_limit_gb=4.0, wait_for_close=False):
        """
        Parameters
        ----------
        image: str
            The docker image or repository to use. Can be tagged or untagged.
               Ex. "ubuntu" or "ubuntu:latest" or "registry.dose.com/ubuntu:latest"
        wait_for_close : bool
            Whether to block for the container to finish closing or simply
            issue an aysynchronous stop without waiting for reply. Note that
            if `False`, stopping the container will fail silently.
        memory_limit_gb : float
            Limit the amount of memory the container may use in Gigabytes.
            Truncates to nearest byte.
        """
        self.image = image
        self.repo, tag, _ = parse_repository_tag(self.image)
        self.tag = tag if tag else "latest"
        self.memory_limit_bytes = int(memory_limit_gb * 1e9)
        self._wait_for_close = wait_for_close

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def run(self, cmd):
        """Just like 'docker run CMD'.

        This is a generator that yields lines of container output.
        """
        exe = ["docker", "run", self.image]
        exe += [c for c in cmd] if hasattr(cmd, "__iter__") else [cmd]
        p = Popen(exe, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        p.wait()
        if p.returncode:
            print("Return code: {}".format(p.returncode))
            raise Exception(err)
        return out


# Shamelessly copied off of docker/compose
# All credit to those guys
# See source here https://github.com/docker/compose/blob/master/compose/service.py#L859
def parse_repository_tag(repo_path):
    """Splits image identification into base image path, tag/digest
    and it's separator.
    Example:
    >>> parse_repository_tag('user/repo@sha256:digest')
    ('user/repo', 'sha256:digest', '@')
    >>> parse_repository_tag('user/repo:v1')
    ('user/repo', 'v1', ':')
    """
    tag_separator = ":"
    digest_separator = "@"

    if digest_separator in repo_path:
        repo, tag = repo_path.rsplit(digest_separator, 1)
        return repo, tag, digest_separator

    repo, tag = repo_path, ""
    if tag_separator in repo_path:
        repo, tag = repo_path.rsplit(tag_separator, 1)
        if "/" in tag:
            repo, tag = repo_path, ""

    return repo, tag, tag_separator
