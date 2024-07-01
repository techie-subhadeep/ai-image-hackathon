import re
import requests

img_dir = "scraped_images"
img_counter = 188
for i in [
    3,
]:
    with open(f"scarp_resources/source{str(i).zfill(2)}.txt", "rb") as f:
        html_source = f.read().decode("utf-8")

    with open(f"scarp_resources/source{str(i).zfill(2)}.regex.txt", "rb") as f:
        regex_str = f.read().decode("utf-8")

    print(len(re.findall(regex_str, html_source)))
    for url in re.findall(regex_str, html_source):
        print(url)
        resp = requests.get(
            url,
            headers={
                "user-agent": r"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
            },
        )
        with open(f"{img_dir}/{str(img_counter).zfill(3)}.jpg", mode="wb") as img_file:
            img_file.write(resp.content)
            img_counter += 1
