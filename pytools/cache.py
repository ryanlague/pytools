
import json
import pickle
from functools import wraps
from pathlib import Path
import logging

import pandas as pd


class CacheTypeError(Exception):
    """A custom exception so we can catch it in @cachePathOption"""
    def __init__(self, *args):
        super().__init__(*args)


FILE_TYPES = {'pickle': {'ext': '.pickle'}, 'json': {'ext': '.json'}, 'df': {'ext': '.pickle'}}


def loadCache(filepath, fileType, deleteIfCorrupt=True):
    filepath = str(filepath)
    obj = None
    try:
        if 'pickle' in fileType:
            with open(filepath, 'rb') as f:
                obj = pickle.load(f)
        elif 'json' in fileType:
            with open(filepath, 'r') as f:
                obj = json.load(f)
        elif 'df' in fileType:
            obj = pd.read_pickle(filepath)
        else:
            raise CacheTypeError(f"Unknown fileType for cache: {fileType}")
    except CacheTypeError as e:
        raise e
    except Exception as e:
        if deleteIfCorrupt:
            Path(filepath).unlink(missing_ok=True)
            logging.error(f"Error opening {filepath}. Deleted it.")
        else:
            raise e
    return obj


def saveCache(obj, filepath, fileType):
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath = str(filepath)
    if fileType == 'pickle':
        with open(filepath, 'wb') as f:
            pickle.dump(obj, f)
    elif fileType == 'json':
        with open(filepath, 'w') as f:
            json.dump(obj, f, indent=4)
    elif fileType == 'df':
        filepath = str(Path(filepath).with_suffix('.pickle'))
        pd.to_pickle(obj, filepath)
    else:
        raise CacheTypeError(f"Unknown fileType for cache: {fileType}")


def CacheDir(cacheType='pickle', alwaysLoadFromDisk=False, deleteIfCorrupt=True, important=False, cacheDir=None, ignoreParams=None):
    """A decorator which caches the return value on disk"""
    cacheType = cacheType.replace('.', '')
    ignoreParams = ignoreParams or []

    def decorator(func):
        @wraps(func)
        def wrapper(instance, *args, **kwargs):
            # cacheDir can be supplied in the the kwargs of the decorated func, 
            # as a property of instance (i.e. instance.cacheDir), 
            # or in the kwargs of the decorator
            # (in that order)
            if 'cacheDir' in kwargs:
                cache_dir = kwargs.pop('cacheDir')
            elif 'cacheDir' in dir(instance):
                cache_dir = instance.cacheDir
            elif cacheDir:
                cache_dir = cacheDir
            else:
                logging.error(f"No cacheDir supplied - so result will not be cached")
                cache_dir = None

            # We can supply a blockCache=True param in the decorator for testing / debug etc.
            if kwargs.get('blockCache'):
                del kwargs['blockCache']
                cache_dir = None

            use_cache = cache_dir is not None
            if use_cache:
                
                # Convert to Path instance
                cache_dir = Path(cache_dir)

                # Build the filepath for the cache
                inst_name = str(instance)
                func_name = f"{func.__module__.split('.')[-1]}_{func.__name__}"

                cache_name = f"{inst_name}_{func_name}"
                if args:
                    args_name = f"args_{'_'.join([str(a) for a in args])}"
                    cache_name = f"{cache_name}_{args_name}"
                if kwargs:
                    kwargs_name = f"kwargs_{'_'.join(f'{str(k)}={str(v)}' for k, v in kwargs.items() if k not in ignoreParams)}"
                    cache_name = f"{cache_name}_{kwargs_name}"

                ext = FILE_TYPES[cacheType]['ext']
                cache_name = cache_name.replace('/', ':')

                # Create a separate folder for all cache files which were the result of this decorator
                if important:
                    cache_dir = cache_dir.joinpath('important')

                cache_path = cache_dir.joinpath(inst_name).joinpath(func_name).joinpath(cache_name).with_suffix(ext)

                MAX_LEN = 260
                if len(cache_path.name) < MAX_LEN:

                    if cache_path.exists():
                        if alwaysLoadFromDisk:
                            res = loadCache(cache_path, fileType=cacheType, deleteIfCorrupt=deleteIfCorrupt)
                        else:
                            if 'decoratorCache' not in dir(instance):
                                instance.decoratorCache = {}
                            if cache_path in instance.decoratorCache:
                                res = instance.decoratorCache[cache_path]
                            else:
                                res = loadCache(cache_path, fileType=cacheType, deleteIfCorrupt=deleteIfCorrupt)
                                instance.decoratorCache[cache_path] = res
                    else:
                        res = func(instance, *args, **kwargs)
                        saveCache(res, cache_path, fileType=cacheType)
                else:
                    logging.error(f"Cache name is too long. could not use cache")
                    res = func(instance, *args, **kwargs)
            else:
                res = func(instance, *args, **kwargs)
            return res
        return wrapper
    return decorator
