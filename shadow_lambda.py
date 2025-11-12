
import json
import os
import decimal
from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple, Optional
import boto3
import math

# ---------- Config ----------
# Provide these via Lambda env vars or override in the event:
# BUCKET_NAME: S3 bucket that contains the farm-report JSONs (default satsure-sage-media)
# EPSILON: numeric tolerance for floating comparisons (default 1e-3)
# LIST_MODE: "ordered" or "unordered" (default "unordered")
# IGNORE_PATHS_JSON: JSON array of JSONPath-like prefixes to ignore (default '[]')
# WRITE_REPORT: "true"/"false" (default "false")

# Key patterns
def satsource_key(request_id: str, ref_id: str) -> str:
    # e.g. farm-reports/<req-id-uuid>/satsource_<refid>.json
    return f"farm-reports/{request_id}/satsource_{ref_id}.json"

def legacy_key(request_id: str, ref_id: str) -> str:
    # e.g. farm-reports/<req-id-uuid>/<refid>.json
    return f"farm-reports/{request_id}/{ref_id}.json"


# ---------- Utilities ----------
def _is_number(x: Any) -> bool:
    return isinstance(x, (int, float, decimal.Decimal)) and not isinstance(x, bool)

def _json_dump_compact(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"), sort_keys=True)

@dataclass
class CompareOptions:
    epsilon: float = 1e-3
    list_mode: str = "unordered"   # or "ordered"
    ignore_paths: List[str] = field(default_factory=list)

    def should_ignore(self, path: str) -> bool:
        # If any ignore prefix matches the current path, skip it.
        return any(path.startswith(prefix) for prefix in self.ignore_paths)


@dataclass
class DiffEntry:
    path: str
    issue: str


class JsonComparator:
    """
    Deep comparator that reports:
      - missing/extra keys
      - type mismatches
      - value differences (numeric tolerance for numbers)
    Path format: $.a.b[0].c
    """
    def __init__(self, options: CompareOptions):
        self.options = options
        self.diffs: List[DiffEntry] = []

    def compare(self, a: Any, b: Any, path: str = "$"):
        if self.options.should_ignore(path):
            return

        # Null / None
        if a is None and b is None:
            return
        # Type-based handling
        if isinstance(a, bool) or isinstance(b, bool):
            if a is not b:
                self._add(path, f"bool mismatch {a} != {b}")
            return

        if _is_number(a) and _is_number(b):
            try:
                fa, fb = float(a), float(b)
            except Exception:
                if a != b:
                    self._add(path, f"number parse mismatch {a} != {b}")
                return
            if math.isfinite(fa) and math.isfinite(fb):
                if abs(fa - fb) > self.options.epsilon:
                    self._add(path, f"number mismatch {fa} != {fb} (>|{self.options.epsilon}|)")
            else:
                if fa != fb:
                    self._add(path, f"number non-finite mismatch {fa} != {fb}")
            return

        if isinstance(a, str) and isinstance(b, str):
            if a != b:
                self._add(path, f"string mismatch '{a}' != '{b}'")
            return

        if isinstance(a, dict) and isinstance(b, dict):
            self._compare_dicts(a, b, path)
            return

        if isinstance(a, list) and isinstance(b, list):
            self._compare_lists(a, b, path)
            return

        # Type mismatch or simple value mismatch
        if type(a) != type(b):
            self._add(path, f"type mismatch {type(a).__name__} != {type(b).__name__}")
            return
        if a != b:
            self._add(path, f"value mismatch {a} != {b}")

    def _compare_dicts(self, a: Dict[str, Any], b: Dict[str, Any], path: str):
        ka, kb = set(a.keys()), set(b.keys())
        for k in sorted(ka - kb):
            if not self.options.should_ignore(f"{path}.{k}"):
                self._add(path, f"extra key in A: {k}")
        for k in sorted(kb - ka):
            if not self.options.should_ignore(f"{path}.{k}"):
                self._add(path, f"missing key in A (present in B): {k}")
        for k in sorted(ka & kb):
            self.compare(a[k], b[k], f"{path}.{k}")

    def _compare_lists(self, a: List[Any], b: List[Any], path: str):
        if self.options.list_mode == "ordered":
            if len(a) != len(b):
                self._add(path, f"length mismatch {len(a)} != {len(b)}")
            for i in range(min(len(a), len(b))):
                self.compare(a[i], b[i], f"{path}[{i}]")
        else:
            # unordered multiset compare using canonical JSON
            from collections import Counter
            ca = Counter(_json_dump_compact(x) for x in a)
            cb = Counter(_json_dump_compact(x) for x in b)
            for k in sorted((ca - cb).elements()):
                self._add(path, f"extra element in A: {k}")
            for k in sorted((cb - ca).elements()):
                self._add(path, f"missing element in A (present in B): {k}")

    def _add(self, path: str, issue: str):
        self.diffs.append(DiffEntry(path=path, issue=issue))

    def result(self) -> Dict[str, Any]:
        return {
            "differences": [dict(path=d.path, issue=d.issue) for d in self.diffs],
            "differenceCount": len(self.diffs),
            "equal": len(self.diffs) == 0,
        }


class S3JsonLoader:
    def __init__(self, bucket: str):
        self.bucket = bucket
        self.s3 = boto3.client("s3")

    def load_json(self, key: str) -> Any:
        obj = self.s3.get_object(Bucket=self.bucket, Key=key)
        data = obj["Body"].read()
        return json.loads(data)

    def write_json(self, key: str, payload: Dict[str, Any]):
        self.s3.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8"),
            ContentType="application/json",
        )


@dataclass
class ShadowTestConfig:
    bucket: str
    request_id: str
    ref_id: str
    epsilon: float = 1e-3
    list_mode: str = "ordered"
    ignore_paths: List[str] = field(default_factory=list)
    write_report: bool = False


class ShadowTester:
    """
    Orchestrates:
      - Load legacy (v4/v5) JSON and satsource (v6 backported) JSON
      - Compare with options
      - Optionally write diff report to S3
    """
    def __init__(self, cfg: ShadowTestConfig):
        self.cfg = cfg
        self.loader = S3JsonLoader(cfg.bucket)

    def run(self) -> Dict[str, Any]:
        key_legacy = legacy_key(self.cfg.request_id, self.cfg.ref_id)
        key_satsource = satsource_key(self.cfg.request_id, self.cfg.ref_id)

        legacy_json = self.loader.load_json(key_legacy)
        v6_json = self.loader.load_json(key_satsource)

        options = CompareOptions(
            epsilon=self.cfg.epsilon,
            list_mode=self.cfg.list_mode,
            ignore_paths=self.cfg.ignore_paths,
        )
        comparator = JsonComparator(options)
        comparator.compare(v6_json, legacy_json, "$")

        result = {
            "requestId": self.cfg.request_id,
            "refId": self.cfg.ref_id,
            "bucket": self.cfg.bucket,
            "legacyKey": key_legacy,
            "satsourceKey": key_satsource,
            **comparator.result(),
        }

        if self.cfg.write_report:
            report_key = f"farm-reports/{self.cfg.request_id}/shadow-diff_{self.cfg.ref_id}.json"
            self.loader.write_json(report_key, result)
            result["reportKey"] = report_key

        return result


# ---------- Lambda handler ----------
def lambda_handler(event, context):
    bucket = (event.get("bucket")
              or os.getenv("BUCKET_NAME"))
    if not bucket:
        bucket = "satsure-sage-media"
    try:
        request_id = event["request_id"]
    except Exception as e:
        KeyError("'request_id' not provided as part of lambda event")
    try:
        ref_id = event["ref_id"]
    except Exception as e:
        KeyError("'ref_id' not provided as part of lambda event")

    epsilon = float(event.get("epsilon") or os.getenv("EPSILON", "1e-3"))
    list_mode = (event.get("list_mode") or os.getenv("LIST_MODE", "ordered")).strip().lower()
    write_report = (event.get("write_report") or os.getenv("WRITE_REPORT", "true")).strip().lower() == "true"

    ignore_paths = []
    ip_env = os.getenv("IGNORE_PATHS_JSON")
    if event.get("ignore_paths"):
        ignore_paths = list(event["ignore_paths"])
    elif ip_env:
        try:
            ignore_paths = json.loads(ip_env)
        except Exception:
            pass

    cfg = ShadowTestConfig(
        bucket=bucket,
        request_id=request_id,
        ref_id=ref_id,
        epsilon=epsilon,
        list_mode=list_mode,
        ignore_paths=ignore_paths,
        write_report=write_report,
    )
    tester = ShadowTester(cfg)
    result = tester.run()
    return {
        "statusCode": 200,
        "body": json.dumps(result)
    }
