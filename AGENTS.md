
You are a senior Python web engineer reviewing an **existing FastAPI + Jinja2 project**.

────────────────────────────────────────────────────────────────────────
🎯  GOAL
Introduce a reusable **server-side component pipeline** (token → HTML) as
described below, while **minimising churn** in the current codebase.
Implement a single demo component called **emoji**.

────────────────────────────────────────────────────────────────────────
📁  DELIVERABLE FORMAT
➊ Output a series of **unified diffs** (`---`, `+++`, `@@`) for every file
   that must be *modified*.
➋ For *new* files, prefix with `# NEW FILE: path/to/file.py` followed by full
   contents.
➌ For *binary* or large static assets (SVGs), output a stub line  
   `# ADD ASSET: static/emoji/thumbs_up.svg (any 24×24 placeholder SVG)`.
➍ End with a **checklist** of manual steps the maintainer must run
   (e.g. `poetry add bleach pydantic`, `pytest`).

*Do **not** re-emit unchanged files; diffs only.*

────────────────────────────────────────────────────────────────────────
🔧  REQUIRED CODE CHANGES

1. **components.py** *(new)* – registry, `@component` decorator, `emoji`
   component.
2. **token_expander.py** *(new)* – `expand_tokens` with:
   • Regex tokenisation  
   • Pydantic param validation  
   • `bleach.clean()` allow-list sanitiser  
   • Exception handling → returns `<code>⚠ …</code>` snippets.
3. **app.py** *(patch)*  
   • Mount `StaticFiles(directory="static", …)` at `/static` *if not present*.  
   • Import `expand_tokens` and apply it in the chat endpoint *before*
     rendering the template.
4. **templates/chat_page.html** *(patch)* – ensure it prints the HTML already
   expanded by the backend (avoid double-escaping).
5. **pyproject.toml / requirements.txt** *(patch)* – add:
   `bleach`, `pydantic`, `markupsafe` (if not already present).
6. **static/emoji/thumbs_up.svg** *(new asset)* – placeholder SVG.
7. **tests/test_components.py** *(new)* – three pytest cases:  
   ✓ Happy path (`thumbs_up`)  
   ✓ Unknown component  
   ✓ Schema failure (`size=9999`).

────────────────────────────────────────────────────────────────────────
🛠  CODING RULES
* Keep Python ≥3.12 compatibility.  
* Do **NOT** break existing routes, models, or business logic.  
* Respect existing lint/format settings (PEP 8 by default).  
* All new functions require concise docstrings.  
* Use logging instead of print.

────────────────────────────────────────────────────────────────────────
🎓  REFERENCE SPEC (abbreviated)

Token example:
```

\[\[component\:emoji name=thumbs\_up size=32]]

````
`EmojiParams` schema:
```python
class EmojiParams(BaseModel):
    name: str  = Field(pattern=r"^[a-z0-9_]+$")
    size: int  = Field(24, ge=8, le=256)
````

Renderer output (raw str, sanitised later):

```html
<img src="/static/emoji/{name}.svg" alt=":{name}:" width="{size}" height="{size}"
     class="inline-block align-middle"/>
```

Allowed HTML after `bleach.clean()`:

* Tags: `img`
* Attrs: `src`, `alt`, `width`, `height`, `class`

────────────────────────────────────────────────────────────────────────
✅  CHECKLIST AT THE END OF YOUR ANSWER

* [ ] Dependencies added
* [ ] Static asset copied
* [ ] `pytest -q` passes
* [ ] Server still starts: `uvicorn app:app`

────────────────────────────────────────────────────────────────────────

### ⚠  IMPORTANT

*Emit ONLY diffs and new-file blocks plus the final checklist—
no extra narrative, no execution instructions.*
────────────────────────────────────────────────────────────────────────
