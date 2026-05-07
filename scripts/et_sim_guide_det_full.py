import os
import runpy
from pathlib import Path


ROOT = Path(__file__).resolve().parent

os.environ.setdefault("ET_EFFECT_PROFILE", "full")
os.environ.setdefault("ET_RUN_ALL_BATCHES", "1")
os.environ.setdefault("ET_OUTPUT_RUN_NAME_OVERRIDE", "guide_det_full_6s")

runpy.run_path(str(ROOT / "et_sim_guide_det_v1_noise_psf.py"), run_name="__main__")
