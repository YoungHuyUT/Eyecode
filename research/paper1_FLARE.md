                     This CVPR paper is the Open Access version, provided by the Computer Vision Foundation.
                                  Except for this watermark, it is identical to the accepted version;
                            the final published version of the proceedings is available on IEEE Xplore.




FLARE: A Failure-Aware Framework for Autonomous Correction and Recovery
                 in Visual-Language Robotic Manipulation

                                                                                                                          ∗
       Ganlong Zhao1,2 Zijia Tang3 Xingping Chen4 Zhanghui Kuang5 Ye Tian6 Guanbin Li4,7,8
       1
         The Chinese University of Hong Kong 2 Centre for Perceptual and Interactive Intelligence
              3
                Duke University 4 Sun Yat-sen University 5 TengenX 6 Tencent Robotics X
    7
      Shenzhen Loop Area Institute 8 Guangdong Key Laboratory of Big Data Analysis and Processing
                                          glzhao@cpii.hk, liguanbin@mail.sysu.edu.cn



                           Abstract                                Despite impressive advances—such as π0 [4] and Open-
                                                                   VLA [18]—current systems remain notably brittle: small
   Vision-Language-Action Models (VLAs) have demon-                perturbations, unexpected object contacts, or slight execu-
strated significant promise in generalizing to complex, long-      tion deviations can cause irreversible task failures. Unlike
horizon robotic manipulation tasks. However, their per-            humans, VLAs lack an intrinsic ability for continuous self-
formance remains brittle, as they are typically trained on         correction. Achieving true robotic autonomy therefore re-
trajectory-monotonic, failure-free demonstrations. This re-        quires not only skillful task execution but also a robust and
liance on “perfect” data leaves them unable to recover             generalizable mechanism for recovery after failure.
from common execution errors, such as a missed grasp, a
                                                                      While previous research attributes brittleness to model
dropped object, or an unexpected collision. In this paper,
                                                                   architecture or control policy limitations [9, 11, 45], we
we propose FLARE, a novel framework that endows VLAs
                                                                   identify a deeper origin in the data regime itself. Human
with robust error recovery capabilities through a “Retry”
                                                                   demonstrations are costly to collect, resulting in datasets
and “Reset” paradigm. First, we introduce a “Retry”
                                                                   that are sparse, success-biased, and lacking in trajectory di-
mechanism by injecting perturbation and bridging seg-
                                                                   versity. Even data recomposition methods such as Mim-
ments that decouple robot pose from environment state into
                                                                   icGen [29] expand dataset volume but fail to address two
demonstrations, enabling the policy to autonomously han-
                                                                   fundamental issues. First, both original and recombined
dle execution deviations. Second, to address critical, state-
                                                                   demonstrations are trajectory-monotonic: the robot consis-
breaking (OOD) failures, we introduce a “Reset” pipeline.
                                                                   tently follows a narrow manifold of poses correlated with
We leverage an MLLM for offline failure analysis to auto-
                                                                   task progress. Consequently, the model learns spurious as-
matically identify OOD states from execution videos. This
                                                                   sociations between its own configuration and task success.
analysis enables the efficient, targeted collection of a small
                                                                   When encountering a valid yet unseen configuration—an
library of object-centric “Reset” skills, which are trained
                                                                   in-distribution (ID) error—the agent cannot resume appro-
to restore the environment to a task-valid state. Our full
                                                                   priately. Second, these datasets are success-centric and con-
framework integrates these learned policies. At inference,
                                                                   tain few, if any, examples of recovery. Catastrophic failures
an online MLLM monitor arbitrates between task execution
                                                                   (e.g., a toppled cup) drive the environment into an out-of-
and “Reset” skills. Experiments on challenging, contact-
                                                                   distribution (OOD) error state, for which the agent has never
rich manipulation tasks show our approach significantly im-
                                                                   observed corrective behavior. Since standard augmenta-
proves task success and robustness.
                                                                   tions recombine only successful data, they cannot synthe-
                                                                   size recovery trajectories, leaving the system unable to re-
                                                                   store a valid task state.
1. Introduction
                                                                      Recent studies have explored several approaches for
Vision-Language-Action (VLA) models have recently
                                                                   robotic self-correction. One direction leverages Multimodal
emerged as a promising paradigm for Embodied Artificial
                                                                   Large Language Models (MLLMs) to provide semantic
Intelligence, integrating perception, language, and control
                                                                   feedback [25, 37, 38, 41]; these systems can recognize high-
to enable robots to execute complex, long-horizon tasks
                                                                   level failures but typically depend on a fixed skill library,
in open-world environments [4, 15, 18, 28, 46, 47, 49].
                                                                   limiting low-level adaptability. Another line of research
  * Corresponding author is Guanbin Li.                            employs reinforcement [13, 27, 33, 43] or instruction-based



                                                             22391


---

              VLA Task Execution                                             behaviors restore the environment to a stable configuration,
             Instruction: Make coffee                     Success            allowing task resumption.
                                                                                 All data—original, retry-augmented, and reset-
                                                                             augmented—are integrated to train a unified VLA
                                                                             system. This system equips the agent with a comprehensive
                                                                             repertoire of skills, where task execution and environment
                                                                             recovery are seamlessly invoked through distinct language
                                                         Give up
                                                                             prompts. During deployment, an online MLLM moni-
                                        Other methods
                     Failure                                                 tor observes task execution and dynamically arbitrates
                                                                             between retry and reset modes. For ID errors, the VLA
                            Ours                                             autonomously recovers through its learned robustness; for
           OOD Error             ID Error                Perturbation
                                                                             OOD errors, the monitor switches the prompt to the corre-
                                                                             sponding reset skill. Once the environment is restored, the
                                                                             system seamlessly resumes the main task. This retry–reset
                                                                             loop operationalizes robust autonomy, enabling resilience
                                                                             to both pose-level and environment-level disturbances.
        Human demo and      Perturbation and
        MLLM correction      Bridging data                                       In summary, our contributions are threefold: (1) A uni-
                                                        Bridging data        fied Retry/Reset paradigm grounded in an ID/OOD er-
                          Retry & Reset                                      ror taxonomy that reframes robotic autonomy as resilience
                                                                             rather than perfection. (2) A perturbation-bridging augmen-
                                                                             tation strategy that decouples robot pose from environment
                                                                             state, equipping VLAs with built-in retry robustness. (3)
Figure 1. FLARE: Failure-Aware Resilience in VLA. Previous                   An MLLM-driven dual-loop system in which the large lan-
methods are brittle, failing from minor perturbations (ID errors) or         guage model serves both as an offline failure analyst for re-
catastrophic states (OOD errors), and do not leverage the VLA’s
                                                                             set skill acquisition and as an online monitor for closed-loop
inherent generative capability for continuous self-correction. Our
FLARE framework introduces an ID/OOD error taxonomy to
                                                                             recovery.
guide a dual Retry/Reset paradigm. We tackle ID errors via                       Overall, FLARE advances embodied intelligence from
built-in Retry robustness and resolve OOD errors with MLLM-                  imitation-driven execution toward resilience-driven auton-
bootstrapped Reset skills, achieving robust, resilient autonomy.             omy, enabling agents not only to act but to recover.

                                                                             2. Related Works
learning [39, 42], which struggles with sample efficiency
                                                                             2.1. Robotic Self-correction Systems
and generalization in long-horizon settings. A unified, data-
centric mechanism capable of enabling self-recovery across                   Research on robotic self-correction generally falls into three
both ID and OOD error regimes remains absent.                                categories. First, MLLM-based approaches treat large mul-
    To this end, we propose FLARE, a Failure-Aware                           timodal models as high-level failure analysts [6, 12, 21, 23,
Retry/Reset framework designed to transform brittle VLAs                     25, 37, 38, 40, 41]. Systems such as REFLECT [26] can
into resilient embodied agents (Fig. 1). At its foundation                   diagnose failures and replan, but their reliance on a fixed
lies an ID/OOD error taxonomy and two complementary re-                      skill library restricts low-level adaptability. Second, rein-
covery mechanisms. Retry addresses ID errors by systemat-                    forcement learning methods [13, 27, 33, 36, 43] aim to
ically decoupling robot pose from environment state. We in-                  explicitly learn recovery behaviors; although frameworks
troduce a perturbation-bridging augmentation strategy that                   like SeRO [17] handle OOD states, they often face pro-
injects random pose perturbations between task segments,                     hibitive sample-efficiency demands in real-world settings.
followed by a bridging segments that reconnects them. This                   Third, data-driven paradigms [39, 42] enhance robustness
process teaches the VLA to execute the correct next step                     via large-scale augmentation. Phoenix [39] connects se-
from diverse configurations, providing built-in retry robust-                mantic reflection to low-level correction through coarse
ness. Reset tackles OOD errors through efficient skill boot-                 motion instructions refined by human feedback, but its
strapping. An offline MLLM (e.g., Gemini [34]) serves as                     template-based prediction–correction pipeline limits gener-
a failure analyst, parsing failure videos to determine which                 alization across tasks and environments.
object requires resetting. This analysis bootstraps the col-
                                                                             2.2. Vision-Language-Action Models
lection of a compact set of object-centric demonstrations
(e.g., “un-topple the cup”), which are further enhanced via                  Recent advances in embodied AI have been driven by
the same perturbation-bridging augmentation. These reset                     Vision-Language-Action (VLA) models [16, 44, 48], which



                                                                        22392


---

unify perception, language, and control within a single                 The “trajectory-monotonic” nature of the demonstration
architecture. This paradigm was initiated by Google’s              dataset Ddemo creates a strong, spurious correlation between
Robotic Transformer series: RT-1 [5] scaled transformer-           set and srt . This is because human demonstrations are not ex-
based policies to real-world control, and RT-2 [49] fur-           haustive; they reflect implicit biases and habits. For exam-
ther co-fine-tuned a large VLM on web and robotic data             ple, a demonstrator might always grasp a cup by its handle
to enable semantic grounding. Building on this founda-             or consistently approach from a similar angle, even if many
tion, OpenVLA [18] offers an open-source pipeline that             other approaches are valid. This results in a highly-biased,
fine-tunes modern VLMs [1–3, 8, 20, 35] to output tok-             low-variance conditional distribution P (srt |set , Ddemo ).
enized robot actions, exhibiting strong zero-shot general-              This correlation is a root cause of VLA brittleness.
ization. Likewise, π0 [4] and π0 -FAST [32] adopt a VLA            Trained on this biased data, πθ overfits and fails to learn
Flow Model [24] built on pre-trained VLMs [3], achiev-             a disentangled representation. Instead of correctly inferring
ing competitive performance on long-horizon, multi-step            task progress primarily from the environment state set (e.g.,
manipulation tasks. Additional works explore more gen-             “the cup is now grasped”), the policy incorrectly learns to
eralizable manipulation pipelines [7, 10, 22, 31, 48]. De-         associate task progress with the specific joint configuration
spite their strong generalization within the distribution of       (set , srt ) seen in demonstrations. This leads to a critical
training tasks, these models remain vulnerable to small            failure: when a minor perturbation creates a state with a
perturbations, unexpected contacts, and minor execution            valid set but a novel srt , the policy incorrectly interprets this
drift—limitations noted in recent benchmarks [9] and a key         valid state as out-of-distribution and fails. For example, the
barrier to reliable open-world autonomy.                           robot’s pose srt might be at a “placing” position, causing the
                                                                   policy to infer the task is at the “placing” stage, even if the
3. Methodology                                                     environment state set shows the object was never success-
                                                                   fully grasped. This explains the paradoxical lack of “retry”
Our goal is to endow VLAs with a robust, generalizable
                                                                   capability in existing VLAs.
error recovery capability. We introduce the Retry/Reset
                                                                        We formalize this challenge by introducing a taxonomy
framework, a unified approach built upon a taxonomy of                                        e
                                                                   of failure states. Let Stask  be the set of all valid environment
failures as either In-Distribution (ID) or Out-of-Distribution
                                                                   states along any successful task execution path.
(OOD) errors. ID errors represent states where the envi-
ronment is still on a valid task trajectory, but the robot’s            Definition 1: In-Distribution (ID) Error. An ID Error
pose is novel; these only require the robot to “retry” the cor-    is a state st = (set , srt ) where the environment state is
rect action from its new pose. OOD errors represent catas-         valid (set ∈ Stask  e
                                                                                         ), but the robot state srt is from a low-
trophic failures (e.g., a toppled object) where the environ-       probability region of the demonstrated conditional distribu-
ment state is unrecoverable by the task policy, requiring a        tion P (srt |set , Ddemo ). The task policy πθ fails because it
dedicated “reset” skill. Our method provides a distinct solu-      has overfitted to the set -srt correlation, even though the task
tion for each case, training a unified VLA system to handle        is still recoverable from set . Recovery requires a “Retry”
both (Fig. 2).                                                     capability.
                                                                        Definition 2: Out-of-Distribution (OOD) Error. An OOD
3.1. Problem Formulation                                           Error is a state st = (set , srt ) where the environment state
We model the VLA agent as a policy πθ . Following mod-             itself is non-recoverable by the standard task policy (set ∈     /
                                                                      e
ern VLA architectures [4, 15, 18], the policy is Marko-            Stask  ). For example, a toppled cup creates a state set that
vian—lacking history—and predicts an action chunk at               no action from πθ (·|Itask ) can salvage. Recovery requires a
based on the current visual observation ot ∈ O and lan-            distinct “Reset” skill.
guage instruction I. This policy, which outputs a distri-               Our goal is to learn a robust, unified policy system that
bution over action sequences at ∈ AK (where K is the               can handle both error types. This system must:
chunk length and A is the action space), is written as:            1. Possess an innate “Retry” capability to autonomously
at ∼ πθ (·|ot , I). This policy is typically trained via imi-           overcome ID Errors by learning a policy decoupled from
tation learning on a dataset of N successful human demon-               srt .
strations, Ddemo = {τi }N                                          2. Include a library of learned “Reset” skills, {πreset,j }, that
                         i=1 .
    A core challenge arises from the nature of the observa-             can be invoked to transform an OOD state set ∈            e
                                                                                                                              / Stask
tion ot and the demonstration data Ddemo . The true state of            back into a valid state set′ ∈ Stask
                                                                                                         e
                                                                                                             .
the world at time t, st , can be decomposed into two com-
                                                                      3.2. Enabling Robust "Retry" via Perturbation &
ponents: the environment state set (e.g., the poses and states
                                                                            Bridging
of all objects) and the robot state srt (e.g., the end-effector
pose and gripper status). The visual observation ot ∈ O is            As mentioned above, a trajectory-monotonic nature of hu-
a rendering of the complete state st .                                man demonstrations is the primary barrier to a VLA’s in-



                                                              22393


---

Failure collection                  Failure analysis                Perturbation & bridging augmentation                                   Close-loop inference
                                    MLLM failure Analysis         Full task                                Subtasks
                    Task                                                                                                                                              Task-
                   library                                                                                                                                          specific
                                                  Gemini                                                                                                           finetuning
                                                                                                                                       Fai lure-enr iched
                                                                                                                                            dat aset

                                                                                                                                                          Skill Bank
                                     Error                                                                Perturbation   Bridging
                                                                Perturbation & Bridging
           Finetuned                Metadata
         Pretrained VLA                                                                                                                                       …        …
                                                                                                                                        Original Reset Reset     Reset
                                                (𝑠′r𝑡 )                    Object path
   Pretrained   Action
      VLM       expert   +           ID Error                                                                                             Skill Skill_1 Skill_K Skill_N
                             LoRA                                         Reset skill data collection
                                                                                         HIFI env state
                                                            OOD Error                                                                                         Gemini
                    Run Policy
                                                                              Gemini                                                                          Match
   𝑠𝑡𝑟                                    Or                                                                                              obs ervati on
                                    OOD Error (𝑠′𝑡e)                                          Required
                                                                                            Reset skill                                          Pretrained   Action   +
                                                                                                                                                    VLM       expert        LoRA
                                                                                                                           Semantic
                                                                                                          Perturbation                                                     Task_K
                                                                            Human                                           failure              Pretrained VLA
              𝑠𝑡𝑒                                                                                          & Bridging        asset
                                                                        demonstration
          observation                                                                                                                                 Run Policy



Figure 2. The overall framework of our method. We first collect the failure data with the VLA model trained with regular demonstrations.
Then we perform the failure analysis with MLLM and formulate the failures with ID/OOD taxonomy. For ID errors, we perform the
perturbation & bridging augmentation to enhance the robustness and “retry” ability of VLA models. For OOD errors, we collect the
object-centric reset skill data. All these data are utilized to obtained a skill bank for further close-loop inference.


nate “retry” capability. While prior work has used segment                                       ai+1 .
stitching to generate new data [29], this approach alone fails                                    To generate these segments efficiently, we adopt the stan-
to solve trajectory monotonicity. We address this by in-                                      dard planner-free kinematic interpolation technique (linear
troducing a novel Perturbation & Bridging augmentation                                        interpolation for position and SLERP for rotation) [29]. The
pipeline that systematically decouples the robot pose (srt )                                  benefit of generating a massive, diverse dataset of retry ex-
from the environment state (set ), thereby building true ro-                                  amples far outweighs the noise from rare, invalid trajecto-
bustness. Our augmentation process is as follows:                                             ries, which is the key to learning the decoupled policy. The
Trajectory Composition We first compose a new, high-                                          initial segment dinit serves the same purpose, decoupling the
level task trajectory from a small library of human-                                          very first action a0 from a fixed starting pose.
demonstrated subtask segments (e.g., “grasp mug,” “place                                      Training Data Generation Crucially, the perturbation ac-
mug”). For a new, randomly sampled scene, we select and                                       tions dA  i are not used as training targets, as they are not
kinematically transform these segments to match the new                                       meaningful actions. Instead, we form new training se-
object poses, stitching them together to form a baseline tra-                                 quences by combining the bridging actions with the subse-
jectory Ttask = (a0 , a1 , . . . , aN ), where ai is an action seg-                           quent task actions. For each augmented trajectory, we add
ment for a task step.                                                                         the following sequences to our training dataset:
Perturbation & Bridging: This baseline trajectory, which                                      • The       original        successful          subsequences    (e.g.,
still suffers from monotonicity, is then fundamentally en-                                       (ai , ai+1 , . . .)).
hanced. We systematically inject “perturbation-bridging”                                      • The new bridging-to-task subsequences (e.g.,
segments di between the task segments, creating a new, ro-                                       (dB
                                                                                                   i , ai+1 , ai+2 , . . .)).
bust trajectory: Taug = (dinit , a0 , d0 , a1 , d1 , . . . , aN ).                            By training on these (dB     i , ai+1 , . . .) sequences, the VLA ex-
                                                                                              plicitly learns to execute the correct task action ai+1 from
Segment Structure: Each segment di consists of two                                            a wide variety of initial robot poses (the end-states of dB       i ).
phases:                                                                                       This directly breaks the spurious pose-state coupling and
• Perturbation (dA i ): A random motion sequence (e.g.,                                       builds in a generalizable, innate “retry” capability.
  random joint velocities or end-effector movements) that
  moves the robot arm to an arbitrary, out-of-distribution                                    3.3. Learning "Reset" Skills via MLLM-driven
  pose. This phase breaks the pose-state correlation.                                              Failure Mining
• Bridging (dB i ): A recovery action sequence that moves                                     The “retry” capability only solves ID errors. It cannot
  the robot from its perturbed pose (at the end of dA  i ) back                               handle OOD errors where the environment itself is in a
  to the valid starting pose required for the next task seg-                                  catastrophic failure state. The “success-centric” nature of
  ment, ai+1 . Specifically, the bridging segment dB    i con-                                demonstration datasets means VLAs are never exposed to
  nects the robot’s perturbed state (at the end of dA
                                                    i ) back to                               such states or their corresponding recovery procedures.
  the valid starting pose required for the next task segment                                     We address this data scarcity with an efficient pipeline to



                                                                                    22394


---

mine, label, and learn object-centric “reset” skills (Fig. 2).        Bridging augmentation to this τreset trajectory.
More specifically, the procedure is as follows:                          This process generates a large-scale dataset Dreset aug that
Failure Collection We first execute our “retry-capable”               makes our “reset” skills robust not only to the robot’s start-
model (trained as in Sec. 3.2) on its designated tasks over           ing pose but also to the contextual layout of the failure itself.
hundreds of episodes. We collect all execution videos and             3.4. Unified Training and Closed-Loop Inference
trajectory data, including both successes and failures.
                                                                      Instead of training a single, monolithic model prone to
Offline MLLM Failure Analysis We then use a Multi-
                                                                      task interference, we adopt a modular and scalable expert
modal LLM as an “offline failure analyst” to process this
                                                                      policy library approach. We leverage Low-Rank Adapta-
large corpus of videos. For each failure video, the MLLM
                                                                      tion (LoRA) [14] to efficiently train a set of specialized pol-
is prompted to provide a structured JSON output specifying:
                                                                      icy adapters on top of a shared, pre-trained VLA backbone.
• error type: (“ID-Retryable” / “OOD-Reset Required”)                 This design allows each policy to achieve high performance
• reset target: (The name of the object that needs resetting,         on its specific task while enabling straightforward system-
   e.g., “cup” or “None”)                                             level scaling.
• error group: (The objects that forms the error, e.g., the
   coffee pod stuck at the coffee pod holder)                         Training an Expert Policy Library Our unified train-
• failure timestamp: (The time t at which the OOD error               ing dataset, comprising Dtask aug (original and “retry-
   occurred)                                                          augmented” task data) and Dreset aug (all augmented “reset”
                                                                      skill data), is used to train this library. Specifically:
    The error group allows us to treat the interacting error                                       task
                                                                      • A main task adapter, πLoRA      , is trained on Dtask aug using
objects (e.g., the “stuck pod” and the “holder”) as a single
                                                                         the main task instruction (e.g., Itask = “make coffee”).
“semantic failure asset.” When generating new reset demon-                                                    reset,j
                                                                      • A distinct reset skill adapter, πLoRA         , is trained for each
strations in the subsequent step, we can sample and place
                                                                         object-centric reset skill j. For example, the “reset cup”
this entire error group into a variety of new scene config-
                                                                         adapter is trained exclusively on its corresponding reset
urations, while preserving the relative poses that define the
                                                                         demonstrations, using the prompt Ireset = “reset the cup.”
failure state st . This ensures our VLA learns to recover
                                                                      This modular approach prevents the conflicting gradients
from the semantic nature of the error (the “stuck” state) re-
                                                                      that can arise from training disparate skills within a single
gardless of the failure’s position in the scene, which is es-
                                                                      set of weights. Furthermore, it provides a clear path for ex-
sential for training generalizable reset skills.
                                                                      tensibility, as new recovery skills can be added to the system
Bootstrapping the Reset Dataset This automated MLLM                   by simply training new LoRA adapters, without disturbing
analysis bootstraps our reset skill collection by providing           existing policies.
a high-quality corpus of OOD failure configurations. For
                                                                      Closed-Loop Orchestration In deployment, the system op-
each failure identified as OOD-Reset Required, the fail-
                                                                      erates as a closed loop orchestrated by the online MLLM
ure timestamp t allows us to extract the precise, high-
                                                                      monitor (Fig. 2).
fidelity environment state st (e.g., the MuJoCo state) from
                                                                      • The system initializes by loading the main task adapter,
our logs.                                                                  task
                                                                         πLoRA  , and begins execution with the prompt Itask .
    This mined dataset consists of (error state, skill label)         • The MLLM monitor observes the VLA’s execution.
pairs. The error state st captures the full physical configu-         • If an ID Error occurs: No intervention is needed. The
ration of the error group (e.g., spod stuck describes the pod’s          VLA’s innate “retry” robustness, learned from our pertur-
exact pose relative to the machine holder). The skill label              bation augmentation, allows it to autonomously recover
is derived from the reset target (e.g., “reset the pod”). This           and continue the task.
corpus of (st , Ireset ) pairs serves as the starting configura-      • If an OOD Error occurs: The MLLM intervenes. It
tions for the next step: for human demonstration collection.             identifies the required reset skill (e.g., “reset the cup”)
Demonstrations and Augmentation For each identified                      and directs the control system to swap the active LoRA
                                                                                                            reset,j
object-centric reset skill (e.g., “reset the cup”), we col-              adapter to the corresponding πLoRA         .
lect a small set (e.g., 10-20) of human demonstrations,               • The VLA, now equipped with its “reset” expert policy,
Dreset human . Each demonstration begins from a correspond-              executes the recovery skill.
ing mined error state st , and the operator provides a recov-         • Once the MLLM confirms the environment is reset to a
ery trajectory τreset to restore the reset target to a valid state.      valid state, it directs the system to reload the main task
                                                                                    task
   This small, curated dataset is then massively expanded.               adapter πLoRA   . The VLA then seamlessly resumes the
To generate a new, robust demonstration, our pipeline first              main task.
preserves the semantic integrity of the failure by placing the        This two-level design, where a high-level MLLM directs a
entire error group (maintaining its internal relative poses)          library of specialized VLA adapters, results in a system that
into a new scene. Then, it applies our same Perturbation &            is robust, high-performing, and easy to scale.



                                                                  22395


---

Table 1. Comparison of experimental results across 9 manipulation tasks in RoboMimic Simulation. The ‘D’ suffix in the task names
denotes the range of object randomization in scene initialization. The results demonstrate that our failure-aware VLA framework for robust
robotic manipulation achieves better performance than all previous methods as well as the strong VLA baselines. Phoenix-Human is gray
as it involves human instruction as the self-reflection subgoal.

                                                                                                                         ThreePiece    ThreePiece
        Methods            Coffee D0   Coffee D1   Stack D0   Stack D1   StackThree D0   StackThree D1   Threading D0                               Mean
                                                                                                                        Assembly D0   Assembly D1
    OpenVLA [18]             42%         18%         84%        86%          36%             20%            20%            28%            8%        38.0%
   Task-conditioned          66%         24%         88%        68%          30%              6%            74%            20%            0%        41.8%
  Subgoal-conditioned        76%         26%         88%        74%          24%             6%             78%            20%            2%        43.8%
  Motion-conditioned         68%         32%         92%        84%          38%             16%            58%            30%            4%        46.9%
 Subgoal Self-reflection     80%         32%        88%         78%          32%             6%             80%            34%           2%         48.0%
     Phoenix [39]             94%         48%        96%        86%          50%             20%             68%           52%            6%        57.8%
    Phoenix-Human            100%        100%       100%        90%          70%             40%            100%           70%           40%        78.9%
        π0.5 [15]            82%         56%        100%        92%          90%             84%             42%           58%           46%        72.2%
          Ours               96%         78%        100%       100%         100%             90%             72%           62%           58%        84.0%



4. Experiment                                                                        bound on the performance of self-reflection methods by
                                                                                     manually correcting the wrong motion instructions.
In this work, we conduct experiments on 9 contact-rich                             • π0.5 [15]. The successor to the π0 VLA model [4], which
manipulation tasks in RoboMimic [30] following previous                              demonstrates improved generalization by training on di-
studies [39]. The detailed description for each task can be                          verse, multi-environment datasets. It serves as the VLA
found in [30] and in our supplementary materials.                                    backbone for our method.
Implementation Details We generated 500 augmented
                                                                                   Comparison Results The overall results are summarized in
demonstrations per task from 10 initial human-collected de-
                                                                                   Table 1. Our method achieves state-of-the-art performance
mos using Mimicgen [29]. Our “retry” augmentation in-
                                                                                   on 8 out of 9 tasks. On the remaining task, Threading D0,
jects perturbation & bridging sequences (max 45◦ rotation,
                                                                                   although we do not obtain the best result, our approach still
0.5m translation) at the trajectory start and between sub-
                                                                                   (1) substantially boosts the performance of the VLA back-
tasks. For “reset” skills, we used Gemini-2.5-Pro to ana-
                                                                                   bone π0.5 and (2) outperforms Phoenix [39], the previous
lyze failure videos. We collected 20 human demos for each
                                                                                   leading method for error recovery.
object-centric reset skill and augmented them to 500 using
                                                                                       Our method achieves an average success rate of 84.0%,
the same perturbation method. We fine-tuned the language
                                                                                   significantly surpassing Phoenix’s 57.8% [39]. While part
model and action expert of π0.5 [15] using LoRA [14], train-
                                                                                   of this gain comes from the strong capability of the π0.5
ing with the Adam optimizer at a constant learning rate of
                                                                                   backbone, our approach still provides an additional 11.8%
2.5 × 10−4 without decay. All results are averaged over 50
                                                                                   improvement over π0.5 alone. More notably, our method
evaluation trials per task following [39]. Further details are
                                                                                   even outperforms Phoenix-Human, demonstrating the com-
available in our supplementary materials.
                                                                                   prehensive advantage of our framework over prior self-
Baselines Following previous studies [39], we compare our                          reflection approaches—even when compared to a baseline
method to the following baselines in three aspects, power-                         supplied with correct human guidance.
ful open-source VLA baselines, conditional diffusion pol-                              For the Stack task, the reset setting is not applicable be-
icy, and self-reflection policy. More details are available in                     cause the task involves stacking two cubes of different col-
the supplementary materials.                                                       ors, and there are almost no non-retryable errors during ex-
• OpenVLA [18]. OpenVLA is fine-tuned to provide base-                             ecution. In this case, our method still achieves compara-
  line performance for multi-task experiments.                                     ble performance, even when multiple baselines (Phoenix-
• Task-conditioned policy [39]. The diffusion policy is                            Human, π0.5 ) reach a 100% success rate.
  trained with the task description as the condition.                                  The ‘D’ suffix in the task names (e.g., D0, D1) denotes
• Subgoal-conditioned policy [39]. A LLaVAv1.5 is fine-                            the range of object randomization during scene initializa-
  tuned to predict subgoals at 5Hz, which are utilized as the                      tion and therefore reflects task difficulty. For example, Cof-
  condition for diffusion policy.                                                  fee D0 contains less variation than Coffee D1 and is thus
• Motion-conditioned policy [39]. A LLaVA-v1.5 is fine-                            easier. Across most tasks, the performance improvement
  tuned as the subgoal self-reflection model and applied to                        provided by our method on the D1 versions is more pro-
  the subgoal-condition policy.                                                    nounced than on the D0 versions. We attribute this to the
• Phoenix [39]. A motion-based self-reflection framework                           decoupling effect of our perturbation-and-bridging strategy,
  for action correction.                                                           which enhances the VLA model’s robustness to environ-
• Phoenix-Human [39]. This method provides an upper                                mental variations.



                                                                            22396


---

                                                                                                       Effect of Rotation (T=0.5 fixed)                                                                          Effect of Translation (R=45 fixed)
Table 2. Success rates of real-world manipulation tasks. Our                             80                                  Performance (%)
                                                                                                                                                                65                                  80                                     Performance (%)
                                                                                                                                                                                                                                                                                65
                                                                                                                             Data Generation Success Rate (%)                                                                              Data Generation Success Rate (%)
method outperforms the baseline in two challenging settings.                             78                                                                     60                                  78                                                                          60




                                                                                                                                                                 Data Generation Success Rate (%)




                                                                                                                                                                                                                                                                                 Data Generation Success Rate (%)
                                                                                         76                                                                                                         76
                                                                                                                                                                55                                                                                                              55




                                                                       Performance (%)




                                                                                                                                                                         Performance (%)
                                                                                         74                                                                                                         74
    Real-World Task (40 trials)   π0.5 (Baseline)   Ours (FLARE)
                                                                                                                                                                50                                                                                                              50
                                                                                         72                                                                                                         72
    Stack Three Blocks                62.5%            75.0%
                                                                                         70                                                                     45                                  70                                                                          45
    Insert U-shaped Block             45.0%            55.0%
                                                                                         68                                                                                                         68
                                                                                                                                                                40                                                                                                              40

                                                                                         66                                                                                                         66
                                                                                                                                                                35                                                                                                               35
                                                                                              0   10      20     30    40      50       60       70        80                                        0.0   0.2         0.4          0.6          0.8         1.0              1.2
                                                                                                           Rotation Angle (degrees)                                                                                          Translation Value



                                                                        Figure 4. The sensitivity of two hyper-parameters, rotation r and
                                                                        translation t for perturbation & bridging. Our method achieves
                                                                        best performance when r = 30◦ and t = 0.7, respectively.


Figure 3. Real-world experimental setup and execution trajecto-
ries. Top: The “Stack Three Blocks” task. Bottom: The “Insert
U-shaped Block” task.


                                                                                                  (a)                                    (b)                                                               (c)                                         (d)
Real-world Validation To verify FLARE’s effectiveness
and address concerns about privileged simulation states,                Figure 5. The failure case for Coffee and ThreePieceAssembly
we conducted real-world experiments on a Piper arm with                 respectively. (a) Reset coffee pod; (b) Reset coffee machine lid;
RealSense D435i (top/wrist views) across two challenging                (c) Reset the T-shaped block; (d) Reset the U-shaped block.
tasks: Stack Three Blocks (long-horizon) and Insert U-
shaped Block (contact-rich). The experimental results are
presented in Table 2 and Fig. 3. We collected only 10 hu-               the two settings, respectively. We also report the corre-
man demos and augmented them to 50 for each task/reset                  sponding demonstration-generation success rate for each
skill. To bypass the need for ground-truth simulator states,            setting, which reflects the efficiency of generating valid
we used Any6D [19] for object pose estimation to facili-                retry demonstrations. As illustrated, larger rotations and
tate data augmentation. This proves that our method can be              translations produce demonstrations with higher variance
deployed using only visual sensors without privileged co-               and therefore yield higher task success rates, but at the cost
ordinate logs. For failure reconstruction, strict coordinate            of reduced generation efficiency. Excessively large pertur-
matching is unnecessary; FLARE relies on approximate                    bations eventually degrade performance. A plausible ex-
failure reconstruction. Collecting roughly similar failure              planation is that the training set contains a limited number
states (e.g., a toppled cup) without precise spatial alignment          of demonstrations, and overly high variance may hinder the
is sufficient, as our perturbation-based augmentation en-               model’s ability to generalize effectively.
sures generalization to diverse real-world poses using only
visual feedback.
                                                                        5.2. Ablations and Analysis for Reset skills learning
                                                                        Ablation of Reset and Human Instruction In this section,
5. Ablation and Analysis                                                we first investigate the importance of reset-skill learning
                                                                        and its application within our framework. Following pre-
5.1. Analysis of Perturbation & Bridging                                vious studies [39], we adopt a multimodal LLM to generate
The Sensitivity of Hyper-Parameters In this section, we                 task prompt that decides which reset skill should be exe-
investigate two key hyperparameters in our perturbation &               cuted based on the current environment state. To assess the
bridging augmentation strategy: the rotation r and the trans-           necessity of this component, we ablate the reset skill en-
lation t. The rotation r controls the rotation angle applied            tirely and also evaluate a variant of our framework that re-
to the robot hand during perturbation, while the translation            places the multimodal LLM with human-provided instruc-
t determines the positional shift. We generate retry demon-             tions, serving as an upper bound.
strations under different combinations of r and t, and fine-                The results are reported in Table 3, covering four set-
tune the VLA model using these demonstrations. All ex-                  tings—“Ours”, “Ours w/o Reset”, “Ours Reset-Only” and
periments are conducted on Coffee D1, and the results are               “Ours-Oracle”—on the Coffee and ThreePieceAssembly
presented in Fig. 4.                                                    tasks. The comparison illustrates the effectiveness of reset-
    As shown in Fig. 4, our method consistently outper-                 skill learning and deployment: removing reset skills re-
forms all baselines, including Phoenix and π0.5 . The best              duces the average success rate by 3.5%. The human-
performance is achieved when r = 30◦ and t = 0.7 in                     instruction variant (Ours-Oracle) achieves an additional 7%



                                                                   22397


---

Table 3. The performance comparison for our method and two                  Table 4. The reset skill success rate and demonstration generation
variants, Ours w/o Reset and Ours-Oracle. Ours w/o Reset only               efficiency on two manipulation tasks. The Reset Object 1 is coffee
applies the perturbation & bridging strategy for VLA model train-           machine lid/T-shaped block, and the reset object 2 is coffee pod/U-
ing, and Ours-Oracle replaces the generated instruction for object          shaped block for Coffee/ThreePieceAssembly. Our method suc-
reset with human feedback. The experimental results demonstrate             cessfully generates demonstrations and trains useful VLA models
the effectiveness of our reset skill learning and error correction.         that can reset the objects when errors occur.

                                            ThreePiece    ThreePiece                            Reset Skill Success Rate   Generation Efficiency
     Methods       Coffee D0   Coffee D1
                                           Assembly D0   Assembly D1
                                                                                                            ThreePiece                ThreePiece
 Ours w/o Reset       92%        74%          60%           54%                Task             Coffee                     Coffee
                                                                                                            Assembly                  Assembly
 Ours Reset-Only     88%         64%          60%           50%
      Ours            96%        78%          62%           58%                Reset Object 1    84%           88%          83.7%       48.6%
  Ours-Oracle        100%        90%          68%           64%                Reset Object 2    24%           20%          11.6%        5.9%


                                                                            Table 5. The performance of failure case indentification of
improvement, suggesting that stronger multimodal LLMs                       Gemini-2.5-Pro on three tasks: Reset/Retry classification, Reset
could further enhance task execution monitoring.                            object identification and Timestamp identification for Coffee and
                                                                            ThreePieceAssembly. The effective failure analysis provides high-
Reset Skill Learning Analysis We further analyze reset-                     quality reset dataset for further demonstration collection.
skill learning by evaluating both task success rate and
demonstration-generation efficiency. Specifically, we select                           Task              Reset/Retry   Reset Object   Timestamp
two tasks—Coffee and ThreePieceAssembly—and examine                                  Coffee                 88%            88%           78%
the two reset objects required for each. For Coffee, the re-                   ThreePiece Assembly          96%            78%           66%
set objects are the coffee machine lid (Object 1) and the
coffee pod (Object 2). For ThreePieceAssembly, the reset
objects correspond to the T-shaped block (Object 1) and the                 components: retry/reset classification, reset-object identifi-
U-shaped block (Object 2). We construct two dedicated en-                   cation, and timestamp identification. As described in Sec. 4,
vironments for reset evaluation, redefine the success condi-                we employ Gemini-2.5-Pro as the multimodal LLM, and the
tions based on the reset target, and apply domain random-                   exact prompts are provided in the supplementary materials.
ization during scene initialization. Fig. 5 visualizes the four                The retry/reset classification accuracy reaches 88% and
reset tasks. Note that in Fig. 5b, the robot must reset the cof-            96% for the two tasks, demonstrating the strong video rea-
fee machine lid before adjusting the coffee pod pose; thus,                 soning capabilities of state-of-the-art multimodal LLMs.
the effective reset object is the lid.                                      Reset-object identification is a two-way classification prob-
   The results are shown in Table 4. For Coffee, the suc-                   lem for each task, achieving accuracies of 88% and 78%.
cess rate for resetting the machine lid reaches 84%, sub-                   For timestamp identification, we compute accuracy by
stantially higher than the coffee pod reset. A similar pat-                 checking whether the identified frame corresponds to the
tern appears in the ThreePieceAssembly tasks, where the T-                  correct reset object.
shaped block reset is significantly easier than resetting the
U-shaped block. Resetting the coffee pod, for example, of-                  6. Conclusion
ten requires grasping a toppled pod, adjusting its pose, and
placing it upright—an operation that is challenging for the                 We presented FLARE, a failure-aware framework that en-
robot hand used in our experiments. These findings sug-                     dows VLA agents with robust autonomy through a dual
gest the need for more advanced manipulation capabilities                   Retry/Reset paradigm. We identified that the brittleness
for pose adjustment in VLA-based error correction, such as                  of current VLAs stems from trajectory-monotonic train-
dexterous in-hand pose refinement.                                          ing data and success-biased distributions. To overcome
   We also report demonstration-generation efficiency in                    this, we proposed a perturbation-based augmentation to fa-
Table 4. As expected, efficiency is lower for more diffi-                   cilitate innate ID retry capabilities and an MLLM-guided
cult reset tasks, matching the success-rate trend. The re-                  pipeline to acquire OOD reset skills. Our approach achieves
duced success rate indicates room for further augmentation                  an 84.0% average success rate across diverse manipulation
and model training, which could potentially enhance error-                  tasks, surpassing existing self-reflection methods and VLA
correction performance.                                                     backbones. While current hardware limits the correction of
                                                                            highly complex object poses, our findings confirm that treat-
Failure Case Identification with Multi-modal LLM To                         ing failure recovery as a distinct, learned capability is es-
evaluate the performance of failure-case identification, we                 sential for open-world robotic deployment. Future research
manually label 50 execution videos for the Coffee and                       will focus on scaling reset skill libraries and enhancing dex-
ThreePieceAssembly and measure accuracy across three                        terous recovery maneuvers.



                                                                       22398


---

Acknowledgments                                                          [11] Jianing Guo, Zhenhong Wu, Chang Tu, Yiyao Ma, Xiangqi
                                                                              Kong, Zhiqian Liu, Jiaming Ji, Shuning Zhang, Yuanpei
This work is sponsored by CIE-Tencent Robotics X Rhino-                       Chen, Kai Chen, et al. On robustness of vision-language-
Bird Focused Research Program and is also supported                           action model against multi-modal perturbations. arXiv
by the National Natural Science Foundation of China                           preprint arXiv:2510.00037, 2025. 1
(NO. 62322608).                                                          [12] Aryaman Gupta, Yusuf Umut Ciftci, and Somil Bansal. From
                                                                              perception logs to failure modes: Language-driven seman-
References                                                                    tic clustering of failures for robot safety. arXiv preprint
                                                                              arXiv:2506.06570, 2025. 2
 [1] Jinze Bai, Shuai Bai, Yunfei Chu, Zeyu Cui, Kai Dang,               [13] Dan Horgan, John Quan, David Budden, Gabriel Barth-
     Xiaodong Deng, Yang Fan, Wenbin Ge, Yu Han, Fei                          Maron, Matteo Hessel, Hado Van Hasselt, and David Sil-
     Huang, et al. Qwen technical report. arXiv preprint                      ver. Distributed prioritized experience replay. arXiv preprint
     arXiv:2309.16609, 2023. 3                                                arXiv:1803.00933, 2018. 1, 2
 [2] Shuai Bai, Keqin Chen, Xuejing Liu, Jialin Wang, Wenbin             [14] Edward J Hu, Yelong Shen, Phillip Wallis, Zeyuan Allen-
     Ge, Sibo Song, Kai Dang, Peng Wang, Shijie Wang, Jun                     Zhu, Yuanzhi Li, Shean Wang, Lu Wang, Weizhu Chen, et al.
     Tang, et al. Qwen2. 5-vl technical report. arXiv preprint                Lora: Low-rank adaptation of large language models. ICLR,
     arXiv:2502.13923, 2025.                                                  1(2):3, 2022. 5, 6
 [3] Lucas Beyer, Andreas Steiner, André Susano Pinto, Alexan-          [15] Physical Intelligence, Kevin Black, Noah Brown, James
     der Kolesnikov, Xiao Wang, Daniel Salz, Maxim Neumann,                   Darpinian, Karan Dhabalia, Danny Driess, Adnan Esmail,
     Ibrahim Alabdulmohsin, Michael Tschannen, Emanuele                       Michael Equi, Chelsea Finn, Niccolo Fusai, et al. π0.5 : a
     Bugliarello, et al. Paligemma: A versatile 3b vlm for trans-             vision-language-action model with open-world generaliza-
     fer. arXiv preprint arXiv:2407.07726, 2024. 3                            tion. arXiv preprint arXiv:2504.16054, 2025. 1, 3, 6
 [4] Kevin Black, Noah Brown, Danny Driess, Adnan Esmail,                [16] Kento Kawaharazuka, Jihoon Oh, Jun Yamada, Ingmar Pos-
     Michael Equi, Chelsea Finn, Niccolo Fusai, Lachy Groom,                  ner, and Yuke Zhu. Vision-language-action models for
     Karol Hausman, Brian Ichter, et al. π0 : A vision-language-              robotics: A review towards real-world applications. IEEE
     action flow model for general robot control. arXiv preprint              Access, 2025. 2
     arXiv:2410.24164, 2024. 1, 3, 6                                     [17] Chan Kim, Jaekyung Cho, Christophe Bobda, Seung-Woo
 [5] Anthony Brohan, Noah Brown, Justice Carbajal, Yevgen                     Seo, and Seong-Woo Kim. Sero: self-supervised reinforce-
     Chebotar, Joseph Dabis, Chelsea Finn, Keerthana Gopalakr-                ment learning for recovery from out-of-distribution situa-
     ishnan, Karol Hausman, Alexander Herzog, Jasmine Hsu,                    tions. In Proceedings of the Thirty-Second International
     et al. Rt-1: Robotics transformer for real-world control at              Joint Conference on Artificial Intelligence, pages 3884–
     scale. Robotics: Science and Systems XIX, 2023. 3                        3892, 2023. 2
                                                                         [18] Moo Jin Kim, Karl Pertsch, Siddharth Karamcheti, Ted Xiao,
 [6] Hongyi Chen, Yunchao Yao, Ruixuan Liu, Changliu Liu, and
                                                                              Ashwin Balakrishna, Suraj Nair, Rafael Rafailov, Ethan P
     Jeffrey Ichnowski. Automating robot failure recovery us-
                                                                              Foster, Pannag R Sanketi, Quan Vuong, et al. Openvla: An
     ing vision-language models with optimized prompts. arXiv
                                                                              open-source vision-language-action model. In Conference
     preprint arXiv:2409.03966, 2024. 2
                                                                              on Robot Learning, pages 2679–2713. PMLR, 2025. 1, 3, 6
 [7] Cheng Chi, Zhenjia Xu, Siyuan Feng, Eric Cousineau, Yilun           [19] Taeyeop Lee, Bowen Wen, Minjun Kang, Gyuree Kang,
     Du, Benjamin Burchfiel, Russ Tedrake, and Shuran Song.                   In So Kweon, and Kuk-Jin Yoon. Any6d: Model-free
     Diffusion policy: Visuomotor policy learning via action dif-             6d pose estimation of novel objects. In Proceedings of
     fusion. The International Journal of Robotics Research, 44               the IEEE/CVF Conference on Computer Vision and Pattern
     (10-11):1684–1704, 2025. 3                                               Recognition, pages 11633–11643, 2025. 7
 [8] Danny Driess, Fei Xia, Mehdi SM Sajjadi, Corey Lynch,               [20] Bo Li, Yuanhan Zhang, Dong Guo, Renrui Zhang, Feng Li,
     Aakanksha Chowdhery, Brian Ichter, Ayzaan Wahid,                         Hao Zhang, Kaichen Zhang, Peiyuan Zhang, Yanwei Li, Zi-
     Jonathan Tompson, Quan Vuong, Tianhe Yu, et al. Palm-                    wei Liu, et al. Llava-onevision: Easy visual task transfer.
     e: an embodied multimodal language model. In Proceedings                 Transactions on Machine Learning Research. 3
     of the 40th International Conference on Machine Learning,           [21] Chenxuan Li, Jiaming Liu, Guanqun Wang, Xiaoqi Li, Six-
     pages 8469–8488, 2023. 3                                                 iang Chen, Liang Heng, Chuyan Xiong, Jiaxin Ge, Ren-
 [9] Senyu Fei, Siyin Wang, Junhao Shi, Zihao Dai, Jikun Cai,                 rui Zhang, Kaichen Zhou, et al. A self-correcting vision-
     Pengfang Qian, Li Ji, Xinzhe He, Shiduo Zhang, Zhaoye Fei,               language-action model for fast and slow system manipula-
     et al. Libero-plus: In-depth robustness analysis of vision-              tion. arXiv preprint arXiv:2405.17418, 2024. 2
     language-action models. arXiv preprint arXiv:2510.13626,            [22] Jacky Liang, Wenlong Huang, Fei Xia, Peng Xu, Karol
     2025. 1, 3                                                               Hausman, Brian Ichter, Pete Florence, and Andy Zeng. Code
[10] Dibya Ghosh, Homer Rich Walke, Karl Pertsch, Kevin                       as policies: Language model programs for embodied control.
     Black, Oier Mees, Sudeep Dasari, Joey Hejna, Tobias                      In 2023 IEEE International Conference on Robotics and Au-
     Kreiman, Charles Xu, Jianlan Luo, et al. Octo: An open-                  tomation (ICRA), pages 9493–9500. IEEE, 2023. 3
     source generalist robot policy. In Robotics: Science and Sys-       [23] Zijun Lin, Jiafei Duan, Haoquan Fang, Dieter Fox, Ranjay
     tems, 2024. 3                                                            Krishna, Cheston Tan, and Bihan Wen. Failsafe: Reasoning




                                                                 22399


---

     and recovery from failures in vision-language-action models.      [36] Shivam Vats, Devesh K Jha, Maxim Likhachev, Oliver Kroe-
     arXiv preprint arXiv:2510.01642, 2025. 2                               mer, and Diego Romeres. Recoverychaining: Learning lo-
[24] Yaron Lipman, Ricky TQ Chen, Heli Ben-Hamu, Maximil-                   cal recovery policies for robust manipulation. arXiv preprint
     ian Nickel, and Matt Le. Flow matching for generative mod-             arXiv:2410.13979, 2024. 2
     eling. arXiv preprint arXiv:2210.02747, 2022. 3                   [37] Zihao Wang, Shaofei Cai, Guanzhou Chen, Anji Liu, Xi-
[25] Kehui Liu, Zixin Tang, Dong Wang, Zhigang Wang, Xue-                   aojian Ma, and Yitao Liang. Describe, explain, plan
     long Li, and Bin Zhao. Coherent: Collaboration of hetero-              and select: Interactive planning with large language mod-
     geneous multi-robot system with large language models. In              els enables open-world multi-task agents. arXiv preprint
     2025 IEEE International Conference on Robotics and Au-                 arXiv:2302.01560, 2023. 1, 2
     tomation (ICRA), pages 10208–10214. IEEE, 2025. 1, 2              [38] Wenke Xia, Dong Wang, Xincheng Pang, Zhigang Wang,
[26] Zeyi Liu, Arpit Bahety, and Shuran Song. Reflect: Summa-               Bin Zhao, Di Hu, and Xuelong Li. Kinematic-aware prompt-
     rizing robot experiences for failure explanation and correc-           ing for generalizable articulated object manipulation with
     tion. In Conference on Robot Learning, pages 3468–3484.                llms. In 2024 IEEE International Conference on Robotics
     PMLR, 2023. 2                                                          and Automation (ICRA), pages 2073–2080. IEEE, 2024. 1, 2
[27] Jingxian Lu, Wenke Xia, Dong Wang, Zhigang Wang, Bin              [39] Wenke Xia, Ruoxuan Feng, Dong Wang, and Di Hu.
     Zhao, Di Hu, and Xuelong Li. Koi: Accelerating online imi-             Phoenix: A motion-based self-reflection framework for fine-
     tation learning via hybrid key-state guidance. arXiv preprint          grained robotic action correction. In Proceedings of the
     arXiv:2408.02912, 2024. 1, 2                                           Computer Vision and Pattern Recognition Conference, pages
[28] Yueen Ma, Zixing Song, Yuzheng Zhuang, Jianye Hao, and                 6981–6990, 2025. 2, 6, 7
     Irwin King. A survey on vision-language-action models for         [40] Chuyan Xiong, Chengyu Shen, Xiaoqi Li, Kaichen Zhou,
     embodied ai. arXiv preprint arXiv:2405.14093, 2024. 1                  Jeremy Liu, Ruiping Wang, and Hao Dong. Aic mllm: Au-
[29] Ajay Mandlekar, Soroush Nasiriany, Bowen Wen, Iretiayo                 tonomous interactive correction mllm for robust robotic ma-
     Akinola, Yashraj Narang, Linxi Fan, Yuke Zhu, and Dieter               nipulation. arXiv preprint arXiv:2406.11548, 2024. 2
     Fox. Mimicgen: A data generation system for scalable robot        [41] Chuyan Xiong, Chengyu Shen, Xiaoqi Li, Kaichen Zhou,
     learning using human demonstrations. In 7th Annual Con-                Jiaming Liu, Ruiping Wang, and Hao Dong. Autonomous
     ference on Robot Learning. 1, 4, 6                                     interactive correction mllm for robust robotic manipulation.
[30] Ajay Mandlekar, Danfei Xu, Josiah Wong, Soroush Nasiri-                In 8th Annual Conference on Robot Learning, 2024. 1, 2
     any, Chen Wang, Rohun Kulkarni, Li Fei-Fei, Silvio                [42] Yifan Yang, Zhixiang Duan, Tianshi Xie, Fuyu Cao, Pinxi
     Savarese, Yuke Zhu, and Roberto Martı́n-Martı́n. What                  Shen, Peili Song, Piaopiao Jin, Guokang Sun, Shaoqing
     matters in learning from offline human demonstrations for              Xu, Yangwei You, et al. Fpc-vla: A vision-language-action
     robot manipulation. In Conference on Robot Learning, pages             framework with a supervisor for failure prediction and cor-
     1678–1690. PMLR, 2022. 6                                               rection. arXiv preprint arXiv:2509.04018, 2025. 2
[31] Abby O’Neill, Abdul Rehman, Abhiram Maddukuri, Ab-                [43] Naoki Yokoyama, Alex Clegg, Joanne Truong, Eric Under-
     hishek Gupta, Abhishek Padalkar, Abraham Lee, Acorn Poo-               sander, Tsung-Yen Yang, Sergio Arnaud, Sehoon Ha, Dhruv
     ley, Agrim Gupta, Ajay Mandlekar, Ajinkya Jain, et al. Open            Batra, and Akshara Rai. Asc: Adaptive skill coordination for
     x-embodiment: Robotic learning datasets and rt-x models:               robotic mobile manipulation. IEEE Robotics and Automa-
     Open x-embodiment collaboration 0. In 2024 IEEE Inter-                 tion Letters, 9(1):779–786, 2023. 1, 2
     national Conference on Robotics and Automation (ICRA),            [44] Dapeng Zhang, Jin Sun, Chenghui Hu, Xiaoyan Wu, Zhen-
     pages 6892–6903. IEEE, 2024. 3                                         long Yuan, Rui Zhou, Fei Shen, and Qingguo Zhou. Pure
[32] Karl Pertsch, Kyle Stachowicz, Brian Ichter, Danny Driess,             vision language action (vla) models: A comprehensive sur-
     Suraj Nair, Quan Vuong, Oier Mees, Chelsea Finn, and                   vey. arXiv preprint arXiv:2509.19012, 2025. 2
     Sergey Levine. Fast: Efficient action tokenization for vision-    [45] Hongyin Zhang, Shuo Zhang, Junxi Jin, Qixin Zeng, Runze
     language-action models. arXiv preprint arXiv:2501.09747,               Li, and Donglin Wang. Robustvla: Robustness-aware rein-
     2025. 3                                                                forcement post-training for vision-language-action models.
[33] John Schulman, Filip Wolski, Prafulla Dhariwal, Alec Rad-              arXiv preprint arXiv:2511.01331, 2025. 1
     ford, and Oleg Klimov. Proximal policy optimization algo-         [46] Ganlong Zhao, Guanbin Li, Weikai Chen, and Yizhou Yu.
     rithms. arXiv preprint arXiv:1707.06347, 2017. 1, 2                    Over-nav: Elevating iterative vision-and-language naviga-
[34] Gemini Team, Rohan Anil, Sebastian Borgeaud, Jean-                     tion with open-vocabulary detection and structured represen-
     Baptiste Alayrac, Jiahui Yu, Radu Soricut, Johan Schalkwyk,            tation. In Proceedings of the IEEE/CVF Conference on Com-
     Andrew M Dai, Anja Hauth, Katie Millican, et al. Gemini: a             puter Vision and Pattern Recognition, pages 16296–16306,
     family of highly capable multimodal models. arXiv preprint             2024. 1
     arXiv:2312.11805, 2023. 2                                         [47] Ganlong Zhao, Guanbin Li, Jia Pan, and Yizhou Yu. Aerial
[35] Hugo Touvron, Thibaut Lavril, Gautier Izacard, Xavier                  vision-and-language navigation with grid-based view selec-
     Martinet, Marie-Anne Lachaux, Timothée Lacroix, Baptiste              tion and map construction. arXiv preprint arXiv:2503.11091,
     Rozière, Naman Goyal, Eric Hambro, Faisal Azhar, et al.               2025. 1
     Llama: Open and efficient foundation language models.             [48] Tony Z Zhao, Vikash Kumar, Sergey Levine, and Chelsea
     arXiv preprint arXiv:2302.13971, 2023. 3                               Finn. Learning fine-grained bimanual manipulation with




                                                                  22400


---

     low-cost hardware. arXiv preprint arXiv:2304.13705, 2023.
     2, 3
[49] Brianna Zitkovich, Tianhe Yu, Sichun Xu, Peng Xu, Ted
     Xiao, Fei Xia, Jialin Wu, Paul Wohlhart, Stefan Welker,
     Ayzaan Wahid, et al. Rt-2: Vision-language-action models
     transfer web knowledge to robotic control. In Conference on
     Robot Learning, pages 2165–2183. PMLR, 2023. 1, 3




                                                               22401


---

