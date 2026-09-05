# RecoverNav — Initial Literature Matrix

**Status:** living review; initial closest-prior-work pass, not exhaustive.  
**Rule:** novelty claims remain provisional until the closest methods are read and compared at methodology level.

## Why this review matters

The broad statement "a robot should preserve recovery/backup options while navigating" is not novel by itself. RecoverNav must identify a narrower contribution relative to formal safety, viability, contingency planning, reachability, dead-end avoidance, and dynamic-navigation work.

## Closest-prior-work matrix

| Work | Core problem | Method / notion | Dynamic / partial information | Evidence | Relationship to RecoverNav | Key distinction to test |
|---|---|---|---|---|---|---|
| Fraichard & Asama, *Inevitable Collision States — a Step Towards Safer Robots?*, Advanced Robotics 18(10), 2004, DOI 10.1163/1568553042674662 | Avoid states from which collision is unavoidable | Inevitable Collision States (ICS); reasons about whether any collision-free future trajectory remains | Explicitly considers moving obstacles; includes safe motion planning under sensing constraints / partially known environments | Formal development + navigation examples | Foundational overlap: future feasible options matter before failure occurs | RecoverNav targets recovery after route invalidation, not merely inevitable collision; this distinction must be formal rather than rhetorical |
| Bouguerra, Fraichard & Fezari, *Viability-Based Guaranteed Safe Robot Navigation*, J. Intelligent & Robotic Systems 95, 2019 | Maintain satisfaction of multiple motion constraints | Viability kernel: states from which at least one admissible trajectory remains | Handles classes of time-varying constraints; online reactive navigation uses offline kernel approximation | Robotic scenarios reported in paper | Strong conceptual overlap with "preserving feasible future options" | RecoverNav needs to show why its recovery target differs from viability/safety and why a lightweight estimator is useful under its sensing/compute assumptions |
| Jung, Estornell & Everett, *Contingency Constrained Planning with MPPI within MPPI*, L4DC/PMLR 283, 2025 | Keep contingency behavior feasible while executing a nominal task | Contingency-MPPI embeds contingency planning inside nominal planning | Designed for sudden changes / contingency execution | Simulation and mobile-robot hardware experiments | Very close overlap: nominal planning explicitly accounts for backup behavior | RecoverNav cannot claim first contingency-aware navigation; it must distinguish estimator, problem setting, route-level decision, observability assumptions, computational profile, or endpoint |
| Srirangam, Jung, Poola & Everett, *SCRAMPPI: Efficient Contingency Planning for Mobile Robot Navigation via Hamilton-Jacobi Reachability*, arXiv:2603.26995, 2026 | Ensure a feasible contingency trajectory to a safe set along nominal behavior | Reach-avoid / Hamilton–Jacobi reachability used to certify contingency feasibility; integrated with MPPI | Environment revealed online; contingency feasibility evolves with observations | Simulation + hardware experiments reported | Extremely close conceptual neighbor: maintaining reachability to a safe set | RecoverNav must not duplicate "maintain backup feasibility". Candidate distinction: empirical recovery-feasibility estimation for route choice in Nav2-style indoor navigation vs certified HJ contingency constraint—but this requires careful full-paper comparison |
| Li et al., *FRTree Planner: Robot Navigation in Cluttered and Unknown Environments with Tree of Free Regions*, 2024 | Navigate unknown/cluttered environments, narrow passages and dead ends | Incremental free-region tree representing topological/geometric navigation options | Online perceptive updates; dynamic obstacles | Simulation + real-world experiments reported | Overlap in alternative-route/free-space topology and dead-end avoidance | RecoverNav should show that its estimator predicts *post-invalidation recovery feasibility*, not simply accessibility or dead-end avoidance |
| Mohanan & Salgoankar, *A survey of robotic motion planning in dynamic environments*, Robotics and Autonomous Systems 100, 2018 | Survey dynamic-environment motion planning | Reviews classical, velocity-based, heuristic and safety approaches | Dynamic environments | Survey | Establishes broad field and historical context | Use as map of prior work, not primary evidence for novelty |

## Adjacent literature that must be added in the next pass

The next review should explicitly include primary sources for:

- ICS-AVOID and probabilistic ICS;
- passive safety / braking ICS under limited field of view;
- velocity obstacles and dynamic-window navigation as conventional dynamic baselines/context;
- contingency planning beyond MPPI;
- reach-avoid / Hamilton–Jacobi safety and backup controllers;
- safe-set and control-invariant-set approaches;
- dead-end prediction/avoidance in partially observed navigation;
- topology-aware global planning in indoor environments;
- Nav2 global planning, replanning, behavior trees and recovery behaviors;
- empirical navigation failure prediction;
- real-robot benchmark methodology for navigation in changing environments.

## Provisional research-gap statement

**Do not quote this as established novelty yet.**

A plausible gap is the following:

> Existing formal and optimization-based methods can enforce or reason about collision avoidance, viability, or explicit contingency feasibility, including methods with hardware demonstrations. It remains to be established whether a computationally lightweight, robot-information-conditioned estimate of *post-invalidation recovery feasibility* can be validated against executed recovery outcomes and then used at route-selection time to reduce a narrowly defined recovery-infeasible failure rate in a conventional ROS 2/Nav2 indoor navigation stack under matched physical trials.

This gap survives only if the continued review finds no prior method with the same estimator target, information assumptions, integration point, and physical endpoint.

## Novelty checklist

Before claiming novelty, answer with citations:

- [ ] Has prior work estimated probability/margin of successful recovery after route invalidation?
- [ ] Has that estimate been validated against executed physical recovery outcomes?
- [ ] Has it been used for pre-invalidation *route choice*, rather than only local control/safety?
- [ ] Does prior work operate with the same partial-observation assumptions?
- [ ] Does prior work integrate with a conventional ROS 2/Nav2 navigation stack?
- [ ] Does prior work compare matched physical trials using a recovery-specific binary endpoint?
- [ ] Is the proposed RecoverNav estimator computationally or experimentally distinct in a meaningful way?

If a close paper answers all of these positively, revise the contribution rather than weakening the comparison.

## Bibliographic anchors

1. T. Fraichard and H. Asama. “Inevitable collision states — a step towards safer robots?” *Advanced Robotics*, 18(10):1001–1024, 2004. DOI: 10.1163/1568553042674662.
2. M. A. Bouguerra, T. Fraichard, and M. Fezari. “Viability-Based Guaranteed Safe Robot Navigation.” *Journal of Intelligent & Robotic Systems*, 95:459–471, 2019.
3. L. Jung, A. Estornell, and M. Everett. “Contingency Constrained Planning with MPPI within MPPI.” *Proceedings of the 7th Annual Learning for Dynamics & Control Conference*, PMLR 283:869–880, 2025.
4. R. H. Srirangam, L. Jung, R. Poola, and M. Everett. “SCRAMPPI: Efficient Contingency Planning for Mobile Robot Navigation via Hamilton-Jacobi Reachability.” arXiv:2603.26995, 2026.
5. Y. Li et al. “FRTree Planner: Robot Navigation in Cluttered and Unknown Environments with Tree of Free Regions.” arXiv:2410.20230, 2024.
6. M. G. Mohanan and A. Salgoankar. “A survey of robotic motion planning in dynamic environments.” *Robotics and Autonomous Systems*, 100:171–185, 2018.

## Review discipline

A title/abstract match is not sufficient for novelty assessment. For the closest works—especially Contingency-MPPI, SCRAMPPI, ICS/viability, and FRTree—the methodology, state/information assumptions, contingency/recovery definition, experiment design, and hardware evaluation must be inspected before the gap is frozen.
