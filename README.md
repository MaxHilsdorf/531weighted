## 531calc

Small personal tool to generate a 5/3/1 training cycle as terminal output.

### How it works

1. Edit [config.yaml](/Users/max/Projects/street_lifting/531calc/config.yaml) with your bodyweight, global zero-weight strictness, lifts, 1RMs, bodyweight coefficients, training max factors, and week setup.
2. Run the script:

```bash
uv run src/main.py
```

3. Copy the printed output into your notes app.

### Config notes

- `bodyweight` is used for lifts that depend on bodyweight.
- `zero_weight_strictness` controls how aggressively reps are reduced globally when a set falls below `0kg`.
- `bodyweight_coefficient` controls how much bodyweight contributes to the calculation.
- Use `1.0` for fully bodyweight-dependent lifts and `0.0` for standard external-weight lifts.
- Use `1.0` for the full automatic reduction and smaller values like `0.5` for a softer adjustment.
- Lifts with a coefficient above `0` are rounded to the nearest `1.25kg`.
- Lifts with a coefficient of `0` are rounded to the nearest `2.5kg`.
- If a computed set falls below `0kg`, the tool prints `0kg` and automatically reduces reps, with a minimum of `1` rep.

### Requirements

- Python 3.12+
- `PyYAML`

If you are using `uv`, dependencies will be installed automatically when needed.
