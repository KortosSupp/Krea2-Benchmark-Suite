# Krea 2 Benchmark Suite

**A six-model visual benchmarking workflow for ComfyUI.**

Compare Krea 2-compatible diffusion models in one workflow, test how they respond to LoRAs and sampling settings, and review visual outputs alongside execution-time and GPU-memory measurements.

> **Release status:** v1.0 workflow / custom-node installer v1.0 RC1. The bundled custom nodes have undergone preliminary static checks, but the installer has **not** been validated on a completely clean ComfyUI installation. Please report reproducible issues with relevant logs.

## Why this project?

Choosing a model for a particular scene often means repeating the same prompt across checkpoints, adjusting sampling parameters, and comparing images by hand. Krea 2 Benchmark Suite brings that process into a single workspace with six configurable model slots, common controls, individual model settings, an image comparison grid, and a performance report.

This is a **comparison tool**, not an automatic model-quality ranking system. The best model still depends on your prompts, LoRAs, preferences, and hardware.

## Features

- **Six model slots:** Compare up to six Krea 2-compatible diffusion models; assign the same model to multiple slots to explore different configurations.
- **Central Decision Panel:** Choose the prompt source, models, shared LoRAs, image dimensions, seed, and batch size.
- **Flexible prompt input:** Use a supplied prompt directly, refine a written description, or derive a prompt from a reference image with an optional local LLM.
- **Final prompt preview:** Inspect the prompt in the red node labeled **`YOUR FINAL (ACTIVE) PROMPT IS HERE`** near the top of the canvas.
- **Shared LoRA selection:** The Pixaroma LoRA configuration is synchronized across six model pipelines by a companion frontend extension.
- **Per-model Private Panels:** Configure sampler, scheduler, CFG, and step count independently for each model slot.
- **Output Comparison Grid:** Combine six outputs into one labeled image. Supported arrangements include **6×1**, **3×2**, and **2×3**; the supplied v1.0 JSON currently uses **3×2**.
- **Performance Scoreboard:** Review per-model KSampler node execution time and device-wide VRAM snapshots; export CSV, TXT, and PNG reports.
- **Timers and organized outputs:** Follow workflow timing and save model outputs and comparison images in date-organized output folders.

## Downloads

| File | Purpose |
| --- | --- |
| `Krea2_Benchmark_Suite_v1.0.json` | Main ComfyUI workflow |
| `Krea2_Benchmark_Installer_v1.0_RC1.zip` | Three workflow-specific custom-node packages and installation notes |

Once the files are published, download the workflow from this repository and the installer from the repository's **Releases** section. The installer is a **release candidate**, not a confirmed universal one-click installer.

## Requirements

- A working installation of **ComfyUI** with a compatible frontend.
- One or more **Krea 2-compatible diffusion models** (a model may be reused in multiple slots).
- Compatible **text encoder(s)** and **VAE(s)** for the selected models.
- Sufficient GPU/CPU memory for the selected models, resolutions, and batch size.
- Optional LoRAs if you want to compare LoRA behavior.
- **LM Studio**, a reachable local API server, and a suitable language/vision model **only if** you use the optional Local LLM prompt-generation paths.

Models, encoders, VAEs, LoRAs, and LM Studio are **not included** in the installer. The JSON may contain example selections that do not exist on your computer; replace them before running.

### Third-party custom-node dependencies

Install these separately, preferably through ComfyUI-Manager or the maintainers' upstream repositories:

| Package | Used for | Upstream |
| --- | --- | --- |
| ComfyUI-Pixaroma | LoRA loading, group/input switching, image saving, labels, timing, VRAM cleanup | [pixaroma/ComfyUI-Pixaroma](https://github.com/pixaroma/ComfyUI-Pixaroma) |
| ComfyUI-AusBoss | Resolution controls and final prompt display | [ausboss/ComfyUI-AusBoss](https://github.com/ausboss/ComfyUI-AusBoss) |
| ComfyUI-Image-Saver | Named diffusion-model loaders | [alexopus/ComfyUI-Image-Saver](https://github.com/alexopus/ComfyUI-Image-Saver) |
| ComfyUI_JPS-Nodes | Text prompt and concatenation nodes | [JPS-GER/ComfyUI_JPS-Nodes](https://github.com/JPS-GER/ComfyUI_JPS-Nodes) |
| ComfyUI_LC123_nodes | Workflow timer | [lonecatone23/ComfyUI_LC123_nodes](https://github.com/lonecatone23/ComfyUI_LC123_nodes) |
| Deno custom nodes | `DenoLocalLLMRefiner` | [Deno2026/comfyui-deno-custom-nodes](https://github.com/Deno2026/comfyui-deno-custom-nodes) |

The exact set of installed versions can affect compatibility. Refer to the installer archive's `DEPENDENCIES.md` for further details. Third-party links are upstream references, not copies of those projects bundled here.

### Workflow-specific custom nodes

The installer archive provides:

| Folder | Function |
| --- | --- |
| `Krea2_Benchmark_Tools` | Timed KSampler, VRAM probes, benchmark report, timer display, six-image comparison grid |
| `ComfyUI-Krea2-Six-Model-Selector` | Synchronizes Model Selector entries with the six model loaders |
| `ComfyUI-Pixaroma-Shared-LoRA` | Synchronizes the master Pixaroma LoRA configuration with follower loaders |

**Do not also install the older `Krea2_Benchmark` folder** alongside `Krea2_Benchmark_Tools`: they can define overlapping node mappings and frontend extensions.

## Installation

1. **Close ComfyUI** and back up your existing `custom_nodes` directory.
2. Install the [third-party custom-node dependencies](#third-party-custom-node-dependencies). Restart ComfyUI if necessary.
3. Download and extract `Krea2_Benchmark_Installer_v1.0_RC1.zip`.
4. Copy the **three folders inside the archive's `custom_nodes/` directory** into your installation's `ComfyUI/custom_nodes/` directory. Do **not** nest an extra `custom_nodes` folder inside it.
5. Do not blindly overwrite any existing folders. Review their versions and back them up first.
6. If your ComfyUI installation requires additional Python packages, install them in the **same Python environment that runs ComfyUI**, following the package's requirements. Do not force-upgrade PyTorch merely to install this toolkit.
7. Restart ComfyUI and hard-refresh the browser if needed.
8. Load `Krea2_Benchmark_Suite_v1.0.json` and replace any missing model, LoRA, VAE, encoder, reference-image, or Local LLM selections with your own.
9. Begin with **batch size 1** and verify your installation before running a full six-model benchmark.

### Optional Windows installer

From the folder containing the extracted `install.ps1` file, you can use PowerShell:

```powershell
.\install.ps1 -ComfyUIPath 'D:\ComfyUI'
```

Replace `D:\ComfyUI` with **your** ComfyUI directory. Review scripts before executing them. This script copies the bundled custom-node folders **only if the target folders do not already exist**. It does not download third-party nodes, install Python packages, alter model files, or start ComfyUI. Linux users can perform the same copy steps manually.

## Quick start

1. Open **Decision Panel** and select your prompt source: reference image, free-text refinement, or a direct prompt.
2. If using a Local LLM, configure the `DenoLocalLLMRefiner` nodes for your installed model and running API server. A Local LLM is not necessary for the direct-prompt route.
3. Confirm the actual text in **`YOUR FINAL (ACTIVE) PROMPT IS HERE`**.
4. Use **Krea 2 | MODEL SELECTOR** to assign your six model slots. You may select the same model more than once.
5. Select compatible LoRA(s), choose image dimensions, set seed and batch size, and review each model's **Private Panel**.
6. **Re-check the corresponding Private Panel whenever you change a model**: sampler, scheduler, CFG, and steps may need adjustment.
7. Run the workflow, then inspect the individual outputs, **Output Comparison Grid**, and **Performance Scoreboard**.

### Getting useful comparisons

For a more controlled comparison, start with the same prompt, image dimensions, batch size, and seed. Be aware that **the same seed does not guarantee equivalent compositions across different models**. Repeat tests before drawing broad conclusions, and change one variable at a time when examining the effects of sampling settings or LoRAs.

## Outputs and measurements

- **Individual images:** Saved by each model's image-save node.
- **Output Comparison Grid:** A combined image labeled by model name; the v1.0 workflow provides 6×1, 3×2, and 2×3 layouts.
- **Performance Scoreboard:** CSV, TXT, and PNG report outputs.
- **Output directories:** The bundled save configuration uses date-based subfolders and filenames incorporating time, model name, and image dimensions. Actual paths depend on the user's ComfyUI configuration.

**Measurement limitations:** VRAM Before/After measurements are snapshots of **device-wide GPU memory**, not a definitive measurement of a single model's exclusive VRAM usage. Timed KSampler results represent **node wall-clock execution time** and may include model loading/preparation work, rather than GPU sampling kernels alone. Compare results with these limitations in mind.

## Troubleshooting

| Symptom | What to check |
| --- | --- |
| Missing custom nodes on load | Install the upstream dependencies and the three supplied custom-node folders; restart ComfyUI and inspect its startup log. |
| Model, LoRA, encoder, or VAE not found | Replace creator-specific selections in the JSON with files installed on your system. |
| `DenoLocalLLMRefiner` errors or long prompt-generation delays | Verify your Local LLM server, configured model, connectivity, and available memory; or select the direct-prompt path. |
| Model Selector or shared LoRA controls do not synchronize | Check the installed frontend extensions, Pixaroma version, browser refresh, and ComfyUI console messages. |
| Out-of-memory errors | Reduce image dimensions and batch size, use smaller model variants, and check GPU memory availability. |
| Unexpected benchmark results | Verify the correct model and its Private Panel settings, LoRA compatibility, and the measurement limitations above. |

When reporting an issue, please include your ComfyUI version, relevant custom-node versions, operating system, GPU/VRAM, a short reproduction procedure, and **redacted** terminal logs. Do not publish private images, local paths, API credentials, or other sensitive data.

## Development and release notes

This project includes original workflow integration and workflow-specific custom nodes, with dependencies on independently maintained third-party ComfyUI extensions. Some techniques were adapted from or informed by other node projects; upstream authors retain their respective rights.

The repository's source-code license and attribution documentation should be finalized **before publicly publishing third-party-derived code**. Until a license is explicitly added, do not assume the files are offered under MIT, Apache-2.0, or any other open-source license.

Current release: **v1.0 / installer RC1**. Clean-install compatibility remains to be verified.

## Feedback and contributions

Found a reproducible bug, missing dependency, or compatibility issue? Please open a GitHub Issue with the steps to reproduce and sanitized logs. Suggestions for improving comparison accuracy, installation, and the user interface are also welcome.

---

*Built to make repeated Krea 2 model comparisons more organized, transparent, and practical. Happy benchmarking!*
