# Future Features

Ideas for later, **not** an implementation queue. Each item should be
scoped and approved individually before work starts — nothing here is
authorized for implementation as-is.

- Smoothing (e.g. rolling average / Savitzky-Golay) of raw heat flow.
- Baseline correction.
- Peak detection on the heat-flow curve.
- Acceleration/deceleration period identification.
- Onset / end-of-hydration-peak detection.
- Multiple-sample comparison (overlaying several runs).
- Excel export of processed data (in addition to the existing CSV export).
- PDF report generation.
- Educational tab (isothermal calorimetry background, trapezoidal rule
  walkthrough, references) — part of the original vision in
  [`product_spec.md`](product_spec.md), deferred from the MVP.
- ASTM/reference section (e.g. ASTM C1702) in-app.
- Better browser-level UI tests (the current smoke test exercises the
  processing/summary pipeline through the same call path the UI uses, but
  does not drive an actual browser file-upload interaction end to end).
