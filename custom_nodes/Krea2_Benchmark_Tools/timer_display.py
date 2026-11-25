"""Portable persistent timer/readout for ComfyUI.

console, display, prefix are normal ComfyUI input widgets and serialize
into the workflow JSON; unlike Crystools' non-serializing display widgets.
"""
import math

class Krea2TimerDisplay:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "any_value": ("*",),
            "console": ("BOOLEAN", {"default": True}),
            "display": ("BOOLEAN", {"default": True}),
            "prefix": ("STRING", {"default": "", "multiline": False}),
            "value_is_ms": ("BOOLEAN", {"default": False}),
        }}

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("formatted_value",)
    FUNCTION = "show"
    CATEGORY = "Krea2/Benchmark Tools"
    OUTPUT_NODE = True

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("nan")

    def show(self, any_value, console=True, display=True, prefix="", value_is_ms=False):
        value = str(any_value)
        if value_is_ms:
            try:
                ms = int(float(any_value))
                if ms < 0: raise ValueError('negative duration')
                value = f"{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d}.{ms%1000:03d}"
            except (ValueError, TypeError, OverflowError):
                value = "N/A"
        label = f"{prefix}{value}"
        if console:
            print(f"[Krea2 Timer Display] {label}")
        return {"ui": {"timer_text": [label if display else ""]},
                "result": (value,)}

NODE_CLASS_MAPPINGS = {"Krea2TimerDisplay": Krea2TimerDisplay}
NODE_DISPLAY_NAME_MAPPINGS = {"Krea2TimerDisplay": "Krea2 Timer Display (Persistent)"}
