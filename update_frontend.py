import os
import re

# Update index.html
with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace Reset Project button with Back to Projects
back_btn = """<button id="backBtn" class="header-btn" title="Back to Projects" style="color: #fff; border: 1px solid #555; border-radius: 6px; padding: 4px 10px; cursor: pointer; background: transparent; display: flex; align-items: center; gap: 5px; font-weight: 500;" onclick="window.location.href='/'">
                <i class="ph ph-arrow-left"></i> Projects
            </button>"""
html = re.sub(r'<button id="newProjectBtn".*?</script>', back_btn, html, flags=re.DOTALL)

# Update Form Actions and Links
html = re.sub(r'action="/detect"', r'action="/project/{{ project_name }}/detect"', html)
html = re.sub(r'href="/export_dataset"', r'href="/project/{{ project_name }}/export_dataset"', html)
html = re.sub(r'href=\'/image/', r'href=\'/project/{{ project_name }}/image/', html)

# Add PROJECT_NAME to JS
html = re.sub(r'<script>\s*const detections =', r'<script>\n                const PROJECT_NAME = "{{ project_name }}";\n                const detections =', html)

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

# Update app.js
with open('static/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

js = js.replace('fetch(\n        "/save_labels",', 'fetch(\n        "/project/" + PROJECT_NAME + "/save_labels",')
js = js.replace('"/image/" +', '"/project/" + PROJECT_NAME + "/image/" +')
js = js.replace('fetch("/progress")', 'fetch("/project/" + PROJECT_NAME + "/progress")')
js = js.replace('fetch("/bulk_rename", {', 'fetch("/project/" + PROJECT_NAME + "/bulk_rename", {')

with open('static/app.js', 'w', encoding='utf-8') as f:
    f.write(js)
