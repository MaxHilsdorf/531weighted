from core.calculators import StrengthCalculator
from core.models import (
    CompetitionAttempt,
    CompetitionAttemptPlan,
    Lift,
    LiftContext,
    LiftPerformance,
    LiftPlan,
    LiftProgramContext,
    LiftSummary,
    ProgramWeek,
    ProgramWeekContext,
    ProgramWeekPlan,
)


class FiveThreeOneProgram(StrengthCalculator):
    def __init__(
        self,
        lift_program_contexts: dict[Lift, LiftProgramContext],
        program_week_contexts: dict[ProgramWeek, ProgramWeekContext],
        bodyweight: float,
        zero_weight_strictness: float = 1.0,
        n_sets: int = 3,
    ):
        super().__init__(
            lift_program_contexts=lift_program_contexts,
            bodyweight=bodyweight,
            zero_weight_strictness=zero_weight_strictness,
        )
        self.program_week_contexts = program_week_contexts
        self.n_sets = n_sets

    def get_lift_summaries(self) -> list[LiftSummary]:
        return [
            LiftSummary(
                lift_context=lift_program_context.lift_context,
                training_max=self.get_training_max(lift_program_context.lift_context),
            )
            for lift_program_context in self.lift_program_contexts.values()
        ]

    def get_program_week_plans(self) -> list[ProgramWeekPlan]:
        week_order = [
            ProgramWeek.FIVE,
            ProgramWeek.THREE,
            ProgramWeek.ONE,
            ProgramWeek.DELOAD,
        ]
        week_plans = []

        for program_week in week_order:
            if program_week not in self.program_week_contexts:
                continue

            lift_plans = [
                LiftPlan(
                    lift_context=lift_program_context.lift_context,
                    performances=self._get_lift_performance(
                        lift_program_context.lift_context, program_week
                    ),
                )
                for lift_program_context in self.lift_program_contexts.values()
            ]
            week_plans.append(
                ProgramWeekPlan(program_week=program_week, lift_plans=lift_plans)
            )

        return week_plans

    def generate_program_report(self) -> str:
        from core.report_formatters import format_program_report

        return format_program_report(self)

    def _get_lift_performance(
        self, lift_context: LiftContext, program_week: ProgramWeek
    ) -> list[LiftPerformance]:
        training_max = self.get_training_max(lift_context, apply_floor=False)
        week_context = self.program_week_contexts[program_week]

        if len(week_context.scaling_factors) != self.n_sets:
            raise ValueError(
                f"Expected {self.n_sets} scaling factors for program week {program_week}, got {len(week_context.scaling_factors)}"
            )

        performances = []
        for index in range(self.n_sets):
            scaling_factor = week_context.scaling_factors[index]
            target_reps = week_context.reps_per_set[index]
            raw_weight = self.get_scaled_weight(
                lift=lift_context.lift,
                base_weight=training_max,
                factor=scaling_factor,
                apply_floor=False,
            )

            if raw_weight < 0:
                weight = 0.0
                reps = self.get_zero_weight_reps(
                    lift=lift_context.lift,
                    raw_weight=raw_weight,
                    target_reps=target_reps,
                )
            else:
                weight = lift_context.lift.round_weight(raw_weight)
                reps = target_reps

            performances.append(
                LiftPerformance(lift=lift_context.lift, weight=weight, reps=reps)
            )

        return performances


class CompetitionAttemptPlanner(StrengthCalculator):
    def __init__(
        self,
        lift_program_contexts: dict[Lift, LiftProgramContext],
        bodyweight: float,
        attempt_factors: list[float],
        zero_weight_strictness: float = 1.0,
    ):
        super().__init__(
            lift_program_contexts=lift_program_contexts,
            bodyweight=bodyweight,
            zero_weight_strictness=zero_weight_strictness,
        )
        self.attempt_factors = attempt_factors

    def get_attempt_plans(self) -> list[CompetitionAttemptPlan]:
        return [
            CompetitionAttemptPlan(
                lift_context=lift_program_context.lift_context,
                attempts=self._get_attempts(lift_program_context.lift_context),
            )
            for lift_program_context in self.lift_program_contexts.values()
        ]

    def generate_attempt_report(self) -> str:
        from core.report_formatters import format_attempt_report

        return format_attempt_report(self)

    def _get_attempts(self, lift_context: LiftContext) -> list[CompetitionAttempt]:
        attempts = []

        for attempt_number, attempt_factor in enumerate(self.attempt_factors, start=1):
            weight = self.get_scaled_weight(
                lift=lift_context.lift,
                base_weight=lift_context.one_rep_max,
                factor=attempt_factor,
            )
            attempts.append(
                CompetitionAttempt(
                    lift=lift_context.lift,
                    attempt_number=attempt_number,
                    weight=lift_context.lift.round_weight(weight),
                )
            )

        return attempts
