# RecoverNav — Closest Prior-Work Deep Review

**Status:** research-development review, 2026-09-05. Novelty remains provisional until the final method and physical protocol are frozen.

## Purpose

This document tests RecoverNav against the closest scientific concepts rather than collecting supportive citations. The goal is to determine what claim is still defensible after accounting for established collision-inevitability, viability, safe replanning, and contingency-planning work.

## Candidate contribution under review

RecoverNav studies whether a lightweight, online, robot-observable estimate of **post-invalidation recovery capacity** can first predict and then reduce navigation failures caused by dynamic route invalidation in partially observed indoor environments.

The intended contribution is **not** generic contingency planning, collision avoidance, safe navigation, or replanning.

---

## 1. Fraichard & Asama — Inevitable Collision States

**Reference:** Thierry Fraichard and Hajime Asama, *Inevitable Collision States — A Step Towards Safer Robots?*, Advanced Robotics 18(10), 2004. DOI: 10.1163/1568553042674662. Earlier IROS version: 2003.

**Core problem:** define states from which collision is inevitable regardless of future robot motion.

**Key idea:** a robot should avoid entering an Inevitable Collision State (ICS). The concept explicitly considers robot and obstacle dynamics and is motivated partly by safe motion under sensing constraints and unexpected obstacles.

**Overlap with RecoverNav:** both reject purely myopic geometric feasibility. Both ask whether a current decision destroys useful future options.

**Non-equivalence:** ICS is fundamentally a collision-inevitability/safety concept. RecoverNav's target is a policy-dependent, post-route-invalidation ability to autonomously continue and complete a navigation task.

**Novelty threat:** very high if RecoverNav is described vaguely as "avoid states with no escape." That principle is established territory.

---

## 2. Bekris & Kavraki — Greedy but Safe Replanning under Kinodynamic Constraints

**Reference:** Kostas E. Bekris and Lydia E. Kavraki, *Greedy but Safe Replanning under Kinodynamic Constraints*, ICRA 2007, pp. 704–710. DOI: 10.1109/ROBOT.2007.363069.

**Core problem:** repeated replanning under partial environmental knowledge, kinodynamic constraints, and finite planning time.

**Key idea:** incrementally reuse planning-tree information while explicitly respecting dynamics and safety in a changing representation of the workspace.

**Overlap:** sensing, planning, execution, and replanning are treated as an interleaved process under partial knowledge.

**Non-equivalence:** RecoverNav does not claim novelty for replanning itself. Its proposed treatment is a **pre-event route-choice preference** intended to preserve later recovery capacity before a specific route invalidation is known.

**Novelty threat:** moderate. Any claim of novelty based on online replanning or partial knowledge alone is invalid.

---

## 3. Bouraine, Fraichard & Salhi — Braking ICS / Passive Motion Safety

**Reference:** Sara Bouraine, Thierry Fraichard, and Hassen Salhi, *Provably Safe Navigation for Mobile Robots with Limited Field-of-Views in Dynamic Environments*, Autonomous Robots, 2012; related IROS 2011 Braking-ICS paper, DOI: 10.1109/IROS.2011.6094901.

**Core problem:** provably safe navigation with limited field of view in unknown dynamic environments.

**Key idea:** relax ICS to Braking ICS and guarantee passive motion safety: when collision cannot be avoided, the robot is at rest.

**Overlap:** explicitly addresses limited sensing and future inability to remain safe.

**Non-equivalence:** RecoverNav should not claim a formal passive-safety guarantee. Its first estimator is empirical and mission-recovery-oriented, not a proof that collision can always be prevented.

**Novelty threat:** high if RecoverNav uses terms such as "guaranteed recovery" or "safe state" without a theorem and matching assumptions.

---

## 4. Bouguerra, Fraichard & Fezari — Viability-Based Guaranteed Safe Navigation

**Reference:** Mohamed Amine Bouguerra, Thierry Fraichard, and Mohamed Fezari, *Viability-Based Guaranteed Safe Robot Navigation*, Journal of Intelligent & Robotic Systems 95, 459–471, 2019. DOI: 10.1007/s10846-018-0955-9.

**Core problem:** guarantee navigation under multiple state/motion constraints, not only collision avoidance.

**Key idea:** use the viability kernel, i.e. states from which at least one future trajectory can satisfy the constraints indefinitely. A conservative approximation is computed offline and used in online navigation.

**Overlap:** the viability concept is mathematically close to the intuition that the robot should remain in states retaining feasible future behavior.

**Non-equivalence:** RecoverNav must not present "having at least one feasible future option" as new. A possible distinct contribution is an online observable **proxy for route-level post-invalidation recovery**, validated against executed outcomes and then used for route choice.

**Novelty threat:** very high if the estimator is merely a renamed viability measure.

---

## 5. Jung, Estornell & Everett — Contingency-MPPI

**Reference:** Leonard Jung, Alexander Estornell, and Michael Everett, *Contingency Constrained Planning with MPPI within MPPI*, Proceedings of L4DC, PMLR 283:869–880, 2025.

**Core problem:** ensure that contingency behavior remains available during nominal execution.

**Key idea:** embed contingency optimization inside nominal MPPI. The method reports both simulation and physical mobile-robot hardware experiments.

**Overlap:** direct prior art against any broad statement that RecoverNav is the first method to preserve backup behavior during nominal motion.

**Candidate distinction:** RecoverNav is aimed at an **unknown future route invalidation** rather than a planner-specified contingency behavior. Its scientific object is an estimator whose predictive validity is tested separately from planner efficacy.

**Novelty threat:** critical. The paper must distinguish estimator validation and unknown-event route-level recoverability from explicit contingency trajectory optimization.

---

## 6. Srirangam, Jung, Poola & Everett — SCRAMPPI

**Reference:** Raj Harshit Srirangam, Leonard Jung, Rohith Poola, and Michael Everett, *SCRAMPPI: Efficient Contingency Planning for Mobile Robot Navigation via Hamilton-Jacobi Reachability*, arXiv:2603.26995, 2026.

**Core problem:** guarantee existence of a feasible trajectory from the nominal plan to a designated safe set.

**Key idea:** formulate contingency feasibility as reach-avoid and use Hamilton–Jacobi reachability to certify the backward reachable set online as the environment is revealed; integrate this with MPPI. The work includes simulation and hardware experiments.

**Overlap:** extremely close conceptual neighbor. It directly formalizes preserving feasible contingency to a safe set while pursuing nominal behavior.

**Candidate distinction:** RecoverNav should not compete by offering a weaker version of a certified safe-set reachability constraint. The strongest remaining angle is **prediction and decision usefulness when the specific future route invalidation and recovery destination are not known beforehand**.

**Novelty threat:** critical. SCRAMPPI must be a central related-work comparison, not a peripheral citation.

---

# Cross-paper conclusion

The following are established and therefore **not acceptable novelty claims**:

- future feasibility matters beyond immediate collision freedom;
- a robot should avoid states from which safe continuation becomes impossible;
- navigation can preserve contingency/backup behavior;
- reachability and viability can formalize future feasible sets;
- robots can replan under partial knowledge;
- contingency-aware methods have already run on physical mobile robots.

## Provisional paper-worthy gap

> **Can a computationally lightweight, interpretable, robot-observable structural estimator predict whether an indoor mobile robot will remain recoverable after an as-yet-unknown local route invalidation, and does using that estimator for pre-event route selection reduce physical-robot recovery failures relative to an otherwise matched conventional planner?**

This produces two distinct studies.

### Study A — estimator validity

Does the pre-event estimator contain predictive information about subsequent executed recovery feasibility on held-out scenarios/trials?

### Study B — decision usefulness

After freezing the estimator, does using it for route selection reduce the prespecified physical-robot recovery-failure endpoint relative to a matched baseline, and at what path-length/latency cost?

Study B must not be used to retroactively tune Study A.

---

# Novelty kill conditions

The contribution must be revised or abandoned if deeper review finds prior work already combining nearly all of the following under comparable assumptions:

1. online pre-event recovery-feasibility estimation from robot-observable map/state information;
2. validation of the estimate against executed physical recovery outcomes;
3. route-level use before invalidation rather than only emergency control;
4. unknown route-invalidating event at decision time;
5. partially observed indoor mobile-robot navigation;
6. conventional navigation-stack integration;
7. matched physical comparison using a recovery-specific endpoint;
8. comparable computational and information assumptions.

---

# Implications for method design

The first estimator must not be a large hand-tuned weighted feature list. It should have explicit semantics and few degrees of freedom.

The selected v1 direction is **bottleneck-aware escape capacity** over currently observed, footprint-aware traversable space. Its exact frozen mathematical definition is maintained separately in `RECOVERABILITY_ESTIMATOR_V1.md`.

---

# Baseline policy

For the primary causal comparison, J0 and RecoverNav must differ only in the recoverability treatment. Perception, localization, controller, costmaps, safety layer, event trigger, replan policy, and robot hardware must be identical.

A reachability/contingency method such as SCRAMPPI is scientifically valuable as a secondary strong reference if it can be implemented under genuinely comparable assumptions, but it must not obscure the clean J0-vs-RecoverNav treatment comparison.

---

# Current conclusion

RecoverNav remains scientifically plausible, but the broad "preserve escape options" idea is not novel. The strongest paper path is an **empirical construct-validation contribution plus a controlled physical-robot route-selection study**.

The next methodological gate is to validate the frozen estimator before allowing it to support any efficacy claim.

## Primary bibliographic anchors

- T. Fraichard and H. Asama, *Inevitable collision states — a step towards safer robots?*, Advanced Robotics, 2004. DOI: 10.1163/1568553042674662.
- K. E. Bekris and L. E. Kavraki, *Greedy but Safe Replanning under Kinodynamic Constraints*, ICRA 2007. DOI: 10.1109/ROBOT.2007.363069.
- S. Bouraine, T. Fraichard, and H. Salhi, Braking-ICS / provably safe navigation work, IROS 2011 / Autonomous Robots 2012. DOI: 10.1109/IROS.2011.6094901.
- M. A. Bouguerra, T. Fraichard, and M. Fezari, *Viability-Based Guaranteed Safe Robot Navigation*, JINT 2019. DOI: 10.1007/s10846-018-0955-9.
- L. Jung, A. Estornell, and M. Everett, *Contingency Constrained Planning with MPPI within MPPI*, L4DC/PMLR 2025.
- R. H. Srirangam, L. Jung, R. Poola, and M. Everett, *SCRAMPPI*, arXiv:2603.26995, 2026.

## Review limitation

This is a focused closest-prior-work review, not yet a systematic review. Before submission, the references and predecessor chains of Contingency-MPPI and SCRAMPPI must be expanded into a broader reproducible literature search.