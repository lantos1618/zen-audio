# zen-audio

Audio analysis implemented in Zen, independent of the macOS window toolkit.
The only native calls are `sin`, `cos`, and `sqrt` from `math.h`.

Register this source library in the app's `build.zen`:

```zen
audio = b.lib("audio", {
    src: Path("../zen-audio/src/audio.zen"), libs: ["m"], paths: [],
}).try();
```

Include `audio` in the executable's dependencies, then import
`analyze, bands = audio`.

`analyze(samples, real, imaginary, magnitudes, count)` uses caller-owned
`Ptr<f64>` buffers. Input and the two scratch buffers have `count` elements;
output has `count / 2 + 1`. All buffers must be distinct and sufficiently large.
The function allocates nothing and leaves input unchanged. It returns false
for null pointers or a count outside the power-of-two range 4–1048576.

The iterative radix-2 FFT applies a periodic Hann window. Magnitudes report
one-sided sinusoid peak amplitude normalized by the window's coherent gain;
DC and Nyquist are not doubled. A unit-amplitude, bin-centered sine away from
the endpoints has magnitude 1 at its bin and 0.5 in each adjacent bin. These
are amplitude values, not power spectral density or decibels. Sample rate is
external: frequency at bin k is `k * sample_rate / count`.

`bands(magnitudes, bins, output, count)` groups non-DC bins into equal-width
frequency bands, reporting each band's peak amplitude. Input/output must not
overlap. It allocates nothing and returns false for invalid sizes or pointers.

Run the standalone sine, silence, DC, Nyquist, window, and invalid-size checks:

```sh
ZEN_STD=../zen/src ../zen/zen build tests/spectrum
./build/spectrum-test
```

`encode_wav(a, samples: Ptr<f32>, count: usize, rate: u32)` returns an owned
binary `String` or `WavEncodeError` (`WavError | AllocError`). It writes mono
IEEE float WAV with `fmt` extension and `fact` chunks. Native little-endian
sample bytes are preserved, including values outside [-1,1]; big-endian hosts,
invalid rates/sizes, and null nonempty sample arrays are rejected. The caller
can save `wav.view()` through `env.fs.write`. This does not resample audio.

Build `tests/wav`, then run `python3 tests/wav/check.py` to independently decode
the header, chunk sizes, sample rate, and exact float samples.
