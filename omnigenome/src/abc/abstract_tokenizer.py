# -*- coding: utf-8 -*-
# file: tokenizer_wrapper.py
# time: 18:37 06/04/2024
# author: YANG, HENG <hy345@exeter.ac.uk> (杨恒)
# github: https://github.com/yangheng95
# huggingface: https://huggingface.co/yangheng
# google scholar: https://scholar.google.com/citations?user=NPq5a_0AAAAJ&hl=en
# Copyright (C) 2019-2024. All Rights Reserved.

from transformers import AutoTokenizer

from ..misc.utils import env_meta_info


class OmniGenomeTokenizer:
    def __init__(self, base_tokenizer=None, max_length=None, **kwargs):
        super().__init__(**kwargs)

        self.metadata = env_meta_info()

        self.base_tokenizer = base_tokenizer
        self.max_length = max_length

        for key, value in kwargs.items():
            self.metadata[key] = value

        self.u2t = kwargs.get("u2t", False)
        self.t2u = kwargs.get("t2u", False)
        self.add_whitespace = kwargs.get("add_whitespace", False)


    @staticmethod
    def from_pretrained(model_name_or_path, **kwargs):
        self = OmniGenomeTokenizer(
            AutoTokenizer.from_pretrained(model_name_or_path, **kwargs)
        )
        return self

    def save_pretrained(self, save_directory):
        self.base_tokenizer.save_pretrained(save_directory)

    def __call__(self, *args, **kwargs):
        padding = kwargs.pop("padding", True)
        truncation = kwargs.pop("truncation", True)
        max_length = kwargs.pop("max_length", self.max_length if self.max_length else 512)
        return_tensor = kwargs.pop("return_tensors", "pt")
        return self.base_tokenizer(
            padding=padding,
            truncation=truncation,
            max_length=max_length,
            return_tensors=return_tensor,
            *args,
            **kwargs
        )

    def tokenize(self, sequence, **kwargs):
        raise NotImplementedError(
            "The tokenize() function should be adapted for different models,"
            " please implement it for your model."
        )

    def encode(self, sequence, **kwargs):
        raise NotImplementedError(
            "The encode() function should be adapted for different models,"
            " please implement it for your model."
        )

    def decode(self, sequence, **kwargs):
        raise NotImplementedError(
            "The decode() function should be adapted for different models,"
            " please implement it for your model."
        )
