# Krea 2 Six-Model Selector — ComfyUI Extension (v14)

This workflow-specific extension synchronizes six model selections in `Krea2SixModelSelector` with six marked model-loader widgets.

## Installation
Place this folder at `ComfyUI/custom_nodes/ComfyUI-Krea2-Six-Model-Selector/`. Restart ComfyUI and hard-refresh the browser. Do not install a second copy of the same extension.

## Compatibility
The frontend synchronizer recognizes `UNETLoader` and `UNet loader with Name (Image Saver)` nodes. A single master and six uniquely numbered targets must be present. It does not load model weights itself.

## Check
Open `workflow/Krea2_Benchmark_Suite_v1.0.json`. Select models in the central panel and verify each of the six corresponding loaders. Run a low-resolution test with batch size 1. Adjust any missing model selections to models installed on your computer.

## Limitations
It wraps ComfyUI's `app.graphToPrompt` and uses periodic UI synchronization. Changes in ComfyUI frontend or loader widget APIs may require updates. No clean-environment execution test is claimed.
