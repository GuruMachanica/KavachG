import urllib.request
import os
import json

base_url = "https://kavachg.onrender.com"
print(f"Testing live models on {base_url} ...")

sample_img = "Frontend/assets/cctv_factory_1.jpg"
if os.path.exists(sample_img):
    with open(sample_img, "rb") as f:
        file_bytes = f.read()

    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    part_header = (
        f"--{boundary}\r\n"
        'Content-Disposition: form-data; name="file"; filename="frame.jpg"\r\n'
        "Content-Type: image/jpeg\r\n\r\n"
    ).encode("utf-8")
    part_footer = f"\r\n--{boundary}--\r\n".encode("utf-8")
    body = part_header + file_bytes + part_footer

    for ep in ["/detect/ppe/", "/detect/pose/", "/detect/fire-smoke/", "/detect/fall/"]:
        try:
            req = urllib.request.Request(
                f"{base_url}{ep}",
                data=body,
                headers={
                    "Content-Type": f"multipart/form-data; boundary={boundary}",
                    "User-Agent": "Mozilla/5.0"
                }
            )
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                print(f"{ep:25} -> Status: {resp.status} OK | Detections: {len(data.get('detections', []))}")
        except Exception as e:
            print(f"{ep:25} -> FAILED: {e}")

for stream_ep in ["/live/ppe", "/live/pose", "/live/fire-smoke", "/live/fall"]:
    try:
        req = urllib.request.Request(f"{base_url}{stream_ep}", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=12) as resp:
            chunk = resp.read(1024)
            print(f"{stream_ep:25} -> Stream Status: {resp.status} OK (received {len(chunk)} bytes)")
    except Exception as e:
        print(f"{stream_ep:25} -> Stream Failed: {e}")
