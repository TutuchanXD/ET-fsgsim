import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RELATIVE_EVENT_LIBRARY = "cosmic_ray/guide_6p5um/event_library_6p5um.npz"
SCRIPT_PATHS = [
    ROOT / "scripts" / "et_sim_guide_det_v1_noise_psf.py",
    ROOT / "scripts" / "et_sim_microlens_guide_det_v1_noise_psf.py",
]


def _module_constants(path):
    module = ast.parse(path.read_text(encoding="utf-8"))
    constants = {}
    for node in module.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if isinstance(target, ast.Name) and isinstance(node.value, ast.Constant):
            constants[target.id] = node.value.value
    return constants


def test_guide_scripts_default_cosmic_rays_on_with_relative_library_path():
    for path in SCRIPT_PATHS:
        constants = _module_constants(path)

        assert constants["GUIDE_ENABLE_COSMIC_RAYS"] is True
        assert constants["DEFAULT_COSMIC_RAY_EVENT_LIBRARY_PATH"] == RELATIVE_EVENT_LIBRARY
