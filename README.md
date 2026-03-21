## 531calc

Small personal tool to generate a 5/3/1 training cycle as terminal output.

### How it works

1. Edit [config.yaml](/Users/max/Projects/street_lifting/531calc/config.yaml) with your bodyweight, lifts, 1RMs, training max factors, and week setup.
2. Run the script:

```bash
uv run src/main.py
```

3. Copy the printed output into your notes app.

### Config notes

- `bodyweight` is used for bodyweight lift calculations.
- `is_bodyweight: true` uses bodyweight-specific training max and set calculations.
- Bodyweight lifts are rounded to the nearest `1.25kg`.
- Non-bodyweight lifts are rounded to the nearest `2.5kg`.

### Requirements

- Python 3.12+
- `PyYAML`

If you are using `uv`, dependencies will be installed automatically when needed.
