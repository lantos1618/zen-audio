# zen-audio

Audio analysis implemented in Zen, independent of the macOS window toolkit.
Scalar mathematics uses `std.math` (`sin`, `cos`, `sqrt`, and `log10`);
windowing, FFT, frequency mapping, and smoothing are ordinary Zen.

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

For speech displays, use:

```zen
voice_bands, smooth_levels = audio
voice_bands(magnitudes, 513, 16000, targets, 32);
smooth_levels(targets, displayed, 32, elapsed_seconds);
```

`voice_bands(magnitudes: Ptr<f64>, bins: usize, rate: u32,
output: Ptr<f64>, count: usize) bool` groups FFT bins into equal mel intervals
from 80 Hz through 4 kHz. The mel axis uses `log10(1 + frequency / 700)`,
putting more bars in the lower voice range than linear whole-spectrum bands.
A count of 32 works well for 1024 samples at 16 kHz. Bins outside the voice
range and DC are ignored; sparse/empty bands remain zero. The peak amplitude
in each band is converted with `20 * log10(amplitude)`, then mapped from
-65 dBFS to -15 dBFS into a clamped 0–1 display level. This is a visualization
of digital peak amplitude, not calibrated sound pressure or a noise gate.
Silence is zero; -20 dBFS is 0.9; amplitudes at/above -15 dBFS saturate at one.
NaN and negative magnitude inputs do not raise a band.

The input length is the one-sided FFT bin count (`fft_count / 2 + 1`). Valid
sizes are 3–524289 bins, 1–128 bands with at most `bins - 1` bands, and sample
rates 8–192 kHz. Input and output must not overlap. Invalid sizes, rates, or
null pointers return false before writing output.

`smooth_levels(target: Ptr<f64>, state: Ptr<f64>, count: usize,
elapsed: f64) bool` smooths caller-owned display state. Initialize `state` to
zero once. Attack uses 35 ms and release uses 180 ms, with a backward-Euler
coefficient `dt / (tau + dt)`; it accounts for elapsed time but is not an exact
exponential filter. Gaps of one second or longer snap to the latest target.
The count must be 1–128 and elapsed seconds must be finite and nonnegative.
Invalid inputs leave state unchanged. Input levels clamp to 0–1, with NaN
mapped to zero. Identical target/state buffers are allowed; partial overlap is
not. Both voice functions allocate nothing and accept no allocator.

Run the voice tone-placement, dB floor/ceiling, silence, bounds, smoothing,
and generated-allocation checks:

```sh
ZEN_STD=../zen/src ../zen/zen build tests/voice
./build/voice-test
python3 tests/voice/no_alloc.py
```

The allocation check guards generated malloc/calloc/realloc calls once mapping
starts, and verifies its guard with an intentionally injected allocation. It
covers the Zen/compiler allocation path rather than intercepting libc internals.

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
