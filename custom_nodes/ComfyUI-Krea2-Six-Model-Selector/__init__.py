"""Krea2 six model selector. UI controls synchronize existing UNETLoader widgets."""
import folder_paths

class Krea2SixModelSelector:
    @classmethod
    def INPUT_TYPES(cls):
        names = folder_paths.get_filename_list("diffusion_models")
        if not names:
            names = ["(no diffusion models found)"]
        return {"required": {f"model_{i}": (names,) for i in range(1, 7)}}

    RETURN_TYPES = ()
    FUNCTION = "select_models"
    CATEGORY = "Krea2/Utilities"

    def select_models(self, **kwargs):
        # This node drives UNETLoader widget values via its frontend extension.
        # It should never be placed in the execution graph as a model loader.
        return ()

NODE_CLASS_MAPPINGS = {"Krea2SixModelSelector": Krea2SixModelSelector}
NODE_DISPLAY_NAME_MAPPINGS = {"Krea2SixModelSelector": "Krea 2 | 6 Model Selector (Sync)"}
WEB_DIRECTORY = "./web"
