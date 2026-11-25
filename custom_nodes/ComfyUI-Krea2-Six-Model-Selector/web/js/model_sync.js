import { app } from "/scripts/app.js";

// Controls only specifically marked loaders in the same graph.
const MASTER_KEY = "krea2_six_model_sync_master";
const SLOT_KEY = "krea2_six_model_sync_slot";
const ACCEPTED_TYPES = new Set(["UNETLoader", "UNet loader with Name (Image Saver)"]);
let busy = false;

function syncModelWidgets() {
  if (busy) return;
  const nodes = app.graph?._nodes ?? [];
  const masters = nodes.filter(n => n.type === "Krea2SixModelSelector" && n.properties?.[MASTER_KEY] === true);
  if (masters.length !== 1) return;
  const targets = nodes.filter(n => ACCEPTED_TYPES.has(n.type) &&
    Number.isInteger(n.properties?.[SLOT_KEY]) && n.properties[SLOT_KEY] >= 1 && n.properties[SLOT_KEY] <= 6);
  if (targets.length !== 6 || new Set(targets.map(n => n.properties[SLOT_KEY])).size !== 6) return;
  const master = masters[0];
  busy = true;
  try {
    for (const loader of targets) {
      const i = loader.properties[SLOT_KEY] - 1;
      const value = master.widgets?.find(w => w.name === `model_${i+1}`)?.value ?? master.widgets?.[i]?.value;
      const target = loader.widgets?.find(w => ["unet_name", "model_name", "ckpt_name"].includes(w.name)) ?? loader.widgets?.[0];
      if (typeof value !== "string" || !target) continue;
      const choices = target.options?.values;
      if (Array.isArray(choices) && !choices.includes(value)) continue;
      if (target.value !== value) {
        target.value = value;
        target.callback?.(value);
        loader.setDirtyCanvas?.(true, true);
      }
    }
  } finally {
    busy = false;
  }
}

app.registerExtension({
  name: "krea2.sixModelSelector.widgetSync.v14",
  setup() {
    if (typeof app.graphToPrompt === "function") {
      const previous = app.graphToPrompt.bind(app);
      app.graphToPrompt = async (...args) => {
        syncModelWidgets();
        return await previous(...args);
      };
    }
    window.setInterval(() => {
      if (app.graph && !document.hidden) syncModelWidgets();
    }, 350);
  },
  afterConfigureGraph() { syncModelWidgets(); }
});
