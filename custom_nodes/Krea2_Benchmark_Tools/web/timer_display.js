import { app } from "../../../scripts/app.js";

app.registerExtension({
  name: "krea2.benchmark.timer_display",
  async beforeRegisterNodeDef(nodeType, nodeData) {
    if (nodeData.name !== "Krea2TimerDisplay") return;
    const previousCreate = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
      const rv = previousCreate?.apply(this, arguments);
      // Only a readout: the three normal input widgets remain serializable.
      const w = this.addWidget("text", "last_result", "—", () => {}, { serialize: false });
      w.options ??= {};
      w.options.serialize = false;
      w.disabled = true;
      this._krea2Readout = w;
      return rv;
    };
    const previousExecuted = nodeType.prototype.onExecuted;
    nodeType.prototype.onExecuted = function (message) {
      previousExecuted?.apply(this, arguments);
      if (this._krea2Readout && Array.isArray(message?.timer_text)) {
        this._krea2Readout.value = message.timer_text[0] || "(display off)";
        this.setDirtyCanvas(true, true);
      }
    };
  },
});
