# Part 2 — Đọc paper và Hiện thực: Failure Recovery trong Thao tác Robot bằng Visual-Language

**Chủ đề:** Failure Recovery (Phục hồi sau lỗi)
**Paper 1:** FLARE: A Failure-Aware Framework for Autonomous Correction and Recovery in Visual-Language Robotic Manipulation — CVPR 2026
**Paper 2:** Can VLMs Diagnose and Recover from VLA Manipulation Faults? (VLA-FixBench + FaultEval) — ICML 2026
**Thư mục hiện thực:** `D:\MinhHuy\EyeCode` (`src/` + `research/`)

---

## 1. Vấn đề nghiên cứu (Research Problem)

Mô hình Vision-Language-Action (VLA: π0, OpenVLA, GR00T N1...) điều khiển robot bằng cách ánh xạ trực tiếp quan sát hình ảnh + câu lệnh ngôn ngữ thành chuỗi hành động. Chúng làm tốt khi mọi thứ đúng kịch bản, nhưng **rất giòn (brittle)**: một nhiễu nhỏ ở tay máy, một va chạm bất ngờ, hay vật thể bị đổ là cả task thất bại không cứu được — không giống con người có khả năng tự sửa lỗi liên tục.

Cả hai paper cùng trả lời một câu hỏi: **làm sao để robot tự phát hiện lỗi và tự phục hồi (recover), thay vì đứng yên chờ can thiệp?**

## 2. Ý tưởng chính và Đóng góp

### 2.1. Paper 1 — FLARE (CVPR 2026, Zhao et al.)

**Chẩn đoán gốc rễ:** sự giòn không nằm ở kiến trúc model mà ở **chế độ dữ liệu (data regime)**. Demo của con người có 2 khiếm khuyết:
1. **Trajectory-monotonic (đơn điệu):** robot luôn đi theo một dải pose hẹp gắn với tiến độ task → policy học *tương quan giả* giữa cấu hình khớp của chính nó và thành công, thay vì đọc trạng thái môi trường. Gặp pose mới (dù vật thể vẫn đúng chỗ) là policy "đơ". (gọi là ID)
2. **Success-centric (chỉ toàn mẫu thành công):** dataset không hề chứa ví dụ phục hồi → gặp trạng thái thảm họa (cốc bị đổ) là hết cách. (gọi là OOD)

**Giải pháp — phân loại lỗi ID/OOD + song kiếm Retry/Reset:**
- **ID Error (In-Distribution):** môi trường vẫn nằm trên quỹ đạo đúng, chỉ pose robot bị lạ → chỉ cần **"Retry"**: chiến lược tăng cường dữ liệu **Perturbation & Bridging** — chèn nhiễu pose ngẫu nhiên giữa các đoạn subtask rồi nối cầu (bridging) quay lại, dạy VLA thực hiện đúng bước tiếp theo từ *mọi* cấu hình. Khả năng retry thành bẩm sinh của policy.
- **OOD Error (Out-of-Distribution):** môi trường đã hỏng (vật đổ, kẹt) → cần **"Reset" skill**: dùng MLLM offline (Gemini) phân tích video lỗi → xác định vật cần reset → thu thập ít demo của con người (10–20) cho skill object-centric ("dựng lại cái cốc") → tăng cường tương tự. Các skill lưu trong **Skill Bank** dưới dạng LoRA adapter riêng, MLLM online làm trọng tài chuyển prompt giữa task chính và reset skill (detect → reset → resume).

**Kết quả báo cáo:** trung bình **84,0% success** trên 9 task RoboMimic (hơn backbone π0.5 là +11,8 điểm, hơn Phoenix 57,8%); real-robot (Stack 3 blocks / Insert U-block): 75,0% / 55,0%.

### 2.2. Paper 2 — VLA-FixBench + FaultEval (ICML 2026, Yan et al.)

Không đề xuất policy mới mà xây **chuẩn đánh giá (benchmark)**: VLM có thực sự giúp VLA chẩn đoán + sửa lỗi không, hay chỉ "bình luận sau trận đấu"?

**Đóng góp:**
- **VLA-FixBench:** 6.034 episode lỗi (40 môi trường sim + 2 robot thật Franka) phủ 3 nhóm lỗi Perception / Planning / Control, 4 mức nghiêm trọng (L0–L3), kèm nhãn chi tiết: stage, loại lỗi, timestamp lỗi, độ lệch không gian 3D, chiến lược sửa.
- **FaultEval:** khung đánh giá 3 tầng static → dynamic → real: (a) *static* — phân loại lỗi (FTC), đánh giá mức nặng (FSR), chấm subtask (SSE); (b) *dynamic* — bộ ba **Stop Time / Rollback Time / vector hiệu chỉnh 3D**, đo bằng GCA (hiệu chỉnh hình học), TLA (định vị thời gian), SSR (success trong sim); (c) *real-time* — Recall/Precision/F2/FPR + success rate trên robot thật. Đánh giá 20 VLM.
- **Cơ chế cộng tác VLM–VLA:** vòng kín **detect → rollback → correct**: VLM phát hiện lỗi, dừng task, rollback về trạng thái an toàn trong quá khứ, cộng vector hiệu chỉnh 3D rồi chạy tiếp.

**Kết quả báo cáo:** can thiệp của chuyên gia (upper bound) cải thiện **+13 điểm trên LIBERO và +35 điểm trên robot thật**; còn VLM tự động hiện tại tăng ít vì **khoảng cách suy luận–thực thi (reasoning–execution gap)**; phát hiện nghịch lý *sensitivity–stability*: model nhạy (GPT-5-2 Recall 0,857) báo động giả nhiều (FPR 0,757) làm hỏng cả trial vốn thành công (SR = 0), còn model dè dặt giữ SSR cao nhờ... ít can thiệp.

## 3. So sánh hai paper

| Tiêu chí | FLARE (CVPR 2026) | VLA-FixBench (ICML 2026) |
|---|---|---|
| Mục tiêu | **Xây** khả năng phục hồi vào trong policy | **Đo** khả năng chẩn đoán/phục hồi của VLM |
| Vai trò VLM/MLLM | Offline phân tích lỗi + online trọng tài chuyển skill | Judger chẩn đoán + ra tham số rollback/hiệu chỉnh |
| Phân loại lỗi | ID (pose lạ) / OOD (môi trường hỏng) | Perception / Planning / Control × L0–L3 |
| Cơ chế phục hồi | Retry bẩm sinh + Reset skill (LoRA bank) | Detect → rollback → correct (vector 3D rời rạc −2..+2) |
| Dữ liệu | Tự tạo: perturbation-bridging + demo reset (10–20/skill) | Dataset 6K episode có nhãn mịn, public benchmark |
| Điểm mạnh | End-to-end chạy thật, số liệu sim + real tốt | Chuẩn hóa, so sánh được 20 model, chỉ ra giới hạn VLM |
| Điểm yếu | Phụ thuộc MLLM phân tích offline; reset vật khó (pod đổ chỉ 24%) | VLM tự động cải thiện ít; rollback sai thời điểm gây hại |

**Nhận xét:** hai paper bổ sung cho nhau — FLARE là "thuốc", VLA-FixBench là "xét nghiệm". Thiết kế đúng đắn là dùng FaultEval để đo, rồi dùng Retry/Reset của FLARE để chữa.

## 4. Thiết lập codebase và Hiện thực quy mô nhỏ

Repo gốc của cả hai paper chưa public kèm bài báo (FLARE: không kèm link code; VLA-FixBench hẹn release tại `https://kakigo.github.io/VLA-FixBench/`), và chạy full (fine-tune π0.5/OpenVLA-7B trên RoboMimic/LIBERO + gọi Gemini/GPT API) vượt quá máy cá nhân. Theo đúng tinh thần "small-scale reproduction", hiện thực **mô phỏng tối giản** tái tạo trung thực 2 cơ chế cốt lõi:

**File:** `src/failure_recovery_demo.py` — chỉ cần `numpy` + `matplotlib`, chạy CPU vài giây:
```
! python D:\MinhHuy\EyeCode\src\failure_recovery_demo.py
```

**Những gì demo tái tạo:**
1. **Taxonomy ID/OOD của FLARE:** môi trường pick-and-place 2D (approach–grasp–transport–place); fault injector tạo 30% ID (tay máy bị đẩy lệch, vật vẫn đúng chỗ) + 20% OOD (vật bị hất văng khỏi trạng thái hợp lệ).
2. **Retry (perturbation-bridging):** mode `retry` nối cầu từ pose nhiễu về vật thể và grasp lại — tương đương việc học từ dữ liệu bridging.
3. **Reset skill:** mode `retry_reset` di chuyển tới vật bị đổ, khôi phục nó về trạng thái hợp lệ rồi resume task — tương đương LoRA reset adapter + MLLM chuyển skill.
4. **Vòng detect–rollback–correct của VLA-FixBench:** judger VLM mô phỏng (Recall 0,85 / FPR 0,08) và oracle-chuyên gia (upper bound), hiệu chỉnh bằng **mô hình học được (hồi quy tuyến tính, có train/test split)** thay vì luật cứng.
5. **Metric:** Success Rate toàn bộ + tách riêng SR_ID / SR_OOD (đúng tinh thần FaultEval đo theo nhóm lỗi), Recall/Precision của judger.

## 5. Kết quả định lượng (lần chạy `seed=1000+i`, N=300 episode/mode)

> *(Số liệu do script sinh ra — xem `research/assets/metrics.json`. Chạy lại lệnh ở mục 4 để tái tạo.)*

| Mode | SR toàn bộ | SR_ID | SR_OOD |
|---|---|---|---|
| Baseline (không phục hồi) | 0,557 | 0,167 | 0,065 |
| Retry (FLARE-ID) | 0,807 | 1,000 | 0,065 |
| Retry + Reset (FLARE full) | 1,000 | 1,000 | 1,000 |
| VLM-loop (detect–rollback–correct) | 0,917 | 0,878 | 0,774 |
| Oracle chuyên gia (upper bound) | 1,000 | 1,000 | 1,000 |

**Judger VLM (mode vlm_loop):** Recall = 0,836 · Precision = 0,907 · Rollback-rate = 0,423.

**Hình:** `research/assets/fig_sr_compare.png` (cột so sánh 5 mode) và `research/assets/fig_trajectories.png` (4 quỹ đạo tay máy/vật thể: baseline-hỏng vs phục hồi-thành công cho ID và OOD).

**Đọc số liệu theo 2 paper:** (a) Retry đưa SR_ID từ 0,167 → 1,000 nhưng SR_OOD vẫn dậm chân ở 0,065 — tái hiện đúng khẳng định của FLARE: retry chỉ chữa được ID, lỗi OOD *bắt buộc* cần reset skill (retry_reset đưa SR_OOD → 1,000); (b) khoảng cách VLM-loop (0,917) → oracle (1,000) tái hiện *reasoning–execution gap* của VLA-FixBench: chẩn đoán đúng chưa đủ, hiệu chỉnh thiếu chính xác vẫn hỏng (SR_OOD của VLM-loop chỉ 0,774 so với 1,000 của oracle).

**Metric học mô hình hiệu chỉnh:** hồi quy tuyến tính đạt MAE train = 0,0383 (n=400), test = 0,0405 (n=200) — chứng tỏ thành phần "học cách sửa" hội tụ tốt, lỗi còn lại của vòng kín nằm ở khâu *detect/rollback* (đúng kết luận paper 2: TLA/GCA mới là nút thắt, không phải nhận diện lỗi).

## 6. Phân tích success / failure cases

**Thành công:**
- **ID + Retry:** tay máy bị đẩy lệch tới 1,5 đơn vị nhưng vật còn nguyên → bridging grasp lại, success gần như nominal. Đây là đóng góp cốt lõi của FLARE: tách pose robot khỏi trạng thái môi trường.
- **OOD + Reset:** vật bị hất văng → reset skill khôi phục về điểm pick rồi resume. Không có bước này success = 0 tuyệt đối.
- **Oracle:** rollback đúng thời điểm + hiệu chỉnh hoàn hảo → upper bound, khớp định tính mức +13/+35 điểm paper 2 báo cáo.

**Thất bại:**
- **OOD không reset (baseline SR_OOD = 0,065; retry SR_OOD = 0,065):** gần như hỏng tuyệt đối — minh họa "success-centric dataset" của FLARE: policy chưa từng thấy trạng thái này nên không có hành vi nào để sinh ra.
- **Missed detection (~16%):** judger VLM bỏ sót lỗi thật (Recall = 0,836) → trượt về baseline, kéo SR_ID xuống 0,878 và SR_OOD xuống 0,774.
- **False alarm (~9%):** judger báo lỗi trên trial vốn thành công (Precision = 0,907) → rollback không cần thiết — đúng nghịch lý sensitivity–stability (paper 2: GPT-5-2 SR = 0 vì FPR 0,757; demo nhẹ hơn nhờ FPR thấp).

## 7. Một limitation và hướng khắc phục

**Limitation (chung cho cả 2 paper, demo cũng tái hiện): hiệu chỉnh không gian thiếu chính xác và can thiệp thiếu hiệu chuẩn độ tin cậy.** FLARE thừa nhận reset vật khó (pod đổ chỉ 24–20%); VLA-FixBench đo được Magnitude Accuracy < 20% ở mọi model và rollback sai thời điểm gây *secondary failures*. Nguyên nhân sâu: VLM suy luận bằng ngôn ngữ/hình ảnh thô, không có grounding hình học chính xác và không biết khi nào mình không chắc.

**Hướng khắc phục đề xuất (kết hợp cả hai paper):**
1. **Confidence-calibrated intervention:** judger chỉ can thiệp khi độ tin cậy vượt ngưỡng thích ứng theo mức nặng (L1/L2/L3) — lỗi nhẹ (redundant motion) thì bỏ qua, lỗi nặng mới rollback. Trực tiếp trị nghịch lý sensitivity–stability.
2. **Hiệu chỉnh có cấu trúc thay vì vector rời rạc:** thay vector −2..+2 bằng đề xuất grasp pose 6D (dùng Any6D như bản real-robot của FLARE) + kiểm chứng trong sim trước khi chấp hành (dry-run rollback), loại secondary failures.
3. **Đóng vòng bằng FaultEval:** mỗi reset skill mới của FLARE phải vượt bài đo GCA/TLA của FaultEval trước khi nhập Skill Bank — biến benchmark của paper 2 thành "cửa kiểm định" cho thuốc của paper 1.

## 8. Nguồn tham khảo

- Paper 1 (bản đọc): `research/paper1_FLARE.md` — Zhao et al., CVPR 2026, tr. 22391–22401.
- Paper 2 (bản đọc): `research/paper2_VLA-FixBench.md` (`yan26r.md`) — Yan et al., ICML 2026 (PMLR 306).
- Project page VLA-FixBench: https://kakigo.github.io/VLA-FixBench/
- Code hiện thực nhỏ: `src/failure_recovery_demo.py`; số liệu + hình: `research/assets/`.
