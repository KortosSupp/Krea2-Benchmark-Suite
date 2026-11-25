# Krea 2 Benchmark Tools — Six-Model Benchmark Suite

Provides the following workflow-specific nodes:
- `AILab_ImageCompare6`: Six-image comparison grid, with model labels and 6x1, 3x2, 2x3 layouts
- `Krea2TimedKSampler`: KSampler node wall time (CUDA-synchronized where available)
- `Krea2VramBefore`, `Krea2VramAfter`: whole-device GPU VRAM snapshots
- `Krea2BenchmarkReport`: CSV, TXT, and PNG scoreboard reports
- Timer Display widget

Install folder at `ComfyUI/custom_nodes/Krea2_Benchmark_Tools/`. Restart ComfyUI and hard-refresh your browser. Do not retain the old `Krea2_Benchmark` package or a separate registered `AILab_ImageCompare6` copy at the same time, as duplicate class registrations can occur. Back up previous installations before changing them.

## Measurement scope
KSampler node timing may include lazy model loading and does not mean pure denoising kernel time. VRAM snapshots measure the whole GPU, not exclusive per-model usage. Results are affected by cache state and other running processes.

## Outputs
Reports are saved within `ComfyUI/output/Krea2_Benchmark/YYYY-MM-DD/`.

## Attribution and licensing checkpoint
`image_compare.py` explicitly credits the AILab Image Compare node in `1038lab/ComfyUI-RMBG` as its design reference. That upstream project is GPL-3.0 licensed. Determine whether this code is a derivative and satisfy any applicable notices, source-disclosure and license terms **before public redistribution**. See `PUBLISHING_REVIEW.md` in the package root. This distribution draft does not assert ownership or relicense third-party code.
