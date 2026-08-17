import re
import subprocess
import sys
import os

def check_html_script(filepath):
    print(f"Checking JS syntax in {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    scripts = re.findall(r'<script.*?>(.*?)</script>', content, re.DOTALL)
    for idx, s in enumerate(scripts):
        # Remove jinja template tags for syntax checking
        cleaned = re.sub(r'\{\{.*?\}\}', '"jinja_var"', s)
        cleaned = re.sub(r'\{%.*?%\}', '', cleaned)

        temp_js = os.path.join(os.path.dirname(filepath), f"temp_test_{idx}.js")
        with open(temp_js, 'w', encoding='utf-8') as tf:
            tf.write(cleaned)

        try:
            res = subprocess.run(['node', '--check', temp_js], capture_output=True, text=True)
            if res.returncode != 0:
                print(f"ERROR in script #{idx} of {filepath}:")
                print(res.stderr)
                os.remove(temp_js)
                sys.exit(1)
        except Exception as e:
            print("node --check failed:", e)
        finally:
            if os.path.exists(temp_js):
                os.remove(temp_js)

    print(f"ALL JS SCRIPTS IN {filepath} ARE VALID!")

if __name__ == '__main__':
    check_html_script('d:/dev/workspace1/pawstar/templates/upload.html')
    check_html_script('d:/dev/workspace1/pawstar/templates/m_upload.html')
