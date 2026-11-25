import { app } from "/scripts/app.js";

// V12: sync only nodes explicitly tagged inside this workflow.
// Pixaroma Loader is still the actual loader; this extension never loads weights.
const ROLE_KEY = "krea2_pixaroma_shared_lora_v12";
const deepCopy = (x) => JSON.parse(JSON.stringify(x));
let lastGraph = null;
let lastFingerprint = null;

function findGroup() {
  const nodes = app.graph?._nodes ?? [];
  const masters = nodes.filter(n => n.type === "PixaromaLoraLoader" && n.properties?.[ROLE_KEY] === "master");
  const targets = nodes.filter(n => n.type === "PixaromaLoraLoader" && n.properties?.[ROLE_KEY] === "follower");
  if (masters.length !== 1 || targets.length !== 5) return null;
  return { master: masters[0], targets };
}

function stateOf(node) {
  // For Pixaroma the widgets[0].value object is serialized as widgets_values[0].
  const w = node.widgets?.find(w => w.name === "loras_ui") ?? node.widgets?.[0];
  const fromWidget = w?.value;
  const fromProperty = node.properties?.loraLoaderState;
  let prop;
  try { prop = typeof fromProperty === "string" ? JSON.parse(fromProperty) : fromProperty; } catch (_) {}
  const state = fromWidget && typeof fromWidget === "object" && Array.isArray(fromWidget.loras)
    ? fromWidget : prop;
  if (!state || !Array.isArray(state.loras)) return null;
  return deepCopy(state);
}

function copyState(node, state) {
  const w = node.widgets?.find(w => w.name === "loras_ui") ?? node.widgets?.[0];
  const newState = deepCopy(state);
  if (w) w.value = newState;
  node.properties ||= {};
  node.properties.loraLoaderState = JSON.stringify(newState);
  // Preserve unrelated node settings, connections, and drawing geometry.
  node.setDirtyCanvas?.(true, true);
}

function synchronize() {
  const group = findGroup();
  if (!group) { lastFingerprint = null; return; }
  const state = stateOf(group.master);
  if (!state) return;
  const fingerprint = JSON.stringify(state);
  if (lastGraph === app.graph && fingerprint === lastFingerprint &&
      group.targets.every(n => JSON.stringify(stateOf(n)) === fingerprint)) return;
  for (const follower of group.targets) {
    if (JSON.stringify(stateOf(follower)) !== fingerprint) copyState(follower, state);
  }
  lastGraph = app.graph;
  lastFingerprint = fingerprint;
}

app.registerExtension({
  name: "krea2.pix.sharedLora.v12",
  setup() {
    // Sync immediately before ComfyUI builds the execution prompt.
    if (typeof app.graphToPrompt === "function") {
      const original = app.graphToPrompt.bind(app);
      app.graphToPrompt = async (...args) => {
        synchronize();
        return await original(...args);
      };
    }
    // Keep follower Pixaroma UI states in step when user edits master.
    window.setInterval(() => {
      if (app.graph && !document.hidden) synchronize();
    }, 400);
  },
  afterConfigureGraph() {
    lastFingerprint = null;
    synchronize();
  }
});
