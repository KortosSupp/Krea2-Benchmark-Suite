import { app } from "../../../scripts/app.js";
import { api } from "../../../scripts/api.js";

app.registerExtension({
    name: "krea2.benchmark.links",
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== "Krea2BenchmarkReport") return;
        const original = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const result = original?.apply(this, arguments);
            const labels = ["CSV", "TXT", "PNG"];
            for (let i = 0; i < 3; i++) {
                this.addWidget("button", "Open " + labels[i] + " report", null, () => {
                    const file = this.properties?.benchmark_files?.[i];
                    if (!file) { alert("Run the benchmark first to create the report."); return; }
                    const query = new URLSearchParams({filename:file.filename,subfolder:file.subfolder,type:file.type});
                    window.open(api.apiURL('/view?' + query.toString()),'_blank','noopener,noreferrer');
                });
            }
            return result;
        };
        const prevExec = nodeType.prototype.onExecuted;
        nodeType.prototype.onExecuted = function(message) {
            prevExec?.apply(this, arguments);
            if (message?.benchmark_files?.length) {
                this.properties ??= {};
                this.properties.benchmark_files = message.benchmark_files;
                this.setDirtyCanvas(true,true);
            }
        };
    }
});
