## 531weighted

Small personal tool to generate a 5/3/1 training cycle and competition attempt suggestions as terminal output.

### How it works

1. Edit [config.yaml](/Users/max/Projects/street_lifting/531calc/config.yaml) with the shared, public defaults for your setup: lift definitions, program weeks, global attempt factors, and any non-sensitive defaults.
2. Optionally create [config.yaml.local](/Users/max/Projects/street_lifting/531calc/config.yaml.local) for personal overrides like your current bodyweight, 1RMs, or stricter local tuning. This file is gitignored.
3. Run the script:

```bash
uv run src/main.py
```

4. Copy the printed output into your notes app.

The output includes:

- a compact competition attempt recommendation block
- a compact 5/3/1 cycle block

The CLI command loads [config.yaml](/Users/max/Projects/street_lifting/531calc/config.yaml) first and then applies [config.yaml.local](/Users/max/Projects/street_lifting/531calc/config.yaml.local) on top when it exists. Lift overrides can be matched by `abbreviation` or `name`.

### Streamlit App

You can also run the web app locally:

```bash
uv run streamlit run app/streamlit_app.py
```

The Streamlit app uses sensible defaults and lets you enter bodyweight and 1RMs directly in the browser.

### Docker

Build the container image:

```bash
make build
```

Run the Streamlit app in Docker:

```bash
make run
```

Run the test suite:

```bash
make test
```

Format the codebase:

```bash
make format
```

Run lint checks:

```bash
make lint
```

The app will be available at `http://localhost:8501`.

### Config notes

- Keep shared structure in [config.yaml](/Users/max/Projects/street_lifting/531calc/config.yaml) and private numbers in [config.yaml.local](/Users/max/Projects/street_lifting/531calc/config.yaml.local).
- `bodyweight` is used for lifts that depend on bodyweight.
- `zero_weight_strictness` controls how aggressively reps are reduced globally when a set falls below `0kg`.
- `competition_attempt_factors` defines the fixed percentage factors used for 1st, 2nd, and 3rd attempt recommendations.
- `bodyweight_coefficient` controls how much bodyweight contributes to the calculation.
- `rounding_increment` controls the load jumps for each lift directly.
- Use `1.0` for fully bodyweight-dependent lifts and `0.0` for standard external-weight lifts.
- Use `1.0` for the full automatic reduction and smaller values like `0.5` for a softer adjustment.
- Use `1.25` for lifts where you can add small plates and `2.5` for barbell lifts like squat.
- If a computed set falls below `0kg`, the tool prints `0kg` and automatically reduces reps, with a minimum of `1` rep.

### Requirements

- Python 3.12+
- `PyYAML`

If you are using `uv`, dependencies will be installed automatically when needed.
