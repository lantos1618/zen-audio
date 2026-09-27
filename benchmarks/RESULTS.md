# Measured baseline

1024-point FFT → 32 voice bands → smoothing, 16 kHz mixed 1/3 kHz input; caller-owned f64 buffers, fixed 1/60-second smoothing step.

Measured 2026-09-27T05:09:50.334185+00:00 on Apple M2 Pro (arm64).
macOS-26.6.2-arm64-arm-64bit

Compiler: `/Users/lyndon/zen-dev/zen/zen`; SHA-256 `5688b03fceaf54fa1a9cb675c25260e1402c47247e9996ba7c51122aa676a285`.
Library SHA-256: `c379455655c97ae139cd8a873d16cbe34b361b528054251e19e7bbb0f44cc5bd`.
Apple clang version 17.0.0 (clang-1700.6.4.2) / Target: arm64-apple-darwin25.6.0 / Thread model: posix / InstalledDir: /Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin

| CFLAGS optimization | Samples | Median µs/iteration | p95 µs/iteration | Median of 16.67 ms frame budget |
|---|---:|---:|---:|---:|
| -O0 | 93 | 126.185 | 137.909 | 0.757% |
| -O2 | 93 | 16.018 | 17.340 | 0.096% |

Background workload: Existing user apps remained running; app builds and native inference benchmarks were paused during this rerun.

Each sample is a 1000-iteration batch mean, not a single-call latency. Each of 3 processes warms 1000 iterations, then reports 31 batches. p95 is nearest-rank over the combined batch means.
Timed sections allocate no buffers and print only after each batch. A checksum and validity checks keep results observable.
The live app was not stopped. These measurements are from a shared desktop and are not a real-time guarantee. They exclude device capture, GPU presentation, model inference, actor transport, and end-to-end UI latency.

Reproduce: `python3 benchmarks/run.py --zen ../zen/zen`.
Exact compiler argv, raw batches, metadata, and JSON results are in ignored `build/benchmarks/`.
