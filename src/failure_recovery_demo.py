"""Tai hien quy mo nho: FLARE (Retry/Reset) + VLA-FixBench (detect-rollback-correct).

Mo phong pick-and-place 2D voi 2 loai loi theo taxonomy cua FLARE:
  - ID error : vat the van nam dung cho, chi tay may bi nhieu (can Retry)
  - OOD error: vat the bi do/lat khoi trang thai hop le (can Reset skill)

Va vong detect-rollback-correct cua VLA-FixBench voi 2 judger:
  - mock VLM judger (recall/FPR huu han) vs human-oracle (upper bound)

Cau truc episode: approach -> grasp check -> recover -> transport -> place.
Chi can: numpy + matplotlib. Chay CPU vai giay.
Cach chay:  python D:\\MinhHuy\\EyeCode\\src\\failure_recovery_demo.py
Ket qua:    D:\\MinhHuy\\EyeCode\\research\\assets\\ (2 hinh PNG + metrics.json)
"""

import json
import os

import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RNG = np.random.default_rng(0)
OUT = r"D:\MinhHuy\EyeCode\research\assets"
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- 1. Hoc nho:
# Hoc bo du doan vector hieu chinh tu loi quan sat (mo phong "hoc kha nang
# sua loi" thay vi dung luat cung). Hoi quy tuyen tinh, train vai ms CPU.
# ----------------------------------------------------------------
def train_correction_model(n_train=400, n_test=200):
    def gen(n):
        err = RNG.uniform(-1.0, 1.0, size=(n, 2))          # loi quan sat (dx, dy)
        corr = -err + RNG.normal(0, 0.05, size=(n, 2))     # hieu chinh ly tuong + nhieu
        return err, corr
    Xtr, Ytr = gen(n_train)
    W, *_ = np.linalg.lstsq(np.hstack([Xtr, np.ones((n_train, 1))]), Ytr, rcond=None)
    for name, n in (("train", n_train), ("test", n_test)):
        X, Y = gen(n) if name == "test" else (Xtr, Ytr)
        pred = np.hstack([X, np.ones((len(X), 1))]) @ W
        mae = float(np.mean(np.abs(pred - Y)))
        print(f"[correction-model] {name} MAE = {mae:.4f} (n={n})")
    return W


W_CORR = train_correction_model()

# ------------------------------------------------- 2. Mo phong episode 2D ---
# Trang thai: ee (tay may), obj (vat), goal. 3 phase: approach-grasp | recover | transport-place.
PICK = np.array([2.0, 2.0])
GOAL = np.array([8.0, 8.0])
GRASP_R = 0.6   # ban kinh gap thanh cong
PLACE_R = 0.8


def run_episode(mode, rng):
    """mode: baseline | retry | retry_reset | vlm_loop | oracle.
    Tra ve (success, trajec_ee, trajec_obj, log)."""
    ee = np.array([0.0, 0.0])
    obj = PICK + rng.normal(0, 0.1, 2)
    holding = False
    grasp_ok = False
    traj_ee, traj_obj = [ee.copy()], [obj.copy()]
    log = {"fault": "none", "detected": False, "rollback": False}

    def step(target, noise=0.05):
        nonlocal ee, obj
        ee = ee + 0.5 * (target - ee) + rng.normal(0, noise, 2)
        if holding:
            obj = ee.copy()
        traj_ee.append(ee.copy())
        traj_obj.append(obj.copy())

    # --- inject fault (30% ID, 20% OOD, 50% nominal) ---
    u = rng.random()
    fault = "ood" if u < 0.20 else ("id" if u < 0.50 else "none")
    log["fault"] = fault

    # --- phase 1: approach (4 buoc), loi xay ra o buoc cuoi ---
    for t in range(4):
        step(obj if t >= 2 else PICK)
        if t == 3 and fault == "id":
            ee = ee + rng.uniform(-1.5, 1.5, 2)   # tay may bi day lech, vat van dung cho
            traj_ee.append(ee.copy())
            traj_obj.append(obj.copy())
        if t == 3 and fault == "ood":
            obj = obj + rng.uniform(-3.0, 3.0, 2)  # vat bi do vang -> trang thai OOD
            traj_ee.append(ee.copy())
            traj_obj.append(obj.copy())

    grasp_ok = np.linalg.norm(ee - obj) < GRASP_R

    def regrasp(steps=6, noise=0.03):
        """Bridging: tu pose hien tai di ve vat the va gap lai."""
        nonlocal grasp_ok
        for _ in range(steps):
            step(obj, noise=noise)
        grasp_ok = np.linalg.norm(ee - obj) < GRASP_R
        log["rollback"] = True

    # --- phase 2: phuc hoi theo tung mode ---
    if mode in ("retry", "retry_reset") and fault == "id" and not grasp_ok:
        # FLARE Retry: kha nang retry bam sinh tu du lieu perturbation-bridging
        regrasp()
    if mode == "retry_reset" and fault == "ood":
        # FLARE Reset skill: toi cho vat bi do, khoi phuc ve trang thai hop le, grasp lai
        for _ in range(8):
            step(obj, noise=0.03)
        obj = PICK.copy()  # reset ve trang thai hop le (upright)
        traj_ee.append(ee.copy())
        traj_obj.append(obj.copy())
        regrasp(steps=8)
    if mode in ("vlm_loop", "oracle") and fault != "none":
        # VLA-FixBench: detect -> rollback -> correct
        recall = 1.0 if mode == "oracle" else 0.85
        detected = rng.random() < recall
        log["detected"] = bool(detected)
        if detected:
            log["rollback"] = True
            err = obj - ee
            corr = -err if mode == "oracle" else np.append(err, 1.0) @ W_CORR
            ee = ee - corr * 0.9  # ap hieu chinh (chuyen gia: hoan hao; VLM: qua model da hoc)
            if fault == "ood":
                for _ in range(4):
                    step(obj, noise=0.03)
                obj = PICK.copy()
                traj_ee.append(ee.copy())
                traj_obj.append(obj.copy())
                regrasp(steps=6)
            else:
                regrasp()
    if mode == "vlm_loop" and fault == "none" and rng.random() < 0.08:
        # False alarm: rollback thua gay detour + nhieu (trade-off sensitivity-stability)
        log["detected"] = True
        for _ in range(2):
            step(ee + rng.normal(0, 0.5, 2), noise=0.2)

    holding = grasp_ok

    # --- phase 3: transport + place ---
    for _ in range(6):
        step(GOAL, noise=0.03)
    success = bool(holding and np.linalg.norm(ee - GOAL) < PLACE_R)
    return success, np.array(traj_ee), np.array(traj_obj), log


# ------------------------------------------------- 3. Danh gia --------------
MODES = ["baseline", "retry", "retry_reset", "vlm_loop", "oracle"]
N = 300
results = {m: {"ok": 0, "by_fault": {"none": [0, 0], "id": [0, 0], "ood": [0, 0]},
               "det_tp": 0, "det_fp": 0, "det_fn": 0, "rb": 0} for m in MODES}
examples = {}

for i in range(N):
    for m in MODES:
        ok, tee, tob, lg = run_episode(m, np.random.default_rng(1000 + i))
        r = results[m]
        r["ok"] += ok
        f = lg["fault"]
        r["by_fault"][f][1] += 1
        r["by_fault"][f][0] += ok
        if f != "none" and lg["detected"]:
            r["det_tp"] += 1
        if f != "none" and not lg["detected"]:
            r["det_fn"] += 1
        if f == "none" and lg["detected"]:
            r["det_fp"] += 1
        r["rb"] += lg["rollback"]
        key = (m, f)
        if key not in examples and f != "none" and (
                (ok and m in ("retry", "retry_reset", "vlm_loop", "oracle"))
                or (not ok and m in ("baseline", "retry"))):
            examples[key] = (tee, tob)

print("\n===== SUCCESS RATE (SR) =====")
metrics = {}
for m in MODES:
    sr = results[m]["ok"] / N
    per = {}
    for f in ("none", "id", "ood"):
        s = results[m]["by_fault"][f]
        per[f] = round(s[0] / max(s[1], 1), 3)
    metrics[m] = {"SR": round(sr, 3), "SR_nominal": per["none"],
                  "SR_ID": per["id"], "SR_OOD": per["ood"]}
    print(f"{m:12s} SR={sr:.3f} | nominal={per['none']:.3f} | SR_ID={per['id']:.3f} | SR_OOD={per['ood']:.3f}")

print("\n===== VLM JUDGER (vlm_loop) =====")
r = results["vlm_loop"]
rec = r["det_tp"] / max(r["det_tp"] + r["det_fn"], 1)
prec = r["det_tp"] / max(r["det_tp"] + r["det_fp"], 1)
print(f"Recall={rec:.3f} Precision={prec:.3f} Rollback-rate={r['rb']/N:.3f}")
metrics["vlm_loop"].update({"recall": round(rec, 3), "precision": round(prec, 3)})

with open(os.path.join(OUT, "metrics.json"), "w") as f:
    json.dump(metrics, f, indent=2)
print(f"\nDa luu metrics.json -> {OUT}")

# ------------------------------------------------- 4. Truc quan hoa ---------
labels = ["Baseline", "Retry", "Retry+Reset", "VLM-loop", "Oracle"]
sr_all = [metrics[m]["SR"] for m in MODES]
sr_id = [metrics[m]["SR_ID"] for m in MODES]
sr_ood = [metrics[m]["SR_OOD"] for m in MODES]
x = np.arange(len(labels))
w = 0.25
plt.figure(figsize=(9, 5))
plt.bar(x - w, sr_all, w, label="Toan bo")
plt.bar(x, sr_id, w, label="Chi ID error")
plt.bar(x + w, sr_ood, w, label="Chi OOD error")
plt.xticks(x, labels, rotation=12)
plt.ylabel("Success Rate")
plt.title("So sanh Baseline vs FLARE-style Retry/Reset vs VLM-loop (N=300, seed=0)")
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_sr_compare.png"), dpi=120)

fig, ax = plt.subplots(2, 2, figsize=(10, 8))
cases = [("baseline", "id", "Baseline gap ID -> FAIL"),
         ("retry", "id", "Retry phuc hoi ID -> OK"),
         ("baseline", "ood", "Baseline gap OOD -> FAIL"),
         ("retry_reset", "ood", "Reset skill phuc hoi OOD -> OK")]
for a, (m, f, title) in zip(ax.ravel(), cases):
    tee, tob = examples.get((m, f), (np.zeros((2, 2)), np.zeros((2, 2))))
    a.plot(tee[:, 0], tee[:, 1], "b-o", ms=3, label="tay may")
    a.plot(tob[:, 0], tob[:, 1], "r--s", ms=3, label="vat the")
    a.scatter(*PICK, c="g", s=80, marker="*")
    a.scatter(*GOAL, c="k", s=80, marker="X")
    a.set_title(title)
    a.legend(fontsize=8)
    a.set_aspect("equal")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_trajectories.png"), dpi=120)
print(f"Da luu 2 hinh PNG -> {OUT}")
