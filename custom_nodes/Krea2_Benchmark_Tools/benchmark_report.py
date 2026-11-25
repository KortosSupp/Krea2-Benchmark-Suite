"""Krea 2 six-model benchmark probes and saved scoreboard.
Install folder under ComfyUI/custom_nodes/Krea2_Benchmark.
GPU readings represent global device state, not model-exclusive attribution.
"""
import csv
import io
import json
import math
from datetime import datetime
from pathlib import Path
import torch
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import folder_paths


def snapshot():
    if not torch.cuda.is_available():
        return {"ok": False, "error": "CUDA unavailable"}
    try:
        torch.cuda.synchronize()
        free, total = torch.cuda.mem_get_info()
        return {"ok": True, "free_bytes": int(free), "total_bytes": int(total),
                "used_bytes": int(total-free),
                "torch_allocated_bytes": int(torch.cuda.memory_allocated()),
                "torch_reserved_bytes": int(torch.cuda.memory_reserved()),
                "timestamp": datetime.now().isoformat(timespec="milliseconds")}
    except Exception as e:
        return {"ok": False, "error": str(e)}


class Krea2VramBefore:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"image": ("IMAGE",)}}
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "before_json")
    FUNCTION = "measure"
    CATEGORY = "Krea2/Benchmark"
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("nan")
    def measure(self, image):
        return (image, json.dumps(snapshot()))


class Krea2VramAfter:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"after_cleanup": ("*",), "before_json": ("STRING",)}}
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("measurement_json",)
    FUNCTION = "measure"
    CATEGORY = "Krea2/Benchmark"
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("nan")
    def measure(self, after_cleanup, before_json):
        try:
            before = json.loads(before_json)
        except (TypeError, ValueError):
            before = {"ok": False, "error": "Invalid before reading"}
        after = snapshot()
        freed = (after["free_bytes"]-before["free_bytes"]) if before.get("ok") and after.get("ok") else None
        return (json.dumps({"before": before, "after": after, "freed_bytes": freed}),)


def font(size, bold=False):
    fonts = ["C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
             "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    for f in fonts:
        try:
            return ImageFont.truetype(f, size)
        except OSError:
            continue
    return ImageFont.load_default()


def gib(n):
    return n / (1024 ** 3) if isinstance(n, (int, float)) else None


def fmt_gib(n):
    x = gib(n)
    return f"{x:+.2f} GiB" if x is not None else "N/A"


def fmt_ms(value):
    try:
        ms=int(float(value))
        if ms < 0: raise ValueError()
        return f"{ms//3600000:02d}:{(ms//60000)%60:02d}:{(ms//1000)%60:02d}.{ms%1000:03d}"
    except (ValueError, TypeError, OverflowError):
        return "N/A"


def draw_board(rows, label):
    W, H = 1340, 890
    img=Image.new('RGB',(W,H),'#101722')
    d=ImageDraw.Draw(img)
    ftitle=font(46,True); fhead=font(23,True); frow=font(24,True); fsmall=font(19)
    d.text((60,48),'KREA 2  /  BENCHMARK SCOREBOARD',font=ftitle,fill='#F5F7FB')
    d.text((62,115),label,font=fsmall,fill='#9DADC3')
    d.rounded_rectangle((54,165,1285,730),radius=20,fill='#1B2635')
    headers=[('MODEL',82),('NODE WALL TIME',480),('VRAM BEFORE',777),('VRAM FREED',1037)]
    for t,x in headers:
        d.text((x,189),t,font=fsmall,fill='#AEBED1')
    colors=['#56A4EC','#67C8B0','#E9AE62','#AE97F5','#E97E98','#7BADE0']
    valid_times=[float(r['time_ms']) for r in rows if r['time_ms'] is not None and r['time_ms']>=0]
    max_time=max(valid_times) if valid_times else 1
    for i,r in enumerate(rows):
        y=240+i*78
        if i%2==0: d.rounded_rectangle((66,y-8,1275,y+68),radius=8,fill='#233247')
        d.text((82,y+8),f"{i+1}. {r['model'][:24]}",font=fsmall,fill='#EAF1FA')
        d.rounded_rectangle((478,y+33,690,y+45),radius=6,fill='#34465C')
        if r['time_ms'] is not None and max_time:
            d.rounded_rectangle((478,y+33,478+max(2,int(212*r['time_ms']/max_time)),y+45),radius=6,fill=colors[i])
        d.text((480,y+2),r['time_fmt'],font=frow,fill='#F1F4F9')
        d.text((778,y+9),fmt_gib(r['before_used']).replace('+',''),font=frow,fill='#DCE8FA')
        freed=r['freed']
        d.text((1038,y+9),fmt_gib(freed),font=frow,fill='#75D8B4' if freed is not None and freed>=0 else '#F2A0A2')
    d.text((60,765),'TIMING: measured inside KSampler node (CUDA synchronized).' ,font=fsmall,fill='#D0D8E4')
    d.text((60,799),'VRAM: device-wide snapshot before/after Pixaroma cleanup; NOT model-exclusive.',font=fsmall,fill='#C7D3E2')
    d.text((60,832),'Includes model loading inside KSampler; not pure sampling. Device VRAM is shared.',font=fsmall,fill='#9DADC3')
    return img


class Krea2BenchmarkReport:
    @classmethod
    def INPUT_TYPES(cls):
        required={}
        for i in range(1,7):
            required[f'model_{i}']=("STRING", {"forceInput": True})
            required[f'time_ms_{i}']=("INT", {"forceInput": True})
            required[f'vram_{i}']=("STRING", {"forceInput": True})
        return {"required": required}
    RETURN_TYPES=("IMAGE","STRING","STRING","STRING")
    RETURN_NAMES=("SCOREBOARD_IMAGE","CSV_PATH","TXT_PATH","PNG_PATH")
    FUNCTION="report"
    CATEGORY="Krea2/Benchmark"
    OUTPUT_NODE=True
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("nan")
    def report(self, **kwargs):
        rows=[]
        for i in range(1,7):
            try: m=json.loads(kwargs[f'vram_{i}'])
            except (ValueError, TypeError): m={}
            before=m.get('before',{}) or {}; after=m.get('after',{}) or {}
            raw_ms=kwargs.get(f'time_ms_{i}')
            try: ms=int(raw_ms); ms=ms if ms>=0 else None
            except (ValueError, TypeError): ms=None
            rows.append({'index':i,'model':str(kwargs.get(f'model_{i}') or f'Model {i}'),
                         'time_ms':ms,'time_fmt':fmt_ms(ms),
                         'before_used':before.get('used_bytes') if before.get('ok') else None,
                         'after_used':after.get('used_bytes') if after.get('ok') else None,
                         'before_free':before.get('free_bytes') if before.get('ok') else None,
                         'after_free':after.get('free_bytes') if after.get('ok') else None,
                         'torch_reserved_before':before.get('torch_reserved_bytes'),
                         'torch_reserved_after':after.get('torch_reserved_bytes'),
                         'freed':m.get('freed_bytes'),
                         'measurement_ok': bool(before.get('ok') and after.get('ok'))})
        now=datetime.now()
        stamp=now.strftime('%Y-%m-%d_%H-%M-%S-%f')
        subfolder='Krea2_Benchmark/'+now.strftime('%Y-%m-%d')
        folder=Path(folder_paths.get_output_directory())/subfolder
        folder.mkdir(parents=True,exist_ok=True)
        basename='Krea2_Benchmark_'+stamp
        csv_name=basename+'.csv'; txt_name=basename+'.txt'; png_name=basename+'.png'
        csv_path=folder/csv_name;txt_path=folder/txt_name;png_path=folder/png_name
        with csv_path.open('w',encoding='utf-8-sig',newline='') as f:
            writer=csv.writer(f)
            writer.writerow(['model_index','model_name','ksampler_node_wall_ms','ksampler_node_wall_hh_mm_ss_mmm','device_used_before_GiB','device_used_after_GiB','device_free_before_GiB','device_free_after_GiB','vram_freed_GiB','torch_reserved_before_GiB','torch_reserved_after_GiB','measurement_ok'])
            for r in rows:
                val=lambda v: '' if v is None else f'{gib(v):.4f}'
                writer.writerow([r['index'],r['model'],r['time_ms'],r['time_fmt'],val(r['before_used']),val(r['after_used']),val(r['before_free']),val(r['after_free']),val(r['freed']),val(r['torch_reserved_before']),val(r['torch_reserved_after']),r['measurement_ok']])
        lines=['KREA 2 BENCHMARK REPORT',f'Run: {stamp}','Timing scope: KSampler node execution (CUDA-synchronized wall time).','Includes model preparation/loading performed inside KSampler, not pure sampling kernel time.','Excludes dependency scheduling and waiting before KSampler begins.','VRAM scope: whole GPU, immediately before and after Pixaroma Free VRAM.','Caution: values are NOT exclusive model footprint. CUDA cache and other jobs affect results.','']
        for r in rows:
            lines += [f"MODEL {r['index']}: {r['model']}",f"  KSampler node wall: {r['time_fmt']} ({r['time_ms']} ms)",f"  Device used before cleanup: {fmt_gib(r['before_used'])}",f"  Device used after cleanup: {fmt_gib(r['after_used'])}",f"  GPU memory freed (difference): {fmt_gib(r['freed'])}",f"  PyTorch reserved before: {fmt_gib(r['torch_reserved_before'])}",f"  PyTorch reserved after: {fmt_gib(r['torch_reserved_after'])}",'']
        txt_path.write_text('\n'.join(lines),encoding='utf-8')
        board=draw_board(rows,stamp)
        board.save(png_path)
        arr=np.asarray(board,dtype=np.float32)/255.0
        tensor=torch.from_numpy(arr.copy()).unsqueeze(0)
        paths=[str(csv_path),str(txt_path),str(png_path)]
        return {'ui':{'images':[{'filename':png_name,'subfolder':subfolder,'type':'output'}],
                      'benchmark_files': [{'filename':name,'subfolder':subfolder,'type':'output'} for name in [csv_name,txt_name,png_name]],
                      'text': paths},
                'result':(tensor,*paths)}


NODE_CLASS_MAPPINGS={'Krea2VramBefore':Krea2VramBefore,'Krea2VramAfter':Krea2VramAfter,'Krea2BenchmarkReport':Krea2BenchmarkReport}
NODE_DISPLAY_NAME_MAPPINGS={'Krea2VramBefore':'VRAM Snapshot BEFORE (Krea2)','Krea2VramAfter':'VRAM Snapshot AFTER (Krea2)','Krea2BenchmarkReport':'KREA 2 Benchmark Scoreboard + CSV/TXT/PNG'}
