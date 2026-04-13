from huggingface_hub import HfApi
import os

api = HfApi()

# IMPORTANT: Paste your HF Write Token here
token = "YOUR_HF_WRITE_TOKEN"
repo_id = "erl-hub/reachy-act"

# Mapping: local_path -> folder_name_on_hf
models = {
    "/nikola_vol/saved_models/reachy/2026-04-09_04-19-28-reachy2_lerobot_act_s7077": "2026-04-09_reachy_s7077",
    "/nikola_vol/saved_models/reachy/2026-04-10_02-38-28-reachy2_lerobot_act_s8655": "2026-04-10_reachy_s8655",
    "/nikola_vol/saved_models/reachy/2026-04-10_02-39-07-reachy2_lerobot_act_s1097": "2026-04-10_reachy_s1097"
}

for local_path, hf_path in models.items():
    if os.path.isdir(local_path):
        print(f"Uploading {hf_path}...")
        api.upload_folder(
            folder_path=local_path,
            path_in_repo=hf_path,
            repo_id=repo_id,
            token=token,
            repo_type="model"
        )
        print(f"Successfully uploaded {hf_path}")
    else:
        print(f"Error: {local_path} not found.")

print("All uploads complete!")
