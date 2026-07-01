"""Compiled regular expressions shared across modules."""

import re
from spectroplot.global_constants import RE_SPECTRUM_ROOT_PATTERN

RE_SPECTRUM_ROOT = re.compile(RE_SPECTRUM_ROOT_PATTERN)
