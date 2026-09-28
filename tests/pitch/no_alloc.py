#!/usr/bin/env python3
"""Prove pitch estimation does not allocate; inject allocation as control."""
from pathlib import Path
import re
import subprocess
import tempfile
source = (Path(__file__).parent / 'build/.zen/pitch/program.c').read_text()
pattern = r'static double (\w*8estimate\w*)\(double \* (\w+), double \* (\w+)\) \{'
m = re.search(pattern, source)
assert m, 'Build tests/pitch first'
name, first, second = m.groups()
renamed = source[:m.start()] + source[m.start():].replace(name+'(', name+'_impl(', 1)
prefix = '''#include <stdlib.h>
static int allocation_guard;
static void *checked_malloc(size_t n) { if (allocation_guard) abort(); return malloc(n); }
static void *checked_calloc(size_t n,size_t m) { if (allocation_guard) abort(); return calloc(n,m); }
static void *checked_realloc(void *p,size_t n) { if (allocation_guard) abort(); return realloc(p,n); }
#define malloc checked_malloc
#define calloc checked_calloc
#define realloc checked_realloc
'''
with tempfile.TemporaryDirectory(prefix='zen-pitch-alloc-') as folder:
    root = Path(folder)
    for negative in (False, True):
        injected = 'free(malloc(1));' if negative else ''
        wrapper = f'\nstatic double {name}(double *a,double *b) {{ allocation_guard=1; {injected} double value={name}_impl(a,b); allocation_guard=0; return value; }}\n'
        (root/'probe.c').write_text(prefix + renamed + wrapper)
        subprocess.run(['clang','-O2','-Wno-parentheses-equality',str(root/'probe.c'),'-o',str(root/'probe')],check=True,timeout=60)
        result=subprocess.run([str(root/'probe')],capture_output=True,timeout=15)
        assert (result.returncode != 0) == negative, result.stderr
print('PASS: pitch estimation allocation-free; injected allocation rejected')
