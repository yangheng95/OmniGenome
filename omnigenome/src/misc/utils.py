# -*- coding: utf-8 -*-
# file: utils.py
# time: 14:45 06/04/2024
# author: YANG, HENG <hy345@exeter.ac.uk> (杨恒)
# github: https://github.com/yangheng95
# huggingface: https://huggingface.co/yangheng
# google scholar: https://scholar.google.com/citations?user=NPq5a_0AAAAJ&hl=en
# Copyright (C) 2019-2024. All Rights Reserved.
import os
import pickle
import sys
import time


def seed_everything(seed=42):
    import random
    import numpy as np
    import torch

    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.backends.cudnn.deterministic = True


class RNA2StructureCache(dict):
    def __init__(self, cache_file=None, *args, **kwargs):
        import RNA

        self.RNA = RNA
        super().__init__(*args, **kwargs)

        if not cache_file:
            cache_file = "__OMNIGENOME_DATA__/rna2stucture.cache.pkl"

        self.cache_file = cache_file

        if not os.path.exists(os.path.dirname(cache_file)):
            os.makedirs(os.path.dirname(cache_file))

        if not os.path.exists(cache_file):
            self.cache = {}
        else:
            print(f"Loading cache from {cache_file}...")
            with open(cache_file, "rb") as f:
                self.cache = pickle.load(f)

        self.queue_num = 0

    def __getitem__(self, key):
        return self.cache[key]

    def __setitem__(self, key, value):
        self.cache[key] = value

    def __str__(self):
        return str(self.cache)

    def __repr__(self):
        return str(self.cache)

    def fold(self, sequence):
        if sequence in self.cache:
            return self.cache[sequence]
        else:
            self.queue_num += 1
            fold = self.RNA.fold(sequence)
            self.cache[sequence] = fold
            return fold

    def update_cache_file(self, cache_file=None):
        if self.queue_num < 100:
            return

        if cache_file is None:
            cache_file = self.cache_file

        print(f"Updating cache file {cache_file}...")
        with open(self.cache_file, "wb") as f:
            pickle.dump(self.cache, f)


def env_meta_info():
    from torch.version import __version__ as torch_version
    from torch.version import cuda as torch_cuda_version
    from torch.version import git_version
    from transformers import __version__ as transformers_version
    from ... import __version__ as omnigenome_version
    from ... import __name__ as omnigenome_name

    return {
        "library_name": omnigenome_name,
        "omnigenome_version": omnigenome_version,
        "torch_version": f"{torch_version}+cu{torch_cuda_version}+git{git_version}",
        "transformers_version": transformers_version,
    }


def naive_secondary_structure_repair(sequence, structure):
    """
    Repair the secondary structure of a sequence.

    Args:
    - sequence: A string representing the sequence.
    - structure: A string representing the secondary structure.

    Returns:
    - repaired_structure: A string representing the repaired secondary structure.
    """
    repaired_structure = ""
    stack = []
    for i, (s, c) in enumerate(zip(structure, sequence)):
        if s == "(":
            stack.append(i)
        elif s == ")":
            if stack:
                stack.pop()
            else:
                repaired_structure += "."
        else:
            repaired_structure += s
    for i in stack:
        repaired_structure = repaired_structure[:i] + "." + repaired_structure[i + 1 :]
    return repaired_structure


def save_args(config, save_path):
    """
    Save arguments to a file.

    Args:
    - config: A Namespace object containing the arguments.
    - save_path: A string representing the path of the file to be saved.

    Returns:
    None
    """
    f = open(os.path.join(save_path), mode="w", encoding="utf8")
    for arg in config.args:
        if config.args_call_count[arg]:
            f.write("{}: {}\n".format(arg, config.args[arg]))
    f.close()


def print_args(config, logger=None):
    """
    Print the arguments to the console.

    Args:
    - config: A Namespace object containing the arguments.
    - logger: A logger object.

    Returns:
    None
    """
    args = [key for key in sorted(config.args.keys())]
    if logger:
        logger.info(args)
    else:
        fprint(args)


def fprint(*objects, sep=" ", end="\n", file=sys.stdout, flush=False):
    """
    Custom print function that adds a timestamp and the pyabsa version before the printed message.

    Args:
        *objects: Any number of objects to be printed
        sep (str, optional): Separator between objects. Defaults to " ".
        end (str, optional): Ending character after all objects are printed. Defaults to "\n".
        file (io.TextIOWrapper, optional): Text file to write printed output to. Defaults to sys.stdout.
        flush (bool, optional): Whether to flush output buffer after printing. Defaults to False.
    """
    from omnigenome import __version__

    print(
        time.strftime(
            "[%Y-%m-%d %H:%M:%S] ({})".format(__version__),
            time.localtime(time.time()),
        ),
        *objects,
        sep=sep,
        end=end,
        file=file,
        flush=flush,
    )
