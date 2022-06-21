
# Built-In Python
import shutil
import uuid
from functools import wraps
import inspect
from pathlib import Path

# XdMind
from xd_pytools.decoratorBase import DecoratorBase


class _UseTmpDir(DecoratorBase):
    def __init__(self, fget, *args, delete=True, **kwargs):
        super().__init__(fget, *args, **kwargs)

        self.delete = delete

        if 'tmpDir' in self.params:
            self.defaultTmpDir = self.params.get('tmpDir').default
        else:
            raise Exception(f"{self.fget} must include the parameter 'tmpDir' to be used with UseTmpDir")

    def decorator(self, instance, *args, **kwargs):
        if self.fget:
            DELETE_DIRS = []

            # We always create a sub-directory of the given tmpDir
            # This way, we know it is safe to delete this dir after running self.fget

            parent_dir = Path(kwargs.get('tmpDir') or './tmp')
            if not parent_dir.exists():
                parent_dir.mkdir(parents=True)
                DELETE_DIRS.append(parent_dir)  # If we make the dir, we can delete it
            tmpDir = parent_dir.joinpath(f'tmp_{uuid.uuid4()}')
            if not tmpDir.exists():
                tmpDir.mkdir(parents=True)
                DELETE_DIRS.append(tmpDir)  # If we make the dir, we can delete it

            # Modify tmpDir so we use this new, one-level-deeper dir which is safe to delete
            kwargs['tmpDir'] = str(tmpDir)

            try:
                res = self.fget(instance, *args, **kwargs)
            except:
                raise
            finally:
                if DELETE_DIRS and self.delete:
                    for d in DELETE_DIRS:
                        if d.exists():
                            shutil.rmtree(str(d))
            return res
        else:
            raise Exception(f"No fget")


def UseTmpDir(_function=None, delete=True):
    """ We wrap the class above so it can be used either with or without arguments"""
    if _function:
        return _UseTmpDir(_function)
    else:
        def decoratorWrapper(_function):
            return _UseTmpDir(_function, delete=delete)

        return decoratorWrapper