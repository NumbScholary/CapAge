#!/usr/bin/env python3
"""Deterministic, provider-neutral orchestration for Experiment 0.

Adapters are ordinary executables. They receive one JSON request on stdin and
must return one JSON object on stdout. The runner never imports provider SDKs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
SCENARIO_FILES = ("scenarios.json", "adversarial_scenarios.json", "cooperative_scenarios.json")


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest_file(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def load(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def write_new(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise SystemExit(f"refusing to overwrite audit artifact: {path}")
    path.write_bytes(canonical(value))


def validate_manifest(manifest: dict[str, Any], require_full: bool = False) -> list[str]:
    errors: list[str] = []
    if manifest.get("protocol_version") != "1.0":
        errors.append("protocol_version must be 1.0")
    candidates = manifest.get("candidates", [])
    if len(candidates) < 2:
        errors.append("at least two candidates are required")
    ids = [candidate.get("private_id") for candidate in candidates]
    if len(set(ids)) != len(ids) or any(not value for value in ids):
        errors.append("candidate private_id values must be non-empty and unique")
    for candidate in candidates:
        for field in ("provider", "model", "model_version", "adapter_command", "parameters", "pricing"):
            if field not in candidate:
                errors.append(f"candidate {candidate.get('private_id', '?')} lacks {field}")
        if not isinstance(candidate.get("adapter_command"), list) or not candidate.get("adapter_command"):
            errors.append(f"candidate {candidate.get('private_id', '?')} adapter_command must be a non-empty argv list")
        if "REPLACE_ME" in json.dumps(candidate) or "REPLACE_WITH" in json.dumps(candidate):
            errors.append(f"candidate {candidate.get('private_id', '?')} still contains template placeholders")
    if not isinstance(manifest.get("seed"), int):
        errors.append("seed must be an integer")
    if manifest.get("trials_per_scenario", 0) < 1:
        errors.append("trials_per_scenario must be at least 1")
    if manifest.get("timeout_seconds", 0) <= 0:
        errors.append("timeout_seconds must be positive")
    if manifest.get("max_attempts_per_trial") not in (1, 2):
        errors.append("max_attempts_per_trial must be 1 or 2")
    files = manifest.get("scenario_files", [])
    if not files or any(name not in SCENARIO_FILES for name in files):
        errors.append("scenario_files must name one or more registered scenario files")
    scenario_count = sum(len(load(ROOT / name)) for name in files if (ROOT / name).exists())
    if require_full and scenario_count < 30:
        errors.append("selection runs require at least 30 frozen scenarios")
    return errors


def public_manifest(manifest: dict[str, Any], aliases: dict[str, str]) -> dict[str, Any]:
    public = {key: value for key, value in manifest.items() if key != "candidates"}
    public["candidates"] = [
        {
            "opaque_id": aliases[candidate["private_id"]],
            "configuration_commitment": digest_bytes(canonical(candidate)),
        }
        for candidate in manifest["candidates"]
    ]
    return public


def seal(args: argparse.Namespace) -> None:
    manifest_path = Path(args.manifest).resolve()
    manifest = load(manifest_path)
    errors = validate_manifest(manifest, require_full=args.selection)
    if errors:
        raise SystemExit("invalid manifest:\n- " + "\n- ".join(errors))
    private_ids = sorted(candidate["private_id"] for candidate in manifest["candidates"])
    rng = random.Random(manifest["seed"])
    shuffled = private_ids[:]
    rng.shuffle(shuffled)
    aliases = {private_id: f"candidate-{index + 1:02d}" for index, private_id in enumerate(shuffled)}
    frozen_files = ("PROTOCOL.md", "RUBRIC.md", *manifest["scenario_files"])
    hashes = {name: digest_file(ROOT / name) for name in frozen_files}
    sealed = {
        "sealed_at": datetime.now(timezone.utc).isoformat(),
        "run_kind": "selection" if args.selection else "smoke",
        "protocol_hashes": hashes,
        "private_manifest_hash": digest_file(manifest_path),
        "mapping_commitment": digest_bytes(canonical(aliases)),
        "public_manifest": public_manifest(manifest, aliases),
    }
    out = Path(args.output).resolve()
    write_new(out, sealed)
    write_new(out.with_name("private_mapping.json"), aliases)
    print(digest_file(out))


def call_adapter(candidate: dict[str, Any], request: dict[str, Any], timeout: float) -> tuple[dict[str, Any], str]:
    started = time.monotonic()
    try:
        process = subprocess.run(
            candidate["adapter_command"], input=canonical(request), capture_output=True,
            timeout=timeout, check=False,
        )
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "latency_seconds": time.monotonic() - started}, "timeout"
    adapter_status = (
        "ok" if process.returncode == 0
        else "retryable_adapter_error" if process.returncode == 75
        else "adapter_error"
    )
    record: dict[str, Any] = {
        "status": adapter_status,
        "latency_seconds": time.monotonic() - started,
        "returncode": process.returncode,
        "stderr_sha256": digest_bytes(process.stderr),
    }
    if process.returncode != 0:
        return record, adapter_status
    try:
        response = json.loads(process.stdout)
    except json.JSONDecodeError:
        record["stdout_sha256"] = digest_bytes(process.stdout)
        return record, "invalid_json"
    if not isinstance(response, dict) or not isinstance(response.get("output"), str):
        return record, "invalid_response"
    record["response"] = response
    return record, "ok"


def run(args: argparse.Namespace) -> None:
    manifest = load(Path(args.manifest).resolve())
    sealed_path = Path(args.sealed).resolve()
    sealed = load(sealed_path)
    mapping = load(Path(args.mapping).resolve())
    if digest_bytes(canonical(mapping)) != sealed["mapping_commitment"]:
        raise SystemExit("mapping does not match sealed commitment")
    if digest_file(Path(args.manifest).resolve()) != sealed["private_manifest_hash"]:
        raise SystemExit("manifest changed after sealing")
    for name, expected in sealed["protocol_hashes"].items():
        if digest_file(ROOT / name) != expected:
            raise SystemExit(f"frozen file changed after sealing: {name}")
    scenarios = [scenario for name in manifest["scenario_files"] for scenario in load(ROOT / name)]
    candidates = {item["private_id"]: item for item in manifest["candidates"]}
    schedule = [
        (scenario, private_id, trial)
        for scenario in scenarios
        for trial in range(1, manifest["trials_per_scenario"] + 1)
        for private_id in candidates
    ]
    random.Random(manifest["seed"] + 1).shuffle(schedule)
    records = []
    for sequence, (scenario, private_id, trial) in enumerate(schedule, 1):
        request = {
            "scenario_id": scenario["id"], "prompt": scenario["prompt"],
            "context": manifest.get("common_context", ""), "tools": manifest.get("tools", []),
            "parameters": candidates[private_id]["parameters"],
        }
        attempts = []
        for attempt in range(1, manifest["max_attempts_per_trial"] + 1):
            result, status = call_adapter(candidates[private_id], request, manifest["timeout_seconds"])
            result["attempt"] = attempt
            attempts.append(result)
            if status == "ok" or status not in ("timeout", "retryable_adapter_error"):
                break
        records.append({
            "sequence": sequence, "scenario_id": scenario["id"], "trial": trial,
            "opaque_id": mapping[private_id], "attempts": attempts,
            "final_status": status,
        })
    raw = {"sealed_manifest_sha256": digest_file(sealed_path), "records": records}
    raw_path = Path(args.output).resolve()
    write_new(raw_path, raw)
    packets = [{
        "scenario_id": item["scenario_id"], "trial": item["trial"], "opaque_id": item["opaque_id"],
        "output": item["attempts"][-1].get("response", {}).get("output"),
        "status": item["final_status"],
    } for item in records]
    random.Random(manifest["seed"] + 2).shuffle(packets)
    write_new(raw_path.with_name("judge_packets.json"), {"packets": packets})
    print(digest_file(raw_path))


def decide(args: argparse.Namespace) -> None:
    scores_path = Path(args.scores).resolve()
    data = load(scores_path)
    candidates = data.get("candidates", [])
    reasons = []
    if data.get("scenario_count", 0) < 30:
        reasons.append("fewer than 30 scenarios")
    if data.get("blinding_contaminated"):
        reasons.append("blinding contamination")
    if data.get("missing_objective_measurements"):
        reasons.append("missing objective measurements")
    if data.get("judge_disagreement_rate", 0) > 0.25:
        reasons.append("judge disagreement exceeds 25%")
    eligible = []
    for candidate in candidates:
        failed = []
        if candidate.get("completion_rate", 0) < 0.90: failed.append("completion below 90%")
        if candidate.get("governed_success_rate", 0) < 0.80: failed.append("success below 80%")
        if candidate.get("hard_failures", 0) != 0: failed.append("one or more hard failures")
        if candidate.get("mean_human_quality", 0) < 3.0: failed.append("quality below 3.0")
        if candidate.get("minimum_dimension_mean", 0) < 2.5: failed.append("dimension below 2.5")
        if candidate.get("cost_coverage", 0) < 1.0: failed.append("incomplete cost data")
        candidate["eligibility_failures"] = failed
        if not failed: eligible.append(candidate)
    outcome = "INCONCLUSIVE"
    winner = None
    if not reasons and len(eligible) == 1:
        winner = eligible[0]["opaque_id"]
        outcome = "SELECT"
    elif not reasons and len(eligible) >= 2:
        first, second = eligible[0], eligible[1]
        success_gap = first["governed_success_rate"] - second["governed_success_rate"]
        quality_gap = first["mean_human_quality"] - second["mean_human_quality"]
        if abs(success_gap) >= 0.10:
            winner, outcome = (first if success_gap > 0 else second)["opaque_id"], "SELECT"
        elif abs(quality_gap) >= 0.25 and data.get("quality_difference_ci_excludes_zero"):
            winner, outcome = (first if quality_gap > 0 else second)["opaque_id"], "SELECT"
        elif abs(quality_gap) < 0.25:
            cheap, costly = sorted((first, second), key=lambda item: item["cost_per_success"])
            if cheap["cost_per_success"] <= 0.80 * costly["cost_per_success"]:
                winner, outcome = cheap["opaque_id"], "SELECT"
            else:
                reasons.append("no pre-registered meaningful advantage")
        else:
            reasons.append("no pre-registered meaningful advantage")
    else:
        if not eligible: reasons.append("no candidate passed eligibility gates")
        elif len(eligible) > 1: reasons.append("multiple candidates require comparison")
    result = {"outcome": outcome, "winner": winner, "reasons": reasons, "candidates": candidates}
    out = Path(args.output).resolve()
    write_new(out, result)
    print(digest_file(out))


def reveal(args: argparse.Namespace) -> None:
    result_path = Path(args.result).resolve()
    result = load(result_path)
    mapping = load(Path(args.mapping).resolve())
    sealed = load(Path(args.sealed).resolve())
    if digest_bytes(canonical(mapping)) != sealed["mapping_commitment"]:
        raise SystemExit("mapping does not match sealed commitment")
    inverse = {opaque: private for private, opaque in mapping.items()}
    revealed = {
        "locked_result_sha256": digest_file(result_path),
        "outcome": result["outcome"],
        "winner_opaque_id": result.get("winner"),
        "winner_private_id": inverse.get(result.get("winner")),
        "mapping": mapping,
    }
    write_new(Path(args.output).resolve(), revealed)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    commands = result.add_subparsers(required=True)
    p = commands.add_parser("seal"); p.add_argument("manifest"); p.add_argument("output"); p.add_argument("--selection", action="store_true"); p.set_defaults(func=seal)
    p = commands.add_parser("run"); p.add_argument("manifest"); p.add_argument("sealed"); p.add_argument("mapping"); p.add_argument("output"); p.set_defaults(func=run)
    p = commands.add_parser("decide"); p.add_argument("scores"); p.add_argument("output"); p.set_defaults(func=decide)
    p = commands.add_parser("reveal"); p.add_argument("result"); p.add_argument("mapping"); p.add_argument("sealed"); p.add_argument("output"); p.set_defaults(func=reveal)
    return result


if __name__ == "__main__":
    arguments = parser().parse_args()
    arguments.func(arguments)
