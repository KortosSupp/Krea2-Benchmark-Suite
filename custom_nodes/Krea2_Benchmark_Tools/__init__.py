"""Krea2 Benchmark Tools: image comparison, timer displays, GPU telemetry and reporting."""
from .image_compare import NODE_CLASS_MAPPINGS as image_nodes, NODE_DISPLAY_NAME_MAPPINGS as image_names
from .timer_display import NODE_CLASS_MAPPINGS as timer_nodes, NODE_DISPLAY_NAME_MAPPINGS as timer_names
from .benchmark_report import NODE_CLASS_MAPPINGS as report_nodes, NODE_DISPLAY_NAME_MAPPINGS as report_names

from .timed_sampler import NODE_CLASS_MAPPINGS as sampler_nodes, NODE_DISPLAY_NAME_MAPPINGS as sampler_names

NODE_CLASS_MAPPINGS = {**image_nodes, **timer_nodes, **report_nodes, **sampler_nodes}
NODE_DISPLAY_NAME_MAPPINGS = {**image_names, **timer_names, **report_names, **sampler_names}
WEB_DIRECTORY = "./web"
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
