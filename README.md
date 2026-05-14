# ET-fsgsim

`ET-fsgsim` collects the ET fine-star-guidance simulation entry scripts that were
previously kept beside the Photosim working trees. The scripts generate
guide-detector image sequences for the FSG attitude-solving chain.

The repository contains both guide-detector families used by ET:

- transit-telescope guide simulations, rendered through the Photosim7
  workflow;
- microlensing-telescope guide simulations, rendered through the Photosim7
  workflow.

Both families use `et_focalplane` geometry and Gaia catalog queries to build
the guide fields, then render images with controlled detector, noise, PSF, and
motion effect profiles.

## Repository contents

- `scripts/et_sim_guide_det_v1_noise_psf.py`
  - Main transit guide-detector simulation driver.
  - Default profile: `v1_noise_psf`.
  - Can run all four guide-detector sky centers or one selected batch.
  - Defines all available effect profiles.
- `scripts/et_sim_guide_det_full.py`
  - Thin wrapper around `et_sim_guide_det_v1_noise_psf.py`.
  - Sets `ET_EFFECT_PROFILE=full`.
  - Sets `ET_RUN_ALL_BATCHES=1`.
  - Sets `ET_OUTPUT_RUN_NAME_OVERRIDE=guide_det_full_6s`.
- `scripts/et_sim_microlens_guide_det_v1_noise_psf.py`
  - Main microlensing guide-detector simulation driver.
  - Default profile: `v1_noise_psf`.
  - Loads detector centers, pixel scale, frame size, and detector order from
    `et_focalplane/data_microlens`.
  - Selects `ETCoordConfig.microlens_guide_only()`.
- `scripts/et_sim_microlens_guide_det_full.py`
  - Thin wrapper around `et_sim_microlens_guide_det_v1_noise_psf.py`.
  - Sets `ET_EFFECT_PROFILE=full`.
  - Sets `ET_RUN_ALL_BATCHES=1`.
  - Sets `ET_OUTPUT_RUN_NAME_OVERRIDE=microlens_guide_photsim7_6s`.
- `config/et_100_det_inputs_1h.xlsx`
  - Runtime baseline spreadsheet copied from the legacy Photosim guide workflow.
  - Both simulation drivers use it as a runtime parameter template and create a
    sanitized per-run copy with hidden telescope FOV offsets disabled.

The Photosim package sources are not vendored here. Both the transit and
microlensing scripts now default to the local Photosim7 checkout through
`PHOTSIM7_ROOT`.
The default runtime spreadsheet is `$ET_DATA_DIR/config/et_100_det_inputs_1h.xlsx`
when that file exists, with a fallback to this repository's
`config/et_100_det_inputs_1h.xlsx`. On the ET workstation, `$ET_DATA_DIR`
defaults to `/home/cxgao/ET/Photsim7-data`, so guide simulations use the same
external parameter asset that Photsim7 documents.

## Transit guide-detector setup

The transit driver overrides the main-detector spreadsheet with guide-detector
parameters in script space:

| Quantity | Value |
| --- | --- |
| Pixel scale | `3.146 arcsec / pix` |
| Pixel width | `6.5 um` |
| Field of view | `1.7 deg` square |
| Exposure duration | `0.25 s` |
| Readout duration | `0.0 s` |
| Observing duration | `6.0 s` |
| Readout noise | `5.0 ADU / pix` |
| Dark + scattered light | `10.0 e-/s/pix` total |
| Dark current split | `5.0 e-/s/pix` |
| Scattered light split | `5.0 e-/s/pix` |
| Sky background | `22 mag/arcsec^2`, converted to `e-/s/pix` |
| Inter-pixel PRV RMS | `3 percent` |
| PSF field angle | `14 deg` |
| PSF field ID | `7` |
| ADC digitization | enabled, 12 bit, clip to `[0, 4095]`, round values |
| Cosmic rays | enabled by default; set `ET_ENABLE_COSMIC_RAYS=0` to disable |
| Cosmic-ray rate | `5 events cm^-2 s^-1` when enabled |

The guide star fields are defined by four hard-coded sky centers:

| Batch | RA deg | Dec deg |
| --- | ---: | ---: |
| `batch0` | `278.18437` | `37.57037` |
| `batch1` | `269.58206` | `57.89966` |
| `batch2` | `310.62391` | `59.26764` |
| `batch3` | `305.03563` | `38.47553` |

The default star-query path is:

- backend: `et_focalplane`
- Gaia root: `/home/cxgao/gaia_dr3_19mag`
- `et_focalplane` root: `/home/cxgao/ET/et_focalplane`
- target epoch: `2000.0`
- base Gaia limit: `G <= 11.0`
- adaptive limit step: `0.5 mag`
- maximum Gaia limit: `G <= 16.0`
- target minimum count: `150` stars per field
- simulation cap: brightest `200` stars per batch
- crop to the simulated detector frame: enabled
- hidden static field offset: disabled by default

The output root defaults to `/home/cxgao/Results/FSG_guide_sims`.

## Microlensing guide-detector setup

The microlensing driver uses the same guide-detector noise, exposure, sky
background, PSF field, and output conventions as the transit baseline until
detector-specific calibration data is available. The geometry is different and
is resolved from `et_focalplane`:

- registry data: `/home/cxgao/ET/et_focalplane/data_microlens`
- config factory: `microlens_guide_only`
- detector order:
  - `guide_top`
  - `guide_left`
  - `guide_bottom`
  - `guide_right`
- detector centers: loaded from each detector's microlensing sky patch;
- pixel scale: averaged from the microlensing detector field corners and pixel
  dimensions;
- frame width: derived from the microlensing guide-detector dimensions.

The microlensing script writes `payload`, `detector_subset`,
`et_coord_config_factory`, and `et_focalplane_geometry_source` into
`run_meta.json` so downstream FSG configs can verify that the microlensing guide
geometry was used.

## Running

Run the transit guide baseline:

```bash
python scripts/et_sim_guide_det_v1_noise_psf.py
```

This runs the default `v1_noise_psf` profile. By default it launches all four
guide-detector batches sequentially.

Run the full profile:

```bash
python scripts/et_sim_guide_det_full.py
```

Run the microlensing guide baseline:

```bash
python scripts/et_sim_microlens_guide_det_v1_noise_psf.py
```

Run the microlensing full profile:

```bash
python scripts/et_sim_microlens_guide_det_full.py
```

Run one selected batch:

```bash
ET_RUN_ALL_BATCHES=0 ET_FIELD_CENTER_INDEX=2 \
python scripts/et_sim_guide_det_v1_noise_psf.py
```

Run a specific profile manually:

```bash
ET_EFFECT_PROFILE=v2_point_drift_jitter \
ET_OUTPUT_RUN_NAME_OVERRIDE=guide_det_v2_point_drift_jitter_6s \
python scripts/et_sim_guide_det_v1_noise_psf.py
```

Useful environment overrides:

| Variable | Purpose | Default |
| --- | --- | --- |
| `PHOTSIM7_ROOT` | Local Photosim7 checkout root | `/home/cxgao/ET/Photsim7` |
| `ET_DATA_DIR` | Photsim7 data root | `/home/cxgao/ET/Photsim7-data` |
| `ET_FOCALPLANE_ROOT` | `et_focalplane` checkout root | `/home/cxgao/ET/et_focalplane` |
| `ET_FOCALPLANE_DATA_DIR` | Microlensing registry data override | `<ET_FOCALPLANE_ROOT>/data_microlens` |
| `GUIDE_GAIA_CATALOG_DIR` | Gaia catalog shard root | `/home/cxgao/gaia_dr3_19mag` |
| `ET_CONFIG_XLSX` | Input spreadsheet path | `$ET_DATA_DIR/config/et_100_det_inputs_1h.xlsx` if present, else `config/et_100_det_inputs_1h.xlsx` |
| `ET_EFFECT_PROFILE` | Effect profile name | `v1_noise_psf` |
| `ET_RUN_ALL_BATCHES` | Run all four sky centers | `true` |
| `ET_FIELD_CENTER_INDEX` | Single-batch index when not running all | `0` |
| `ET_OUTPUT_ROOT_OVERRIDE` | Output root | `/home/cxgao/Results/FSG_guide_sims` |
| `ET_OUTPUT_RUN_NAME_OVERRIDE` | Output run name | `guide_det_v1_noise_psf_6s` |
| `ET_MAX_SIM_STARS` | Bright-star cap per batch | `200` |
| `ET_PROFILE_TARGET_FRAMES` | Optional frame-count cap | unset |
| `ET_ENABLE_ADC_DIGITIZATION` | Enable final ADC clip/round | `true` |
| `ET_ADC_BIT_DEPTH` | ADC bit depth | `12` |
| `ET_ADC_MIN_VALUE` | ADC lower bound | `0.0` |
| `ET_ADC_ROUND_VALUES` | Round after clipping | `true` |
| `ET_ENABLE_COSMIC_RAYS` | Enable Poisson cosmic-ray injection | `true` |
| `ET_COSMIC_RAY_EVENT_LIBRARY_PATH` | Cosmic-ray NPZ event library; relative paths resolve from `ET_DATA_DIR` | `cosmic_ray/guide_6p5um/event_library_6p5um.npz` |
| `ET_COSMIC_RAY_EVENT_LIBRARY_PIXEL_SIZE_UM` | Pixel size of selected event library | `6.5` |
| `ET_COSMIC_RAY_EVENT_RATE_PER_CM2_S` | Event rate per detector area and exposure | `5.0` |
| `ET_COSMIC_RAY_SEED` | Cosmic-ray RNG seed | `12345` |

## Common output products

Each batch writes under:

```text
<output_root>/<run_name>/batch<i>_ra<ra>_dec<dec>/
```

Important products:

- `run_meta.json`
  - effect profile and component flags;
  - guide detector parameters;
  - star-query history and final Gaia limit;
  - frame timing;
  - truth coordinate convention;
  - motion split frequency and jitter metadata.
- `stars.ecsv` or `stars.csv`
  - selected truth catalog for the batch;
  - Gaia source information where available;
  - detector truth coordinates from `et_focalplane`.
- `frames/scope0_coadd_*.npz`
  - streamed image frames;
  - `images`;
  - `variant_ids`;
  - `time_s`;
  - `cadence_s`;
  - frame truth payload fields.
  - when cosmic rays are enabled: `cosmic_ray_mask` and
    `cosmic_ray_events`.
- `preview_*.png`
  - first-frame log-scaled preview image.
- `cache/jitter/`
  - cached jitter-integrated PSF trajectories when the active profile uses
    jitter-integrated PSFs.

## Effect profile summary

All profiles share the same guide-detector geometry, Gaia query, PSF field ID,
streaming output, and metadata logic. They differ in the variant flags and in
which dynamic motion components are added.

### `v1_noise_psf`

This is the default baseline for FSG image-to-centroid testing.

Enabled:

- target star rendering;
- background star rendering;
- diffuse sky background;
- scattered light;
- dark current;
- readout noise;
- static PSF rendering with guide PSF field ID `7`;
- frame truth export;
- adaptive Gaia field query through `et_focalplane`.

Disabled:

- stellar photon noise;
- gain effects;
- whole-pixel gain effects;
- jitter;
- jitter-integrated PSF;
- frame-to-frame pointing drift;
- DVA drift;
- thermal drift;
- momentum dump jumps;
- PSF breathing;
- inter-pixel response variation;
- intra-pixel response variation;
- pixel-phase response;
- static hidden field offset.

This profile is useful when the goal is to test centroid extraction, source
matching, and attitude solving under a controlled image-level noise background
without adding attitude-motion or detector-response systematics.

### `full`

This profile uses the active simulator's default variant flags plus all script-level
dynamic components.

Enabled:

- stellar photon noise;
- diffuse sky background;
- scattered light;
- dark current;
- readout noise;
- gain effects;
- whole-pixel gain normal distribution;
- whole-pixel gain sinusoidal modulation;
- target star and background stars;
- jitter;
- jitter-integrated PSF;
- low-frequency pointing drift;
- DVA drift;
- thermal drift;
- momentum dump jumps when the configured observing duration is long enough for
  the configured momentum-dump cycle;
- PSF breathing through the `psf_scale` dynamic parameter;
- inter-pixel response variation;
- intra-pixel response variation;
- pixel-phase response;
- coadding support from the variant default.

The wrapper `et_sim_guide_det_full.py` selects this profile and writes to
`guide_det_full_6s` unless overridden.

### `v2_point_drift_jitter`

This profile adds pointing motion and exposure-level jitter to the v1 baseline.

Enabled beyond `v1_noise_psf`:

- jitter;
- jitter-integrated PSF;
- frame-to-frame pointing drift.

Motion model details:

- The script computes `split_hz = 1 / raw_frame_integration_s` by default.
- ET PSD components at or below `split_hz` become frame-to-frame drift.
- TESS roll motion at or below `split_hz` is added to frame-to-frame drift.
- TESS motion above `split_hz` is used to build jitter-integrated PSFs.
- The TESS x/y high-frequency jitter amplitude is multiplied by `2`.

Disabled:

- DVA;
- thermal drift;
- momentum dump jumps;
- PRV/subpixel response;
- gain effects;
- stellar photon noise.

### `v3_dva`

This profile isolates DVA drift on top of the v1 baseline.

Enabled beyond `v1_noise_psf`:

- DVA drift dynamic motion;
- `enable_dva_drift` in the variant.

The DVA model is loaded from:

```text
<ET_DATA_DIR>/DVA/et/ET_DVA_effect_models_slim_v231117.pkl
```

Disabled:

- jitter-integrated PSF;
- frame-to-frame pointing PSD drift;
- thermal drift;
- momentum dump jumps;
- PRV/subpixel response;
- gain effects;
- stellar photon noise.

### `v4_thermal`

This profile isolates thermal drift behavior on top of the v1 baseline.

Enabled beyond `v1_noise_psf`:

- thermal drift dynamic motion;
- `enable_pointing_drift` in the variant so the thermal motion component is
  applied.

The thermal drift component uses the Photosim
`et_tess_thermal_drift_model` with the script's current field-angle
approximation.

Disabled:

- jitter-integrated PSF;
- frame-to-frame pointing PSD drift;
- DVA drift;
- momentum dump jumps;
- PRV/subpixel response;
- gain effects;
- stellar photon noise.

### `v5_prv_subpixel`

This profile isolates detector response effects on top of the v1 baseline.

Enabled beyond `v1_noise_psf`:

- inter-pixel response variation;
- intra-pixel response variation;
- pixel-phase response.

Disabled:

- jitter-integrated PSF;
- frame-to-frame pointing PSD drift;
- DVA drift;
- thermal drift;
- momentum dump jumps;
- gain effects;
- stellar photon noise.

## Motion and jitter split

The script separates slow frame-to-frame drift from fast exposure-level jitter
using the raw-frame integration time:

```text
split_hz = 1 / raw_frame_integration_s
```

For the default guide exposure, the raw integration time is driven by the
active simulator timing model after the script overrides the spreadsheet parameters.
Slow motion at or below `split_hz` is treated as detector-frame centroid drift.
Fast motion above `split_hz` is folded into jitter-integrated PSFs for the
profiles that enable them.

This distinction matters for FSG validation: slow drift should appear as
frame-to-frame truth motion, while fast jitter should broaden the effective PSF
within a frame.

## Offset policy

The script intentionally disables hidden telescope-wide random offsets:

- it creates a runtime copy of the spreadsheet;
- it sets `Telescope FOV Max Offset = 0`;
- it sets `Target Max Offset = 0`;
- it leaves `APPLY_STATIC_FIELD_OFFSET = False` by default.

If an experiment needs a global field offset, choose explicit
`STATIC_FIELD_OFFSET_X_PIX` and `STATIC_FIELD_OFFSET_Y_PIX` values in the script
or add a controlled environment/config interface before using it for precision
debugging.

## Relationship to FSG

The generated frame batches are consumed by `fsglib`, especially the guide
first-frame workflows:

- transit guide real-centroid solve:
  `examples/run_guide_first_frame.py`
- microlensing guide real-centroid solve:
  `examples/run_microlens_guide_first_frame.py`
- truth/noise comparison workflows:
  `examples/run_guide_first_frame_truth_noise.py`
  and `examples/run_guide_first_frame_truth_noise_exact.py`

The FSG config must point `guide_init.dataset_root` to the output run directory
created by these scripts.
