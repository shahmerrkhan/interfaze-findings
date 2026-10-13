import os, json, time, base64, requests

API_KEY = os.environ["INTERFAZE_API_KEY"]
IMAGE_PATH = "cat.png"  # change to the ORIGINAL cat photo, not the screenshot
URL = "https://api.interfaze.ai/v1/chat/completions"

with open(IMAGE_PATH, "rb") as f:
    b64 = base64.b64encode(f.read()).decode()

body = {
    "model": "interfaze-1",
    "messages": [
        {"role": "system", "content": "<task>object_detection</task>"},
        {"role": "user", "content": [
            {"type": "text", "text": "Detect all objects in this image."},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
        ]},
    ],
}
headers = {"Authorization": f"Bearer {API_KEY}", "x-interfaze-bypass-cache": "true"}

parsed_runs = []
for i in range(1, 6):
    start = time.time()
    r = requests.post(URL, headers=headers, json=body, timeout=120)
    elapsed = time.time() - start
    if r.status_code != 200:
        print(f"run {i} failed: {r.status_code} {r.text[:300]}")
        break
    data = r.json()
    with open(f"run_{i}.json", "w") as f:
        json.dump(data, f)
    usage = data.get("usage", {})
    print(f"run {i}: {elapsed:.1f}s, in {usage.get('prompt_tokens')}, out {usage.get('completion_tokens')}, vcache {data.get('vcache')}")
    content = data["choices"][0]["message"]["content"]
    try:
        parsed_runs.append(json.loads(content))
    except Exception:
        parsed_runs.append(content)

def boxes(p):
    return [(o["label"], json.dumps(o["bounds"], sort_keys=True))
            for o in p["result"]["detected_objects"]]

if len(parsed_runs) > 1:
    base = parsed_runs[0]
    for i, p in enumerate(parsed_runs[1:], start=2):
        try:
            b1, b2 = boxes(base), boxes(p)
            l1, l2 = {x[0] for x in b1}, {x[0] for x in b2}
            print(f"run {i} vs run 1: full match {p == base}, same boxes {b1 == b2}, "
                  f"labels lost {sorted(l1 - l2)}, labels gained {sorted(l2 - l1)}")
        except Exception as e:
            print(f"run {i}: could not compare ({e})")
