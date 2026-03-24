from core.models import Lift, LiftContext, LiftProgramContext


class StrengthCalculator:
    def __init__(
        self,
        lift_program_contexts: dict[Lift, LiftProgramContext],
        bodyweight: float,
        zero_weight_strictness: float = 1.0,
    ):
        self.lift_program_contexts = lift_program_contexts
        self.bodyweight = bodyweight
        self.zero_weight_strictness = min(max(zero_weight_strictness, 0.0), 1.0)

    def get_training_max(
        self, lift_context: LiftContext, apply_floor: bool = True
    ) -> float:
        training_max_factor = self.lift_program_contexts[
            lift_context.lift
        ].training_max_factor
        return self.get_scaled_weight(
            lift=lift_context.lift,
            base_weight=lift_context.one_rep_max,
            factor=training_max_factor,
            apply_floor=apply_floor,
        )

    def get_scaled_weight(
        self, lift: Lift, base_weight: float, factor: float, apply_floor: bool = True
    ) -> float:
        bodyweight_offset = lift.bodyweight_offset(self.bodyweight)
        scaled_weight = ((base_weight + bodyweight_offset) * factor) - bodyweight_offset
        if apply_floor:
            return max(0.0, scaled_weight)

        return scaled_weight

    def get_zero_weight_reps(
        self, lift: Lift, raw_weight: float, target_reps: int
    ) -> int:
        actual_total_load = lift.bodyweight_offset(self.bodyweight)
        if actual_total_load <= 0:
            return 1

        target_total_load = actual_total_load + raw_weight
        equivalent_reps = 30 * (
            (target_total_load * (1 + (target_reps / 30))) / actual_total_load - 1
        )
        adjusted_reps = target_reps - (
            self.zero_weight_strictness * (target_reps - equivalent_reps)
        )
        return max(1, min(target_reps, round(adjusted_reps)))
