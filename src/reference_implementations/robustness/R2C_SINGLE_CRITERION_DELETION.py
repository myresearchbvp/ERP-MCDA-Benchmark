#!/usr/bin/env python3
"""ERP-MCDA benchmark — prespecified single-criterion deletion analysis.

This execution-only reference implementation reproduces the documented one-at-a-time
criterion deletions and method-compatible recomputations used in the benchmark. It does
not implement terminal-weight perturbation, native source-defined sensitivity, or
decision-matrix perturbation.
"""
from __future__ import annotations

import argparse
import csv
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

import numpy as np
import scipy
from scipy.optimize import minimize, LinearConstraint, Bounds

SPEC_FILENAME = "R2C_EXECUTION_SPEC.csv"
NP11_NE_REASON = "NUMERICAL_NONUNIQUENESS_AND_SOLVER_FAILURE_UNDER_PRESPECIFIED_LITERAL_PROTOCOL"



def read_csv(path: Path) -> List[dict]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: Iterable[dict], fields: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(fields), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def fmt(x: float) -> str:
    return format(float(x), ".15g")


def bools(x: bool) -> str:
    return "YES" if bool(x) else "NO"


def canonical_set(indices: Sequence[int], alternatives: Sequence[str]) -> str:
    s = set(int(i) for i in indices)
    return "|".join(a for i, a in enumerate(alternatives) if i in s)


def rank_details(scores: Sequence[float], alternatives: Sequence[str], higher: bool) -> dict:
    scores = np.asarray(scores, dtype=float)
    if scores.ndim != 1 or len(scores) != len(alternatives) or not np.isfinite(scores).all():
        raise ValueError("invalid terminal score vector")
    pref = scores if higher else -scores
    better = np.array([np.sum(pref > pref[i]) for i in range(len(pref))], dtype=int)
    equal = np.array([np.sum(pref == pref[i]) for i in range(len(pref))], dtype=int)
    comp = 1 + better
    mid = 1.0 + better + (equal - 1) / 2.0
    win = np.flatnonzero(comp == 1)
    top2 = np.flatnonzero(comp <= 2)
    chunks = []
    for r in sorted(set(comp.tolist())):
        labs = [alternatives[i] for i, rr in enumerate(comp) if rr == r]
        chunks.append(" = ".join(labs))
    return {
        "competition": comp,
        "midrank": mid,
        "winner_indices": win,
        "top2_indices": top2,
        "winner_set": canonical_set(win, alternatives),
        "weak_order": " > ".join(chunks),
    }


def kendall_tau_b_from_orders(baseline_scores: Sequence[float], perturbed_scores: Sequence[float], higher: bool) -> float:
    b = np.asarray(baseline_scores, float)
    p = np.asarray(perturbed_scores, float)
    if not higher:
        b = -b
        p = -p
    C = D = Tx = Ty = 0.0
    n = len(b)
    for i in range(n - 1):
        for j in range(i + 1, n):
            br = 1 if b[i] > b[j] else (-1 if b[i] < b[j] else 0)
            pr = 1 if p[i] > p[j] else (-1 if p[i] < p[j] else 0)
            if br == 0:
                if pr != 0:
                    Tx += 1
            else:
                if pr == br:
                    C += 1
                elif pr == -br:
                    D += 1
                else:
                    Ty += 1
    denom = math.sqrt((C + D + Tx) * (C + D + Ty))
    return float("nan") if denom == 0 else (C - D) / denom


def ordinary_metrics(baseline_scores: np.ndarray, scores: np.ndarray, alternatives: Sequence[str], higher: bool) -> dict:
    bdet = rank_details(baseline_scores, alternatives, higher)
    ddet = rank_details(scores, alternatives, higher)
    if len(bdet["winner_indices"]) != 1:
        raise ValueError("ordinary-case baseline winner must be unique")
    if len(bdet["top2_indices"]) != 2:
        raise ValueError("ordinary-case baseline top-2 must contain exactly two alternatives")
    bwin = int(bdet["winner_indices"][0])
    btop2 = set(map(int, bdet["top2_indices"]))
    dwin = set(map(int, ddet["winner_indices"]))
    dtop2 = set(map(int, ddet["top2_indices"]))
    overlap = len(btop2 & dtop2) / 2.0
    tau = kendall_tau_b_from_orders(baseline_scores, scores, higher)
    return {
        "baseline_winner_retained": bwin in dwin,
        "exact_winner_set": ddet["winner_set"],
        "baseline_top2_both_retained": btop2.issubset(dtop2),
        "baseline_top2_overlap_share": overlap,
        "MARD": float(np.mean(np.abs(ddet["midrank"] - bdet["midrank"]))),
        "Kendall_tau_b": tau,
        "complete_weak_order": ddet["weak_order"],
    }


def score_vector_text(alternatives: Sequence[str], scores: Sequence[float], metric: str) -> str:
    return ";".join(f"{a}:{metric}={fmt(v)}" for a, v in zip(alternatives, scores))


class Inputs:
    def __init__(self, r1a: Path, r1b: Path, r1c: Path, r1d: Path, r2a: Path, r2b: Path):
        self.r1a, self.r1b, self.r1c, self.r1d, self.r2a, self.r2b = r1a, r1b, r1c, r1d, r2a, r2b
        self.r2a_baselines = read_csv(r2a / "R2A_BASELINE_SPECIFICATION.csv")
        self._load_np01()
        self._load_np02()
        self._load_np03()
        self._load_np04()
        self._load_np05()
        self._load_np07()
        self._load_np11()
        self._load_np12()

    # ---------- NP01 ----------
    @staticmethod
    def fuzzy_matrix(rows: List[dict], group: str, names: Sequence[str]) -> np.ndarray:
        M = np.empty((len(names), len(names), 3), float)
        idx = {x: i for i, x in enumerate(names)}
        for r in rows:
            if r["input_group"] == group:
                M[idx[r["row_id"]], idx[r["col_id"]]] = [float(r["value_l"]), float(r["value_m"]), float(r["value_u"])]
        return M

    @staticmethod
    def fuzzy_weights(M: np.ndarray) -> np.ndarray:
        n = M.shape[0]
        g = np.prod(M, axis=1) ** (1.0 / n)
        s = g.sum(axis=0)
        inv = np.array([1 / s[2], 1 / s[1], 1 / s[0]])
        fw = g * inv
        crisp = fw.mean(axis=1)
        return crisp / crisp.sum()

    def _load_np01(self):
        rows = read_csv(self.r1a / "NP01" / "NP01_EXTRACTION.csv")
        self.np01_main_names = ["Technical", "Corporate", "Financial"]
        self.np01_groups = [
            ("FAHP_TECHNICAL", ["Functionality", "Compatibility", "Usability", "Accessibility", "Security"]),
            ("FAHP_CORPORATE", ["References", "Adequacy", "After_sales", "Know_how"]),
            ("FAHP_FINANCIAL", ["License", "Consultancy", "Maintenance"]),
        ]
        self.np01_main_matrix = self.fuzzy_matrix(rows, "FAHP_MAIN", self.np01_main_names)
        self.np01_local_matrices = [(g, list(names), self.fuzzy_matrix(rows, g, names)) for g, names in self.np01_groups]
        self.np01_main_weights = self.fuzzy_weights(self.np01_main_matrix)
        self.np01_criteria = [f"Cr{i}" for i in range(1, 13)]
        self.np01_alts = ["A", "B", "C", "D"]
        X = np.empty((4, 12), float)
        ai = {a: i for i, a in enumerate(self.np01_alts)}
        ci = {c: i for i, c in enumerate(self.np01_criteria)}
        for r in rows:
            if r["input_group"] == "TOPSIS_DECISION":
                X[ai[r["row_id"]], ci[r["col_id"]]] = float(r["value"])
        self.np01_X = X
        mapping = []
        k = 0
        for parent_idx, (_, names, _) in enumerate(self.np01_local_matrices):
            for local_idx, name in enumerate(names):
                mapping.append((self.np01_criteria[k], parent_idx, local_idx, name))
                k += 1
        self.np01_mapping = mapping

    def np01_run(self, deleted: str | None) -> np.ndarray:
        global_weights = []
        retained_cols = []
        for parent_idx, (_, names, M) in enumerate(self.np01_local_matrices):
            idxs = list(range(len(names)))
            global_offset = sum(len(x[1]) for x in self.np01_local_matrices[:parent_idx])
            local_deleted = None
            if deleted is not None:
                for crit, pidx, lidx, _ in self.np01_mapping:
                    if crit == deleted and pidx == parent_idx:
                        local_deleted = lidx
                        break
            if local_deleted is not None:
                idxs.remove(local_deleted)
            Mr = M[np.ix_(idxs, idxs, [0, 1, 2])]
            lw = self.fuzzy_weights(Mr)
            for pos, original_local in enumerate(idxs):
                global_weights.append(self.np01_main_weights[parent_idx] * lw[pos])
                retained_cols.append(global_offset + original_local)
        W = np.asarray(global_weights, float)
        X = self.np01_X[:, retained_cols]
        R = X / np.sqrt((X ** 2).sum(axis=0))
        V = R * W
        pis, nis = V.max(axis=0), V.min(axis=0)
        dp = np.sqrt(((V - pis) ** 2).sum(axis=1))
        dm = np.sqrt(((V - nis) ** 2).sum(axis=1))
        return dm / (dp + dm)

    # ---------- NP02 ----------
    def _load_np02(self):
        rows = read_csv(self.r1a / "NP02" / "NP02_EXTRACTION.csv")
        self.np02_criteria = ["C1_Adaptability", "C2_Financial", "C3_Simplicity", "C4_Provider_services", "C5_Implementation_approach"]
        self.np02_alts = ["ERP_A", "ERP_B"]
        def mat(group: str, names: Sequence[str]) -> np.ndarray:
            M = np.empty((len(names), len(names)), float)
            idx = {x: i for i, x in enumerate(names)}
            for r in rows:
                if r["input_group"] == group:
                    M[idx[r["row_id"]], idx[r["col_id"]]] = float(r["value"])
            return M
        self.np02_M = mat("CRITERIA_PAIRWISE", self.np02_criteria)
        self.np02_local = np.column_stack([
            self.ahp(mat("ALT_" + c, self.np02_alts)) for c in self.np02_criteria
        ])

    @staticmethod
    def ahp(M: np.ndarray) -> np.ndarray:
        return (M / M.sum(axis=0)).mean(axis=1)

    def np02_run(self, deleted: str | None) -> np.ndarray:
        keep = [i for i, c in enumerate(self.np02_criteria) if c != deleted]
        M = self.np02_M[np.ix_(keep, keep)]
        cw = self.ahp(M)
        A = self.np02_local[:, keep]
        return A @ cw

    # ---------- NP03 ----------
    def _load_np03(self):
        rows = read_csv(self.r1a / "NP03" / "NP03_EXTRACTION.csv")
        self.np03_criteria = [f"ERP{i:02d}" for i in range(1, 16)]
        self.np03_alts = ["ERPsys1", "ERPsys2", "ERPsys3", "ERPsys4"]
        ci = {c: i for i, c in enumerate(self.np03_criteria)}
        ai = {a: i for i, a in enumerate(self.np03_alts)}
        self.np03_w = np.empty(15, float)
        self.np03_R = np.empty((15, 4), float)
        for r in rows:
            if r["input_group"] == "FAHP_PUBLISHED_NORMALIZED_WEIGHTS":
                self.np03_w[ci[r["row_id"]]] = float(r["value"])
            elif r["input_group"] == "TOPSIS_PUBLISHED_NORMALIZED_MATRIX":
                self.np03_R[ci[r["row_id"]], ai[r["col_id"]]] = float(r["value"])

    def np03_run(self, deleted: str | None, erp04_cost: bool) -> np.ndarray:
        keep = [i for i, c in enumerate(self.np03_criteria) if c != deleted]
        w = self.np03_w[keep].copy(); w /= w.sum()
        R = self.np03_R[keep, :]
        labels = [self.np03_criteria[i] for i in keep]
        V = R * w[:, None]
        best, worst = V.max(axis=1), V.min(axis=1)
        cost_labels = {"ERP03"} | ({"ERP04"} if erp04_cost else set())
        for j, c in enumerate(labels):
            if c in cost_labels:
                best[j], worst[j] = V[j].min(), V[j].max()
        dp = np.sqrt(((V - best[:, None]) ** 2).sum(axis=0))
        dm = np.sqrt(((V - worst[:, None]) ** 2).sum(axis=0))
        return dm / (dp + dm)

    # ---------- NP04 ----------
    def _load_np04(self):
        rows = read_csv(self.r1b / "NP04" / "NP04_INTERMEDIATES.csv")
        self.np04_alts = [f"SFT-{i}" for i in range(1, 7)]
        self.np04_criteria = ["EIS", "SR", "CMI", "CS", "EU", "RS", "SFR", "QSS", "F", "IC", "PC", "MSC"]
        self.np04_norm = {}
        self.np04_weights = {}
        self.np04_dirs = {}
        for r in rows:
            key = (r["alternative"], r["criterion"])
            self.np04_norm[key] = (float(r["normalized_low"]), float(r["normalized_high"]))
            self.np04_weights[r["criterion"]] = (float(r["weight_low"]), float(r["weight_high"]))
            self.np04_dirs[r["criterion"]] = r["direction"]

    @staticmethod
    def prod(xs: Iterable[float]) -> float:
        p = 1.0
        for x in xs:
            p *= x
        return p

    def np04_run(self, deleted: str | None) -> np.ndarray:
        criteria = [c for c in self.np04_criteria if c != deleted]
        b = [c for c in criteria if self.np04_dirs[c] == "benefit"]
        k = [c for c in criteria if self.np04_dirs[c] == "cost"]
        if not b or not k:
            raise ValueError("NP04 deletion unexpectedly empties benefit or cost group")
        raw = {}
        for a in self.np04_alts:
            kp = (sum(self.np04_norm[(a, c)][0] * self.np04_weights[c][0] for c in b),
                  sum(self.np04_norm[(a, c)][1] * self.np04_weights[c][1] for c in b))
            km = (sum(self.np04_norm[(a, c)][0] * self.np04_weights[c][0] for c in k),
                  sum(self.np04_norm[(a, c)][1] * self.np04_weights[c][1] for c in k))
            pp = (self.prod(self.np04_norm[(a, c)][0] * self.np04_weights[c][0] for c in b),
                  self.prod(self.np04_norm[(a, c)][1] * self.np04_weights[c][1] for c in b))
            pm = (self.prod(self.np04_norm[(a, c)][0] * self.np04_weights[c][0] for c in k),
                  self.prod(self.np04_norm[(a, c)][1] * self.np04_weights[c][1] for c in k))
            raw[a] = {
                "Ysd": (kp[0] - km[1], kp[1] - km[0]),
                "Ytd": (pp[0] - pm[1], pp[1] - pm[0]),
                "Ysr": (kp[0] / km[1], kp[1] / km[0]),
                "Ytr": (pp[0] / pm[1], pp[1] / pm[0]),
            }
        normu = {}
        keys = ["Ysd", "Ytd", "Ysr", "Ytr"]
        for key in keys:
            den = 1 + max(raw[a][key][1] for a in self.np04_alts)
            for a in self.np04_alts:
                lo, hi = raw[a][key]
                normu[(a, key)] = ((1 + lo) / den, (1 + hi) / den)
        crisp = []
        for a in self.np04_alts:
            lo = sum(normu[(a, key)][0] for key in keys) / 4
            hi = sum(normu[(a, key)][1] for key in keys) / 4
            crisp.append((lo + hi) / 2)
        return np.asarray(crisp, float)

    # ---------- NP05 ----------
    def _load_np05(self):
        rows = read_csv(self.r1b / "NP05" / "NP05_EXTRACTION.csv")
        self.np05_alts = ["A1", "A2", "A3"]
        self.np05_criteria = [f"C{i}" for i in range(1, 7)]
        scale = {}
        ratings = defaultdict(list)
        self.np05_dirs = {}
        self.np05_const = {}
        for r in rows:
            if r["input_group"] == "linguistic_scale":
                scale[r["linguistic_term"]] = float(r["value"])
            elif r["input_group"] == "linguistic_rating":
                ratings[(r["alternative"], r["criterion"])].append((r["decision_maker"], r["linguistic_term"]))
                self.np05_dirs[r["criterion"]] = r["direction"]
            elif r["input_group"] == "method_constant":
                self.np05_const[r["parameter"]] = float(r["value"])
        self.np05_hfe = {(a, c): sorted(set(scale[t] for _, t in ratings[(a, c)])) for a in self.np05_alts for c in self.np05_criteria}
        if {c for c in self.np05_criteria if self.np05_dirs[c] == "cost"} != {"C6"}:
            raise ValueError("NP05 C6 must be sole cost criterion")

    def np05_ce1(self, h: Sequence[float], q: float) -> float:
        hs = sorted(h); L = len(h)
        T = (1 + q) * math.log(1 + q) - (2 + q) * (math.log(2 + q) - math.log(2))
        s = 0.0
        for t in range(L):
            a = hs[t]; b = 1 - hs[L - 1 - t]; mid = (2 + q * a + q * b) / 2
            s += ((1 + q * a) * math.log(1 + q * a)) / 2
            s += ((1 + q * b) * math.log(1 + q * b)) / 2
            s -= mid * math.log(mid)
        return 2 * s / (L * T)

    def np05_ce2(self, h: Sequence[float], beta: float) -> float:
        hs = sorted(h); L = len(h); denom = (1 - 2 ** (1 - beta)) * L
        s = 0.0
        for t in range(L):
            a = hs[t]; b = 1 - hs[L - 1 - t]
            s += a ** beta / 2 + b ** beta / 2 - ((a + b) / 2) ** beta
        return s / denom

    def np05_entropy(self, kind: str, h: Sequence[float]) -> float:
        if kind == "CE-I":
            ce = self.np05_ce1(h, self.np05_const["q_CE_I"])
        else:
            ce = self.np05_ce2(h, self.np05_const["beta_CE_II"])
        return 1 - ce

    def np05_weights(self, kind: str, dist: str, criteria: Sequence[str]) -> np.ndarray:
        ds = []
        for c in criteria:
            ev = [self.np05_entropy(kind, self.np05_hfe[(a, c)]) for a in self.np05_alts]
            dif = [self.np05_const["HFEE_reference"] - x for x in ev]
            if dist == "Hamming":
                d = sum(abs(x) for x in dif) / len(dif)
            elif dist == "Euclidean":
                d = math.sqrt(sum(x * x for x in dif) / len(dif))
            elif dist == "Hausdorff":
                d = max(abs(x) for x in dif)
            else:
                raise ValueError(dist)
            ds.append(d)
        ds = np.asarray(ds, float)
        return ds / ds.sum()

    @staticmethod
    def np05_weighted_hfe(h: Sequence[float], w: float) -> List[float]:
        return [1 - (1 - mu) ** w for mu in h]

    @staticmethod
    def np05_phfe_score(vals: Sequence[float]) -> float:
        vals = np.asarray(vals, float); s = vals.sum()
        if s <= 0:
            raise ValueError("NP05 P-HFE score denominator nonpositive")
        p = vals / s
        return float(np.dot(vals, p) / p.sum())

    def np05_run(self, kind: str, dist: str, deleted: str | None) -> np.ndarray:
        criteria = [c for c in self.np05_criteria if c != deleted]
        if "C6" not in criteria:
            raise ValueError("NP05 C6 deletion is NE and must not be executed")
        w = self.np05_weights(kind, dist, criteria)
        sc = {}
        for a in self.np05_alts:
            for j, c in enumerate(criteria):
                sc[(a, c)] = self.np05_phfe_score(self.np05_weighted_hfe(self.np05_hfe[(a, c)], w[j]))
        z = {}
        for c in criteria:
            den = sum(sc[(a, c)] for a in self.np05_alts)
            for a in self.np05_alts:
                z[(a, c)] = sc[(a, c)] / den
        benefit = [c for c in criteria if self.np05_dirs[c] == "benefit"]
        cost = [c for c in criteria if self.np05_dirs[c] == "cost"]
        if not benefit or not cost:
            raise ValueError("NP05 native COPRAS benefit/cost group empty")
        sben = {a: sum(z[(a, c)] for c in benefit) for a in self.np05_alts}
        scost = {a: sum(z[(a, c)] for c in cost) for a in self.np05_alts}
        mincost = min(scost.values()); sumcost = sum(scost.values())
        denom = sum(mincost / scost[a] for a in self.np05_alts)
        Q = {a: sben[a] + (mincost * sumcost) / (scost[a] * denom) for a in self.np05_alts}
        maxQ = max(Q.values())
        return np.asarray([self.np05_const["utility_percent_scale"] * Q[a] / maxQ for a in self.np05_alts], float)

    # ---------- NP07 ----------
    def _load_np07(self):
        rows = read_csv(self.r1c / "NP07" / "NP07_EXTRACTION.csv")
        b07 = [r for r in rows if r["publication"].startswith("NP07_Kilic_2015")]
        self.np07_criteria = list(dict.fromkeys(r["criterion"] for r in b07 if r["input_group"] == "criterion_weight"))
        self.np07_alts = ["A", "B", "C", "D", "E"]
        ci = {c: i for i, c in enumerate(self.np07_criteria)}; ai = {a: i for i, a in enumerate(self.np07_alts)}
        self.np07_w = np.empty(len(self.np07_criteria), float)
        self.np07_X = np.empty((5, len(self.np07_criteria)), float)
        self.np07_p = np.empty(len(self.np07_criteria), float)
        for r in b07:
            if r["input_group"] == "criterion_weight": self.np07_w[ci[r["criterion"]]] = float(r["value"]) / 100.0
            elif r["input_group"] == "alternative_score": self.np07_X[ai[r["alternative"]], ci[r["criterion"]]] = float(r["value"])
            elif r["input_group"] == "preference_function": self.np07_p[ci[r["criterion"]]] = float(r["value"])

    def np07_run(self, deleted: str | None) -> np.ndarray:
        keep = [i for i, c in enumerate(self.np07_criteria) if c != deleted]
        w = self.np07_w[keep].copy(); w /= w.sum()
        X = self.np07_X[:, keep]; p = self.np07_p[keep]
        n = len(self.np07_alts); pi = np.zeros((n, n), float)
        for a in range(n):
            for b in range(n):
                if a == b: continue
                d = X[a] - X[b]
                P = np.where(d <= 0.0, 0.0, np.where(d < p, d / p, 1.0))
                pi[a, b] = float(np.dot(w, P))
        plus = pi.sum(axis=1) / (n - 1); minus = pi.sum(axis=0) / (n - 1)
        return plus - minus

    # ---------- NP11 ----------
    def _load_np11(self):
        self.np11_rows = read_csv(self.r1d / "NP11" / "NP11_EXTRACTION.csv")
        self.np11_criteria = [f"C{i}" for i in range(1, 7)]
        self.np11_alts = [f"S{i}" for i in range(1, 5)]
        self.np11_M = float(next(r["value"] for r in self.np11_rows if r["input_id"] == "LFPP_M"))
        inter = read_csv(self.r1d / "NP11" / "NP11_CALCULATED_INTERMEDIATES.csv")
        self.np11_local = np.empty((6, 4), float)
        ci = {c: i for i, c in enumerate(self.np11_criteria)}; si = {s: i for i, s in enumerate(self.np11_alts)}
        for r in inter:
            if r["stage"] == "local_system" and r["metric"] == "weight":
                self.np11_local[ci[r["basis"]], si[r["item"]]] = float(r["value"])

    @staticmethod
    def lfpp(ids: Sequence[str], pairs: Sequence[dict], M: float) -> dict:
        index = {x: i for i, x in enumerate(ids)}
        trip = []
        for r in pairs:
            i = index[r["row_id"]]; j = index[r["col_id"]]
            trip.append((i, j, float(r["l"]), float(r["m"]), float(r["u"])))
        trip.sort()
        n = len(ids); k = len(trip); N = n + 1 + 2 * k
        def objective(z):
            lam = z[n]; d = z[n + 1:n + 1 + k]; e = z[n + 1 + k:]
            return (1 - lam) ** 2 + M * (float(d @ d) + float(e @ e))
        def jac(z):
            g = np.zeros(N); g[n] = 2 * (z[n] - 1)
            g[n + 1:n + 1 + k] = 2 * M * z[n + 1:n + 1 + k]
            g[n + 1 + k:] = 2 * M * z[n + 1 + k:]
            return g
        A = []; lb = []
        for q, (i, j, l, m, u) in enumerate(trip):
            r = np.zeros(N); r[i] = 1; r[j] = -1; r[n] = -math.log(m / l); r[n + 1 + q] = 1
            A.append(r); lb.append(math.log(l))
            r = np.zeros(N); r[i] = -1; r[j] = 1; r[n] = -math.log(u / m); r[n + 1 + k + q] = 1
            A.append(r); lb.append(-math.log(u))
        cons = LinearConstraint(np.vstack(A), np.asarray(lb), np.full(2 * k, np.inf))
        bnds = Bounds(np.zeros(N), np.full(N, np.inf))
        z0 = np.zeros(N); z0[:n] = 1.0; z0[n] = 0.5; z0[n + 1:] = 0.1
        res = minimize(objective, z0, jac=jac, constraints=[cons], bounds=bnds, method="SLSQP",
                       options={"ftol": 1e-14, "maxiter": 20000, "disp": False})
        if not res.success:
            raise RuntimeError("NP11 LFPP SLSQP failed: " + str(res.message))
        x = res.x[:n]; ex = np.exp(x - x.max()); weights = ex / ex.sum()
        return {"weights": weights, "lambda": float(res.x[n]), "objective": float(res.fun), "message": str(res.message)}

    def np11_run(self, deleted: str | None) -> Tuple[np.ndarray, dict]:
        retained = [c for c in self.np11_criteria if c != deleted]
        pairs = [r for r in self.np11_rows if r["kind"] == "criteria_pairwise" and r["row_id"] in retained and r["col_id"] in retained]
        expected = len(retained) * (len(retained) - 1) // 2
        if len(pairs) != expected:
            raise ValueError(f"NP11 reduced criteria matrix missing pairs: {len(pairs)} != {expected}")
        sol = self.lfpp(retained, pairs, self.np11_M)
        idx = [self.np11_criteria.index(c) for c in retained]
        totals = sol["weights"] @ self.np11_local[idx, :]
        return totals, sol

    # ---------- NP12 ----------
    def _load_np12(self):
        rows = read_csv(self.r1d / "NP12" / "NP12_EXTRACTION.csv")
        cr = [r for r in rows if r["kind"] == "criterion"]
        self.np12_criteria = [r["criterion"] for r in cr]
        self.np12_alts = ["A1", "A2", "A3"]
        self.np12_w = np.asarray([float(r["weight"]) for r in cr], float)
        self.np12_X = np.asarray([[float(r[a]) for a in self.np12_alts] for r in cr], float)
        self.np12_dirs = [r["direction"] for r in cr]

    def np12_run(self, deleted: str | None) -> dict:
        keep = [i for i, c in enumerate(self.np12_criteria) if c != deleted]
        w = self.np12_w[keep].copy(); w /= w.sum()
        X = self.np12_X[keep, :]
        dirs = [self.np12_dirs[i] for i in keep]
        reg = np.zeros_like(X)
        for j in range(len(keep)):
            if dirs[j] == "min": best = float(X[j].min()); worst = float(X[j].max())
            else: best = float(X[j].max()); worst = float(X[j].min())
            reg[j] = 0.0 if best == worst else (best - X[j]) / (best - worst)
        weighted = w[:, None] * reg
        S = weighted.sum(axis=0); R = weighted.max(axis=0)
        Sstar, Sminus, Rstar, Rminus = float(S.min()), float(S.max()), float(R.min()), float(R.max())
        if Sminus == Sstar or Rminus == Rstar:
            raise ValueError("NP12 deletion collapses VIKOR denominator")
        q = 0.5
        Q = q * (S - Sstar) / (Sminus - Sstar) + (1 - q) * (R - Rstar) / (Rminus - Rstar)
        DQ = 1.0 / (len(self.np12_alts) - 1)
        order = np.argsort(Q, kind="stable")
        best_idx, second_idx = int(order[0]), int(order[1])
        qbest, qsecond = float(Q[best_idx]), float(Q[second_idx])
        c1 = (qsecond - qbest) >= DQ
        c2 = (S[best_idx] == S.min()) or (R[best_idx] == R.min())
        if c1 and c2:
            rec_mask = Q == qbest
        elif c1 and not c2:
            rec_mask = (Q == qbest) | (Q == qsecond)
        else:
            rec_mask = (Q - qbest) < DQ
        if not np.any(rec_mask):
            raise ValueError("NP12 empty recommendation set")
        return {"Q": Q, "S": S, "R": R, "C1": bool(c1), "C2": bool(c2), "DQ": DQ, "rec_mask": rec_mask}


# ---- prospective specification -------------------------------------------------

def baseline_map(inp: Inputs) -> Dict[Tuple[str, str], dict]:
    out = {}
    for r in inp.r2a_baselines:
        npid = r["NP_ID"]
        if npid == "NP03":
            cfg = "A_STRICT_EXPLICIT_DIRECTION" if r["baseline_id"] == "NP03_A_STRICT_EXPLICIT_DIRECTION" else "ERP04_COST_PARALLEL"
        elif npid == "NP05":
            cfg = r["publication_model_configuration"]
        elif npid == "NP07":
            if r["baseline_id"] != "NP07_KILIC2015_PRIMARY":
                continue
            cfg = "KILIC_2015_PROMETHEE_II"
        elif npid == "NP11":
            cfg = "LFPP_REDUCED_CRITERIA"
        elif npid == "NP12":
            cfg = "VIKOR_Q050"
        else:
            cfg = f"{npid}_PRIMARY"
        out[(npid, cfg)] = r
    return out


def make_spec(inp: Inputs) -> List[dict]:
    bm = baseline_map(inp)
    rows = []
    fields_common = {
        "scope": "SINGLE_CRITERION_DELETION_ONLY",
        "terminal_weight_perturbation_rerun": "NO",
        "native_sensitivity": "NO",
        "decision_matrix_perturbation": "NO",
    }
    def add(npid, cfg, deleted, app, op, source_checkpoint, note="", baseline_key=None):
        key = baseline_key or (npid, cfg)
        br = bm.get(key, {})
        row = {
            "NP_ID": npid,
            "configuration_or_branch": cfg,
            "deleted_criterion": deleted,
            "applicability": app,
            "operation_type": op,
            "source_checkpoint": source_checkpoint,
            "baseline_id": br.get("baseline_id", ""),
            "baseline_role": br.get("baseline_role", ""),
            "baseline_winner": br.get("baseline_winner", ""),
            "baseline_complete_weak_order": br.get("baseline_complete_weak_order", ""),
            "note": note,
            **fields_common,
        }
        rows.append(row)

    for c in inp.np01_criteria:
        add("NP01", "NP01_PRIMARY", c, "APPLICABLE", "NATIVE_REWEIGHTING_AFTER_DELETION",
            "data/standardized/runtime/R1A/NP01/NP01_EXTRACTION.csv — reduced fuzzy-AHP local reciprocal matrix + TOPSIS decision matrix",
            "delete within own local FAHP parent; keep 3 main-criterion weights unchanged; regenerate global weights")
    for c in inp.np02_criteria:
        add("NP02", "NP02_PRIMARY", c, "APPLICABLE", "NATIVE_REWEIGHTING_AFTER_DELETION",
            "data/standardized/runtime/R1A/NP02/NP02_EXTRACTION.csv — reduced criteria AHP matrix + retained local alternative priorities")
    for cfg, cost04 in [("A_STRICT_EXPLICIT_DIRECTION", False), ("ERP04_COST_PARALLEL", True)]:
        for c in inp.np03_criteria:
            add("NP03", cfg, c, "APPLICABLE", "TERMINAL_POSTWEIGHT_DELETION",
                "data/standardized/runtime/R1A/NP03/NP03_EXTRACTION.csv — Table-3 normalized D2 checkpoint + Table-2 scalar weights",
                "same deleted criterion in both prospectively fixed direction branches")
    for c in inp.np04_criteria:
        add("NP04", "NP04_PRIMARY", c, "APPLICABLE", "TERMINAL_POSTWEIGHT_DELETION",
            "data/standardized/runtime/R1B/NP04/NP04_INTERMEDIATES.csv — prespecified primary literal rough normalized matrix + printed rough weights",
            "remaining rough weights unchanged; no interval collapse; no Table-6/rounding explanatory comparison outside the primary reconstruction")
    configs = [("CE-I", "Hamming"), ("CE-I", "Euclidean"), ("CE-I", "Hausdorff"),
               ("CE-II", "Hamming"), ("CE-II", "Euclidean"), ("CE-II", "Hausdorff")]
    for kind, dist in configs:
        cfg = f"p-HFC_{kind}_{dist}"
        for c in ["C1", "C2", "C3", "C4", "C5"]:
            add("NP05", cfg, c, "APPLICABLE", "NATIVE_REWEIGHTING_AFTER_DELETION",
                "data/standardized/runtime/R1B/NP05/NP05_EXTRACTION.csv — retained HFEs with entropy-distance normalization recomputed",
                "q=2 and beta=3 fixed; C6 retained as sole cost criterion")
        add("NP05", cfg, "C6", "NE", "NE",
            "data/standardized/runtime/R1B/NP05/NP05_EXTRACTION.csv",
            "sole cost criterion; deletion makes native COPRAS cost-side formula undefined")
    for c in ["VRC", "CRC", "SRC"]:
        add("NP06", "NP06_NE", c, "NE", "NE", "results/reference/native/NP06/NP06_COMPUTED_OUTPUTS_PRECOMPARISON.csv",
            "Single-criterion deletion NE: no defensible reduced Choquet capacity; interaction-off comparison reserved for native sensitivity", baseline_key=("NP06", "NP06_PRIMARY"))
    for c in inp.np07_criteria:
        add("NP07", "KILIC_2015_PROMETHEE_II", c, "APPLICABLE", "TERMINAL_POSTWEIGHT_DELETION",
            "data/standardized/runtime/R1C/NP07/NP07_EXTRACTION.csv — printed ANP weights + performance/preference-function system",
            "printed weights renormalized after deletion; V-shape p=2 fixed; Temur & Bolat CBDO excluded")
    for c in ["c1", "c2", "c3", "c4"]:
        add("NP08", "NP08_NE", c, "NE", "NE", "docs/KNOWN_NE_AND_LIMITATIONS.md",
            "no terminally unique LP solution/tie-break baseline", baseline_key=("NP08", "NP08_PRIMARY"))
    for c in ["Xi11", "Xi12", "Xi13", "Xi14", "Xi15", "Xi21", "Xi22", "Xi23", "Xi24", "Xi31", "Xi32", "Xi33"]:
        add("NP09", "NP09_NE", c, "NE", "NE", "docs/KNOWN_NE_AND_LIMITATIONS.md",
            "literal native chain becomes nonfinite before terminal output", baseline_key=("NP09", "NP09_PRIMARY"))
    for c in [f"C{i}" for i in range(1, 17)]:
        add("NP10", "NP10_NE", c, "NE", "NE", "results/reference/resolved/NP10_D_O_SOURCE_RESOLUTION.csv",
            "source limitation: the operative Qb/Qn cost/benefit map is not uniquely provided and Supplementary Tables S1–S6 are unavailable; no unique terminal baseline is defined (D0/O3)", baseline_key=("NP10", "NP10_PRIMARY"))
    for c in inp.np11_criteria:
        add("NP11", "LFPP_REDUCED_CRITERIA", c, "NE", "NE",
            "data/standardized/runtime/R1D/NP11/NP11_EXTRACTION.csv criteria fuzzy matrix + prespecified single-criterion deletion execution rule",
            NP11_NE_REASON)
    for c in inp.np12_criteria:
        add("NP12", "VIKOR_Q050", c, "APPLICABLE", "TERMINAL_POSTWEIGHT_DELETION",
            "data/standardized/runtime/R1D/NP12/NP12_EXTRACTION.csv — raw 3×18 data/directions/weights; R2B source-native VIKOR acceptance rule",
            "q/v=0.5 fixed; native recommendation set primary; top-Q leader secondary")
    return rows


SPEC_FIELDS = [
    "NP_ID", "configuration_or_branch", "deleted_criterion", "applicability", "operation_type", "source_checkpoint",
    "baseline_id", "baseline_role", "baseline_winner", "baseline_complete_weak_order", "note",
    "scope", "terminal_weight_perturbation_rerun", "native_sensitivity", "decision_matrix_perturbation"
]


def expected_baseline_order(inp: Inputs, npid: str, cfg: str) -> str:
    bm = baseline_map(inp)
    r = bm[(npid, cfg)]
    return r["baseline_complete_weak_order"]


def compute_baselines(inp: Inputs, include_np11: bool = True) -> Dict[Tuple[str, str], dict]:
    b = {}
    b[("NP01", "NP01_PRIMARY")] = {"scores": inp.np01_run(None), "alts": inp.np01_alts, "higher": True, "metric": "CC"}
    b[("NP02", "NP02_PRIMARY")] = {"scores": inp.np02_run(None), "alts": inp.np02_alts, "higher": True, "metric": "final_weight"}
    b[("NP03", "A_STRICT_EXPLICIT_DIRECTION")] = {"scores": inp.np03_run(None, False), "alts": inp.np03_alts, "higher": True, "metric": "Ci"}
    b[("NP03", "ERP04_COST_PARALLEL")] = {"scores": inp.np03_run(None, True), "alts": inp.np03_alts, "higher": True, "metric": "Ci"}
    b[("NP04", "NP04_PRIMARY")] = {"scores": inp.np04_run(None), "alts": inp.np04_alts, "higher": True, "metric": "Y_crisp"}
    for kind, dist in [("CE-I", "Hamming"), ("CE-I", "Euclidean"), ("CE-I", "Hausdorff"), ("CE-II", "Hamming"), ("CE-II", "Euclidean"), ("CE-II", "Hausdorff")]:
        cfg = f"p-HFC_{kind}_{dist}"
        b[("NP05", cfg)] = {"scores": inp.np05_run(kind, dist, None), "alts": inp.np05_alts, "higher": True, "metric": "U_percent"}
    b[("NP07", "KILIC_2015_PROMETHEE_II")] = {"scores": inp.np07_run(None), "alts": inp.np07_alts, "higher": True, "metric": "net_flow"}
    if include_np11:
        np11_scores, np11_sol = inp.np11_run(None)
        b[("NP11", "LFPP_REDUCED_CRITERIA")] = {"scores": np11_scores, "alts": inp.np11_alts, "higher": True, "metric": "total_global_weight", "solver": np11_sol}
    v = inp.np12_run(None)
    b[("NP12", "VIKOR_Q050")] = {"scores": v["Q"], "alts": inp.np12_alts, "higher": False, "metric": "Q", "vikor": v}
    return b


def validate_baselines(inp: Inputs) -> List[str]:
    baselines = compute_baselines(inp)
    notes = []
    for (npid, cfg), bd in baselines.items():
        observed = rank_details(bd["scores"], bd["alts"], bd["higher"])["weak_order"]
        expected = expected_baseline_order(inp, npid, cfg)
        if observed != expected:
            raise ValueError(f"baseline mismatch {npid}/{cfg}: observed={observed!r} expected={expected!r}")
        if npid != "NP12":
            det = rank_details(bd["scores"], bd["alts"], bd["higher"])
            if len(det["winner_indices"]) != 1:
                raise ValueError(f"non-unique ordinary baseline winner {npid}/{cfg}")
        notes.append(f"{npid}/{cfg}: undeleted baseline weak order {observed} — PASS")
    v = baselines[("NP12", "VIKOR_Q050")]["vikor"]
    rec = canonical_set(np.flatnonzero(v["rec_mask"]), inp.np12_alts)
    if rec != "A2":
        raise ValueError(f"NP12 baseline native recommendation set mismatch: {rec}")
    notes.append("NP12/VIKOR_Q050: undeleted native recommendation set A2 at q/v=0.5 — PASS")
    return notes




DELETION_FIELDS = [
    "NP_ID", "configuration_or_branch", "deleted_criterion", "operation_type", "status",
    "baseline_winner_retained", "exact_winner_set", "baseline_top2_both_retained", "baseline_top2_overlap_share",
    "MARD", "Kendall_tau_b", "complete_weak_order", "terminal_score_vector",
    "baseline_recommendation_set_retained", "baseline_A2_in_recommendation_set", "exact_native_recommendation_set",
    "top_Q_leader_set_SECONDARY", "C1_acceptable_advantage", "C2_acceptable_stability",
    "native_solver_status", "native_solver_objective", "method_note"
]

def deletion_row_ordinary(npid, cfg, deleted, op, baseline, scores, metric, method_note="", solver=None) -> dict:
    m = ordinary_metrics(baseline["scores"], scores, baseline["alts"], baseline["higher"])
    return {
        "NP_ID": npid, "configuration_or_branch": cfg, "deleted_criterion": deleted, "operation_type": op, "status": "EXECUTED",
        "baseline_winner_retained": bools(m["baseline_winner_retained"]), "exact_winner_set": m["exact_winner_set"],
        "baseline_top2_both_retained": bools(m["baseline_top2_both_retained"]), "baseline_top2_overlap_share": fmt(m["baseline_top2_overlap_share"]),
        "MARD": fmt(m["MARD"]), "Kendall_tau_b": fmt(m["Kendall_tau_b"]), "complete_weak_order": m["complete_weak_order"],
        "terminal_score_vector": score_vector_text(baseline["alts"], scores, metric),
        "baseline_recommendation_set_retained": "", "baseline_A2_in_recommendation_set": "", "exact_native_recommendation_set": "",
        "top_Q_leader_set_SECONDARY": "", "C1_acceptable_advantage": "", "C2_acceptable_stability": "",
        "native_solver_status": solver.get("message", "") if solver else "", "native_solver_objective": fmt(solver["objective"]) if solver else "",
        "method_note": method_note,
    }


def execute_deletions(args, inp: Inputs, out: Path) -> None:
    spec_rows = read_csv(out / SPEC_FILENAME)
    applicable = [r for r in spec_rows if r["applicability"] == "APPLICABLE"]
    baselines = compute_baselines(inp, include_np11=False)
    results = []

    for r in applicable:
        npid, cfg, deleted, op = r["NP_ID"], r["configuration_or_branch"], r["deleted_criterion"], r["operation_type"]
        baseline = baselines[(npid, cfg)]
        if npid == "NP01":
            scores = inp.np01_run(deleted)
            results.append(deletion_row_ordinary(npid, cfg, deleted, op, baseline, scores, "CC",
                "reduced local fuzzy-AHP matrix; main-criterion weights unchanged; TOPSIS fully recomputed"))
        elif npid == "NP02":
            scores = inp.np02_run(deleted)
            results.append(deletion_row_ordinary(npid, cfg, deleted, op, baseline, scores, "final_weight",
                "reduced criteria AHP matrix recomputed; retained local alternative priorities synthesized"))
        elif npid == "NP03":
            scores = inp.np03_run(deleted, cfg == "ERP04_COST_PARALLEL")
            results.append(deletion_row_ordinary(npid, cfg, deleted, op, baseline, scores, "Ci",
                "D2 normalized row removed; remaining weights renormalized; branch-specific PIS/NIS and Ci recomputed"))
        elif npid == "NP04":
            scores = inp.np04_run(deleted)
            results.append(deletion_row_ordinary(npid, cfg, deleted, op, baseline, scores, "Y_crisp",
                "prespecified primary rough-normalized criterion omitted; remaining rough weights unchanged; native WISP utilities recomputed"))
        elif npid == "NP05":
            # cfg p-HFC_CE-I_Hamming etc.
            parts = cfg.split("_")
            kind, dist = parts[1], parts[2]
            scores = inp.np05_run(kind, dist, deleted)
            results.append(deletion_row_ordinary(npid, cfg, deleted, op, baseline, scores, "U_percent",
                "entropy-distance normalization recomputed over retained criteria; q=2/beta=3 fixed; COPRAS rerun with C6 retained"))
        elif npid == "NP07":
            scores = inp.np07_run(deleted)
            results.append(deletion_row_ordinary(npid, cfg, deleted, op, baseline, scores, "net_flow",
                "deleted printed ANP weight removed; retained printed weights renormalized; PROMETHEE II p=2 recomputed"))
        elif npid == "NP11":
            scores, sol = inp.np11_run(deleted)
            results.append(deletion_row_ordinary(npid, cfg, deleted, op, baseline, scores, "total_global_weight",
                "reduced LFPP criteria model solved with prespecified M=10^3/SLSQP settings; local ERP vectors fixed; DEMATEL excluded; nonuniqueness warning retained", sol))
        elif npid == "NP12":
            v = inp.np12_run(deleted)
            Q = v["Q"]
            b = baselines[("NP12", "VIKOR_Q050")]
            bdet = rank_details(b["scores"], b["alts"], False); ddet = rank_details(Q, b["alts"], False)
            tau = kendall_tau_b_from_orders(b["scores"], Q, False)
            mard = float(np.mean(np.abs(ddet["midrank"] - bdet["midrank"])))
            b_rec = b["vikor"]["rec_mask"]; d_rec = v["rec_mask"]
            rec_label = canonical_set(np.flatnonzero(d_rec), b["alts"])
            topq = ddet["winner_set"]
            results.append({
                "NP_ID": npid, "configuration_or_branch": cfg, "deleted_criterion": deleted, "operation_type": op, "status": "EXECUTED",
                "baseline_winner_retained": "", "exact_winner_set": "", "baseline_top2_both_retained": "", "baseline_top2_overlap_share": "",
                "MARD": fmt(mard), "Kendall_tau_b": fmt(tau), "complete_weak_order": ddet["weak_order"],
                "terminal_score_vector": score_vector_text(b["alts"], Q, "Q"),
                "baseline_recommendation_set_retained": bools(np.array_equal(b_rec, d_rec)),
                "baseline_A2_in_recommendation_set": bools(bool(d_rec[b["alts"].index("A2")])),
                "exact_native_recommendation_set": rec_label,
                "top_Q_leader_set_SECONDARY": topq,
                "C1_acceptable_advantage": bools(v["C1"]), "C2_acceptable_stability": bools(v["C2"]),
                "native_solver_status": "", "native_solver_objective": "",
                "method_note": "q/v fixed at 0.5; weights renormalized after deletion; source-native VIKOR recommendation conditions applied; top-Q leader secondary",
            })
        else:
            raise ValueError(npid)

    write_csv(out / "R2C_DELETION_LEVEL_RESULTS.csv", results, DELETION_FIELDS)
    write_ne_records(spec_rows, out)
    write_np03_summary(results, out)
    write_np05_summary(results, out)
    write_np12_summary(results, baselines, out)
    write_case_summary(results, baselines, out)
    write_cross_case_summary(results, out)
    write_method_notes(out, results)


def write_ne_records(spec_rows: List[dict], out: Path) -> None:
    ne = []
    # keep configuration-level C6 rows for NP05, but summarize global NE lineages one row each in this file as well.
    for r in spec_rows:
        if r["applicability"] != "NE": continue
        ne.append({
            "NP_ID": r["NP_ID"], "configuration_or_branch": r["configuration_or_branch"], "deleted_criterion": r["deleted_criterion"],
            "status": "NE", "reason": r["note"], "source_checkpoint": r["source_checkpoint"]
        })
    write_csv(out / "R2C_NE_RECORDS.csv", ne, ["NP_ID", "configuration_or_branch", "deleted_criterion", "status", "reason", "source_checkpoint"])


def agg_num(vals: List[float], fn) -> str:
    x = [v for v in vals if math.isfinite(v)]
    return "" if not x else fmt(fn(np.asarray(x, float)))


def case_summary_row(npid, cfg, rows: List[dict], baseline: dict) -> dict:
    winner = [r["baseline_winner_retained"] == "YES" for r in rows]
    top2 = [r["baseline_top2_both_retained"] == "YES" for r in rows]
    mard = [float(r["MARD"]) for r in rows]
    tau = [float(r["Kendall_tau_b"]) for r in rows if r["Kendall_tau_b"] not in ("", "nan")]
    baseline_order = rank_details(baseline["scores"], baseline["alts"], baseline["higher"])["weak_order"]
    changed = [r["deleted_criterion"] for r in rows if r["complete_weak_order"] != baseline_order]
    critical = [r["deleted_criterion"] for r in rows if r["baseline_winner_retained"] != "YES"]
    counts = Counter(r["exact_winner_set"] for r in rows)
    return {
        "NP_ID": npid, "configuration_or_branch": cfg, "applicable_deletions": str(len(rows)),
        "winner_retained_count": str(sum(winner)), "winner_retention_share": fmt(np.mean(winner)),
        "top2_both_retained_count": str(sum(top2)), "top2_retention_share": fmt(np.mean(top2)),
        "MARD_mean": agg_num(mard, np.mean), "MARD_median": agg_num(mard, np.median), "MARD_max": agg_num(mard, np.max),
        "Kendall_tau_b_mean": agg_num(tau, np.mean), "Kendall_tau_b_median": agg_num(tau, np.median), "Kendall_tau_b_min": agg_num(tau, np.min),
        "winner_critical_deleted_criteria": "|".join(critical),
        "deletions_causing_complete_order_change": "|".join(changed),
        "winner_set_counts": ";".join(f"{k}:{counts[k]}" for k in sorted(counts)),
        "recommendation_set_retained_count": "", "recommendation_set_retention_share": "", "A2_in_recommendation_set_count": "", "A2_in_recommendation_set_share": "",
        "recommendation_set_counts": "", "top_Q_leader_counts_SECONDARY": "",
        "caveat": "finite descriptive share of enumerated single-criterion deletions; not a probability",
    }


CASE_SUMMARY_FIELDS = [
    "NP_ID", "configuration_or_branch", "applicable_deletions", "winner_retained_count", "winner_retention_share",
    "top2_both_retained_count", "top2_retention_share", "MARD_mean", "MARD_median", "MARD_max",
    "Kendall_tau_b_mean", "Kendall_tau_b_median", "Kendall_tau_b_min", "winner_critical_deleted_criteria",
    "deletions_causing_complete_order_change", "winner_set_counts",
    "recommendation_set_retained_count", "recommendation_set_retention_share", "A2_in_recommendation_set_count", "A2_in_recommendation_set_share",
    "recommendation_set_counts", "top_Q_leader_counts_SECONDARY", "caveat"
]


def write_case_summary(results: List[dict], baselines: dict, out: Path) -> None:
    groups = defaultdict(list)
    for r in results:
        groups[(r["NP_ID"], r["configuration_or_branch"])].append(r)
    rows = []
    for key in sorted(groups):
        npid, cfg = key
        rr = groups[key]
        if npid == "NP12":
            rec = [r["baseline_recommendation_set_retained"] == "YES" for r in rr]
            a2 = [r["baseline_A2_in_recommendation_set"] == "YES" for r in rr]
            mard = [float(r["MARD"]) for r in rr]
            tau = [float(r["Kendall_tau_b"]) for r in rr]
            rc = Counter(r["exact_native_recommendation_set"] for r in rr)
            qc = Counter(r["top_Q_leader_set_SECONDARY"] for r in rr)
            critical = [r["deleted_criterion"] for r in rr if r["baseline_recommendation_set_retained"] != "YES"]
            rows.append({
                "NP_ID": npid, "configuration_or_branch": cfg, "applicable_deletions": str(len(rr)),
                "winner_retained_count": "", "winner_retention_share": "", "top2_both_retained_count": "", "top2_retention_share": "",
                "MARD_mean": fmt(np.mean(mard)), "MARD_median": fmt(np.median(mard)), "MARD_max": fmt(np.max(mard)),
                "Kendall_tau_b_mean": fmt(np.mean(tau)), "Kendall_tau_b_median": fmt(np.median(tau)), "Kendall_tau_b_min": fmt(np.min(tau)),
                "winner_critical_deleted_criteria": "|".join(critical),
                "deletions_causing_complete_order_change": "|".join(r["deleted_criterion"] for r in rr if r["complete_weak_order"] != "A2 > A1 > A3"),
                "winner_set_counts": "",
                "recommendation_set_retained_count": str(sum(rec)), "recommendation_set_retention_share": fmt(np.mean(rec)),
                "A2_in_recommendation_set_count": str(sum(a2)), "A2_in_recommendation_set_share": fmt(np.mean(a2)),
                "recommendation_set_counts": ";".join(f"{k}:{rc[k]}" for k in sorted(rc)),
                "top_Q_leader_counts_SECONDARY": ";".join(f"{k}:{qc[k]}" for k in sorted(qc)),
                "caveat": "native VIKOR recommendation set is primary; top-Q leader is secondary; finite deletion shares are descriptive, not probabilities",
            })
        else:
            rows.append(case_summary_row(npid, cfg, rr, baselines[key]))
    write_csv(out / "R2C_CASE_LEVEL_SUMMARY.csv", rows, CASE_SUMMARY_FIELDS)


def write_np03_summary(results: List[dict], out: Path) -> None:
    by = {(r["configuration_or_branch"], r["deleted_criterion"]): r for r in results if r["NP_ID"] == "NP03"}
    rows = []
    for c in [f"ERP{i:02d}" for i in range(1, 16)]:
        a = by[("A_STRICT_EXPLICIT_DIRECTION", c)]; b = by[("ERP04_COST_PARALLEL", c)]
        rows.append({
            "deleted_criterion": c,
            "primary_winner_retained": a["baseline_winner_retained"], "parallel_winner_retained": b["baseline_winner_retained"],
            "primary_exact_winner_set": a["exact_winner_set"], "parallel_exact_winner_set": b["exact_winner_set"],
            "primary_complete_weak_order": a["complete_weak_order"], "parallel_complete_weak_order": b["complete_weak_order"],
            "primary_MARD": a["MARD"], "parallel_MARD": b["MARD"],
            "primary_Kendall_tau_b": a["Kendall_tau_b"], "parallel_Kendall_tau_b": b["Kendall_tau_b"],
            "same_winner_set_between_branches": bools(a["exact_winner_set"] == b["exact_winner_set"]),
            "same_complete_weak_order_between_branches": bools(a["complete_weak_order"] == b["complete_weak_order"]),
            "source_resolution_rule": "NONE_FROM_DELETION_OUTCOMES — source direction ambiguity remains prospectively parallel",
        })
    fields = list(rows[0].keys())
    write_csv(out / "R2C_NP03_PARALLEL_BRANCH_COMPARISON.csv", rows, fields)


def write_np05_summary(results: List[dict], out: Path) -> None:
    rr = [r for r in results if r["NP_ID"] == "NP05"]
    rows = []
    configs = sorted(set(r["configuration_or_branch"] for r in rr))
    for c in ["C1", "C2", "C3", "C4", "C5"]:
        sub = [r for r in rr if r["deleted_criterion"] == c]
        sub.sort(key=lambda r: r["configuration_or_branch"])
        win = np.asarray([1.0 if r["baseline_winner_retained"] == "YES" else 0.0 for r in sub])
        mard = np.asarray([float(r["MARD"]) for r in sub]); tau = np.asarray([float(r["Kendall_tau_b"]) for r in sub])
        row = {
            "deleted_criterion": c, "configuration_count": str(len(sub)),
            "winner_retention_min": fmt(win.min()), "winner_retention_median": fmt(np.median(win)), "winner_retention_max": fmt(win.max()),
            "MARD_min": fmt(mard.min()), "MARD_median": fmt(np.median(mard)), "MARD_max": fmt(mard.max()),
            "Kendall_tau_b_min": fmt(tau.min()), "Kendall_tau_b_median": fmt(np.median(tau)), "Kendall_tau_b_max": fmt(tau.max()),
            "all_six_agree_exact_winner_set": bools(len(set(r["exact_winner_set"] for r in sub)) == 1),
            "all_six_agree_complete_weak_order": bools(len(set(r["complete_weak_order"] for r in sub)) == 1),
            "six_configuration_results": " || ".join(f"{r['configuration_or_branch']}[winner={r['exact_winner_set']};order={r['complete_weak_order']};MARD={r['MARD']};tau={r['Kendall_tau_b']}]" for r in sub),
            "pooling_rule": "DESCRIPTIVE ACROSS SIX CO-PRIMARY CONFIGURATIONS ONLY; NOT POOLED AS INDEPENDENT OBSERVATIONS",
        }
        rows.append(row)
    fields = list(rows[0].keys())
    write_csv(out / "R2C_NP05_SIX_CONFIGURATION_SUMMARY.csv", rows, fields)


def write_np12_summary(results: List[dict], baselines: dict, out: Path) -> None:
    rr = [r for r in results if r["NP_ID"] == "NP12"]
    rows = []
    for r in rr:
        rows.append({
            "deleted_criterion": r["deleted_criterion"], "q_v": "0.5",
            "exact_native_recommendation_set": r["exact_native_recommendation_set"],
            "baseline_recommendation_set_retained": r["baseline_recommendation_set_retained"],
            "baseline_A2_in_recommendation_set": r["baseline_A2_in_recommendation_set"],
            "top_Q_leader_set_SECONDARY": r["top_Q_leader_set_SECONDARY"],
            "complete_Q_weak_order": r["complete_weak_order"], "MARD": r["MARD"], "Kendall_tau_b": r["Kendall_tau_b"],
            "C1_acceptable_advantage": r["C1_acceptable_advantage"], "C2_acceptable_stability": r["C2_acceptable_stability"],
            "Q_score_vector": r["terminal_score_vector"],
        })
    write_csv(out / "R2C_NP12_VIKOR_DELETION_SUMMARY.csv", rows, list(rows[0].keys()))


def write_cross_case_summary(results: List[dict], out: Path) -> None:
    # One row per benchmark lineage. NP03 and NP05 remain single lineages with branch/config summaries in-cell.
    by = defaultdict(list)
    for r in results: by[r["NP_ID"]].append(r)
    case_rows = read_csv(out / "R2C_CASE_LEVEL_SUMMARY.csv")
    cs = defaultdict(list)
    for r in case_rows: cs[r["NP_ID"]].append(r)
    rows = []
    for n in range(1, 13):
        npid = f"NP{n:02d}"
        if npid in {"NP06", "NP08", "NP09", "NP10", "NP11"}:
            reason = {"NP06":"reduced Choquet capacity not defensible", "NP08":"no terminally unique baseline", "NP09":"literal native chain nonfinite", "NP10":"D0 source limitation; Qb/Qn map + S1–S6 unavailable", "NP11":NP11_NE_REASON}[npid]
            rows.append({"NP_ID":npid,"single_criterion_deletion_applicability":"NE","operation_type":"NE","applicable_deletion_count":"0",
                         "winner_or_recommendation_retention_share":"NE","winner_or_recommendation_critical_deletions":"NE","branch_configuration_caveat":reason})
            continue
        if npid == "NP03":
            a = next(r for r in cs[npid] if r["configuration_or_branch"] == "A_STRICT_EXPLICIT_DIRECTION")
            b = next(r for r in cs[npid] if r["configuration_or_branch"] == "ERP04_COST_PARALLEL")
            rows.append({"NP_ID":npid,"single_criterion_deletion_applicability":"APPLICABLE","operation_type":"TERMINAL_POSTWEIGHT_DELETION","applicable_deletion_count":"15 unique criteria × 2 prospectively paired branches",
                         "winner_or_recommendation_retention_share":f"primary={a['winner_retention_share']}; parallel={b['winner_retention_share']}",
                         "winner_or_recommendation_critical_deletions":f"primary={len([x for x in a['winner_critical_deleted_criteria'].split('|') if x])}; parallel={len([x for x in b['winner_critical_deleted_criteria'].split('|') if x])}",
                         "branch_configuration_caveat":"two branches reported separately; no pooled denominator and no source-direction resolution from the single-criterion deletion analysis"})
        elif npid == "NP05":
            vals = [float(r["winner_retention_share"]) for r in cs[npid]]
            crit = [len([x for x in r["winner_critical_deleted_criteria"].split('|') if x]) for r in cs[npid]]
            rows.append({"NP_ID":npid,"single_criterion_deletion_applicability":"APPLICABLE_WITH_C6_NE","operation_type":"NATIVE_REWEIGHTING_AFTER_DELETION","applicable_deletion_count":"5 unique criteria × 6 co-primary configurations; C6 NE",
                         "winner_or_recommendation_retention_share":f"median_across_configs={fmt(np.median(vals))}; range={fmt(np.min(vals))}..{fmt(np.max(vals))}",
                         "winner_or_recommendation_critical_deletions":f"median_across_configs={fmt(np.median(crit))}; range={min(crit)}..{max(crit)}",
                         "branch_configuration_caveat":"all six co-primary; descriptive across configurations only; no pooled denominator/selection of most stable"})
        elif npid == "NP12":
            r = cs[npid][0]
            rows.append({"NP_ID":npid,"single_criterion_deletion_applicability":"APPLICABLE","operation_type":"TERMINAL_POSTWEIGHT_DELETION","applicable_deletion_count":r["applicable_deletions"],
                         "winner_or_recommendation_retention_share":r["recommendation_set_retention_share"],
                         "winner_or_recommendation_critical_deletions":str(len([x for x in r["winner_critical_deleted_criteria"].split('|') if x])),
                         "branch_configuration_caveat":"native VIKOR recommendation set at q/v=0.5 is primary; top-Q leader secondary"})
        else:
            r = cs[npid][0]
            op = by[npid][0]["operation_type"]
            rows.append({"NP_ID":npid,"single_criterion_deletion_applicability":"APPLICABLE","operation_type":op,"applicable_deletion_count":r["applicable_deletions"],
                         "winner_or_recommendation_retention_share":r["winner_retention_share"],
                         "winner_or_recommendation_critical_deletions":str(len([x for x in r["winner_critical_deleted_criteria"].split('|') if x])),
                         "branch_configuration_caveat":"NP07 counts Kılıç 2015 executable baseline only" if npid=="NP07" else ("LFPP ERP-ranking only; DEMATEL excluded; optimizer nonuniqueness warning retained" if npid=="NP11" else "")})
    fields = ["NP_ID","single_criterion_deletion_applicability","operation_type","applicable_deletion_count","winner_or_recommendation_retention_share","winner_or_recommendation_critical_deletions","branch_configuration_caveat"]
    write_csv(out / "R2C_CROSS_CASE_SUMMARY.csv", rows, fields)


def write_method_notes(out: Path, results: List[dict]) -> None:
    counts = Counter(r["NP_ID"] for r in results)
    text = f"""ERP-MCDA benchmark — R2C CASE METHOD NOTES

SCOPE
Executed deterministic single-criterion deletion analysis under the prespecified protocol and documented applicability plan.
No terminal-weight perturbation rerun, native sensitivity, or decision-matrix perturbation is part of this execution.

EXECUTED DELETION-OUTCOME ROW COUNTS
NP01={counts['NP01']} (12); NP02={counts['NP02']} (5); NP03={counts['NP03']} (30 = 15×2 paired branches); NP04={counts['NP04']} (12); NP05={counts['NP05']} (30 = C1–C5×6 co-primary configurations); NP07={counts['NP07']} (11); NP11={counts['NP11']} (0; single-criterion deletion NE); NP12={counts['NP12']} (18).
Total executed deletion-outcome rows={len(results)}. Expected=118.

METHOD INPUTS AND RULES
NP01 — NATIVE_REWEIGHTING_AFTER_DELETION. The deleted subcriterion is removed from its own local triangular-fuzzy reciprocal pairwise matrix; that local fuzzy-AHP vector is recomputed with the prespecified literal geometric-mean/defuzzification algorithm. Three main-criterion weights remain unchanged. Global weights and TOPSIS are regenerated. No simple final-weight deletion substitute is used.
NP02 — NATIVE_REWEIGHTING_AFTER_DELETION. The reduced criteria AHP matrix is solved by the prespecified column-normalization/row-mean rule; retained local alternative priorities are synthesized.
NP03 — TERMINAL_POSTWEIGHT_DELETION from the prespecified D2 normalized checkpoint. Both A_STRICT_EXPLICIT_DIRECTION and ERP04_COST_PARALLEL are run for the same 15 deletion labels, separately, with no branch selection from outcomes.
NP04 — TERMINAL_POSTWEIGHT_DELETION on the prespecified primary literal raw-supplement rough-normalized checkpoint. Remaining printed rough weights are not renormalized or collapsed; native rough-WISP K/P and four utility families are recomputed. The Table-6/rounding explanatory comparison outside the primary reconstruction is not used.
NP05 — NATIVE_REWEIGHTING_AFTER_DELETION for C1–C5 in all six co-primary CE-I/CE-II × Hamming/Euclidean/Hausdorff configurations. Entropy-distance normalization is recomputed over retained criteria and the full p-HFC/COPRAS downstream chain is rerun. C6 is NE because it is the sole cost criterion; q=2 and beta=3 stay fixed.
NP06 — NE. No reduced Choquet capacity or Shapley-index renormalization was invented. The publication-reported interaction-off comparison is treated separately under the source-defined sensitivity scope; no uniquely executable source-defined no-interaction reconstruction is available.
NP07 — Kılıç et al. 2015 only. TERMINAL_POSTWEIGHT_DELETION with retained printed ANP weights renormalized and PROMETHEE II recomputed; V-shape p=2 fixed. Temur & Bolat CBDO is not emulated.
NP08 — NE because no terminally unique baseline/tie-break exists.
NP09 — NE because the literal native chain becomes nonfinite before terminal output.
NP10 — NE at final D0/O3 source resolution because the concrete Qb/Qn map and Supplementary Tables S1–S6 are unavailable; no unique terminal baseline can be defined from the documented public source chain.
NP11 — NE for single-criterion deletion (C1–C6) by prespecified execution rule. Reason: NUMERICAL_NONUNIQUENESS_AND_SOLVER_FAILURE_UNDER_PRESPECIFIED_LITERAL_PROTOCOL. No NP11 criterion deletion, solver recovery, alternate start, multistart, alternate solver, tolerance/bound/M change, gauge constraint, analytical tie-break, or fallback was run. DEMATEL remains excluded.
NP12 — TERMINAL_POSTWEIGHT_DELETION with remaining published weights renormalized and q/v fixed at 0.5. S/R/Q and the same source-native VIKOR C1/C2 compromise-acceptance rule are recomputed. Native recommendation set is primary; top-Q leader is secondary only. The five publication-reported q/v values are reproduced separately by the source-defined sensitivity module.

SCIENTIFIC INTERPRETATION
Deletion fractions are descriptive shares of the finite, prospectively enumerated one-at-a-time criterion omissions under method-compatible recomputation. They are not probabilities and are not pooled into an ERP-literature-wide robustness/failure rate.
"""
    (out / "R2C_CASE_METHOD_NOTES.txt").write_text(text, encoding="utf-8")



def parse_args():
    ap=argparse.ArgumentParser(description="Run the prespecified single-criterion deletion analysis.")
    ap.add_argument("--r1a",type=Path,required=True); ap.add_argument("--r1b",type=Path,required=True)
    ap.add_argument("--r1c",type=Path,required=True); ap.add_argument("--r1d",type=Path,required=True)
    ap.add_argument("--r2a",type=Path,required=True); ap.add_argument("--r2b",type=Path,required=True)
    ap.add_argument("--spec",type=Path,required=True); ap.add_argument("--out",type=Path,required=True)
    return ap.parse_args()

def main():
    args=parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    import shutil
    shutil.copy2(args.spec,args.out/SPEC_FILENAME)
    inp=Inputs(args.r1a,args.r1b,args.r1c,args.r1d,args.r2a,args.r2b)
    execute_deletions(args,inp,args.out)
    return 0

if __name__=="__main__":
    raise SystemExit(main())

