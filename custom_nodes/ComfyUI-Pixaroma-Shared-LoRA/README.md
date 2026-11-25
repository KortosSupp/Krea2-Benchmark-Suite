# Pixaroma Shared LoRA — Krea 2 Six-Model Benchmark (v12)

This frontend extension synchronizes the selected LoRA list and settings from a designated master Pixaroma LoRA loader to five designated followers. It does not modify the upstream Pixaroma package and does not itself load LoRA weights.

## Installation
Place this folder at `ComfyUI/custom_nodes/ComfyUI-Pixaroma-Shared-LoRA/`. Install the upstream Pixaroma package separately. Restart ComfyUI and hard-refresh the browser.

## Usage
Open `workflow/Krea2_Benchmark_Suite_v1.0.json`, choose LoRAs using the master Pixaroma LoRA loader in Decision Panel, then confirm the five follower loaders update. Use LoRAs compatible with each selected model; model-specific behavior may differ.

## Limitations
Follower edits may be overwritten by subsequent synchronization. This extension wraps `app.graphToPrompt` and uses a periodic frontend check; upstream interface changes can break compatibility. No clean-environment execution test is claimed.
