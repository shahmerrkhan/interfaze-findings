# Interfaze findings

Tested Oct 12, 2026 using the playground and the API (model interfaze-1). Everything here is from a small number of runs on one machine, so treat it as a lead, not a benchmark.

## Reproduce the detection test

1. `pip install requests`
2. `export INTERFAZE_API_KEY=your_key`
3. Put any photo next to the scripts as `cat.png`
4. `python3 test_cache.py` (5 identical Run Task object detection requests with `x-interfaze-bypass-cache: true`)
5. `python3 compare.py` (compares the 5 responses)

My raw responses are in `run_1.json` to `run_5.json`.

## 1. Object detection isn't repeatable with the cache bypassed

Same photo, same prompt, 5 runs gave 5 different object lists. Only 3 labels (arm, pants, person) appeared in every run. "cat" appeared in 4 of 5 and was split into cat_0 and cat_1 in the other. Output size ranged from 766 to 1,095 tokens. For the labels that did repeat, boxes stayed within 1 to 2 pixels, except one "person" box that was 17 pixels wider.

## 2. OCR drops accents on clear text

On two synthetic resume PDFs (one with a text layer, one scanned), "Español" and "Français" came back as "Espanol" and "Francais", while "Café Lumière", "Zürich" and "Álvarez" came through correctly. The PDFs are fake and I'm happy to share them.

## 3. Detection has no confidence field, and requested ones looked unstable

Run Task detection returns a label, bounds and a polygon, with no confidence. The interfaze-1-lite announcement says confidence comes back on every run, and the OCR docs show it. When I asked for confidence through a JSON schema, the same image got a top score of 0.89 in one run and 0.99 in the next, and in both runs the scores fell in the order the objects were listed.

## 4. Cache behavior is hard to see

The cache is on by default. Repeating a playground request was fast with almost no output tokens (2.9s and 14 tokens, versus 7.7s and 1,356 the first time), which looks like a cache hit. The `vcache` field from the docs came back empty in my API responses, so I could only judge from timing and token counts.

## Suggested fixes (guesses from the outside)

- **Detection:** constrain the label set or make the labeling step deterministic, or return detector-only output in Run Task.
- **Accents:** check whether the OCR post-processing normalizes text in a way that strips combining marks, and compare raw and final output.
- **Confidence:** return detector confidence in Run Task output, or return null instead of model-written numbers, and document which tasks return it.
- **Cache:** show a cache-hit indicator in the playground and always include `vcache` in responses.

Shahmeer Khan, https://www.linkedin.com/in/shahmerrkhann/
