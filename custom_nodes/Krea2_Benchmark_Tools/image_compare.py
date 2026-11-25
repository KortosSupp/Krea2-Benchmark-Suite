# AILab_ImageCompare6.py
#
# Attribution: Inspired by the Image Compare node in 1038lab/ComfyUI-RMBG.
# Upstream source: https://github.com/1038lab/ComfyUI-RMBG
# Upstream license: GNU General Public License v3.0.
# This file is distributed under GPL-3.0-only as a conservative licensing
# choice pending final verification of code provenance.
# See LICENSE and THIRD_PARTY_NOTICES.md in this directory.
# Standalone ComfyUI custom node compatible with the IMAGE tensor conventions
# used by 1038lab/ComfyUI-RMBG's AILab_ImageCompare.
#
# Install:
#   <ComfyUI>\custom_nodes\ComfyUI-RMBG\AILab_ImageCompare6.py
#
# This is intentionally a separate node so RMBG updates do not require editing
# py/AILab_ImageMaskTools.py.

import os
import numpy as np
import torch
from PIL import Image, ImageDraw, ImageFont


class AILab_ImageCompare6:
    def __init__(self):
        self.font_size = 20
        self.padding = 10
        self.text_color = "#000000"
        self.bg_color = "#FFFFFF"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text1": ("STRING", {"default": "Image 1"}),
                "text2": ("STRING", {"default": "Image 2"}),
                "text3": ("STRING", {"default": "Image 3"}),
                "text4": ("STRING", {"default": "Image 4"}),
                "text5": ("STRING", {"default": "Image 5"}),
                "text6": ("STRING", {"default": "Image 6"}),
                "size_base": (
                    ["largest", "smallest",
                     "image1", "image2", "image3",
                     "image4", "image5", "image6"],
                    {"default": "largest"},
                ),
                "text_color": ("COLORCODE", {"default": "#000000"}),
                "bg_color": ("COLORCODE", {"default": "#FFFFFF"}),
                "layout": (["6x1", "3x2", "2x3"], {"default": "6x1"}),
            },
            "optional": {
                "image1": ("IMAGE",),
                "image2": ("IMAGE",),
                "image3": ("IMAGE",),
                "image4": ("IMAGE",),
                "image5": ("IMAGE",),
                "image6": ("IMAGE",),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("IMAGE",)
    FUNCTION = "generate"
    CATEGORY = "🧪AILab/🖼️IMAGE"

    def get_font(self):
        try:
            if os.name == "nt":
                return ImageFont.truetype("arial.ttf", self.font_size)
            path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
            if os.path.exists(path):
                return ImageFont.truetype(path, self.font_size)
            return ImageFont.load_default()
        except Exception:
            return ImageFont.load_default()

    def create_text_panel(self, width, text):
        text = str(text)
        font = self.get_font()
        temp = Image.new("RGB", (max(1, width), self.font_size * 3), self.bg_color)
        draw = ImageDraw.Draw(temp)
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        final_h = max(int(th * 1.5), self.font_size * 2)
        panel = Image.new("RGB", (max(1, width), final_h), self.bg_color)
        draw = ImageDraw.Draw(panel)
        x = max(0, (width - tw) // 2)
        y = max(0, (final_h - th) // 2)
        draw.text((x, y), text, font=font, fill=self.text_color)
        return panel

    @staticmethod
    def tensor_to_pil(t):
        # One ComfyUI IMAGE frame: H,W,C; float normally 0..1.
        arr = t.detach().cpu().float().numpy()
        arr = np.clip(arr, 0.0, 1.0)
        arr = (arr * 255.0).round().astype(np.uint8)

        if arr.ndim == 2:
            return Image.fromarray(arr, mode="L").convert("RGB")
        if arr.shape[-1] == 1:
            return Image.fromarray(arr[..., 0], mode="L").convert("RGB")
        if arr.shape[-1] >= 3:
            return Image.fromarray(arr[..., :3], mode="RGB")
        raise ValueError(f"Unsupported IMAGE frame shape: {arr.shape}")

    @staticmethod
    def pil_to_tensor(img):
        arr = np.asarray(img.convert("RGB")).astype(np.float32) / 255.0
        return torch.from_numpy(arr).unsqueeze(0)

    def _select_base_image(self, pil_map, size_base):
        if size_base in pil_map:
            return size_base

        if size_base == "smallest":
            return min(pil_map, key=lambda k: pil_map[k].width * pil_map[k].height)

        if size_base not in ("largest", "smallest"):
            print(
                f"[Image Compare 6 RMBG] size_base '{size_base}' is unavailable; "
                "falling back to largest."
            )

        return max(pil_map, key=lambda k: pil_map[k].width * pil_map[k].height)

    @staticmethod
    def _resize_to_height(img, target_h):
        if img.height == target_h:
            return img
        target_w = max(1, round(img.width * (target_h / img.height)))
        return img.resize((target_w, target_h), Image.Resampling.LANCZOS)

    def _compose_cells(self, cells, layout):
        """Combine image/caption cells without cropping or stretching images."""
        columns = {"6x1": 6, "3x2": 3, "2x3": 2}.get(layout, 6)
        columns = min(columns, len(cells))
        rows = [cells[i:i + columns] for i in range(0, len(cells), columns)]

        # Each column has a consistent width; each row has a consistent height.
        col_widths = [max(row[c].width for row in rows if c < len(row))
                      for c in range(columns)]
        row_heights = [max(cell.height for cell in row) for row in rows]
        canvas_w = sum(col_widths) + self.padding * (columns - 1)
        canvas_h = sum(row_heights) + self.padding * (len(rows) - 1)
        canvas = Image.new("RGB", (canvas_w, canvas_h), self.bg_color)

        y = 0
        for row_idx, row in enumerate(rows):
            x = 0
            for col_idx, cell in enumerate(row):
                left = x + (col_widths[col_idx] - cell.width) // 2
                top = y + (row_heights[row_idx] - cell.height) // 2
                canvas.paste(cell, (left, top))
                x += col_widths[col_idx] + self.padding
            y += row_heights[row_idx] + self.padding
        return canvas

    def generate(
        self,
        text1, text2, text3, text4, text5, text6,
        size_base="largest",
        text_color="#000000",
        bg_color="#FFFFFF",
        layout="6x1",
        image1=None, image2=None, image3=None,
        image4=None, image5=None, image6=None,
    ):
        self.text_color = text_color
        self.bg_color = bg_color

        images = [image1, image2, image3, image4, image5, image6]
        texts = [text1, text2, text3, text4, text5, text6]

        active = []
        for i, tensor in enumerate(images, start=1):
            if tensor is not None and hasattr(tensor, "shape") and tensor.shape[0] > 0:
                active.append((f"image{i}", tensor, texts[i - 1]))

        if len(active) < 2:
            print("[Image Compare 6 RMBG] At least two images are required.")
            return (torch.zeros((1, 64, 64, 3), dtype=torch.float32),)

        batch_sizes = [item[1].shape[0] for item in active]
        batch_size = min(batch_sizes)
        if len(set(batch_sizes)) > 1:
            print(
                "[Image Compare 6 RMBG] Input batches have different sizes "
                f"{batch_sizes}; using first {batch_size} frame(s)."
            )

        outputs = []

        for b in range(batch_size):
            pil_map = {
                label: self.tensor_to_pil(tensor[b])
                for label, tensor, _ in active
            }

            base_label = self._select_base_image(pil_map, size_base)
            target_h = pil_map[base_label].height

            cells = []
            for label, _, caption in active:
                img = self._resize_to_height(pil_map[label], target_h)
                text_panel = self.create_text_panel(img.width, caption)

                cell = Image.new(
                    "RGB",
                    (img.width, img.height + text_panel.height),
                    self.bg_color,
                )
                cell.paste(img, (0, 0))
                cell.paste(text_panel, (0, img.height))
                cells.append(cell)

            canvas = self._compose_cells(cells, layout)

            outputs.append(self.pil_to_tensor(canvas))

        # Different batch frames normally have the same final dimensions.
        # Pad defensively if they do not.
        max_h = max(t.shape[1] for t in outputs)
        max_w = max(t.shape[2] for t in outputs)
        padded = []
        bg = tuple(int(bg_color.lstrip("#")[i:i+2], 16) / 255.0 for i in (0, 2, 4))
        for t in outputs:
            if t.shape[1] == max_h and t.shape[2] == max_w:
                padded.append(t)
                continue
            p = torch.empty((1, max_h, max_w, 3), dtype=torch.float32)
            p[..., 0] = bg[0]
            p[..., 1] = bg[1]
            p[..., 2] = bg[2]
            p[:, :t.shape[1], :t.shape[2], :] = t
            padded.append(p)

        return (torch.cat(padded, dim=0),)


NODE_CLASS_MAPPINGS = {
    "AILab_ImageCompare6": AILab_ImageCompare6,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AILab_ImageCompare6": "Image Compare 6 (RMBG) 🖼️×6",
}
