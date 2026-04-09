#!/usr/bin/env python3
"""Launch Lerobot training on Nautilus (Kubernetes Pod or Job) with optional queueing."""

from __future__ import annotations

import copy
import json
import os
import random
import signal
import subprocess
import sys
import tempfile
import threading
from dataclasses import dataclass
from datetime import datetime
from typing import Annotated, Any, Dict, List, Optional

import tyro
import yaml

LEROBOT_ALGOS = frozenset({"act", "pi05", "groot"})
# Kubernetes label for queue grouping (must match queue_watcher.py).
LEROBOT_QUEUE_GROUP_LABEL_KEY = "lerobot_queue_group"

# region agent log
_DEBUG_LOG_PATH = "/home/dwait/dwait_ws/reachy_pollen/.cursor/debug-aded23.log"


def _agent_debug_log(
    message: str,
    data: Dict[str, Any],
    hypothesis_id: str,
    run_id: str = "pre-fix",
) -> None:
    import time

    payload = {
        "sessionId": "aded23",
        "timestamp": int(time.time() * 1000),
        "location": "launch_nautilus_pods.py",
        "message": message,
        "data": data,
        "hypothesisId": hypothesis_id,
        "runId": run_id,
    }
    try:
        with open(_DEBUG_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload) + "\n")
    except OSError:
        pass


# endregion


@dataclass
class NautilusPodConfig:
    dataset: Annotated[
        Optional[str],
        tyro.conf.arg(
            name="dataset",
            help="Hugging Face dataset repo id (e.g. pollen-robotics/pick_and_place_bottle). Not required for --algo DUMMY.",
            aliases=["-d"],
        ),
    ] = None

    algo: Annotated[
        str,
        tyro.conf.arg(
            name="algo",
            help="Policy: act, pi05, groot, or DUMMY (sleep pod for cluster tests).",
            aliases=["-a"],
        ),
    ] = "act"

    repeat: Annotated[
        int,
        tyro.conf.arg(
            name="repeat",
            help="Number of runs with different random seeds.",
            aliases=["-nr"],
        ),
    ] = 1

    jobs: Annotated[
        bool,
        tyro.conf.arg(
            name="jobs",
            help="Launch as Kubernetes Job instead of Pod.",
            aliases=["-j"],
        ),
    ] = False

    yaml_file: Annotated[
        Optional[str],
        tyro.conf.arg(
            name="yaml_file",
            help="Path to Job or Pod YAML template.",
            aliases=["-y"],
        ),
    ] = None

    namespace_pod_limit: Annotated[
        int,
        tyro.conf.arg(
            name="namespace_pod_limit",
            help="Max active pods in namespace; extra jobs submit suspended (0 = no limit). Jobs only.",
            aliases=["-nl"],
        ),
    ] = 0

    max_concurrent: Annotated[
        int,
        tyro.conf.arg(
            name="max_concurrent",
            help="Max of our jobs running at once (0 = only namespace limit applies).",
            aliases=["-mc"],
        ),
    ] = 0

    dry_run: Annotated[
        bool,
        tyro.conf.arg(
            name="dry_run",
            help="Print the container bash script and exit (no kubectl).",
        ),
    ] = False

    state_only_act: Annotated[
        bool,
        tyro.conf.arg(
            name="state_only_act",
            help="For ACT on proprio-only datasets, remap observation.state -> observation.environment_state.",
        ),
    ] = False

    train_extra: Annotated[
        Optional[str],
        tyro.conf.arg(
            name="train_extra",
            help="Extra raw args appended to lerobot-train (quoted as a single string).",
        ),
    ] = None


@dataclass
class ContainerSpec:
    name: str
    shell_body: str

    def to_k8s_container(self, template_container: Dict[str, Any]) -> Dict[str, Any]:
        out = copy.deepcopy(template_container)
        out["name"] = self.name
        out["command"] = ["/bin/bash", "-c"]
        out["args"] = [f"set -euo pipefail && \\\n{self.shell_body}"]
        return out


def _normalize_algo(raw: str) -> str:
    a = raw.strip().upper()
    if a == "DUMMY":
        return "DUMMY"
    lower = raw.strip().lower()
    if lower in LEROBOT_ALGOS:
        return lower
    raise ValueError(f"Unknown --algo {raw!r}; expected one of act, pi05, groot, DUMMY")


def _dataset_slug(dataset: str) -> str:
    return dataset.replace("/", "-").replace("_", "-").lower()


def _bash_single_quote(s: str) -> str:
    """Safe inside bash single-quoted string."""
    return s.replace("'", "'\"'\"'")


def build_lerobot_script(
    dataset: str, policy_type: str, job_name: str, state_only_act: bool = False, train_extra: Optional[str] = None
) -> str:
    """Bash body (after set -e): conda env, ffmpeg, pip extras, convert, train (Nautilus image)."""
    repo = _bash_single_quote(dataset)
    if policy_type == "act":
        pip_install = "pip install 'lerobot[reachy2]'"
    elif policy_type == "groot":
        pip_install = (
            "pip install flash-attn --no-build-isolation && pip install 'lerobot[reachy2,groot]'"
        )
    elif policy_type == "pi05":
        pip_install = "pip install 'lerobot[reachy2,pi]'"
    else:
        raise ValueError(policy_type)
    # lerobot>=~0.5: convert lives under lerobot.scripts; 0.4.x uses lerobot.datasets.v30
    convert_dual = (
        f"if python -c \"import importlib.util as u, sys; "
        f"sys.exit(0 if u.find_spec('lerobot.scripts.convert_dataset_v21_to_v30') else 1)\"; then \\\n"
        f"  python -m lerobot.scripts.convert_dataset_v21_to_v30 --repo-id='{repo}' --push-to-hub 0; \\\n"
        f"else \\\n"
        f"  python -m lerobot.datasets.v30.convert_dataset_v21_to_v30 --repo-id='{repo}' --push-to-hub 0; \\\n"
        f"fi"
    )
    # region agent log
    _agent_debug_log(
        "build_lerobot_script convert step",
        {
            "policy_type": policy_type,
            "dataset": dataset,
            "strategy": "dual_path_scripts_or_datasets_v30",
        },
        "H1",
    )
    # endregion
    train_cmd = (
        f"lerobot-train --dataset.repo_id='{repo}' --policy.type={policy_type} --job_name={job_name} "
        f"--wandb.enable=true --policy.device=cuda --policy.push_to_hub=false"
    )
    if policy_type == "act" and state_only_act:
        train_cmd += " --rename_map='{\"observation.state\":\"observation.environment_state\"}'"
    if train_extra:
        train_cmd += f" {train_extra.strip()}"

    # region agent log
    _agent_debug_log(
        "act proprioception mode resolution",
        {
            "policy_type": policy_type,
            "state_only_act": state_only_act,
            "uses_rename_map": bool(policy_type == "act" and state_only_act),
            "has_train_extra": bool(train_extra and train_extra.strip()),
        },
        "H2",
    )
    # endregion
    # region agent log
    _agent_debug_log(
        "final lerobot-train command built",
        {
            "contains_rename_map": "--rename_map" in train_cmd,
            "command_preview": train_cmd[:400],
        },
        "H3",
    )
    # endregion
    return f"""conda create -y -n lerobot python=3.12 && \\
source /opt/conda/etc/profile.d/conda.sh && conda activate lerobot && \\
export LD_LIBRARY_PATH=/opt/conda/envs/lerobot/lib:$LD_LIBRARY_PATH && \\
conda install -y ffmpeg=7.1.1 -c conda-forge && \\
{pip_install} && \\
{convert_dual} && \\
{train_cmd}"""


def build_dummy_script() -> str:
    return "sleep 21600"


class NautilusResource:
    def __init__(self, name: str, containers: List[ContainerSpec], is_job: bool = False):
        self.name = name
        self.containers = containers
        self.is_job = is_job

    def generate_yaml_config(
        self,
        template_file: str,
        suspend: bool = False,
        queue_group_label: Optional[str] = None,
    ) -> str:
        with open(template_file, "r") as f:
            config = yaml.safe_load(f)

        config["metadata"]["name"] = self.name
        if queue_group_label:
            config.setdefault("metadata", {}).setdefault("labels", {})
            config["metadata"]["labels"][LEROBOT_QUEUE_GROUP_LABEL_KEY] = queue_group_label

        if self.is_job:
            spec_inner = config["spec"]["template"]["spec"]
            base_c = spec_inner["containers"][0]
            spec_inner["containers"] = [c.to_k8s_container(base_c) for c in self.containers]
            config["spec"]["backoffLimit"] = 25
            if suspend:
                config["spec"]["suspend"] = True
            else:
                config["spec"].pop("suspend", None)
        else:
            spec_inner = config["spec"]
            base_c = spec_inner["containers"][0]
            spec_inner["containers"] = [c.to_k8s_container(base_c) for c in self.containers]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as tmp:
            yaml.safe_dump(config, tmp, default_flow_style=False, sort_keys=False)
            return tmp.name

    def launch(
        self,
        template_file: str,
        suspend: bool = False,
        queue_group_label: Optional[str] = None,
    ) -> bool:
        path = self.generate_yaml_config(
            template_file, suspend=suspend, queue_group_label=queue_group_label
        )
        try:
            subprocess.run(["kubectl", "apply", "-f", path], check=True)
            kind = "job" if self.is_job else "pod"
            state = " (suspended)" if suspend else ""
            print(f"Launched {kind}{state}: {self.name}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to launch {self.name}: {e}")
            return False
        finally:
            os.unlink(path)


class NautilusPod(NautilusResource):
    def __init__(self, name: str, containers: List[ContainerSpec]):
        super().__init__(name, containers, is_job=False)


class NautilusJob(NautilusResource):
    def __init__(self, name: str, containers: List[ContainerSpec]):
        super().__init__(name, containers, is_job=True)


def make_resource_name(ts: str, algo: str, slug: str, repeat_idx: int, repeat_total: int, seed: int) -> str:
    """RFC 1123-ish: max 63 chars for DNS label; keep short."""
    algo_p = algo.lower().replace("_", "-")
    part = f"lerobot-{ts}-{algo_p}-s{seed}"
    if repeat_total > 1:
        part = f"{part}-r{repeat_idx + 1}of{repeat_total}"
    if slug:
        part = f"{part}-{slug}"[:62].rstrip("-")
    return part[:63].strip("-")


# --- Queue (label LEROBOT_QUEUE_GROUP_LABEL_KEY; must match queue_watcher.py) ---


def get_active_pod_count() -> int:
    try:
        result = subprocess.run(
            ["kubectl", "get", "pods", "-o", "json"],
            capture_output=True,
            text=True,
            check=True,
        )
        pods = json.loads(result.stdout)
        n = 0
        for pod in pods.get("items", []):
            phase = pod.get("status", {}).get("phase", "")
            if phase in ("Pending", "Running", "Unknown"):
                n += 1
        return n
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        print(f"Warning: failed to query pods: {e}")
        return 0


@dataclass
class OurJobStatuses:
    active_names: List[str]
    completed_names: List[str]
    suspended_names: List[str]


def get_our_job_statuses(queue_group_id: str) -> OurJobStatuses:
    try:
        result = subprocess.run(
            [
                "kubectl",
                "get",
                "jobs",
                "-l",
                f"{LEROBOT_QUEUE_GROUP_LABEL_KEY}={queue_group_id}",
                "-o",
                "json",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        data = json.loads(result.stdout)
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        print(f"Warning: failed to query jobs: {e}")
        return OurJobStatuses([], [], [])

    active, completed, suspended = [], [], []
    for job in data.get("items", []):
        name = job["metadata"]["name"]
        spec_suspended = job.get("spec", {}).get("suspend", False)
        conditions = job.get("status", {}).get("conditions", [])
        is_done = any(
            c.get("type") in ("Complete", "Failed") and c.get("status") == "True" for c in conditions
        )
        if is_done:
            completed.append(name)
        elif spec_suspended:
            suspended.append(name)
        else:
            active.append(name)
    return OurJobStatuses(active, completed, suspended)


def compute_available_slots(
    namespace_pod_limit: int,
    max_concurrent: int,
    active_pod_count: int,
    our_active_count: int,
) -> int:
    ns_slots = namespace_pod_limit - active_pod_count
    if max_concurrent > 0:
        our_slots = max_concurrent - our_active_count
        return max(0, min(ns_slots, our_slots))
    return max(0, ns_slots)


def unsuspend_jobs(job_names: List[str]) -> int:
    ok = 0
    for name in job_names:
        try:
            subprocess.run(
                ["kubectl", "patch", "job", name, "-p", '{"spec":{"suspend":false}}'],
                capture_output=True,
                text=True,
                check=True,
            )
            print(f"  Unsuspended job: {name}")
            ok += 1
        except subprocess.CalledProcessError as e:
            print(f"  Failed to unsuspend {name}: {e}")
    return ok


def monitor_and_unsuspend(
    queue_group_id: str,
    namespace_pod_limit: int,
    max_concurrent: int,
    poll_interval: int = 30,
) -> None:
    stop_event = threading.Event()

    def _sigint(_s, _f):
        stop_event.set()

    prev = signal.signal(signal.SIGINT, _sigint)
    try:
        while not stop_event.is_set():
            statuses = get_our_job_statuses(queue_group_id)
            active_pods = get_active_pod_count()
            total_ours = (
                len(statuses.active_names)
                + len(statuses.completed_names)
                + len(statuses.suspended_names)
            )
            print(
                f"\n[Queue] Namespace pods: {active_pods}/{namespace_pod_limit} | "
                f"Ours: {len(statuses.active_names)} running, "
                f"{len(statuses.completed_names)} done, "
                f"{len(statuses.suspended_names)} queued "
                f"({len(statuses.completed_names)}/{total_ours} complete)"
            )
            if not statuses.suspended_names and not statuses.active_names:
                print("[Queue] All jobs finished.")
                break
            if stop_event.is_set():
                print(
                    f"\n[Queue] Interrupted. {len(statuses.suspended_names)} jobs suspended. "
                    f"Re-attach: python nautilus_configs/queue_watcher.py "
                    f"--label {queue_group_id} -nl {namespace_pod_limit}"
                )
                break
            if statuses.suspended_names:
                slots = compute_available_slots(
                    namespace_pod_limit,
                    max_concurrent,
                    active_pods,
                    len(statuses.active_names),
                )
                if slots > 0:
                    batch = statuses.suspended_names[:slots]
                    print(f"  Unsuspending {len(batch)} job(s)...")
                    unsuspend_jobs(batch)
                else:
                    print(f"  No slots, waiting {poll_interval}s...")
            else:
                print(f"  Waiting for {len(statuses.active_names)} active job(s)...")
            stop_event.wait(timeout=poll_interval)
    finally:
        signal.signal(signal.SIGINT, prev)


def main() -> None:
    cfg = tyro.cli(NautilusPodConfig)
    algo = _normalize_algo(cfg.algo)

    if algo != "DUMMY" and not cfg.dataset:
        print("Error: --dataset is required unless --algo DUMMY", file=sys.stderr)
        sys.exit(1)

    use_job = cfg.jobs and algo != "DUMMY"
    nautilus_type = "job" if use_job else "pod"
    if cfg.yaml_file is None:
        yaml_path = f"nautilus_configs/db-lerobot-{nautilus_type}.yaml"
    else:
        yaml_path = cfg.yaml_file

    ts = datetime.now().strftime("%m%d-%H%M")
    queue_group_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    queuing = use_job and cfg.namespace_pod_limit > 0
    slug = _dataset_slug(cfg.dataset) if cfg.dataset else ""

    if cfg.dry_run:
        for i in range(cfg.repeat):
            seed = random.randint(1, 10000)
            if algo == "DUMMY":
                body = build_dummy_script()
                print(f"=== DUMMY run {i + 1}/{cfg.repeat} seed={seed} ===\n{body}\n")
            else:
                job_name = f"reachy2_lerobot_{algo}_s{seed}"
                body = build_lerobot_script(
                    cfg.dataset,
                    algo,
                    job_name,
                    state_only_act=cfg.state_only_act,
                    train_extra=cfg.train_extra,
                )
                print(f"=== {algo} run {i + 1}/{cfg.repeat} job_name={job_name} ===\n{body}\n")
        # region agent log
        _agent_debug_log(
            "dry_run finished",
            {"has_dual_convert": "lerobot.scripts.convert" in body and "datasets.v30" in body},
            "H1",
            run_id="post-fix",
        )
        # endregion
        return

    actual = cfg.repeat
    print(f"Launching {actual} {nautilus_type}(s) | template {yaml_path}")
    if algo == "DUMMY":
        print("  DUMMY: sleep pod (jobs flag ignored)")
    else:
        print(f"  dataset={cfg.dataset} algo={algo}")

    initial_slots = actual
    if queuing:
        ap = get_active_pod_count()
        initial_slots = compute_available_slots(
            cfg.namespace_pod_limit, cfg.max_concurrent, ap, 0
        )
        print(
            f"[Queue] Pods {ap}/{cfg.namespace_pod_limit} | slots {initial_slots} | group {queue_group_id}"
        )

    launched_active = 0
    launched_suspended = 0

    for i in range(actual):
        seed = random.randint(1, 10000)
        name = make_resource_name(ts, algo, slug, i, cfg.repeat, seed)

        if algo == "DUMMY":
            shell = build_dummy_script()
        else:
            job_name = f"reachy2_lerobot_{algo}_s{seed}"
            shell = build_lerobot_script(
                cfg.dataset,
                algo,
                job_name,
                state_only_act=cfg.state_only_act,
                train_extra=cfg.train_extra,
            )

        ctr = ContainerSpec(name=f"lerobot-{algo.lower()}-s{seed}", shell_body=shell)

        if use_job:
            res: NautilusResource = NautilusJob(name, [ctr])
        else:
            res = NautilusPod(name, [ctr])

        suspend = queuing and (launched_active >= initial_slots)
        ok = res.launch(
            yaml_path,
            suspend=suspend,
            queue_group_label=queue_group_id if queuing else None,
        )
        if ok:
            if suspend:
                launched_suspended += 1
            else:
                launched_active += 1

    if queuing and launched_suspended > 0:
        print(f"\n[Queue] {launched_active} active + {launched_suspended} suspended; monitoring...")
        monitor_and_unsuspend(queue_group_id, cfg.namespace_pod_limit, cfg.max_concurrent)
    elif queuing:
        print(f"\n[Queue] All {launched_active} jobs started without queuing.")


if __name__ == "__main__":
    main()
