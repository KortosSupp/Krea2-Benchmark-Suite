"""Measure the *actual node execution* of standard ComfyUI KSampler.

Metric: CUDA-synchronized KSampler.sample wall time, including any model
materialization/loading and sampling performed by that call. This is NOT
pure denoising-kernel time. No time is counted before the node starts.
"""
import time
import math
import torch
from nodes import KSampler

class Krea2TimedKSampler(KSampler):
    @classmethod
    def INPUT_TYPES(cls):
        old = super().INPUT_TYPES()
        required = dict(old['required'])
        optional = dict(old.get('optional', {}))
        optional['previous_cleanup'] = ('STRING', {'forceInput': True})
        return {'required': required, 'optional': optional}

    RETURN_TYPES = ('LATENT', 'INT')
    RETURN_NAMES = ('LATENT', 'node_wall_ms')
    FUNCTION = 'timed_sample'
    CATEGORY = 'Krea2/Benchmark Tools'

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        # Explicit re-run of a benchmark should not recycle a cached duration.
        return float('nan')

    def timed_sample(self, model, seed, steps, cfg, sampler_name, scheduler,
                     positive, negative, latent_image, denoise=1.0,
                     previous_cleanup=None):
        if previous_cleanup is not None:
            # Dependency is intentionally evaluated BEFORE the timer starts.
            # A prior failed telemetry reading is not considered successful cleanup.
            pass
        cuda = torch.cuda.is_available()
        if cuda:
            torch.cuda.synchronize()
        start = time.perf_counter_ns()
        try:
            output = super().sample(model, seed, steps, cfg, sampler_name,
                                    scheduler, positive, negative, latent_image,
                                    denoise)
        finally:
            if cuda:
                torch.cuda.synchronize()
        elapsed_ms = round((time.perf_counter_ns() - start) / 1_000_000)
        print(f'[Krea2 Timed KSampler] node wall time: {elapsed_ms} ms; '
              f'includes any loading and sampling inside KSampler')
        return (output[0], int(elapsed_ms))

NODE_CLASS_MAPPINGS = {'Krea2TimedKSampler': Krea2TimedKSampler}
NODE_DISPLAY_NAME_MAPPINGS = {'Krea2TimedKSampler': 'Krea2 Timed KSampler (Node Wall)'}
