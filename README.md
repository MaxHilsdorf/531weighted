## 531weighted

531weighted is a hobby project for streetlifting and weighted calisthenics athletes.

It helps with two things:

- generating a 5/3/1-style training cycle
- suggesting competition attempts

You can use it either as a local CLI tool or as a Streamlit web app.

### Hosted app

The app is hosted at [https://531weighted.streamlit.app](https://531weighted.streamlit.app).

### Local usage

Shared defaults live in [config.yaml](config.yaml).

Private personal numbers can go in [config.yaml.local](config.yaml.local). This file is optional and gitignored. Use [config.yaml.template](config.yaml.template) as a starting point.

The app loads [config.yaml](config.yaml) first, then applies [config.yaml.local](config.yaml.local) if it exists.

Run the CLI:

```bash
uv run src/main.py
```

Run the Streamlit app locally:

```bash
uv run streamlit run streamlit_app.py
```

The local web app will be available at `http://localhost:8501`.

### Dev commands

```bash
make test
make format
make lint
```

Optional Docker workflow:

```bash
make build
make run
```

### Disclaimer: AI Usage
A significant portion of the source code in this repository was AI generated and not all code was reviewed by a human. Mindful usage is adviced.

### Notes
- `bodyweight_coefficient` controls how much bodyweight counts toward a lift
- `rounding_increment` controls the jump size for that lift
- `zero_weight_strictness` controls how hard the app reduces reps when a computed load drops below `0kg`
