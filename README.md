# Reachy_Pollen

Reachy_Pollen is a Python-based control and experimentation framework for the Reachy robot, built on top of the official SDK. It provides modular tools for robot manipulation, teleoperation integration, and rapid prototyping of control algorithms, enabling streamlined development of perception, planning, and interaction pipelines.

Documentation: [https://pollen-robotics.github.io/reachy2-sdk/reachy2_sdk/reachy_sdk.html](https://pollen-robotics.github.io/reachy2-sdk/reachy2_sdk/reachy_sdk.html)

# Setup

## Docker

Image Dowload: [https://hub.docker.com/r/pollenrobotics/reachy2](https://hub.docker.com/r/pollenrobotics/reachy2)

General Docker

```
docker run --rm --platform linux/amd64 -p 8888:8888 -p 6080:6080 -p 50051:50051 --name reachy2 docker.io/pollenrobotics/reachy2
```

Gazebo Docker

```
docker run --rm --platform linux/amd64 -p 8888:8888 -p 6080:6080 -p 50051:50051 --name reachy2 docker.io/pollenrobotics/reachy2 start_rviz:=true start_sdk_server:=true fake:=true orbbec:=false gazebo:=true
```

Mujoco Docker

```
docker run --rm --platform linux/amd64 -p 8888:8888 -p 6080:6080 -p 50051:50051 --name reachy2 docker.io/pollenrobotics/reachy2 start_rviz:=true start_sdk_server:=true fake:=true orbbec:=false mujoco:=true
```

Different Scene Docker

```
docker run --rm --platform linux/amd64 -p 8888:8888 -p 6080:6080 -p 50051:50051 --name reachy2 docker.io/pollenrobotics/reachy2 start_rviz:=true start_sdk_server:=true fake:=true orbbec:=false mujoco:=true scene:=fruits
```

## Virtual Envrionment

Setup virtual environment

- Linux

```
python3.10 -m venv reachy2
source reachy2/bin/activate
```

- Windows

```
py -3.10 -m venv reachy2
.\reachy2\Scripts\Activate
```

Install requirments

```
pip install -r requirements.txt
```

## Visualization

Rviz: [http://localhost:6080/vnc.html?autoconnect=1&resize=remote%e2%81%a0](http://localhost:6080/vnc.html?autoconnect=1&resize=remote%e2%81%a0)

# Teleoperation

## Setup

1. Dowload the VR headset app: https://www.meta.com/quest/setup/?srsltid=AfmBOorKOuGUIU7NR95vBQ4dcVi464ir4qGZndC4WYzo4wcg1Jpg4bKb
  - Connect the VR headset to the local machine 
  - Make sure that you can display the computer screen in the VR headset world
2. Install the Pollen Reachy latest VR application: https://github.com/pollen-robotics/Reachy2Teleoperation/releases/latest/download/Reachy2Teleoperation_installer.exe
  - Select the Complete installation for gstreamer
  - Launch the application Reachy2Teleoperation from your computer
  - Connect to the robot by setting the `robot name` = {anything} and `robot IP` = {either name `“r2-0008.local”` or IP `192.168.10.172`} 
  - Try connecting to reachy and verify if you see
    - a green text telling you “Connected to Reachy”
    - the view of the robot displayed in miniature
    - a good network connection indication
3. If the "Connection Failed" once entering the transition room with "motor","audio", and other configurations not being connected then:
  - Need to install gstreamer correctly: [https://gstreamer.freedesktop.org/data/pkg/windows/1.27.90/msvc/?__goaway_challenge=meta-refresh&__goaway_id=9cf305064589a1220ab9c6f4cbaec4b1&__goaway_referer=https%3A%2F%2Fforum.pollen-robotics.com%2F](https://gstreamer.freedesktop.org/data/pkg/windows/1.27.90/msvc/?__goaway_challenge=meta-refresh&__goaway_id=9cf305064589a1220ab9c6f4cbaec4b1&__goaway_referer=https%3A%2F%2Fforum.pollen-robotics.com%2F)
    - gstreamer-1.0-msvc-x86_64-1.27.90.msi            2026-01-08 01:17     89M    
    - gstreamer-1.0-devel-msvc-x86_64-1.27.90.msi    2026-01-08 01:13     317M
  - After that we need to setup windows path environmental variables: 
  - Restart PowerShell and verify if the gstreamer is correctly setup: 
4. If experiencing issues with VR headset not properly moving the arms and not reflecting that in the teleoperation app then:
  - Set the VR flag environmental variable: 

## Dataset Recording
### Recording
```
lerobot-record `
--robot.type=reachy2 `
--robot.ip_address=192.168.137.162 `
--robot.id=r2-0008 `
--robot.use_external_commands=true `
--robot.with_mobile_base=true `
--robot.with_l_arm=true `
--robot.with_r_arm=true `
--robot.with_neck=true `
--robot.with_antennas=true `
--robot.with_left_teleop_camera=false `
--robot.with_right_teleop_camera=false `
--robot.with_torso_camera=false `
--robot.camera_width=640 `
--robot.camera_height=480 `
--robot.disable_torque_on_disconnect=false `
--robot.max_relative_target=5.0 `
--teleop.type=reachy2_teleoperator `
--teleop.ip_address=192.168.137.162 `
--teleop.use_present_position=true `
--teleop.with_mobile_base=true `
--teleop.with_l_arm=true `
--teleop.with_r_arm=true `
--teleop.with_neck=true `
--teleop.with_antennas=true `
--dataset.repo_id=pollen_robotics/record_test `
--dataset.single_task="Reachy 2 recording test" `
--dataset.num_episodes=1 `
--dataset.episode_time_s=10 `
--dataset.fps=30 `
--dataset.push_to_hub=false `
--dataset.private=true `
--dataset.streaming_encoding=false `
--dataset.encoder_threads=8 `
--display_data=false
```

Higher Frequency Setup
- Windows
```
lerobot-record `
--robot.type=reachy2 `
--robot.ip_address=192.168.137.162 `
--robot.id=r2-0008 `
--robot.use_external_commands=true `
--robot.with_mobile_base=false `
--robot.with_l_arm=true `
--robot.with_r_arm=true `
--robot.with_neck=true `
--robot.with_antennas=false `
--robot.with_left_teleop_camera=false `
--robot.with_right_teleop_camera=false `
--robot.with_torso_camera=true `
--robot.camera_width=640 `
--robot.camera_height=480 `
--teleop.type=reachy2_teleoperator `
--teleop.ip_address=192.168.137.162 `
--teleop.use_present_position=true `
--teleop.with_mobile_base=false `
--teleop.with_l_arm=true `
--teleop.with_r_arm=true `
--teleop.with_neck=true `
--teleop.with_antennas=false `
--dataset.repo_id=erl-hub/reachy-pick-and-place-test `
--dataset.root="outputs\reachy_local_test" `
--dataset.single_task="Reachy 2 pick and place test" `
--dataset.num_episodes=1 `
--dataset.episode_time_s=40 `
--dataset.fps=15 `
--dataset.vcodec=h264 `
--dataset.streaming_encoding=false `
--dataset.push_to_hub=false `
--display_data=false `
--resume=false
```

-Linux
```
lerobot-record \
  --robot.type=reachy2 \
  --robot.ip_address="localhost" \
  --robot.id="r2-0008" \
  --robot.use_external_commands=true \
  --robot.with_mobile_base=false \
  --robot.with_l_arm=true \
  --robot.with_r_arm=true \
  --robot.with_neck=true \
  --robot.with_antennas=false \
  --robot.with_left_teleop_camera=false \
  --robot.with_right_teleop_camera=false \
  --robot.with_torso_camera=true \
  --robot.camera_width=640 \
  --robot.camera_height=480 \
  --teleop.type=reachy2_teleoperator \
  --teleop.ip_address="localhost" \
  --teleop.use_present_position=true \
  --teleop.with_mobile_base=false \
  --teleop.with_l_arm=true \
  --teleop.with_r_arm=true \
  --teleop.with_neck=true \
  --teleop.with_antennas=false \
  --dataset.repo_id="erl-hub\reachy-pick-and-place-test2" \
  --dataset.root="outputs\reachy_local_test" \
  --dataset.single_task="Reachy 2 local recording" \
  --dataset.num_episodes=1 \
  --dataset.episode_time_s=45 \
  --dataset.fps=15 \
  --dataset.vcodec=h264 \
  --dataset.push_to_hub=false \
  --display_data=false \
  --play_sounds=false \
  --resume=false
```

```
docker run -dit \
  --name lerobot_container \
  --net=host \
  --pid=host \
  -v $(pwd)/robot_reachy2.py:/lerobot/src/lerobot/robots/reachy2/robot_reachy2.py \
  huggingface/lerobot-cpu \
  sleep infinity    
```

- Remove or rename dataset after every recording:

```
Remove-Item -Recurse -Force "C:\Users\nikra\.cache\huggingface\lerobot\erl-hub\reachy-pick-and-place"
Remove-Item -Recurse -Force "C:\Users\nikra\.cache\huggingface\lerobot\erl-hub\reachy-pick-and-place-images"
```


### Upload the datasets
```
# Navigate to the data
cd "C:\Users\nikra\.cache\huggingface\lerobot\erl-hub\reachy-pick-and-place"

# Use the dedicated CLI uploader (often bypasses API timeouts)
huggingface-cli upload erl-hub/reachy-pick-and-place . . --repo-type=dataset
```

### Profiling
```
Get-Process | Where-Object {$_.ProcessName -like "*python*"}
```

```
py-spy record -o lerobot_profile.svg --pid 24016
```

### Replaying
- Locally
```
lerobot-replay `
    --robot.type=reachy2 `
    --robot.ip_address=192.168.137.162 `
    --robot.id=r2-0008 `
    --robot.use_external_commands=false `
    --robot.with_mobile_base=false `
    --robot.with_l_arm=true `
    --robot.with_r_arm=true `
    --robot.with_neck=true `
    --dataset.repo_id=erl-hub/reachy-pick-and-place-test `
    --dataset.root=outputs\reachy_local_test `
    --dataset.episode=0
```

- Hub
```
lerobot-replay `
--robot.type=reachy2 `
--robot.ip_address=192.168.137.162 `
--robot.id=r2-0008 `
--robot.use_external_commands=false `
--robot.with_mobile_base=false `
--robot.with_l_arm=true `
--robot.with_r_arm=true `
--robot.with_neck=true `
--robot.with_antennas=false `
--dataset.repo_id="erl-hub/reachy-pick-and-place" `
--dataset.episode=4
```

## Training policies:

### Training locally

#### Ensure that ffmpeg is installed as follows for training models locally
```
sudo apt update && sudo apt upgrade -y
sudo add-apt-repository ppa:ubuntuhandbook1/ffmpeg7
sudo apt update
sudo apt install ffmpeg -y
```

#### Convert dataset to required format
```
python -m lerobot.datasets.v30.convert_dataset_v21_to_v30 --repo-id=pollen-robotics/pick_and_place_bottle && \
```

#### Start training
```
lerobot-train --dataset.repo_id=pollen-robotics/pick_and_place_bottle --policy.type=act --job_name=reachy2_lerobot_act --wandb.enable=false --policy.device=cuda --policy.push_to_hub=false"
```

### Training on Nautilus cluster
LeRobot-on-Nautilus code lives under `(nautilus/training/)`: the launcher `(nautilus/training/launch_nautilus_pods.py)`, Kubernetes Pod/Job templates (`db-lerobot-*.yaml`), and `(nautilus/training/queue_watcher.py)` for job queuing.

Each training container: creates a Conda env, installs FFmpeg and the right `lerobot[...]` extras, converts the dataset from v2.1 to v3.0 when needed, then runs `lerobot-train` on CUDA with Weights & Biases enabled and `policy.push_to_hub=false` (override or extend with `--train_extra`).

**Weights & Biases:** The Pod and Job templates inject `WANDB_API_KEY` from a Kubernetes secret named `wandb-secret` (key `api-key`). Create it once in your namespace so runs can log to your W&B workspace—for example:

```
kubectl create secret generic wandb-secret-nikola --from-literal=api-key=<YOUR_WANDB_API_KEY>
```

Without that secret, runs will not show up under your W&B account, or training may fail if not key is found.

**Supported policy:** use `act` or `groot` for real training runs. The launcher also accepts `pi05`, but this is **not fully functional yet and is not supported** in this workflow.


| Option                  | Short | Description                                                                                                                                                                      |
| ----------------------- | ----- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--dataset`             | `-d`  | Hugging Face dataset repo id (required unless `--algo DUMMY`).                                                                                                                   |
| `--algo`                | `-a`  | `act` , `groot`  — supported. `pi05` — experimental in the launcher only; not supported yet. `DUMMY` — long-running sleep pod for cluster tests; ignores `--jobs`. |
| `--repeat`              | `-nr` | Number of runs, each with a random seed (default `1`).                                                                                                                           |
| `--jobs`                | `-j`  | Use a Kubernetes **Job** instead of a **Pod** (template `db-lerobot-job.yaml`).                                                                                                  |
| `--yaml_file`           | `-y`  | Custom path to Pod or Job YAML template (defaults: templates next to the launcher, `db-lerobot-pod.yaml` / `db-lerobot-job.yaml` under `nautilus/training/`).                    |
| `--namespace_pod_limit` | `-nl` | **Jobs only:** max active pods counted in the namespace; extra jobs are created **suspended** and unsuspended when capacity appears (`0` = no queuing).                          |
| `--max_concurrent`      | `-mc` | **Jobs with queuing:** cap how many of *our* jobs run at once (`0` = only the namespace limit applies).                                                                          |
| `--dry_run`             |       | Print the generated container script and exit (no `kubectl`).                                                                                                                    |
| `--state_only_act`      |       | For ACT on proprio-only data, adds `--rename_map='{"observation.state":"observation.environment_state"}'` to training.                                                           |
| `--train_extra`         |       | Single string of extra arguments appended to `lerobot-train` (quote carefully in your shell).                                                                                    |
| `--save_models`         |       | Persist training outputs: creates a timestamped `--output_dir` under the PVC (default base `--models_root`).                                                                     |
| `--models_root`         |       | Base directory on the pod for saved runs when `--save_models` is set (default `/pers_vol/dwait/saved_models/lerobot`).                                                           |


**Queuing:** If you use `--jobs` and set `--namespace_pod_limit` to a positive value, the launcher labels jobs with a queue group, starts as many as fit, and keeps unsuspending the rest as pods finish. If you interrupt that process (e.g. Ctrl+C), re-attach with `(nautilus/training/queue_watcher.py)` using the printed `--label` and the same `-nl` (and concurrency) you used at launch.

#### Examples

Train an image-based ACT policy on `pollen-robotics/pick_and_place_bottle`:
```
python nautilus/training/launch_nautilus_pods.py -a act -d pollen-robotics/pick_and_place_bottle
```

Train an image-based ACT policy on datasets and saving it to HuggingFace:
```
python nautilus/training/launch_nautilus_pods.py -a act -d erl-hub/reachy-pick-and-place-images -j --save_models --upload_to_hub --hf_model_repo erl-hub/reachy-act --train_extra "--steps=100000 --eval_freq=20000 --wandb.enable=false"
```

Dry-run the generated container script (no cluster submit):

```
python nautilus/training/launch_nautilus_pods.py --dry_run -a act -d pollen-robotics/pick_and_place_bottle
```

Submit three seeded Jobs with a namespace cap of 200 pods (queued jobs unsuspend as capacity frees):

```
python nautilus/training/launch_nautilus_pods.py -j -nl 200 -nr 3 -a act -d pollen-robotics/pick_and_place_bottle
```

### Deploying policies on reachy2
Pass the repo for trained policy best checkpoint as `policy.path`. Videos and trajectories from rollouts will be saved at `dataset.repo_id`

```
lerobot-record `
  --robot.type=reachy2 `
  --robot.ip_address="192.168.137.162" `
  --robot.id="r2-0008" `
  --robot.use_external_commands=false `
  --robot.with_mobile_base=false `
  --robot.with_l_arm=true `
  --robot.with_r_arm=true `
  --robot.with_neck=true `
  --robot.with_antennas=false `
  --robot.with_left_teleop_camera=false `
  --robot.with_right_teleop_camera=false `
  --robot.with_torso_camera=true `
  --robot.camera_width=640 `
  --robot.camera_height=480 `
  --policy.path=erl-hub/reachy-act-execute-pick-and-place `
  --dataset.repo_id="erl-hub/eval_reachy-pick-and-place" `
  --dataset.root="outputs/reachy_local_test" `
  --dataset.single_task="Reachy 2 rollout local recording" `
  --dataset.num_episodes=1 `
  --dataset.episode_time_s=120 `
  --dataset.fps=15 `
  --dataset.vcodec=h264 `
  --dataset.push_to_hub=false `
  --play_sounds=false `
  --resume=true
```

### Policy registry

Use this table to track policies you train or deploy. Extend rows as you add methods; replace placeholders with your checkpoints, parameter counts, and run notes.

| Policy | Method | Size | Hardware | 
| ------ | ------ | ---- | -------- | 
| `act` | Action Chunking Transformer (`--policy.type=act`) | 250MB | CPU; Intel Core 9 (RTX GeForce 2080+)||


























#### Groot
```
apt-get update && apt-get install -y wget ca-certificates git build-essential

# Install miniconda
wget -q https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh
bash /tmp/miniconda.sh -b -p /opt/miniconda
eval "$(/opt/miniconda/bin/conda shell.bash hook)"
conda create -y -n lerobot python=3.12                  # Accept terms of service using the commands in error message
conda activate lerobot

conda install -y -c conda-forge ffmpeg=7.1.1

pip install 'lerobot[reachy2]'
pip install torch==2.7.1 torchvision==0.22.1 torchaudio==2.7.1 --index-url https://download.pytorch.org/whl/cu126    
pip install "ninja>=1.11.1,<2.0.0" "packaging>=24.2,<26.0"


# Build flash-attn
export MAX_JOBS=4
export TORCH_CUDA_ARCH_LIST="7.5"  
pip install "flash-attn>=2.5.9,<3.0.0" --no-build-isolation
pip 

# Finally, install lerobot with groot and reachy2 support
pip install "lerobot[reachy2,groot]==0.5.1"


# Verify
python -c "import torch; print(torch.__version__, torch.version.cuda, torch.cuda.is_available())"
python -c "import flash_attn; print('flash-attn OK')"


# Train
python -m lerobot.scripts.convert_dataset_v21_to_v30 --repo-id pollen-robotics/pick_and_place_bottle

lerobot-train \
  --dataset.repo_id='pollen-robotics/pick_and_place_bottle' \
  --policy.type=groot \
  --job_name='reachy2_groot_pick_and_place_bottle' \
  --policy.device=cuda \
  --wandb.enable=true \
  --policy.push_to_hub=false

```




conda install -y -c conda-forge ffmpeg=7.1.1
pip install --upgrade pip setuptools==80.10.2
pip install "lerobot[reachy2,groot]==0.5.1"

pip install --force-reinstall \
  torch==2.7.1 torchvision==0.22.1 torchaudio==2.7.1 \
  --index-url https://download.pytorch.org/whl/cu126

# pin transformers only, without letting pip re-resolve torch
pip install --force-reinstall --no-deps transformers==4.52.4
pip install --force-reinstall --no-deps accelerate==1.13.0


# flash-attn (if needed)
pip install "ninja>=1.11.1,<2.0.0" "packaging>=24.2,<26.0"
pip install "flash-attn>=2.5.9,<3.0.0" --no-build-isolation

pip install --force-reinstall --no-deps tokenizers==0.21.4
pip install --force-reinstall --no-deps numpy==2.2.6 setuptools==80.10.2

pip install --force-reinstall --no-deps \
  "huggingface-hub==0.36.2" \
  "fsspec==2026.2.0" \
  "packaging==25.0"

pip install --force-reinstall --no-deps \
  "transformers==4.56.2" \
  "tokenizers==0.21.4" \
  "huggingface-hub==0.36.2"

pip install --force-reinstall --no-deps tokenizers==0.22.2

pip install -U decord

pip install -U av

pip install --force-reinstall --no-deps "av==15.1.0"

pip install --force-reinstall --no-deps \
  "transformers==4.57.1" \
  "tokenizers==0.22.2" \
  "huggingface-hub==0.36.2"

pip install --force-reinstall --no-deps \
  "transformers==4.57.6" \
  "tokenizers==0.22.2" \
  "huggingface-hub==0.36.2"

lerobot-train   --dataset.repo_id='pollen-robotics/pick_and_place_bottle'   --dataset.video_backend=pyav   --policy.type=groot   --job_name='reachy2_groot_smoke'   --policy.device=cuda   --wandb.enable=true   --policy.push_to_hub=false   --batch_size=2   --policy.batch_size=8   --num_workers=2   --policy.dataloader_num_workers=2   --steps=200   --save_freq=200












# NOVA
apt-get update && apt-get install -y wget ca-certificates git build-essential
wget -q https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh
bash /tmp/miniconda.sh -b -p /opt/miniconda
eval "$(/opt/miniconda/bin/conda shell.bash hook)"

git clone https://github.com/NVIDIA/Isaac-GR00T
cd Isaac-GR00T

conda create -n gr00t python=3.10
conda activate gr00t
pip install --upgrade setuptools
pip install -e .[base]
pip install --no-build-isolation flash-attn==2.7.1.post4 

pip install torch==2.7.1 torchvision==0.22.1 torchaudio==2.7.1 --index-url https://download.pytorch.org/whl/cu126 
pip install psutil ninja packaging
pip install "flash-attn==2.7.4.post1" --no-build-isolation

pip install -U pip setuptools wheel

git clone --recurse-submodules https://github.com/ganatrask/NOVA.git
cd NOVA/
git submodule update --init --recursive
cd Isaac-GR00T/
patch -p1 < ../patches/add_reachy2_embodiment.patch
pip install -e .

apt-get update && apt-get install -y openmpi-bin libopenmpi-dev
pip install mpi4py
apt-get update && apt-get install -y ffmpeg libavcodec-dev libavformat-dev libavutil-dev

hf download ganatrask/NOVA --local-dir /workspace/data/reachy2_100 --repo-type=dataset
python -m gr00t.experiment.launch_finetune --base-model-path nvidia/GR00T-N1.6-3B --dataset-path /workspace/data/reachy2_100/ --embodiment-tag REACHY2   --modality-config-path /workspace/NOVA/configs/reachy2_modality_config.py --num-gpus 1 --global-batch-size 32 --max-steps 30000 --save-steps 3000 --output-dir ./checkpoints/groot-reachy2


#Upload
hf auth login
hf repo create erl-hub/reachy-groot --type model --private   # once, if needed
hf upload erl-hub/reachy-groot-NOVA ./checkpoints/groot-reachy2/checkpoint-30000 . --repo-type model