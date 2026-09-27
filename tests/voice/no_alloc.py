#!/usr/bin/env python3
"""Guard generated allocation calls once voice mapping starts; prove the guard."""
from pathlib import Path
import re
import subprocess
import tempfile

source = (Path(__file__).parent / "build/.zen/voice/program.c").read_text()
pattern = r"(static bool [^\n]*voice_bands[^\n]*\{\n)"
assert len(re.findall(pattern, source)) == 1
prefix = '''#include <stdlib.h>
static int voice_allocation_guard;
static void *voice_malloc(size_t n) { if (voice_allocation_guard) abort(); return malloc(n); }
static void *voice_calloc(size_t n, size_t m) { if (voice_allocation_guard) abort(); return calloc(n, m); }
static void *voice_realloc(void *p, size_t n) { if (voice_allocation_guard) abort(); return realloc(p, n); }
#define malloc voice_malloc
#define calloc voice_calloc
#define realloc voice_realloc
'''
with tempfile.TemporaryDirectory(prefix="zen-voice-noalloc-") as temporary:
    root = Path(temporary)
    for control in (False, True):
        injection = "    voice_allocation_guard = 1;\n"
        if control:
            injection += "    (void)malloc(1);\n"
        instrumented = prefix + re.sub(pattern, lambda m: m.group(1) + injection, source)
        path = root / "probe.c"
        path.write_text(instrumented)
        binary = root / "probe"
        subprocess.run(["cc", "-std=c99", "-Wno-parentheses-equality", str(path), "-lm", "-o", str(binary)], check=True)
        result = subprocess.run([str(binary)], capture_output=True, text=True)
        assert (result.returncode != 0) == control, (control, result.returncode, result.stdout, result.stderr)
print("Voice mapping/smoothing allocation guard passed; injected-allocation control failed as expected")
