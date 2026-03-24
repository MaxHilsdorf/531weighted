from models import (
    LiftProgramContext,
    ProgramWeekContext,
    LiftPerformance,
    LiftContext,
    ProgramWeek,
    Lift
)


class FiveThreeOneProgram:
    def __init__(self, lift_program_contexts: dict[Lift, LiftProgramContext], program_week_contexts: dict[ProgramWeek, ProgramWeekContext], bodyweight: float, zero_weight_strictness: float = 1.0, n_sets: int = 3):
        self.lift_program_contexts = lift_program_contexts
        self.program_week_contexts = program_week_contexts
        self.bodyweight = bodyweight
        self.zero_weight_strictness = min(max(zero_weight_strictness, 0.0), 1.0)
        self.n_sets = n_sets

    def generate_program_report(self) -> str:
        report_lines = ["5/3/1 Program", "============="]
        week_order = [ProgramWeek.FIVE, ProgramWeek.THREE, ProgramWeek.ONE, ProgramWeek.DELOAD]

        report_lines.extend(["", "Lift Overview"])

        for lift_program_context in self.lift_program_contexts.values():
            lift_context = lift_program_context.lift_context
            training_max = self._get_training_max(lift_context)
            report_lines.append(
                f"  {lift_context.lift.name}: 1RM {self._format_weight(lift_context.one_rep_max)}kg, TM {self._format_weight(training_max)}kg"
            )

        for program_week in week_order:
            if program_week not in self.program_week_contexts:
                continue

            report_lines.extend([
                "",
                f"Week {program_week.value}",
            ])

            for lift_program_context in self.lift_program_contexts.values():
                lift_context = lift_program_context.lift_context
                performances = self._get_lift_performance(lift_context, program_week)
                performance_summary = ", ".join(
                    f"{self._format_weight(performance.weight)}kg*{performance.reps}"
                    for performance in performances
                )
                report_lines.append(f"  {lift_context.lift.name}: {performance_summary}")

        return "\n".join(report_lines)

    def _get_lift_performance(self, lift_context: LiftContext, program_week: ProgramWeek) -> list[LiftPerformance]:
        training_max = self._get_training_max(lift_context, apply_floor=False)
        
        if len(self.program_week_contexts[program_week].scaling_factors) != self.n_sets:
            raise ValueError(f"Expected {self.n_sets} scaling factors for program week {program_week}, got {len(self.program_week_contexts[program_week].scaling_factors)}")
        
        performances = []
        for i in range(self.n_sets):
            scaling_factor = self.program_week_contexts[program_week].scaling_factors[i]
            target_reps = self.program_week_contexts[program_week].reps_per_set[i]
            raw_weight = self._get_working_weight(
                lift=lift_context.lift,
                training_max=training_max,
                scaling_factor=scaling_factor,
                apply_floor=False,
            )

            if raw_weight < 0:
                weight = 0.0
                reps = self._get_zero_weight_reps(
                    lift=lift_context.lift,
                    raw_weight=raw_weight,
                    target_reps=target_reps,
                )
            else:
                weight = lift_context.lift.round_weight(raw_weight)
                reps = target_reps

            performances.append(LiftPerformance(lift=lift_context.lift, weight=weight, reps=reps))
        
        return performances

    def _get_training_max(self, lift_context: LiftContext, apply_floor: bool = True) -> float:
        training_max_factor = self.lift_program_contexts[lift_context.lift].training_max_factor

        return self._scale_with_bodyweight_offset(
            base_weight=lift_context.one_rep_max,
            factor=training_max_factor,
            lift=lift_context.lift,
            apply_floor=apply_floor,
        )

    def _get_working_weight(self, lift: Lift, training_max: float, scaling_factor: float, apply_floor: bool = True) -> float:
        return self._scale_with_bodyweight_offset(
            base_weight=training_max,
            factor=scaling_factor,
            lift=lift,
            apply_floor=apply_floor,
        )

    def _get_zero_weight_reps(self, lift: Lift, raw_weight: float, target_reps: int) -> int:
        actual_total_load = lift.bodyweight_offset(self.bodyweight)
        if actual_total_load <= 0:
            return 1

        target_total_load = actual_total_load + raw_weight
        equivalent_reps = 30 * (
            (target_total_load * (1 + (target_reps / 30))) / actual_total_load - 1
        )

        adjusted_reps = target_reps - (self.zero_weight_strictness * (target_reps - equivalent_reps))
        return max(1, min(target_reps, round(adjusted_reps)))

    def _scale_with_bodyweight_offset(self, base_weight: float, factor: float, lift: Lift, apply_floor: bool = True) -> float:
        bodyweight_offset = lift.bodyweight_offset(self.bodyweight)
        scaled_weight = ((base_weight + bodyweight_offset) * factor) - bodyweight_offset
        if apply_floor:
            return max(0.0, scaled_weight)

        return scaled_weight

    @staticmethod
    def _format_weight(weight: float) -> str:
        return f"{weight:.2f}".rstrip("0").rstrip(".")