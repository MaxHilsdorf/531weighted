from models import (
    LiftProgramContext,
    ProgramWeekContext,
    LiftPerformance,
    LiftContext,
    ProgramWeek,
    Lift
)


class FiveThreeOneProgram:
    def __init__(self, lift_program_contexts: dict[Lift, LiftProgramContext], program_week_contexts: dict[ProgramWeek, ProgramWeekContext], bodyweight: float, n_sets: int = 3):
        self.lift_program_contexts = lift_program_contexts
        self.program_week_contexts = program_week_contexts
        self.bodyweight = bodyweight
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
        training_max = self._get_training_max(lift_context)
        
        if len(self.program_week_contexts[program_week].scaling_factors) != self.n_sets:
            raise ValueError(f"Expected {self.n_sets} scaling factors for program week {program_week}, got {len(self.program_week_contexts[program_week].scaling_factors)}")
        
        performances = []
        for i in range(self.n_sets):
            scaling_factor = self.program_week_contexts[program_week].scaling_factors[i]
            raw_weight = self._get_working_weight(
                training_max=training_max,
                scaling_factor=scaling_factor,
                is_bodyweight_lift=lift_context.lift.is_bodyweight,
            )
            weight = lift_context.lift.round_weight(raw_weight)
            reps = self.program_week_contexts[program_week].reps_per_set[i]
            performances.append(LiftPerformance(lift=lift_context.lift, weight=weight, reps=reps))
        
        return performances

    def _get_training_max(self, lift_context: LiftContext) -> float:
        training_max_factor = self.lift_program_contexts[lift_context.lift].training_max_factor

        if not lift_context.lift.is_bodyweight:
            return lift_context.one_rep_max * training_max_factor

        return max(0.0, ((self.bodyweight + lift_context.one_rep_max) * training_max_factor) - self.bodyweight)

    def _get_working_weight(self, training_max: float, scaling_factor: float, is_bodyweight_lift: bool) -> float:
        if not is_bodyweight_lift:
            return training_max * scaling_factor

        return max(0.0, ((self.bodyweight + training_max) * scaling_factor) - self.bodyweight)

    @staticmethod
    def _format_weight(weight: float) -> str:
        return f"{weight:.2f}".rstrip("0").rstrip(".")