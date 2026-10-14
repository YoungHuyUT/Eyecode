            Can VLMs Diagnose and Recover from VLA Manipulation Faults?


         Bowen Yan * 1 Jiahao Xiao * 1 Kehui Liu 1 Jianbo Zhang 2 Zicheng Zhang 1 Qi Jia 1 Zhongjie Jia 2
                            Haoming Song 2 Chunyi Li 3 Bin Zhao 1 Guangtao Zhai 1


                           Abstract                                   quently experience failures in robotic manipulation tasks.
        Existing VLA models frequently fail in robotic                Fault diagnosis heavily relies on expert knowledge and man-
        manipulation tasks, with poorly structured fault              ual intervention, making it difficult to scale. The diagnostic
        types that often require expert diagnosis. While              process is often subjective, lacks standardized evaluation
        VLMs offer strong explanatory capabilities, their             criteria, and suffers from insufficient responsiveness for
        effectiveness in assisting VLAs is limited by their           real-time systems. These challenges underscore the need
        unclear role in diagnostics and inadequate collabo-           for principled, standardized benchmarks and automated re-
        ration mechanisms. To address this, we introduce              covery mechanisms that can evaluate and improve failure
        VLA-FixBench, a fault evaluation dataset that                 handling in a reproducible and real-time manner.
        spans perception, planning, and control failures,             Vision–Language Models (VLM) exhibit semantic under-
        and provides annotations for task stages, fault               standing capabilities in task explanation and strategy guid-
        types, and spatiotemporal repair strategies. We               ance (Wang et al., 2025b; Zhang et al., 2025b;c), raising a
        further propose FaultEval, a static-to-dynamic-               natural question: Can VLMs effectively assist VLAs in
        to-real evaluation framework that benchmarks                  fault diagnosis and correction? Prior evaluation efforts
        20 VLMs across multiple fault-related dimen-                  have primarily focused on static task understanding, such
        sions. Building on these insights, we design a                as spatial reasoning and visual question answering (Zhang
        VLM–VLA collaboration mechanism that local-                   et al., 2025d; Chen et al., 2025), with limited study of multi-
        izes spatiotemporal deviations and rolls back task            level VLM-VLA collaboration (Yang et al., 2025b). Al-
        execution to enable targeted recovery. Experi-                though existing benchmarks capture certain VLM capabil-
        ments show that FaultEval reliably characterizes              ities (Wang et al., 2025a; Wu et al., 2025c;b; Zhang et al.,
        VLM-based closed-loop diagnosis and repair. The               2025a), their impact on improving VLA performance re-
        upper-bound analysis using human expert inter-                mains unclear (Grislain et al., 2025). Moreover, current
        vention shows that an idealized feedback loop can             VLM-VLA interactions are largely instruction-based and
        improve task success rates by 13% on LIBERO                   lack a unified closed-loop framework for diagnosis and re-
        and 35% on real-world robots. Our code, bench-                covery (Yang et al., 2025a; Thoduka et al., 2024). As a
        mark, and project page will be publicly released              result, existing methods face key limitations: insufficient
        at: https://kakigo.github.io/VLA-FixBench/                    focus on VLM-VLA collaboration with no standardized
                                                                      interfaces (Yang et al., 2025b; Chen et al., 2024), coarse
                                                                      datasets lacking fine-grained fault and repair annotations,
                                                                      the absence of a unified evaluation framework for VLM-
1. Introduction
                                                                      assisted repair in embodied manipulation, and inconsistent
With the rapid advancement of embodied intelligence,                  fault taxonomies that fail to decouple perception, control,
Vision-Language-Action (VLA) models have demonstrated                 and planning errors. To address these challenges, we in-
increasing advantages in scenarios such as industrial assem-          troduce VLA-FixBench, a benchmark for VLM-assisted
bly, logistics sorting, and household services. However, due          VLA fault diagnosis and recovery, with over 6,000 anno-
to current technical limitations, existing VLA models fre-            tated failure cases across perception, planning, and control.
    *
                                                                      To our knowledge, VLA-FixBench is the first benchmark
   Equal contribution 1 Shanghai AI Laboratory, Shanghai, China       that jointly evaluates static diagnosis, temporal rollback lo-
2
 Shanghai Jiao Tong University, Shanghai, China 3 Nanyang
Technological University, Singapore.       Correspondence to:         calization, geometric correction, simulation recovery, and
Chunyi Li <lichunyi@pjlab.org.cn>, Guangtao Zhai <zhaiguang-          real-robot recovery for VLM-assisted VLA manipulation
tao@pjlab.org.cn>.                                                    faults. Based on VLA-FixBench, we propose FaultEval, a
                                                                      unified static-to-dynamic-to-real evaluation framework that
Proceedings of the 43 rd International Conference on Machine          assesses VLM performance in fault identification, severity
Learning, Seoul, South Korea. PMLR 306, 2026. Copyright 2026
by the author(s).                                                     estimation, temporal localization, spatial correction, and

                                                                  1


---

                                                Can VLMs Diagnose and Recover from VLA Faults?

  Level-1
  The robot             Approach
                                                                                                                   �                Human Judger System
  performs the task                                                                                                             •     [Error-A] and [Level-2] identified .
  but exhibits           Grasp                                                   Distortion   Pose error
  redundant motions.                         Retry！                                                                             •     Failure localized at [step i].
                        Transport
                                                                      Blur                                 Collision            •     Rollback to [step i−1].        Success




                                                                               n
                                                                                                                                •     Apply a small [+x offset].      Rate




                                                                                                   P la
                                                                                 o
                                                                             pti
  Level-2




                                                                                                      nn
                                                                       rce
 The robot arm is       Approach                       Overexposure
                                                                                 VLA-Fix                       Sequence error
                                                                                                                                       What abilities are missing in




                                                                                                        ing
                                                                      Pe
 not performing the
 task, but the task      Grasp
                                                                                 Bench-6K                                              VLMs compared to humans?
 can still continue.   Transport
                                                         Noise                                                      Aimless
                                                                                                                   wandering          VLM Judger System                  Success
                                                                                                                                                                          Rate
  Level-3                                                                            Control
 The robot arm is       Approach                                                                                                •     [Error type] and [level-?] uncertain.
 not performing the
                         Grasp                                   Delay                                                          •     Failure roughly localized around [step j].
 task, and the task

                                                                                                                   �
                                                                                                           Noise
 can no longer                                                                                                                  •     Rollback to a [nearby step].
                       Transport
 continue.                                                                     Swing     Overshooting                           •     Apply a tentative [-x offset]


    Failure Understanding                                    Temporal Localization                                                      Spatial Deviation
                                                                Understanding                                                            Understanding
 Task: Turn on the stove and place                         Task: Open the teapot lid and place                                      Task: Unplug the connector and
       the moka pot on it.                                       the tea bag into the teapot.                                             insert it into the black socket.
 Error: Inaccurate end-effector positioning                Error: The gripper skipped the lid-opening and                           Error: A slight VLA planning deviation along
       causes a collision that topples the moka pot.              grasped the tea bag, causing a sequence error.                           ⟨dis⟩ causes the gripper to miss the USB.
         Can VLM correctly identify the number and                 Which step should the gripper return to                                 How much positional offset is needed for
               types of manipulation errors?                            complete the first subtask?                                                 successful grasping?


Figure 1. Overview of VLA-FixBench, Center: Hierarchical failure types in Perception, Planning, and Control. Left: Severity
definitions ranging from redundant motions (Level-1) to catastrophic failures (Level-3). Right: Performance disparity between Human
and VLM judgers in closed-loop error recovery. Bottom: Three evaluation dimensions: Failure identification, Temporal localization for
rollback, and Spatial deviation estimation for corrective action.


closed-loop recovery. We further construct a VLM–VLA                                                   causal reasoning, repair suggestion, and temporal con-
collaboration mechanism that enables fault detection, roll-                                            sistency, and evaluates 20 representative vision lan-
back, and action repair during VLA execution. Based on                                                 guage models.
VLA-FixBench, we additionally construct and validate a
VLM–VLA collaboration mechanism that enables real-                                                 • VLM-VLA collaboration mechanism, a VLM–VLA
time fault detection, rollback, and action repair during VLA                                         collaboration mechanism that leverages VLM-based
execution. Although the automated VLM–VLA loop still                                                 fault detection and repair guidance to form a closed-
provides limited gains due to the reasoning-execution gap,                                           loop perception, decision and execution feedback sys-
human-expert upper-bound intervention demonstrates the                                               tem, achieving an average 13% improvement in task
potential of the proposed detect–rollback–correct mecha-                                             success rates across multi-task evaluations.
nism. By providing accurate recovery parameters, expert
intervention improves task success rates on LIBERO (Liu
et al., 2023)and real-world robots. These results suggest                                      2. Related Works
that rollback-based recovery can substantially improve task                                    2.1. Robotic Failure Diagnosis and Recovery
robustness when fault localization and corrective actions are
sufficiently accurate.                                                                         Early studies on robotic fault diagnosis primarily focus on
                                                                                               low-level anomaly detection (Zhao et al., 2025), such as
Our main contributions are summarized as follows:                                              joint torque deviation, force–torque inconsistency, or trajec-
   • VLA-FixBench, a robotic manipulation fault evalua-                                        tory tracking errors (Thoduka et al., 2024).These approaches
     tion dataset comprising 6k failure cases covering per-                                    are effective for detecting deviations but lack task-level in-
     ception, control, and cognition errors, with fine-grained                                 terpretability and offer no actionable repair guidance. To
     annotations of sub-task stages, error types, and repair                                   bridge low-level signals and task execution, some works
     strategies.                                                                               analyze failures in specific manipulation tasks. As a re-
                                                                                               sult, existing failure analyses remain fragmented and lack
   • FaultEval, a unified evaluation framework that bench-                                     a unified framework for systematic evaluation across tasks
     marks VLMs across fault recognition, localization,                                        and models (Lin et al., 2025).Classical learning-based ap-

                                                                                          2


---

                                                                          Can VLMs Diagnose and Recover from VLA Faults?

 Dataset Construction                                                       Static Benchmark                                              Dynamic Benchmark
                                                                            Vision-LMM




                                                                                                                                                                                               Textual Description
                                                                                                Whether each subtask is
                                                                                                successfully completed?

                                                                                                TaskA-1:True,TaskA-2...TaskB-2:False             Sim                     Real
      step-a          step-b ··· step-g                     step-h
                                                                                                                                          Task : Open the middle drawer of the cabinet.
                                  1 Task stage decomposition                                    What type of error occurred?
                                     Approach             Approach
                                      Grasp      ···        Grasp
                                                                            Video-LLM
                                                                                                                          Error type：F
                                     Transport             Transport
                                                                                                                                                  1s     2s            3s               4s                     5s            6s      7s
   ANNOTATION                 Open the teapot lid     Put the teabag in
                                                                              1s
                                                                                               When should the task be stopped?                                                                                                                    Success Rate




                                                                                   ✂️
                                                                                                                                                                                                                                              Environmental damage ️
                                                                                                                                                                                                                     Retry                     Robot arm damage ️
  2 Task Quality Evaluation           3 Task Temporal and Spatial                                                                                        Error severity level
                                        Localization                                                                         Time：5s                                                         Roll back time                       Stop time
                                                                              2s




                                                                                   ✂️
                                                                                                                                                              Can roll back ?
    Failure type classification         Failure onset timestamp
                                                                                               What is the severity level of the error?
                                         x - offset                                                                                                     x-offset = 0        Roll back
         Failure severity                                                                                                                                                     time
                                        y - offset                            3s                                               Level-2                  y-offset = 0
                                                                                                                                                        z-offset = 1
                                        z - offset
                                                                                           Convenience                                                                              Accuracy
        Failure description




Figure 2. Overview of the VLA-FixBench framework. The pipeline includes: (Left) Dataset Construction with hierarchical task
decomposition and spatio-temporal failure annotations; (Middle) Static Benchmark for evaluating VLMs’ diagnostic reasoning; and
(Right) Dynamic Benchmark for assessing closed-loop performance and error recovery. The bottom axis indicates the trade-off between
evaluation convenience and physical accuracy.


proaches employ supervised classifiers or temporal mod-                                                       tion heads to maintain broad semantic knowledge while
els to predict failure states from sensory inputs. While                                                      fine-tuning on robotic trajectories. These models represent
effective within constrained settings, these models strug-                                                    actions as a structured sequence within a generative frame-
gle to generalize to heterogeneous failure types and offer                                                    work. However, as task complexity increases, these models
limited interpretability or corrective guidance. Reinforce-                                                   frequently suffer from error accumulation in multi-stage
ment learning has been explored for failure recovery by                                                       execution, where minor initial deviations often escalate into
learning corrective behaviors through interaction, includ-                                                    irreversible system failures (Khanna et al., 2025). While
ing recent efforts that guide agents back to in-distribution                                                  existing benchmarks like LIBERO (Liu et al., 2023)provide
states after Out-Of-Distribution (OOD) failures (Kim et al.,                                                  rigorous environments to assess task success rates , they
2025). While effective in specific domains (Li et al., 2026),                                                 largely overlook the underlying failure behaviors. Current
such methods typically rely on task rewards or policy-level                                                   evaluation standards remain predominantly binary, lacking
supervision, embedding recovery implicitly in learned be-                                                     the fine-grained diagnostic granularity required to categorize
haviors. Consequently, they offer limited interpretability,                                                   specific faults or understand the mechanisms of error recov-
generalize poorly across diverse manipulation tasks, and                                                      ery. This gap necessitates a more comprehensive framework
lack explicit task-level fault diagnosis and repair represen-                                                 to analyze and rectify VLA model vulnerabilities. In con-
tations. Recent VLMs demonstrate strong capabilities in                                                       trast to prior work, we focus on task-level, interpretable,
visual understanding, explanation, and high-level reason-                                                     and recoverable failures in robotic manipulation. We intro-
ing, enabling applications in task planning and instruction                                                   duce a unified benchmark and evaluation framework that
following. Despite promising results, the role of VLMs in                                                     systematically characterizes failure types, severity, and spa-
assisting VLAs during failure remains unclear (Dai et al.,                                                    tiotemporal repair behaviors, and explicitly measures how
2024; Pacaud et al., 2025).As a result, it is difficult to as-                                                VLMs contribute to closed-loop fault recovery in VLAs.
sess whether VLMs genuinely improve robotic robustness
or merely provide plausible post-hoc explanations.                                                            3. Construction of VLA-FixBench
                                                                                                              Hierarchical Failure Classification To diagnose VLA fail-
2.2. Benchmark and Failure Evaluation of VLM
                                                                                                              ures, we design a two-level hierarchical classification (Fig-
Recent advancements in Vision-Language-Action (VLA)                                                           ure 1). The first level categorizes failures by functional
models have significantly enhanced the capabilities of em-                                                    stage—perception, control, and planning—to localize errors.
bodied agents in diverse manipulation tasks (Team, 2025;                                                      The second level evaluates failure severity from the perspec-
Duan et al., 2024). The fundamental principle of VLA                                                          tive of recoverability, considering task continuity, motion
models lies in cross-modal grounding, where visual per-                                                       quality, and environmental impact. Failures are grouped
ceptions are interleaved with textual prompts to condition                                                    into four levels: no noticeable failure, minor disturbance,
the robot policy. Architectures like OpenVLA (Kim et al.,                                                     self-recoverable failure, and unrecoverable failure requir-
2024) and GR00T N1 (NVIDIA et al., 2025) utilize frozen                                                       ing human intervention. This scheme unifies functional
vision-language backbones augmented with lightweight ac-                                                      attribution with severity assessment, providing a consistent

                                                                                                         3


---

                                                                                                                    Can VLMs Diagnose and Recover from VLA Faults?

                               Level-3                                                                                   LLaVA-OneVision                                 Y-AA                                                  Qwen3VL-235B
                                                                                                                                                                                     

     FIH                                                                                        Level-2              Doubao-Video              Y-DC                                                           X-DC         InternVL3-78B
                                                                                                                     InternVL3-78B                                                                                         LLaMA-3.2-90B-Vision
                                                                                      
                                                                                                                     Qwen3-VL-235B                                    
                                                                                                                                                                                                                               Gemini-2-5-pro
                                            
                                                                                                                         GPT5-2                                                           
                                                                                                                                                                                                                           GPT-5-2
SG                                                          
                                                                                                          Level-1        Gemini-3-Flash    Z-AA                                                  
                                                                                                                                                                                                                   X-AA   Doubao-Seed-1-6-Vision
                                                                     
                                                                                                                                                                                                       
                         
                                                                                                                                                           
                                                                                                                                                                                         
  AOCI                                                                                          MLT                                            Z-DC                                                           RIT
                                                       P&P                                                                                                                               FOT
Figure 3. Left: Static diagnostic accuracy across different task domains and severity levels. Right: Dynamic diagnostic performance,
including Geometric Correction Accuracy (GCA) and Temporal Localization Accuracy (TLA).


framework for VLA failure analysis.                                                                                                              the failure, and the Subtask Success Evaluation (SSE)
Multi-dimensional Annotation We develop a fine-grained                                                                                           si = {si,1 , . . . , si,m } representing the binary completion
annotation framework to construct a high-resolution failure                                                                                      status si,j ∈ {0, 1} across m sequential subtasks.
map across three integrated dimensions: temporal, spatial,                                                                                       To reduce the computational cost and localization difficulty
and semantic. Specifically, the framework incorporates: (i)                                                                                      of long-horizon task evaluation, we adopt a stage-wise re-
Sub-task Success, evaluating stage-wise completion; (ii)                                                                                         construction strategy. Each task is temporally segmented
Qualitative Evaluation, identifying fault types and severity                                                                                     into consecutive stages, with visual observations sampled at
levels; (iii) Temporal Localization, determining failure onset                                                                                   fixed intervals and provided sequentially to the model. This
timestamps; and (iv) Spatial Characterization, measuring                                                                                         design enables image-only models to be evaluated under a
the deviations of end-effectors or key objects.                                                                                                  unified protocol. The detailed breakdown of dimensions is
Dataset Statistics. VLA-FixBench comprises 6,034 task                                                                                            provided in Appendix E .
execution episodes collected from 40 simulated and two
real-robot environments. The dataset systematically cap-                                                                                         4.2. Dynamic Evaluation
tures a wide spectrum of failure types, stages, and severity
levels. Frequent failures such as Jitter, Grasp Instability,                                                                                     We formalize the dynamic evaluation as a closed-loop re-
and Stagnation appear in over 25% of samples, while rare                                                                                         covery task requiring precise temporal and spatial reasoning.
failures (e.g., Wrong Placement, Target Occluded) occur in                                                                                       For each failure scenario i, the model generates a dynamic
less than 7%, supporting edge-case analysis. The detailed                                                                                        recovery tuple dˆi = ⟨t̂stop , t̂rb , vi ⟩, consisting of the Stop
statistics are provided in Appendix A.                                                                                                           Time t̂stop ∈ R≥0 representing the predicted timestamp
                                                                                                                                                 for operation cessation upon failure detection, the Rollback
                                                                                                                                                 Time t̂rb ∈ R≥0 specifying the target historical state for re-
4. FaultEval Evaluation Framework                                                                                                                version, and the 3D Correction Vector vi = [vx , vy , vz ]⊤ .
We propose a dual-track framework combining a static “writ-                                                                                      In this vector, each discrete element va ∈ {−2, . . . , 2}
ten examination” and a dynamic “road test.” The static track                                                                                     (a ∈ {x, y, z}) quantifies the spatial adjustment intensity
evaluates fault identification, severity estimation, and spa-                                                                                    required to compensate for the manifested execution error.
tiotemporal localization, while the dynamic track assesses                                                                                       To assess corrective capabilities of multimodal models
closed-loop repair effectiveness and final task success. To-                                                                                     in robotic manipulation, we design a dynamic evaluation
gether, these complementary tracks balance efficiency and                                                                                        framework in simulation, focusing on corrective behavior
accuracy, enabling systematic model comparison and diag-                                                                                         during task execution, measured by Geometric Correction
nosis for VLA systems.                                                                                                                           Accuracy (GCA), Temporal Localization Accuracy (TLA),
                                                                                                                                                 and Simulation Success Rate (SSR).
4.1. Static Evaluation
We formalize the static evaluation as a multi-label predic-
tion task conditioned on an input video V and a linguis-                                                                                         VLM-VLA Self-Correction Mechanism We propose a
tic instruction I. For each sample i, the model generates                                                                                        VLM-VLA closed-loop self-correction mechanism that ad-
a diagnostic tuple ŷi = ⟨fi , li , si ⟩ comprising the Fault                                                                                    dresses the limitations of conventional local repairs by cor-
Type Classification (FTC) fi ∈ F identifying the spe-                                                                                            recting errors at their semantic and decision-making roots.
cific category of the detected failure, the Fault Severity                                                                                       Based on the defined state space, the recovery process is for-
Rating (FSR) li ∈ {0, 1, 2, 3} gauging the intensity of                                                                                          mulated as a detection-rollback-correction sequence. Given
                                                                                                                                                 a historical trajectory τ = {s0 , a0 , . . . , ststop }, the mecha-
                                                                                                                                                 nism is defined as follows:
                                                                                                                                           4


---

                                          Can VLMs Diagnose and Recover from VLA Faults?

Table 1. Static Evaluation Results of Fault Type Classification (FTC), Sub-task Success Evaluation (SSE), and Fault Severity Rating
(FSR) across VLA Models.[Keys: Best/Second best in group]Abbreviations and severity definitions are provided in Appendix E.

                                                Fault Type Classification                Sub-task Success Evaluation        Fault Severity Rating
 Model
                                       SOE    LMA     LGD     TLE    TRM        VDF   P&P    SG    AOCI MLT        FIH    L-0   L-1     L-2     L-3
 Gemini-3-Flash(DeepMind, 2025a)      0.2035 0.4215 0.2542 0.6602 0.1004 0.9074 0.6139 0.5704 0.5403 0.6604 0.6094 0.6956 0.1206 0.3783 0.7165
 GPT-5.2(OpenAI, 2025b)               0.2516 0.2727 0.2226 0.3844 0.0633 0.3195 0.6433 0.6161 0.5530 0.7060 0.4906 0.2960 0.1580 0.5052 0.5632
 Llama-3.2-90B-Vision(Meta, 2024)     0.2713 0.2400 0.1484 0.4691 0.1277 0.7383 0.5124 0.6203 0.4747 0.4940 0.5103 0.1987 0.4886 0.1691 0.2605
 Qwen3-VL-235B(Bai et al., 2025)      0.5033 0.2776 0.0123 0.5483 0.0611 0.4002 0.4149 0.5751 0.4597 0.4919 0.4763 0.2490 0.5073 0.0087 0.4764
 InternVL2.5-78B(OpenGVLab, 2024)     0.3786 0.1009 0.2329 0.4571 0.0404 0.4528 0.4092 0.5651 0.4614 0.4974 0.5853 0.3002 0.6861 0.0671 0.1405
 InternVL3-78B (OpenGVLab, 2025)      0.4551 0.2078 0.0426 0.3692 0.0939 0.4460 0.4075 0.5236 0.4777 0.4315 0.5347 0.3065 0.6611 0.0288 0.2516
 Ovis2-34B(Lu et al., 2024)           0.4770 0.2225 0.0084 0.4365 0.0437 0.3619 0.4343 0.6218 0.5234 0.4813 0.4257 0.0000 0.8669 0.2006 0.0511
 Doubao-Seed-1.6(Doubao Team, 2025)   0.2684 0.2973 0.2401 0.2165 0.0526 0.3755 0.5022 0.4611 0.3867 0.4973 0.5082 0.6288 0.3371 0.1485 0.2141
 InternVL3-38B (Zhu et al., 2025)     0.1751 0.0275 0.0381 0.4191 0.1004 0.2702 0.4868 0.5530 0.4597 0.4366 0.4882 0.3431 0.3576 0.3867 0.2427
 Doubao-1-5-vision-pro (Guo et al., 2025) 0.2797 0.1859 0.0336 0.4757 0.0552 0.3534 0.3771 0.4170 0.4661 0.5294 0.4462 0.5236 0.3258 0.0013 0.2375
 InternVL3-14B (Zhu et al., 2025)     0.4595 0.2167 0.0477 0.1965 0.0688 0.2481 0.3765 0.3960 0.4262 0.4600 0.5579 0.2469 0.7505 0.0087 0.0690
 Qwen2.5-VL-72B(Wu et al., 2025a)     0.5602 0.1508 0.0045 0.2888 0.2183 0.0875 0.3602 0.3550 0.4124 0.4004 0.3180 0.0021 0.3243 0.2415 0.3091
 Phi-4(Phi Team, 2025)                0.1299 0.0010 0.0000 0.0000 0.1854 0.0000 0.2795 0.3330 0.4046 0.3272 0.3742 0.9960 0.0000 0.0000 0.0175
 mPLUG-Owl3-7B (Ye et al., 2024)      0.1685 0.0003 0.0000 0.0000 0.0142 0.0136 0.3164 0.3272 0.3684 0.3068 0.3049 0.2793 0.6154 0.0456 0.0166
 LLaVA-OneVision(An et al., 2025)     0.0613 0.0000 0.0000 0.0000 0.0207 0.0000 0.2259 0.2836 0.2654 0.2736 0.2682 0.0931 0.0000 0.5031 0.5709



1) Failure Detection and Stop: The system identifies a                          bottleneck. Our goal is therefore not to maximize representa-
failure and triggers a stop at the predicted timestamp tstop                    tional richness, but to balance generality, executability, and
when the current state ststop falls into the failure state space                cross-model comparability. Experimental results validate
Cf ail . Formally, the termination condition is expressed                       this choice: even with this minimal interface, human-in-the-
as:ststop ∈ Cf ail .The robot ceases operation immediately                      loop corrections yield 13% improvement in simulation and
upon detection, providing the temporal basis for the subse-                     35% on real robots, and precise rollback outperforms coarse
quent rollback operation.                                                       task restarts, demonstrating that the interface is sufficient to
                                                                                support effective recovery while current VLMs remain lim-
2) Rollback Step: A rollback operator R is invoked to                           ited by temporal and spatial grounding rather than interface
revert the robot from the failed state ststop to a previously                   expressivity.
recorded safe state strb :                                                      3) Spatial Correction: Upon reaching strb , the system
                                                                                applies the 3D correction vector v to adjust the subsequent
                          .
         R(ststop , trb ) = strb ,    s.t. 0 ≤ trb < tstop          (1)         execution. The rectified initial action a′trb is computed as:
                                                                                        a′t̂rb = π(strb ) + ∆p,        where ∆p = δ · v             (2)
This ensures the recovery starts from a stable configuration
within the execution history.                                                   Here, ∆p = [∆px , ∆py , ∆pz ]⊤ represents the physical
                                                                                spatial offset, and δ is the unit magnitude constant.
Design Rationale of the Repair Interface: The defined
dynamic tuple—Stop Time, Rollback Time, and 3D Correc-                          Evaluation Capability Dimensions The dynamic evalua-
tion Vector—is an intentionally minimal yet sufficient inter-                   tion framework comprises three core capability dimensions:
face to translate VLM diagnostic capabilities into actionable                   Geometric Correction Accuracy (GCA). GCA evaluates
recovery signals. This design follows three principles: (1)                     the model’s ability to correct execution deviations along
clarity and simplicity, allowing general black-box VLMs to                      three aspects: Axis Alignment (AA), Direction Consistency
integrate without model-specific output heads or adapters;                      (DC), and Magnitude Accuracy (MA). By analyzing spatial
(2) direct mapping from semantic fault judgment through                         vectors of corrective actions, this metric quantifies whether
temporal localization to geometric correction, forming an                       the proposed corrections align with the intended task direc-
interpretable detect–rollback–correct chain; (3) minimal                        tion and scale.
sufficiency, providing the controller with unambiguous in-                      Temporal Localization Accuracy (TLA). TLA formalizes
formation necessary for effective execution. While richer                       the temporal reasoning required for rollback-based recovery.
representations such as bounding boxes, points, masks, or                       It defines two critical decision points: the Fault Onset Time
full trajectory sequences were considered, they introduce                       (FOT), marking the earliest detectable deviation from suc-
additional barriers: structured geometric annotations are                       cessful execution, and the Rollback Initiation Time (RIT),
not reliably producible by all VLMs, and translating them                       indicating when the system should revert to a previous exe-
into executable corrections imposes a separate translation                      cution state. By requiring models to localize both moments,

                                                                            5


---

                                                    Can VLMs Diagnose and Recover from VLA Faults?

Table 2. Simulation Results on Dynamic Evaluation Metrics: Geometric Correction Accuracy (GCA), Temporal Localization Accuracy
(TLA), and Simulation Success Rate (SSR). [Keys: Best/Second best in group]
                                                                            GCA                                                   TLA                      SSR
                 Metrics                             X                       Y                            Z              FOT             RIT
                                                                                                                                                  10   object goal spatial
                                             AA     DC      MA      AA      DC       MA           AA     DC      MA      LFS             EFS
 Human                                      100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00               100.00         100.00   62.50 96.50 89.50 92.00
 Doubao-Seed-1.6 (Doubao Team, 2025)        16.28   10.47   5.81    61.22   27.55    16.33       68.75   56.25   30.21   43.31          29.94    37.50 88.00 65.00 60.50
 GPT-5.2 (OpenAI, 2025b)                    45.35   24.42   15.12   63.27   32.65    20.41       33.33   22.92   11.46   40.13          19.75    37.00 70.50 51.50 48.50
 Gemini-2.5-Pro (DeepMind, 2025b)           41.86   24.42   11.63   46.94   30.61    15.31       31.25   16.67   10.42   48.41          35.67    31.50 79.50 64.00 67.00
 Gemini-2.5-Flash (DeepMind, 2025b)         41.86   19.77   11.63   38.78   22.45    17.35       36.46   28.12   13.54   31.21          29.94    37.00 81.50 66.50 70.00
 ChatGPT-4o-Latest (OpenAI, 2024)           58.14   31.40   17.44   29.59   15.31    9.18        14.58   9.38    4.17    30.57          26.11    31.50 75.00 54.50 49.50
 GPT-5 (OpenAI, 2025a)                      68.60   32.56   12.79   21.43   12.24    7.14         8.33   4.17    0.00    31.85          27.39    36.00 86.00 55.00 52.00
 Llama-3.2-90B-Vision (Meta, 2024)          12.79   4.65    1.16    14.29   8.16     5.10        31.25   12.50   5.21    52.87          23.57    29.50 56.50 66.50 70.00
 InternVL3-38B (Zhu et al., 2025)           23.26   11.63   6.98    14.29   4.08     3.06        10.42   6.25    6.25    32.48           8.92    34.50 69.50 68.50 71.50
 Qwen-2.5-VL-72B (Wu et al., 2025a)         20.93   11.63   8.14    1.02    0.00     0.00        16.67   10.42   5.21    14.01           5.10    28.00 66.00 74.50 79.00
 InternVL3-78B (OpenGVLab, 2025)            12.79   3.49    1.16    12.24   4.08     2.04         8.33   6.25    3.12    29.30           5.10    35.00 71.00 65.50 72.50
 GPT-4o (OpenAI, 2024)                       4.65   2.33    1.16    0.00    0.00     0.00        18.75   9.38    3.12    34.39          14.01    27.50 70.50 56.50 66.00
 Qwen-2.5-VL-7B (Wu et al., 2025a)           4.65   3.49    2.33    3.06    1.02     0.00         0.00   0.00    0.00     9.55           3.82    31.50 80.00 76.00 83.00
 Gemini-2-Flash (DeepMind, 2025b)            0.00   0.00    0.00    0.00    0.00     0.00         1.04   1.04    0.00     3.18           2.55    40.00 85.50 75.50 82.50
 Qwen3-VL-235B (Bai et al., 2025)            1.16   1.16    0.00    0.00    0.00     0.00         0.00   0.00    0.00     0.64           0.00    41.50 79.50 76.50 83.50
 Doubao-1-5-vision-pro (Guo et al., 2025)    0.00   0.00    0.00    0.00    0.00     0.00         1.04   0.00    0.00     1.91           0.00    38.50 75.50 76.50 83.50
 OpenVLA-7B Only                              -       -       -       -       -          -         -       -       -       -              -      43.00 86.50 86.50 83.50




TLA captures whether a judger can support recovery poli-                                         we calculate the diagnostic accuracy independently for each
cies that are temporally precise rather than relying on coarse                                   severity level k ∈ {1, 2, 3}. The accuracy for level k is
task-level restarts alone.                                                                       defined as:
Simulation Success Rate (SSR). SSR measures end-to-end
                                                                                                                                  1 X
task completion over the entire execution horizon in sim-                                                          AcckF SR =         1(li = li∗ )                     (4)
ulation, reflecting the overall stability and effectiveness of                                                                    Nk
                                                                                                                                        i∈Dk
the closed-loop control system. SSR is computed over all
four LIBERO task suites, providing a unified assessment                                          where Dk = {i | li∗ = k} is the subset of samples with
of performance consistency across diverse manipulation                                           ground truth severity level k, and Nk = |Dk | is the total
settings.                                                                                        number of samples in that subset. This categorical break-
                                                                                                 down allows us to identify potential sensitivity gaps,such as
4.3. Real-Time Evaluation                                                                        a model inability to distinguish critical Level-3 failures from
                                                                                                 minor Level-1 perturbations, which is crucial for assessing
To evaluate the practical performance of multimodal models                                       safety-critical performance.
in real-world robotic manipulation, we conduct on-robot
experiments. Video streams are transmitted to the VLM at                                         3) Subtask Success Accuracy (SSA): This metric evalu-
1 Hz for real-time fault diagnosis, rollback decisions, and                                      ates the ability of model to track task progress across multi-
corrective action recommendations.                                                               ple stages in practice:
                                                                                                                                                     
4.4. Metrics                                                                                                           N
                                                                                                                     1 X 1 X
                                                                                                                                  mi
                                                                                                          SSA =                       1(si,j = s∗i,j )    (5)
Static Evaluation Metrics. We employ the following three                                                            N i=1 mi j=1
metrics to quantitatively assess diagnostic proficiency:
1) FTC Accuracy : This metric measures model precision                                           where mi is the number of subtasks in sample i, and s∗i,j is
in identifying the correct failure category:                                                     the success label for the j-th subtask.
                                            N                                                    Dynamic evaluation metrics.
                                      1 X
                    AccFTC =                1(fi = fi∗ )                           (3)
                                      N i=1
                                                                                                 1) Geometric Correction Quality (GCQ): The model
where N is the number of instances, fi∗ is the ground truth                                      predicts a 3D correction vector v = [vx , vy , vz ]⊤ , where
fault type and 1(·) is the indicator function.                                                   va = 0 signifies no correction. For each axis a requir-
                                                                                                 ing a ground truth correction (va∗ ̸= 0), we evaluate per-
2) Level-specific Severity Accuracy (AcckF SR ): To in-                                          formance through three hierarchical binary indicators: (i)
                                                                                                                           (a)
vestigate model sensitivity to failures of varying intensities,                                  Axis Alignment (AA), 1AA = 1(va ̸= 0), which as-

                                                                                             6


---

                                       Can VLMs Diagnose and Recover from VLA Faults?
                                                                                                                                                                                                                                                                                                           
sesses whether the model identifies the necessity of cor-                                                                                                                                                                                               




                                                                         L
rection on the specific axis; (ii) Direction Consistency
        (a)      (a)                                                                                                                                                                                                                                    
(DC), 1DC = 1AA · 1(sgn(va ) = sgn(va∗ )), ensuring the




                                                                         K
                                                                                                                                                                                                                                                                                                           
corrective force is applied in the correct direction; and (iii)                                                                                                                                                                                         




                                                                         J
                                  (a)      (a)
Magnitude Accuracy (MA), 1M A = 1DC · 1(va = va∗ ),
representing a precise match in correction intensity. This                                                                                                                                                                                                             




                                                                         I
hierarchical formulation ensures that higher-level metrics
                                                                                                                                                                                                                                                        




                                                                         H
(DC and MA) are strictly contingent upon the success of the
preceding diagnostic steps in order.                                                                                                                                                                                                                                   




                                                                         G
2) Temporal Localization Accuracy (TLA): To evaluate                                                                                                                                                                                                    




                                                                         F
model temporal responsiveness, we define binary scoring
                                                                                                                                                                                                                                                                       
functions for Stop Time (tstop ) and Rollback Time (trb )




                                                                         E
predictions, measuring whether the predicted timestamps
                                                                                                                                                                                                                                                        




                                                                         D
fall within a tolerance window around the ground truth.
                                                                                                                                   D               E               F          G             H          I                                                  J             K               L
The score for stop time prediction t̂stop is defined as:
                                                                                  Figure 4. Faults correlation analysis. Conditional failure depen-
         (
            1, if t̂stop ∈ t∗stop − ∆−       ∗       +
                                                         
                                     stop , tstop + ∆stop                         dency heatmap over fine-grained fault types. Each entry denotes
 Sstop =                                                    (6)
            0, otherwise                                                          P (b | a), the probability that failure type b occurs simultaneously
                                                                                  or subsequently given failure type a.
∆−          +
  stop and ∆stop denote the early and late tolerances for stop-                                                                                                                         Fault Type
                                                                                                                                                                                                  a                                             
time prediction. This asymmetric window allows for a slight                                                                                                                                                                                                                                          
                                                                         3  ) D X O W  _  7 D V N  / H Q J W K 

---




                                                                                                                                                                                                  b




                                                                                                                                                                                                                                                                                                        $ Y H U D J H   ) D X O W  7 \ S H V 

---


                                                                                                                                                                                                  c
                                                                                                                                                                                                                                                




                                                                                                                                                                                                         ) D L O X U H  6 W H S  , Q G H [
delay in detection while penalizing premature stops.                                                                                                                                           d
                                                                                                                                                                                                  e                                                                                                     
                                                                                                                          
                                                                                                                                                                                                  f
                                                                                                                                                                                                  g
                                                                                                                                                                                                                                                                                                       
                                                                                                                          
                                                                                                                                                                                                  h
                                                                                                                                                                                                  i
Similarly, the score for rollback time prediction t̂rb is con-                                                                                                                                                                                                                                      

strained by a tighter window to ensure precise recovery:                                                                                                                                                                                                                                            
                                                                                                                          
               (                                                                                                                                                                                                                                                                                    

                 1, if t̂rb ∈ t∗rb − ∆−     ∗     +
                                                    
                                      rb , trb + ∆rb                                                                                                                                                                                                                                    
        Srb =                                              (7)                                                                                      Task Length                                                                                                      7 D V N  / H Q J W K
                 0, otherwise
                                                                                  Figure 5. The left figure shows the relationship between different
where t∗ denotes the GT timestamp, and ∆−          rb and ∆rb
                                                             +                    fault types occurrence probability and task length, while the right
                                                                                  figure shows the relationship between the fault-stage occurrence
are the early and late tolerances for rollback-time prediction.
                                                                                  probability and task length.

Real-time evaluation metrics To assess on-robot fault di-                         mark (Liu et al., 2023), and conducted simulation evalua-
agnosis performance, we adopt metrics that jointly measure                        tions on both the LIBERO and LIBERO-Pro (Zhou et al.,
sensitivity, robustness, and task effectiveness. Recall quanti-                   2025) task suites. Then we inject systematic perturbations
fies the proportion of true faults correctly detected, empha-                     into actions and visual inputs to elicit diverse failures in spa-
sizing sensitivity to failures where missed detections incur                      tial reasoning and multi-step execution. Real-world samples
high cost. Precision measures the proportion of predicted                         were acquired via a Franka arm across Tea Preparation and
faults that are correct, reflecting reliability and resistance to                 Charging Plug Insertion tasks, where variations in lighting,
false alarms. The F2-Score combines Recall and Precision                          distractors, and target poses induced a wide range of varied
with greater emphasis on Recall, providing an integrated                          execution faults.
assessment of fault detection capability. The False Positive                      Curation and Benchmarking. The resulting dataset is cu-
Rate (FPR) captures the proportion of non-fault instances                         rated with fine-grained annotations (failure type, subtask,
incorrectly flagged as faults, indicating intervention stabil-                    and severity). We evaluated a diverse model suite, including
ity. Finally, Success Rate (SR) directly measures task com-                       GPT-4o, Gemini-2.5, and Qwen series, across four simula-
pletion under model assistance, serving as the most direct                        tion subsets and physically realistic environments.
indicator of real-world operational effectiveness.

5. Results                                                                          5.2. Static Evaluation Results
                                                                                    Static evaluation (Table 1) reveals a clear performance strati-
5.1. Experimental Setup
                                                                                    fication among VLMs. Proprietary models, notably Gemini-
Data Acquisition.For simulation, we fine-tuned OpenVLA-                             3-Flash and GPT-5.2,consistently dominate the leaderboard:
7B (Kim et al., 2024) using data from the LIBERO bench-                             Gemini excels in perception-centric tasks (VDF: 0.9074;

                                                                    7


---

                                                        Can VLMs Diagnose and Recover from VLA Faults?

                     1                      2                    3                     4        5.3. Dynamic Evaluation Results
                                                                                                Dynamic evaluation measures the synergy between diagnos-
                                                                                                tic reasoning and physical execution. GCA results reveal
                                                                              VLM：Stop！
                                                                                                a universal difficulty hierarchy across all models: Magni-
                    8                       7                    6                     5        tude Accuracy (MA) ¿Direction Consistency (DC) ¿Axis
                                                                                                Alignment (AA). While top-tier models like GPT-5 and
           Success！                                                         VLM：Rollback！       GPT-5.2 demonstrate superior diagnostic precision, achiev-
                                                                                                ing the highest AA scores (up to 68.60%).Their Magnitude
   Figure 6. Failure recovery in the real-robot make-tea task.                                  Accuracy (MA) remains a significant bottleneck (¡20%),
                                                                                                indicating a persistent gap in fine-grained geometric control.
                                                                                                We observe clear and consistent performance differences
Table 3. Real-robot evaluation results. The performance is mea-                                 across X, Y, and Z. Y achieves the most balanced and overall
sured across diagnostic metrics (Recall, Precision, F2-Score, and                               strongest performance across AA, DC, and MA, while X
FPR) and the manipulation Success Rate (SR). [Keys: Best/Second                                 remains competitive on AA and DC but underperforms on
best]
                                                                                                MA. In contrast, Z exhibits a pronounced degradation across
  Model                                     Recall   Precision   F2-Score     FPR     SR        all metrics, particularly MA, indicating a substantially more
 Gemini-2.5-Pro (DeepMind, 2025b)           0.1795    0.4667      0.2047     0.1333   20
                                                                                                challenging setting. This trend is consistent across models,
 Gemini-2.5-Flash (DeepMind, 2025b)         0.1429    0.4167      0.1645     0.0933   25
 Llama-3.2-90B-Vision (Meta, 2024)          0.4821    0.6429      0.5075     0.4286   0         suggesting that the observed gaps are driven by intrinsic
 GPT-5-2 (OpenAI, 2025b)                    0.8571    0.4286      0.7143     0.7568   0         differences among the evaluation settings rather than model-
 Qwen-2.5-VL-7B (Wu et al., 2025a)          0.5333    0.2667      0.4444     0.7097   10
 Qwen3-VL-235B (Bai et al., 2025)           0.2162    0.7273      0.2516     0.0588   15        specific effects.
 Doubao-1-5-vision-pro(Guo et al., 2025)    0.1923    0.6667      0.2242     0.1042   20        TLA results further distinguish models by their temporal
 Doubao-Seed-1.6 (Doubao Team, 2025)        0.2353    0.6667      0.2703     0.1395   15
 Groot-N1.5-3B Only (NVIDIA et al., 2025)       -        -           -          -     30
                                                                                                responsiveness, with Llama-3.2-90B and Gemini-2.5-Pro
 Human                                          -        -           -          -     65        leading in fault onset and rollback timing. However, high
                                                                                                diagnostic scores do not linearly translate to task success.
                                                                                                SSR results expose a correction paradox: aggressive models
                                                                                                (e.g., GPT series) often suffer from lower success rates than
L-3: 0.7165), whereas GPT-5.2 exhibits superior robustness                                      the baseline due to secondary failures induced by imprecise
in long-horizon reasoning, leading the multi-object long-                                       adjustments. In contrast, conservative models like Qwen3-
sequence tasks (MLT: 0.7060). Conversely, open-source                                           235B maintain high SSR (83.50%) primarily through a
models like Qwen2.5/3-VL and InternVL achieve parity                                            silent intervention strategy, underscoring the critical trade-
in high-level semantic understanding, with Qwen2.5-VL-                                          off between proactive correction and operational stability in
78B outperforming all closed-source models in spatial ob-                                       real-world deployments.
ject errors (SOE: 0.5602). Across fault categories, a sharp
perceptual-logical divergence emerges. While visual dis-                                        5.4. Real-Time Evaluation Results
tortion faults are handled reliably, performance collapses
                                                                                                Real-robot evaluations (Table 3) validate the sensitivity-
on task relevance misjudgment (TRM) and lack of goal-
                                                                                                stability paradox. GPT-5-2 achieves the highest sensitiv-
directedness (LGD), with even top-tier models failing to
                                                                                                ity (Recall: 0.8571, F2-Score: 0.7143), but its high FPR
surpass 0.2 accuracy. A similar pattern persists in severity
                                                                                                (0.7568) causes task failure (SR: 0), indicating that over-
assessment: models exhibit distinct sensitivities toward mi-
                                                                                                sensitive diagnosis can disrupt nominal executions. By con-
nor (L-1) or critical (L-3) failures, yet moderate-level faults
                                                                                                trast, Qwen3-VL-235B is more conservative, with the high-
(L-2) remain a universal blind spot (¡0.2). Interestingly,
                                                                                                est Precision (0.7273) and lowest FPR (0.0588), though
perception-limited models like LLaVA-OneVision maintain
                                                                                                its SR (15%) remains below the Groot-N1.5-only baseline.
strong critical failure detection (L-3: 0.5709), suggesting
                                                                                                The drop in real-robot success rate reflects two competing
their utility as conservative safety sentries rather than com-
                                                                                                effects: correction benefit and intervention cost. Current
prehensive diagnosticians.
                                                                                                VLMs may misclassify trajectories that would have suc-
Ultimately, SSE is the most discriminative signal for as-
                                                                                                ceeded without intervention, triggering unnecessary rollback
sessing a model’s understanding of task-level execution
                                                                                                or correction and turning successes into failures. However,
outcomes. In contrast, FTC primarily reflects a model’s
                                                                                                in several cases, they correctly detect that the VLA policy
multimodal perception and semantic classification capabil-
                                                                                                has entered a local optimum or erroneous trajectory, trig-
ity. Together, these results indicate that the key limitation of
                                                                                                ger rollback, and enable successful re-execution, converting
current diagnostic agents lies not in fault recognition itself,
                                                                                                failed trials into successful ones. These cases suggest that
but in reliable spatio-temporal grounding of task progress
                                                                                                the proposed detect–rollback–correct chain can translate
and outcomes, motivating the need for more finer-grained
                                                                                                correct diagnosis into effective physical recovery. Existing
supervision in future VLA systems.

                                                                                            8


---

                                     Can VLMs Diagnose and Recover from VLA Faults?

VLMs can answer diagnostic questions in static settings, but         results demonstrate that closed-loop self-correction is criti-
this ability does not reliably transfer to real robots, where        cal for mitigating error accumulation and enabling reliable
recovery requires spatio-temporal grounding, calibrated cor-         long-horizon manipulation.
rection, and confidence-aware decisions. Thus, our real-             Impact of Rollback Step Selection We further analyze
robot experiments do not claim that off-the-shelf VLMs               recovery strategies by comparing naive task-level rollback
solve robotic recovery; rather, they expose the mismatch be-         with rollback to intermediate execution steps. While re-
tween current VLM benchmarks and the capabilities needed             setting to the initial task pose improves performance over
to improve embodied manipulation success. VLA-FixBench               no correction, it remains consistently inferior to rollback
uses fault diagnosis and rollback-based recovery as a testbed        strategies that localize failures to appropriate temporal seg-
to bridge this gap.                                                  ments, achieving an average improvement of 8.3% points in
Real-Time Latency and Inspection Protocol Our real-                  simulation. This highlights that effective recovery requires
robot evaluation uses a sparse pause-and-inspect protocol            precise temporal fault localization rather than coarse task
instead of querying the VLM at every control step. Each              restarts, validating the design of our rollback mechanism.
task typically triggers only 3–6 diagnoses. Between two
inspection points, the robot is controlled solely by the VLA         6. Conclusion and Outlook
policy, so continuous execution is not affected by VLM la-
tency. In each cycle, the VLA executes for a fixed 1-second          We present VLA-FixBench, a unified benchmark for evalu-
window, recorded as a 20-FPS video segment; robot mo-                ating VLM-driven fault diagnosis and recovery in robotic
tion and VLA inference are then paused for VLM-based                 manipulation, integrating static reasoning, simulation-based
diagnosis; if a recoverable failure is detected, rollback and        closed-loop testing, and real-robot validation. We further
correction are performed before execution resumes. Thus,             show that VLM–VLA collaboration with closed-loop self-
VLM latency is explicitly included in the closed-loop cycle:         correction improves robustness on average. Looking ahead,
                                                                     our results suggest that the main bottleneck is not merely
             Tloop = Texec + Tvlm + Trollback ,           (8)
                                                                     static fault recognition, but the reliable transformation of
where Texec = 1s, Tvlm is the average VLM inference                  semantic diagnosis into temporally grounded, spatially cal-
latency, and Trollback is the physical rollback and correction       ibrated, and physically executable recovery actions. This
time. This design is not merely for latency accommodation:           highlights the need for finer-grained supervision, safer cor-
when the VLA enters an erroneous trajectory or local failure         rection policies, confidence-calibrated intervention mech-
mode, it may repeat ineffective actions and consume more             anisms, and stronger spatio-temporal grounding in future
time than sparse VLM inspection. The real-robot setup is             VLM–VLA systems.
therefore a sparse diagnostic-and-recovery loop that trades
limited inspection latency for recovery from failures that the
VLA alone cannot escape.
                                                                     Acknowledgements
                                                                     a) This work was supported by New Generation Artifi-
5.5. Alignment Between Static and Dynamic Evaluation
                                                                     cial Intelligence-National Science and Technology Major
Static evaluation primarily measures high-level fault under-         Project (2025ZD0124104) in collaboration with Shanghai
standing and reasoning, whereas simulation evaluation em-            Artificial Intelligence Laboratory. b) This work was sup-
phasizes spatiotemporal precision and physical execution ac-         ported by the Shanghai Municipal Special Program for Ba-
curacy. As a result, models excelling in semantic reasoning          sic Research on General AI Foundation Models (Grant No.
do not necessarily perform well in closed-loop control, and          2025SHZDZX025D09), in collaboration with Shanghai Ar-
no existing model achieves strong performance across both            tificial Intelligence Laboratory. c) This work was supported
dimensions. We compute rank correlations between static              in part by the National Natural Science Foundation of China
and simulation evaluations, obtaining Spearman’s ρ = 0.43            under Grants 62225112, 625B2118.
and Kendall’s τ = 0.33. This underscores the necessity
of maintaining both evaluation subsets to comprehensively            Impact Statement
assess VLA robustness.
                                                                     This paper studies failure diagnosis and recovery for Vision-
5.6. Ablation Study                                                  Language-Action (VLA) models. By analyzing how VLM-
Effectiveness of Self-Correction Across all evaluated tasks,         based judgers detect and respond to manipulation failures,
human-in-the-loop correction consistently yields substantial         our work aims to improve robotic reliability and reduce unin-
performance gains over open-loop execution, improving av-            tended behaviors in long-horizon tasks. These mechanisms
erage success rates by 13% points in simulation and by 35%           may help reduce physical damage and operational risks in
points on real robots , significantly enhancing task robust-         structured environments such as warehouses, laboratories,
ness in both simulated and physical environments. These              and assistive settings.

                                                                 9


---

                                   Can VLMs Diagnose and Recover from VLA Faults?

References                                                        Khanna, P., Naoum, A., Yadollahi, E., Björkman, M., and
                                                                    Smith, C. Reflex dataset: A multimodal dataset of human
                                                                    reactions to robot failures and explanations, 2025. URL
An, X., Xie, Y., Yang, K., and Zhang, Deng, J. Llava-               https://arxiv.org/abs/2502.14185.
  onevision-1.5: Fully open framework for democratized            Kim, C., Seo, S.-W., and Kim, S.-W. Lamour: Leverag-
  multimodal training. In arXiv, 2025.                              ing language models for out-of-distribution recovery in
Bai, S., Cai, Y., Zhu, Y., and Zhu, K. Qwen3-vl techni-             reinforcement learning, 2025. URL https://arxiv.
  cal report, 2025. URL https://arxiv.org/abs/                      org/abs/2503.17125.
  2511.21631.                                                     Kim, M. J., Pertsch, K., and Finn, C. Openvla: An
                                                                    open-source vision-language-action model, 2024. URL
Chen, H., Yao, Y., Liu, R., Liu, C., and Ichnowski, J. Au-
                                                                    https://arxiv.org/abs/2406.09246.
  tomating robot failure recovery using vision-language
  models with optimized prompts, 2024. URL https:                 Li, H., Lei, K., Zang, S., Hu, K., Liang, Y., An, B., Li, X.,
  //arxiv.org/abs/2409.03966.                                       and Xu, H. Failure-aware rl: Reliable offline-to-online
                                                                    reinforcement learning with self-recovery for real-world
Chen, K., Xie, S., Ma, Z., Sanketi, P. R., and Goldberg,            manipulation, 2026. URL https://arxiv.org/
  K. Robo2vlm: Visual question answering from large-                abs/2601.07821.
  scale in-the-wild robot manipulation datasets, 2025. URL
  https://arxiv.org/abs/2505.15517.                               Lin, Z., Duan, J., Fang, H., Fox, D., Krishna, R., Tan, C.,
                                                                    and Wen, B. Failsafe: Reasoning and recovery from
Dai, Y., Lee, J., Fazeli, N., and Chai, J. Racer: Rich              failures in vision-language-action models, 2025. URL
  language-guided failure recovery policies for imitation           https://arxiv.org/abs/2510.01642.
  learning, 2024. URL https://arxiv.org/abs/
  2409.14674.                                                     Liu, B., Zhu, Y., Gao, C., Feng, Y., Liu, Q., Zhu, Y., and
                                                                    Stone, P. Libero: Benchmarking knowledge transfer for
DeepMind, G. Gemini 3 flash model card. Tech-                       lifelong robot learning, 2023. URL https://arxiv.
  nical report, Google DeepMind, December 2025a.                    org/abs/2306.03310.
  URL            https://storage.googleapis.
  com/deepmind-media/Model-Cards/                                 Lu, S., Li, Y., Chen, Q.-G., Xu, Z., Luo, W., Zhang, K.,
  Gemini-3-Flash-Model-Card.pdf.                                    and Ye, H.-J. Ovis: Structural embedding alignment for
                                                                    multimodal large language model, 2024. URL https:
DeepMind, G.       Gemini 2.5:   Updates to                         //arxiv.org/abs/2405.20797.
  our family of thinking models.     https:
                                                                  Meta. Llama-3.2-90b-vision. Model card / techni-
 //developers.googleblog.com/en/
                                                                   cal documentation on Hugging Face, 2024. URL
  gemini-2-5-thinking-model-updates/,
                                                                   https://huggingface.co/meta-llama/
  2025b.
                                                                   Llama-3.2-90B-Vision. Llama-3.2-90B-Vision.
Doubao Team.       Doubao-seed-1.6 vision-language                NVIDIA, Zhang, H., Zhao, Y., Zheng, R., and Zhu, Y.
  model.   Technical report / model announcement,                  Gr00t n1: An open foundation model for generalist hu-
  2025. URL https://seed.bytedance.com/en/                         manoid robots, 2025. URL https://arxiv.org/
  seed1_6. Open model in Doubao series.                            abs/2503.14734.
Duan, J., Pumacay, W., Kumar, N., Wang, Y. R., Tian, S.,          OpenAI.   Gpt-4o system card. Technical report,
 Yuan, W., Krishna, R., Fox, D., Mandlekar, A., and Guo,            OpenAI, 2024.   URL https://openai.com/
 Y. Aha: A vision-language-model for detecting and rea-             zh-Hans-CN/index/gpt-4o-system-card/.
  soning over failures in robotic manipulation, 2024. URL
  https://arxiv.org/abs/2410.00371.                               OpenAI. Gpt-5 system card. Technical report, Ope-
                                                                    nAI, 2025a.          URL https://openai.com/
Grislain, C., Rahimi, H., Sigaud, O., and Chetouani, M. I-          zh-Hans-CN/index/introducing-gpt-5/.
  failsense: Towards general robotic failure detection with         Official system card and technical description.
  vision-language models, 2025. URL https://arxiv.
  org/abs/2509.16072.                                             OpenAI. Gpt-5.2. Technical report / model announce-
                                                                    ment, 2025b. URL https://openai.com/index/
Guo, D., Wu, F., Wang, Z., Huang, Z., Zhu, Z., and Song,            introducing-gpt-5-2/. Official introduction of
  Z. Seed1.5-vl technical report, 2025. URL https:                  GPT-5.2 with improved multimodal and reasoning capa-
 //arxiv.org/abs/2505.07062.                                        bilities.

                                                             10


---

                                   Can VLMs Diagnose and Recover from VLA Faults?

OpenGVLab. Internvl2.5: Advanced multimodal large                  Wu, K., Xu, S., Chen, H., Wang, C., Li, Z., Wang, Y., and
  language model series (including internvl2.5-78b).                Zhong, F. Vlm can be a good assistant: Enhancing embod-
  Model card / technical documentation on Hugging                   ied visual tracking with self-improving vision-language
  Face, 2024. URL https://huggingface.co/                           models, 2025c. URL https://arxiv.org/abs/
  OpenGVLab/InternVL2_5-78B. InternVL2.5 fam-                       2505.20718.
  ily described with architecture details.
                                                                   Yang, S., Li, H., Chen, Y., Wang, B., Tian, Y., Wang,
OpenGVLab. Internvl3: Advanced multimodal large lan-                 T., Wang, H., Zhao, F., Liao, Y., and Pang, J. In-
  guage model series (including internvl3-78b). Model                structvla: Vision-language-action instruction tuning from
  card / technical documentation on Hugging Face, 2025.              understanding to manipulation, 2025a. URL https:
  URL https://huggingface.co/OpenGVLab/                              //arxiv.org/abs/2507.17520.
  InternVL3-78B. InternVL3 describes extensions
                                                                   Yang, Z., Chen, Y., Zhou, X., Yan, J., Song, D., Liu, Y., Li,
  over InternVL2.5 with enhanced perception and reason-
                                                                     Y., Zhang, Y., Zhou, P., Chen, H., and Sun, L. Agentic
  ing.
                                                                     robot: A brain-inspired framework for vision-language-
                                                                     action models in embodied agents, 2025b. URL https:
Pacaud, P., Garcia, R., Chen, S., and Schmid, C. Guardian:
                                                                     //arxiv.org/abs/2505.23450.
  Detecting robotic planning and execution errors with
  vision-language models, 2025. URL https://arxiv.                 Ye, J., Xu, H., Liu, H., Hu, A., Yan, M., Qian, Q., Zhang,
  org/abs/2512.01946.                                                J., Huang, F., and Zhou, J. mplug-owl3: Towards long
                                                                     image-sequence understanding in multi-modal large lan-
Phi Team.  Phi-4 large language model. Model                         guage models, 2024. URL https://arxiv.org/
  card / model announcement, 2025.      URL                          abs/2408.04840.
  https://huggingface.co/microsoft/
  Phi-4-multimodal-instruct. Phi-4 general                         Zhang, L., Dong, J., Bai, K., Ni, M., Marton, Z.-C., Chen,
  LLM.                                                               Z., and Zhang, J. Responsiblerobotbench: Benchmark-
                                                                     ing responsible robot manipulation using multi-modal
Team, G. R. Gemini robotics: Bringing ai into the physi-             large language models, 2025a. URL https://arxiv.
  cal world, 2025. URL https://arxiv.org/abs/                        org/abs/2512.04308.
  2503.20020.
                                                                   Zhang, Z., Wang, J., Guo, Y., et al. Aibench: Towards
Thoduka, S., Hochgeschwender, N., Gall, J., and Plöger,             trustworthy evaluation under the 45° law. Displays, pp.
  P. G. A multimodal handover failure detection dataset              103255, 2025b. ISSN 0141-9382. doi: 10.1016/j.displa.
  and baselines. In 2024 IEEE International Conference               2025.103255.
  on Robotics and Automation (ICRA), pp. 17013–17019.
  IEEE, May 2024.        doi: 10.1109/icra57147.2024.              Zhang, Z., Wang, J., Wen, F., Guo, Y., et al. Large multi-
  10610143. URL http://dx.doi.org/10.1109/                           modal models evaluation: A survey. SCIENCE CHINA In-
  ICRA57147.2024.10610143.                                           formation Sciences, 68(12):221301–221369, 2025c. doi:
                                                                     https://doi.org/10.1007/s11432-025-4676-4.
Wang, J., Zhang, Z., Guo, Y., Wen, F., Shen, Y., Liang, Y.,        Zhang, Z., Wang, Y., Xie, H., Zhao, S., Liu, M., Lu, Y., He,
 Wu, Y., Li, W., Li, C., Chen, Z., Jia, Q., and Zhai, G.             X., Cheng, Z., and Peng, Y. Evaluating multimodal large
 The ever-evolving science exam, 2025a. URL https:                   language models with daily composite tasks in home
 //arxiv.org/abs/2507.16514.                                         environments, 2025d. URL https://arxiv.org/
                                                                     abs/2509.17425.
Wang, Z., Shen, R., and Stadie, B. Wonderful team: Zero-
 shot physical task planning with visual llms, 2025b. URL          Zhao, E., Raval, V., Zhang, H., Mao, J., Shangguan, Z.,
 https://arxiv.org/abs/2407.19094.                                   Nikolaidis, S., Wang, Y., and Seita, D. Manipbench:
                                                                     Benchmarking vision-language models for low-level
Wu, C., Li, J., Cai, Y., and Liu, Z. Qwen-image techni-              robot manipulation, 2025. URL https://arxiv.
 cal report, 2025a. URL https://arxiv.org/abs/                       org/abs/2505.09698.
 2508.02324.
                                                                   Zhou, X., Xu, Y., Tie, G., Chen, Y., Zhang, G., Chu, D.,
Wu, K., Hou, C., and Tang, J. Robomind: Benchmark on                 Zhou, P., and Sun, L. Libero-pro: Towards robust and
 multi-embodiment intelligence normative data for robot              fair evaluation of vision-language-action models beyond
 manipulation, 2025b. URL https://arxiv.org/                         memorization, 2025. URL https://arxiv.org/
 abs/2412.13877.                                                     abs/2510.03827.

                                                              11


---

                                Can VLMs Diagnose and Recover from VLA Faults?

Zhu, J., Wang, W., Dai, J., and Wang, W. Internvl3:
  Exploring advanced training and test-time recipes for
  open-source multimodal models, 2025. URL https:
  //arxiv.org/abs/2504.10479.




                                                          12


---

                                     Can VLMs Diagnose and Recover from VLA Faults?

A. Dataset Overview and Composition
Dataset Statistics. The dataset comprises 6,034 task execution episodes collected from both simulated and real-robot
settings. It includes 40 simulated task settings and two real-robot task settings, namely Tea Preparation and Charging Plug
Insertion. These settings cover pick-and-place, multi-step composite manipulation, switch/button interaction, and simple
tool-use scenarios. Pick-and-place tasks constitute roughly 45% of samples, multi-step composite tasks 35%, and the
remaining task types about 20%, ensuring diversity in task complexity, operational patterns, and scene coverage.
The dataset systematically captures a wide spectrum of failure types, stages, and severity levels. Frequent failures such as
Jitter, Grasp Instability, and Stagnation appear in over 25% of samples, while rare failures (e.g., Wrong Placement, Target
Occluded) occur in less than 7%, supporting edge-case analysis. Approximately 64% of episodes contain 2–3 failure types,
and 7.5% include four or more, allowing multi-failure interaction studies. In terms of severity, level-2 (self-recoverable)
failures dominate at 63.2%, followed by level-3 failures at 13%, while error-free executions account for 16%. Temporal
analysis indicates that failures are evenly distributed in short tasks but concentrate in middle-to-late stages for longer tasks,
emphasizing the importance of robustness in long-horizon manipulations.
  0. No Error / Success – Task completed smoothly without any issues.

  1. Jitter – High-frequency shaking or vibration of the arm/gripper during motion or hold.

  2. Grasp Instability / End-effector Error – Incorrect positioning or unstable grasp (slip, off-center hold).

  3. Stagnation / Local Minima – Robot stops or loops without progress.

  4. Aimless Wandering – Motion without approaching the target.

  5. Sequence Error / False Success – Skipping or misordering steps, or false assumption of success.

  6. Wrong Placement – Correct manipulation but incorrect final pose/location.

  7. Target Occluded – Target not visible to the robot.

  8. Task Object Accident – Accidental dropping or knocking over of the target object.

  9. Non-Task Object Accident – Collision with or displacement of non-target objects.

10. Visual Perception Failure – Blur, black screen, exposure issues, or noise in visual input.
                                                                                                                 gaussian_noise_std 25
                                                                                                                gaussian_noise_std 90
                                                                                                                   gaussian_blur_k5_s1.5




                                          Figure 7. Examples of perception error types.


                                                               13


---

                                     Can VLMs Diagnose and Recover from VLA Faults?




                                                                                                                gaussian_blur_k9_s2.5
                                                                                                                 jpeg2000_compression_0.07
                                                                                                                   jpeg2000_compression_0.01
                                                                                                                   block_distortion_b32_r0.8
                                                                                                                    block_distortion_b64_r1.0
                                                                                                                       brightness_shift_-255
                                                                                                                              brightness_shift_100



                                          Figure 8. Examples of perception error types.



B. Annotation
All human-involved procedures, including data annotation and human baseline testing, were conducted in accordance with
institutional ethical guidelines. The annotators consisted of ten graduate students with engineering backgrounds, who were
compensated fairly in accordance with institutional standards. No personally identifiable information (PII) was collected.
Data Annotation Protocol
We employ an video annotation tool to manually annotate errors in robot manipulation videos. The annotation process
consists of four main stages: interface familiarization, video playback control, error-type annotation with phase identification,
and result saving/navigation.
Annotation Interface The annotation interface, illustrated in Fig. 10, is divided into four functional regions:


   • Left Video Panel: Displays the robot operation video for annotation, with controls for play, pause, and frame-by-frame
     navigation.

                                                               14


---

                                    Can VLMs Diagnose and Recover from VLA Faults?




                                  Figure 9. Examples of failure types in real robot experiments.


   • Central Annotation Panel: Provides a set of checkboxes for error types. The annotator selects all observed error
     categories based on the video content.
   • Right Information Panel: Shows metadata for the current video, including task difficulty level (Level 1–3), task ID,
     and success/failure indication.
   • Bottom Control Panel: Contains buttons for saving annotations, navigating to the previous/next video, and jumping to
     a specific video by ID.

Annotation Procedure The standard workflow for annotators is as follows:
(1) Video Playback & Observation. The annotator first plays the video in the left panel to observe the complete task
execution. To enhance efficiency, the following keyboard shortcuts are supported: Key A: Rewind video by 0.5 seconds.
Key S: Toggle play/pause.Key D: Fast-forward video by 0.5 seconds.
(2) Multi-label Error Annotation. During or after playback, the annotator selects all applicable error types from the central
panel. Our system defines error categories primarily as:Interaction Errors: Includes sliding without clear task progress,
continuing after a failed grasp, incorrect phase sequence, misplacement, and complete occlusion of the target object.Object
State Errors: Includes the task object being knocked over, dropped, or moved out of the workspace.
(3) Phase Identification & Temporal Localization. For complex tasks requiring fine-grained analysis, the annotator must
specify the phase during which the error occurs and mark its start and end timestamps on the video timeline to ensure precise
error localization.
(4) Saving & Navigation. Upon completion, clicking “Save & Next” submits the annotation and loads the next video.
Annotators can click “Previous” to review or modify the last record, or directly navigate to a specific video by entering its
ID and clicking “Jump”.
Quality Assurance All annotators undergo standardized training using the same guideline documentation. Prior to formal
annotation, each annotator must complete a set of calibration videos, achieving an accuracy of over 90% to qualify. To
ensure reliability, 10% of the annotated videos are randomly selected and reviewed by an expert annotator.

C. Real - Metrics
Fault Sensitivity and Coverage. Measured by Recall, this metric reflects the model’s ability to detect faults during real
robot execution. Higher Recall indicates broader fault coverage, potentially at the cost of increased false alarms.

                                                               15


---

                                         Can VLMs Diagnose and Recover from VLA Faults?
Operating method——Interface Introduction                                     Operating Methods - Basic Procedures
                                                                                                                                                                     Global Hotkeys:

                                                                                                                                                                     A key: Rewind
                                                                                                                               0. [Optional] For new tasks you       video by 0.5
                                                                                                                                                                     seconds
                                                                                                                               haven't seen before, click the
                                                             need                                                              standard video on the right to        S key: Play and
                                                           annotator           1. The first time you click on                  understand the overall task           pause video
                                                                               the video on the left, select                   content.
                                                           GT Video            "Play".                                                                               D key: Fast
                                                                                                                                                                     forward video by
                                                                                                 2.Do these situations occur in multiple-                            0.5 seconds
                                                                                                 choice questions?
                                                           Annotation
                                                            Area 1                                                    3. Select the phase time, phase
                                                                                                                      determination, and rules will follow.
                                                           Annotation
                                                            Area 2

                                                                                                                      4. After rating, click "Save and Next"; If you
                                                                                                                      have made changes to the previous entry,
                                                           Functional                                                 click "Previous"; To jump to the ID: first enter
                                                             area                                                     the ID number, then click "Jump".


                     Figure 10. Annotation interface and operating procedure used for VLA-FixBench data annotation.


    Prediction Accuracy and Robustness. Precision and FPR evaluate the correctness of fault predictions and the frequency of
    false interventions. High Precision together with low FPR indicates robust and reliable decision-making.
    Overall Fault Diagnosis Performance. The F2-Score balances Recall and Precision with greater emphasis on Recall,
    providing an integrated measure of fault detection capability.

    D. Tolerance Windows for Temporal Scoring
    For the binary temporal scoring functions in Sec. 4.4, we use fixed asymmetric tolerance windows. Specifically, the stop-time
    score Sstop is evaluated within                ∗
                                                     tstop − ∆−        ∗       +
                                                                                   
                                                               stop , tstop + ∆stop ,

    where we set ∆−               +
                    stop = 1 and ∆stop = 3 (in frames). This design penalizes premature stops more strongly while allowing a
    small delay in detection.
    Similarly, the rollback-time score Srb is evaluated within

                                                        trb − ∆−
                                                       ∗            ∗     +
                                                                             
                                                               rb , trb + ∆rb ,

    where we set ∆−           +
                  rb = 2 and ∆rb = 1 (in frames). This tighter window encourages precise recovery timing.


    E. Statics Table
    In the Stable-Static evaluation setting, the abbreviation labels describe both the semantic type of manipulation failures and
    the task domain in which each failure is observed. For fault-type categories, SOE denotes Spatial-Object Errors, referring to
    cases where the gripper or end-effector fails to reach the correct target position and therefore becomes spatially misaligned
    with the intended object or interaction point; LMA denotes Low-level Motion Anomaly, which captures abnormal low-level
    motion behaviors of the robot arm or gripper, including jittering, overshooting, oscillation, stagnation, or unstable holding;
    LGD denotes Lack of Goal-Directedness, where the robot may continue moving smoothly but fails to make meaningful
    progress toward the task goal, or remains trapped in local loops, idle states, or ineffective motion patterns; TLE denotes
    Temporal/Logical Error, referring to failures in sub-task ordering, skipped necessary steps, or continuing subsequent actions
    under the false assumption that a previous failed sub-task has succeeded; TRM denotes Task Relevance Misjudgment, where
    the robot misidentifies which object, region, or interaction target is relevant to the current instruction and consequently
    manipulates the wrong target or performs task-irrelevant behavior; and VDF denotes Visual Distortion Failures, covering
    failures caused by corrupted or incomplete visual input, such as image noise, blur, distortion, occlusion, over-exposure,
    under-exposure, or missing visual information. For task-domain categories, P & P denotes Pick-and-Place, covering standard
    manipulation tasks that involve grasping, transporting, and placing objects; SG denotes Spatial Grasping, emphasizing
    tasks that require accurate spatial reasoning for grasp pose selection and object approach; AOCI denotes Articulated Object
    and Container Interaction, covering constrained interactions with drawers, doors, microwave doors, containers, or other
    articulated structures; MLT denotes Multi-object Long-sequence Tasks, referring to long-horizon manipulation scenarios
    involving multiple objects, multiple sub-steps, and sequential reasoning; and FIH denotes Functional Interaction and Hybrid
    Tasks, which include fine-grained functional manipulation, compound skills, coordinated object use, or hybrid task settings

                                                                        16


---

                                    Can VLMs Diagnose and Recover from VLA Faults?

requiring deeper understanding of object usage and task purpose. Together, these Stable-Static labels characterize what type
of failure occurs and under which manipulation domain the failure is observed.

F. Dynamic Table
In the Stable-Dynamic evaluation setting, the abbreviation labels describe temporal fault localization and geometric
correction quality during continuous robotic execution. For temporal localization, FOT denotes Fault Onset Time, the
earliest time point at which the execution can be identified as deviating from a successful task trajectory; RIT denotes
Rollback Initiation Time, defined as the target historical time point to which the system should roll back in order to return
to a previously safe and recoverable state; LFS denotes Late Failure Step, a tolerant fault-detection metric that allows
the predicted failure step to be slightly later than the true failure onset while penalizing overly premature stopping; and
EFS denotes Earlier Failure Step, a tolerant rollback metric that allows the predicted rollback point to be slightly earlier
than the ideal rollback target, since earlier rollback is often safer than rolling back too late. For geometric correction, AA
denotes Axis Alignment, measuring whether the predicted correction is made along the same spatial axis as the ground-truth
correction; DC denotes Direction Consistency, measuring whether the predicted correction follows the same direction as
the ground-truth correction along the correct axis; and MA denotes Magnitude Accuracy, measuring whether the predicted
correction matches the ground-truth correction in scale or magnitude. Together, these Stable-Dynamic metrics evaluate
when a model identifies or rolls back from a failure, and whether its corrective action is geometrically aligned with the
required recovery direction and magnitude.




                                                             17


---

