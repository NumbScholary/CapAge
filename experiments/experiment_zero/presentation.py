#!/usr/bin/env python3
"""Create independently randomized, judge-visible Experiment 0 packets.

The stable candidate aliases used by the core runner remain private. Each
judge instead sees response-01 and response-02 labels that are local to one
scenario/trial packet. Presentation mappings are generated and committed
before candidate outputs exist.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
PRESENTATION_VERSION = "1.0"


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


def write_text_new(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise SystemExit(f"refusing to overwrite audit artifact: {path}")
    path.write_text(value, encoding="utf-8")


def load_scenarios(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    scenarios = [
        scenario
        for name in manifest["scenario_files"]
        for scenario in load(ROOT / name)
    ]
    identifiers = [scenario["id"] for scenario in scenarios]
    if len(identifiers) != len(set(identifiers)):
        raise SystemExit("scenario identifiers must be unique")
    return scenarios


def build_private_presentation(
    manifest: dict[str, Any],
    candidate_mapping: dict[str, str],
    scenarios: list[dict[str, Any]],
) -> dict[str, Any]:
    config = manifest.get("presentation", {})
    judge_count = config.get("judge_count")
    labels = config.get("display_labels")
    if judge_count != 2:
        raise SystemExit("selection presentation requires exactly two judges")
    if labels != ["response-01", "response-02"]:
        raise SystemExit("display_labels must be response-01 and response-02")
    opaque_ids = sorted(candidate_mapping.values())
    if len(opaque_ids) != 2:
        raise SystemExit("this pairwise presentation layer requires exactly two candidates")

    groups = [
        {"scenario_id": scenario["id"], "trial": trial}
        for scenario in scenarios
        for trial in range(1, manifest["trials_per_scenario"] + 1)
    ]
    judges: dict[str, list[dict[str, Any]]] = {}
    for judge_index in range(judge_count):
        judge_id = f"judge-{chr(ord('a') + judge_index)}"
        rng = random.Random(manifest["seed"] + 1000 + judge_index)
        packet_order = [dict(group) for group in groups]
        rng.shuffle(packet_order)

        # Balance the visible first position while keeping its per-packet
        # assignment unpredictable to a judge.
        orientations = [0] * (len(groups) // 2) + [1] * (len(groups) - len(groups) // 2)
        rng.shuffle(orientations)
        packets = []
        for group, orientation in zip(packet_order, orientations):
            ordered = opaque_ids if orientation == 0 else list(reversed(opaque_ids))
            packet_id = f"{judge_id}-{group['scenario_id']}-t{group['trial']:02d}"
            packets.append({
                "packet_id": packet_id,
                **group,
                "responses": [
                    {"display_id": labels[index], "opaque_id": opaque_id}
                    for index, opaque_id in enumerate(ordered)
                ],
            })
        judges[judge_id] = packets

    return {
        "presentation_version": PRESENTATION_VERSION,
        "source_manifest_sha256": None,
        "source_candidate_mapping_sha256": None,
        "label_scope": "per-scenario-trial",
        "balanced_first_position": True,
        "judges": judges,
    }


def seal(args: argparse.Namespace) -> None:
    manifest_path = Path(args.manifest).resolve()
    mapping_path = Path(args.candidate_mapping).resolve()
    manifest = load(manifest_path)
    candidate_mapping = load(mapping_path)
    scenarios = load_scenarios(manifest)
    private = build_private_presentation(manifest, candidate_mapping, scenarios)
    private["source_manifest_sha256"] = digest_file(manifest_path)
    private["source_candidate_mapping_sha256"] = digest_file(mapping_path)

    private_path = Path(args.private_output).resolve()
    write_new(private_path, private)
    commitment = {
        "presentation_version": PRESENTATION_VERSION,
        "private_presentation_mapping_sha256": digest_file(private_path),
        "source_manifest_sha256": digest_file(manifest_path),
        "source_candidate_mapping_sha256": digest_file(mapping_path),
        "scenario_file_sha256": {
            name: digest_file(ROOT / name) for name in manifest["scenario_files"]
        },
        "judge_ids": sorted(private["judges"]),
        "packets_per_judge": len(scenarios) * manifest["trials_per_scenario"],
        "response_labels": manifest["presentation"]["display_labels"],
        "label_scope": "per-scenario-trial",
        "balanced_first_position": True,
    }
    commitment_path = Path(args.commitment_output).resolve()
    write_new(commitment_path, commitment)
    print(digest_file(commitment_path))


def record_index(raw: dict[str, Any]) -> dict[tuple[str, int, str], dict[str, Any]]:
    result = {}
    for record in raw["records"]:
        key = (record["scenario_id"], record["trial"], record["opaque_id"])
        if key in result:
            raise SystemExit(f"duplicate raw record: {key}")
        result[key] = record
    return result


def build_judge_bundle(
    judge_id: str,
    presentation_packets: list[dict[str, Any]],
    scenarios: list[dict[str, Any]],
    raw: dict[str, Any],
    rubric_text: str,
    rubric_sha256: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    scenario_by_id = {scenario["id"]: scenario for scenario in scenarios}
    records = record_index(raw)
    packets = []
    score_packets = []
    for presentation_packet in presentation_packets:
        scenario = scenario_by_id[presentation_packet["scenario_id"]]
        visible_responses = []
        score_responses = []
        for response in presentation_packet["responses"]:
            key = (
                presentation_packet["scenario_id"],
                presentation_packet["trial"],
                response["opaque_id"],
            )
            if key not in records:
                raise SystemExit(f"presentation mapping lacks raw record: {key}")
            record = records[key]
            output = record["attempts"][-1].get("response", {}).get("output")
            visible_responses.append({
                "display_id": response["display_id"],
                "status": record["final_status"],
                "output": output,
            })
            score_responses.append({
                "display_id": response["display_id"],
                "scores": {
                    dimension: None for dimension in scenario["applicable_dimensions"]
                },
                "governed_objective_success": None,
                "hard_failure": None,
                "notes": "",
            })
        packets.append({
            "packet_id": presentation_packet["packet_id"],
            "scenario_id": scenario["id"],
            "trial": presentation_packet["trial"],
            "domain": scenario["domain"],
            "title": scenario["title"],
            "prompt": scenario["prompt"],
            "success_conditions": scenario["success_conditions"],
            "applicable_dimensions": scenario["applicable_dimensions"],
            "responses": visible_responses,
        })
        score_packets.append({
            "packet_id": presentation_packet["packet_id"],
            "scenario_id": scenario["id"],
            "trial": presentation_packet["trial"],
            "responses": score_responses,
        })
    bundle = {
        "experiment": "Experiment 0 full selection v1",
        "judge_id": judge_id,
        "instructions": (
            "Response numbers are local to each packet and are independently "
            "randomized. Do not infer a persistent model identity from response-01 "
            "or response-02. Score verbatim outputs using the frozen rubric."
        ),
        "rubric_sha256": rubric_sha256,
        "rubric": rubric_text,
        "packets": packets,
    }
    score_template = {
        "experiment": bundle["experiment"],
        "judge_id": judge_id,
        "blinding_contaminated": False,
        "packets": score_packets,
    }
    return bundle, score_template


def markdown_bundle(bundle: dict[str, Any]) -> str:
    lines = [
        f"# {bundle['experiment']} — {bundle['judge_id']}",
        "",
        f"> {bundle['instructions']}",
        "",
        "## Frozen scoring rubric",
        "",
        bundle["rubric"].rstrip(),
        "",
    ]
    for index, packet in enumerate(bundle["packets"], 1):
        lines.extend([
            f"## Packet {index}: {packet['scenario_id']} — {packet['title']}",
            "",
            "### Question",
            "",
            packet["prompt"],
            "",
            "### Success conditions",
            "",
            *[f"- {condition}" for condition in packet["success_conditions"]],
            "",
            "### Applicable dimensions",
            "",
            ", ".join(packet["applicable_dimensions"]),
            "",
        ])
        for response in packet["responses"]:
            display = response["display_id"].replace("-", " ").title()
            lines.extend([
                f"### {display}",
                "",
                "<!-- BEGIN VERBATIM MODEL OUTPUT -->",
                response["output"] or "",
                "<!-- END VERBATIM MODEL OUTPUT -->",
                "",
            ])
    return "\n".join(lines)


def structural_keys(value: Any) -> list[str]:
    keys: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            keys.append(key)
            keys.extend(structural_keys(item))
    elif isinstance(value, list):
        for item in value:
            keys.extend(structural_keys(item))
    return keys


def render(args: argparse.Namespace) -> None:
    manifest_path = Path(args.manifest).resolve()
    sealed_path = Path(args.sealed).resolve()
    candidate_mapping_path = Path(args.candidate_mapping).resolve()
    commitment_path = Path(args.presentation_commitment).resolve()
    private_path = Path(args.private_presentation).resolve()
    raw_path = Path(args.raw_trials).resolve()
    output_dir = Path(args.output_directory).resolve()

    manifest = load(manifest_path)
    sealed = load(sealed_path)
    candidate_mapping = load(candidate_mapping_path)
    commitment = load(commitment_path)
    private = load(private_path)
    raw = load(raw_path)

    if digest_file(private_path) != commitment["private_presentation_mapping_sha256"]:
        raise SystemExit("presentation mapping does not match pre-output commitment")
    if digest_file(manifest_path) != commitment["source_manifest_sha256"]:
        raise SystemExit("manifest changed after presentation seal")
    if digest_file(candidate_mapping_path) != commitment["source_candidate_mapping_sha256"]:
        raise SystemExit("candidate mapping changed after presentation seal")
    if digest_bytes(canonical(candidate_mapping)) != sealed["mapping_commitment"]:
        raise SystemExit("candidate mapping does not match sealed manifest")
    if raw["sealed_manifest_sha256"] != digest_file(sealed_path):
        raise SystemExit("raw trials do not match sealed manifest")
    if private["source_manifest_sha256"] != digest_file(manifest_path):
        raise SystemExit("private presentation source manifest mismatch")

    scenarios = load_scenarios(manifest)
    rubric_path = ROOT / "RUBRIC.md"
    rubric_text = rubric_path.read_text(encoding="utf-8")
    expected_records = len(scenarios) * manifest["trials_per_scenario"] * len(candidate_mapping)
    if len(raw["records"]) != expected_records:
        raise SystemExit(f"expected {expected_records} raw records, found {len(raw['records'])}")

    for judge_id, presentation_packets in private["judges"].items():
        bundle, score_template = build_judge_bundle(
            judge_id,
            presentation_packets,
            scenarios,
            raw,
            rubric_text,
            digest_file(rubric_path),
        )
        if "opaque_id" in structural_keys(bundle):
            raise SystemExit("judge-visible bundle leaks opaque_id")
        write_new(output_dir / f"{judge_id}-packets.json", bundle)
        write_text_new(output_dir / f"{judge_id}-packets.md", markdown_bundle(bundle))
        write_new(output_dir / f"{judge_id}-scores-template.json", score_template)

    print(commitment["private_presentation_mapping_sha256"])


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    commands = result.add_subparsers(required=True)

    p = commands.add_parser("seal")
    p.add_argument("manifest")
    p.add_argument("candidate_mapping")
    p.add_argument("commitment_output")
    p.add_argument("private_output")
    p.set_defaults(func=seal)

    p = commands.add_parser("render")
    p.add_argument("manifest")
    p.add_argument("sealed")
    p.add_argument("candidate_mapping")
    p.add_argument("presentation_commitment")
    p.add_argument("private_presentation")
    p.add_argument("raw_trials")
    p.add_argument("output_directory")
    p.set_defaults(func=render)
    return result


if __name__ == "__main__":
    arguments = parser().parse_args()
    arguments.func(arguments)
