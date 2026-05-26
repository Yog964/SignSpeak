# ISL SignSpeak Database

This folder contains the structured landmark CSV datasets used for ISL SignSpeak.

## Layout

- `AB`, `DC`, `JB`, `PB`, `SB`, `VB`: original contributor-wise datasets.
- `Structured`: category-wise datasets copied into a single database location for easier training and review.
- `dataset_manifest.csv`: generated index of every CSV in this database folder, including label, path, and sample count.

## CSV Format

Each CSV stores MediaPipe landmark features with columns for `x_*`, `y_*`, `z_*`, `visibility_*`, and the final `action` label column.
