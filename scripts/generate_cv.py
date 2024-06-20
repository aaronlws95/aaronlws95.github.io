import re
import subprocess

if __name__ == "__main__":
    with open("cv/cv.html", "r") as f:
        cv_html_str = f.read()

    # Update CV displayed on website
    body_content = re.search(r"<body>(.*?)</body>", cv_html_str, re.DOTALL)
    with open("cv/cv_body.js", "w") as f:
        f.write(f"document.write(`<body>\n{body_content.group(1)}\n</body>`)")

    # Generate CV PDF version
    subprocess.run(
        [
            "wkhtmltopdf",
            "--enable-local-file-access",
            "cv/cv.html",
            "cv/aaronlow_cv.pdf",
        ],
        shell=False,
    )

    print("--- Successfully generated CV ---")