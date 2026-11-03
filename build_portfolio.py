"""Deep LinkedIn Activity Tracer, Visual Portfolio Builder & HKUST CS Recommendation Generator.

Uses Gemini Computer Use (`types.ComputerUse`) combined with custom portfolio tools
(`save_evidence_screenshot`, `extract_and_save_page_images`, `record_portfolio_item`)
to autonomously navigate LinkedIn sub-pages and activity posts, download images/screenshots,
compile a rich visual portfolio (`portfolio/portfolio.html` & `portfolio/portfolio.md`),
and generate an evidence-backed HKUST Computer Science recommendation letter.
"""

import argparse
from datetime import datetime
import html
import json
from pathlib import Path
import re
import sys
import time
from typing import Any, Dict, List
import urllib.request

from google.auth import exceptions as auth_exceptions
from google.genai import types
from google.genai.types import Content, Part
from playwright.sync_api import sync_playwright
import termcolor

import main as cu_main

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

DEFAULT_PROFILE_URL = "https://www.linkedin.com/in/hiu-tung-cheung-esther-085656387/"
DEFAULT_PORTFOLIO_DIR = "portfolio"


def slugify(text: str) -> str:
    """Create a filesystem-safe slug from text."""
    slug = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fff_-]+", "_", text.strip())
    return slug.strip("_")[:60] or "item"


class PortfolioStore:
    """Manages saved screenshots, downloaded activity images, and structured findings."""

    def __init__(self, base_dir: str = DEFAULT_PORTFOLIO_DIR) -> None:
        self.base_path = Path(base_dir).resolve()
        self.screenshots_dir = self.base_path / "screenshots"
        self.images_dir = self.base_path / "images"
        self.manifest_path = self.base_path / "manifest.json"

        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        self.images_dir.mkdir(parents=True, exist_ok=True)

        if self.manifest_path.exists():
            try:
                self.data = json.loads(self.manifest_path.read_text(encoding="utf-8"))
            except Exception:
                self.data = {"screenshots": [], "images": [], "items": []}
        else:
            self.data = {"screenshots": [], "images": [], "items": []}

    def save_manifest(self) -> None:
        self.manifest_path.write_text(
            json.dumps(self.data, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    def save_evidence_screenshot(
        self, page, category: str, title: str, description: str
    ) -> Dict[str, Any]:
        """Save a PNG screenshot of the current browser viewport to ./portfolio/screenshots/."""
        idx = len(self.data["screenshots"]) + 1
        filename = f"{idx:02d}_{slugify(category)}_{slugify(title)}.png"
        filepath = self.screenshots_dir / filename
        page.screenshot(path=str(filepath), type="png")

        rel_path = f"screenshots/{filename}"
        entry = {
            "id": idx,
            "category": category,
            "title": title,
            "description": description,
            "url": page.url,
            "path": rel_path,
            "timestamp": datetime.now().isoformat(),
        }
        self.data["screenshots"].append(entry)
        self.save_manifest()
        termcolor.cprint(f"    [Portfolio] Saved screenshot -> {rel_path}", color="green")
        return {"status": "saved", "path": rel_path, "title": title}

    def extract_and_save_page_images(
        self, page, category: str, context_note: str
    ) -> Dict[str, Any]:
        """Extract visible content images (post photos, certificates, project media) and download them."""
        js_extract = """
        () => {
            const imgs = Array.from(document.querySelectorAll('img'));
            const results = [];
            for (const img of imgs) {
                const rect = img.getBoundingClientRect();
                const src = img.currentSrc || img.src || '';
                if (!src || src.startsWith('data:')) continue;
                // Filter out tiny icons/avatars, keep meaningful content images
                if (rect.width < 120 || rect.height < 90) continue;
                if (rect.bottom < 0 || rect.top > window.innerHeight * 1.5) continue;
                if (src.includes('profile-displayphoto') || src.includes('ghost-person') || src.includes('company-logo_100_100')) continue;
                results.push({
                    src: src,
                    alt: (img.alt || '').trim(),
                    width: Math.round(rect.width),
                    height: Math.round(rect.height)
                });
            }
            return results;
        }
        """
        try:
            candidates = page.evaluate(js_extract)
        except Exception as e:
            return {"status": "error", "error": str(e)}

        saved_files = []
        existing_urls = {img["src"] for img in self.data["images"]}

        for item in candidates[:8]:
            src = item["src"]
            if src in existing_urls:
                continue
            idx = len(self.data["images"]) + 1
            filename = f"img_{idx:02d}_{slugify(category)}.jpg"
            filepath = self.images_dir / filename
            try:
                req = urllib.request.Request(
                    src,
                    headers={
                        "User-Agent": (
                            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
                        )
                    },
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    filepath.write_bytes(resp.read())

                rel_path = f"images/{filename}"
                entry = {
                    "id": idx,
                    "category": category,
                    "context_note": context_note,
                    "alt": item.get("alt", ""),
                    "src": src,
                    "page_url": page.url,
                    "path": rel_path,
                    "width": item["width"],
                    "height": item["height"],
                    "timestamp": datetime.now().isoformat(),
                }
                self.data["images"].append(entry)
                existing_urls.add(src)
                saved_files.append(rel_path)
                termcolor.cprint(f"    [Portfolio] Downloaded image -> {rel_path}", color="cyan")
            except Exception as dl_err:
                print(f"    [Portfolio] Could not download {src[:60]}...: {dl_err}")

        self.save_manifest()
        return {
            "status": "ok",
            "downloaded_count": len(saved_files),
            "files": saved_files,
        }

    def record_portfolio_item(
        self,
        section: str,
        title: str,
        date: str,
        organization: str,
        details: str,
        relevance_to_hkust_cs: str,
    ) -> Dict[str, Any]:
        """Record a structured achievement, post, project, award, or certification."""
        entry = {
            "id": len(self.data["items"]) + 1,
            "section": section,
            "title": title,
            "date": date,
            "organization": organization,
            "details": details,
            "relevance_to_hkust_cs": relevance_to_hkust_cs,
            "timestamp": datetime.now().isoformat(),
        }
        self.data["items"].append(entry)
        self.save_manifest()
        termcolor.cprint(
            f"    [Portfolio] Recorded item [{section}]: {title}", color="magenta"
        )
        return {"status": "recorded", "item_id": entry["id"]}


# Tool declaration functions exposed to Gemini
def save_evidence_screenshot(category: str, title: str, description: str) -> dict:
    """Saves a screenshot of the current browser view as visual evidence in the student's portfolio.

    Args:
        category: Category of evidence (e.g. 'activity_post', 'conference_talk', 'scholarship_award', 'certification', 'leadership', 'project').
        title: Short descriptive title for this screenshot.
        description: Detailed explanation of what is shown in this screenshot and why it matters.
    """
    return {"status": "saved"}


def extract_and_save_page_images(category: str, context_note: str) -> dict:
    """Downloads visible content photos/images from the current page (such as event photos, conference slides, project screenshots, or certificates) into ./portfolio/images/.

    Args:
        category: Category tag (e.g. 'pycon_hk', 'aws_summit', 'hkoscon', 'microsoft_vtc', 'scholarship', 'certifications', 'activity').
        context_note: Context describing what posts or achievements these images belong to.
    """
    return {"status": "ok"}


def record_portfolio_item(
    section: str,
    title: str,
    date: str,
    organization: str,
    details: str,
    relevance_to_hkust_cs: str,
) -> dict:
    """Records a detailed achievement, activity post, conference presentation, project, scholarship, or certification into the structured portfolio manifest.

    Args:
        section: Section name ('Conference & Research', 'AI & Cloud Projects', 'Honors & Scholarships', 'Community Leadership', 'Certifications', 'Academic Background').
        title: Title of the activity, post, award, talk, or certification.
        date: Date or timeframe (e.g. 'Oct 2026', 'Jun 2026', '2025 - Present').
        organization: Issuing organization, conference, or institution (e.g. 'PyCon Hong Kong', 'AWS Summit HK', 'HKOSCon', 'The Cathay Group', 'HKIIT').
        details: Full verbatim or comprehensive details traced from the post or sub-page, including technical stack, teammates/mentors, and outcomes.
        relevance_to_hkust_cs: How this specific item demonstrates readiness for HKUST's Computer Science degree program.
    """
    return {"status": "recorded"}


def run_exploration_stage(
    client,
    page,
    store: PortfolioStore,
    stage_name: str,
    target_url: str,
    stage_prompt: str,
    max_iterations: int,
    model: str,
    screen_width: int,
    screen_height: int,
) -> str:
    """Run a Gemini Computer Use exploration stage on a specific LinkedIn URL."""
    termcolor.cprint(f"\n==========================================", color="cyan")
    termcolor.cprint(f"STAGE: {stage_name}", color="cyan")
    termcolor.cprint(f"URL:   {target_url}", color="cyan")
    termcolor.cprint(f"==========================================", color="cyan")

    page.goto(target_url)
    try:
        page.wait_for_load_state(timeout=6000)
    except Exception:
        pass
    time.sleep(2)

    config = types.GenerateContentConfig(
        tools=[
            types.Tool(
                computer_use=types.ComputerUse(
                    environment=types.Environment.ENVIRONMENT_BROWSER,
                    enable_prompt_injection_detection=True,
                )
            ),
            types.Tool(
                function_declarations=[
                    types.FunctionDeclaration.from_callable(
                        client=client, callable=save_evidence_screenshot
                    ),
                    types.FunctionDeclaration.from_callable(
                        client=client, callable=extract_and_save_page_images
                    ),
                    types.FunctionDeclaration.from_callable(
                        client=client, callable=record_portfolio_item
                    ),
                ]
            ),
        ]
    )

    initial_screenshot = page.screenshot(type="png")
    contents: List[Content] = [
        Content(
            role="user",
            parts=[
                Part(text=stage_prompt),
                Part.from_bytes(data=initial_screenshot, mime_type="image/png"),
            ],
        )
    ]

    stage_summary = ""
    for iteration in range(max_iterations):
        print(f"\n--- [{stage_name}] Iteration {iteration + 1}/{max_iterations} ---")
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=config,
        )
        candidate = response.candidates[0]
        contents.append(candidate.content)

        if not cu_main.has_function_calls(response):
            stage_summary = response.text or ""
            print(f"[{stage_name}] Completed:\n{stage_summary[:400]}...")
            break

        # Intercept custom portfolio function calls and delegate browser calls to cu_main
        custom_results = []
        browser_calls = []
        for part in candidate.content.parts:
            if hasattr(part, "function_call") and part.function_call:
                fc = part.function_call
                fname = fc.name
                args = dict(fc.args) if fc.args else {}
                if fname == "save_evidence_screenshot":
                    res = store.save_evidence_screenshot(
                        page,
                        category=args.get("category", stage_name),
                        title=args.get("title", "screenshot"),
                        description=args.get("description", ""),
                    )
                    custom_results.append((fname, res))
                elif fname == "extract_and_save_page_images":
                    res = store.extract_and_save_page_images(
                        page,
                        category=args.get("category", stage_name),
                        context_note=args.get("context_note", ""),
                    )
                    custom_results.append((fname, res))
                elif fname == "record_portfolio_item":
                    res = store.record_portfolio_item(
                        section=args.get("section", stage_name),
                        title=args.get("title", ""),
                        date=args.get("date", ""),
                        organization=args.get("organization", ""),
                        details=args.get("details", ""),
                        relevance_to_hkust_cs=args.get("relevance_to_hkust_cs", ""),
                    )
                    custom_results.append((fname, res))
                else:
                    browser_calls.append(part)

        results = list(custom_results)
        if browser_calls:
            # Build a temporary response wrapper containing only browser calls
            temp_resp = types.GenerateContentResponse(
                candidates=[
                    types.Candidate(
                        content=types.Content(role="model", parts=browser_calls)
                    )
                ]
            )
            browser_results = cu_main.execute_function_calls(
                temp_resp, page, screen_width, screen_height
            )
            results.extend(browser_results)

        if not results:
            break

        feedback_content = cu_main.get_function_responses(page, results)
        contents.append(feedback_content)
    else:
        contents.append(
            Content(
                role="user",
                parts=[
                    Part(
                        text="Stop calling tools and summarize all detailed findings gathered in this stage."
                    )
                ],
            )
        )
        final_resp = client.models.generate_content(model=model, contents=contents)
        stage_summary = final_resp.text or ""

    return stage_summary


def generate_portfolio_and_letter(
    client,
    model: str,
    store: PortfolioStore,
    stage_summaries: Dict[str, str],
) -> None:
    """Synthesize the collected evidence, images, and stage notes into portfolio files and the HKUST CS letter."""
    termcolor.cprint(
        "\nSynthesizing Visual Portfolio & Evidence-Backed HKUST CS Recommendation Letter...",
        color="yellow",
    )

    manifest_json = json.dumps(store.data, indent=2, ensure_ascii=False)
    combined_summaries = "\n\n".join(
        f"## Stage: {k}\n{v}" for k, v in stage_summaries.items()
    )

    # 1. Generate deeply detailed HKUST CS Recommendation Letter
    letter_prompt = f"""
You are writing a formal, deeply compelling, evidence-backed academic & mentorship recommendation letter for **Hiu Tung Cheung (Esther / 張曉彤)** for admission to the **Bachelor of Engineering in Computer Science (BEng in CS)** program at **The Hong Kong University of Science and Technology (HKUST)**.

The recommender is **Cyrus Wong (黃俊彥)**, Senior Lecturer in the Department of Information Technology at the Hong Kong Institute of Information Technology (HKIIT) / IVE (Lee Wai Lee), who has taught, mentored, and co-presented with Esther (including at PyCon Hong Kong 2026).

Use ALL the concrete, specific facts, project architectures, conference presentations, scholarships, certifications, and community leadership roles traced from her LinkedIn profile and activity feed below:

### Structured Portfolio Manifest:
{manifest_json}

### Stage Exploration Notes:
{combined_summaries}

### Requirements for the Letter:
1. **No generic filler**: Every paragraph must cite real evidence, exact event names, dates, technical stacks (Kubernetes, GKE, AWS, Azure, Linux/Red Hat, Embodied AI Robotics, Computer Vision attendance verification, etc.), and specific achievements traced from her profile.
2. **Structure**:
   - **Header & Salutation**: Addressed to the Admissions Committee, Department of Computer Science and Engineering (CSE), The Hong Kong University of Science and Technology (HKUST).
   - **Opening & Relationship**: State how long and in what capacity Cyrus Wong has known Esther (as her lecturer in the Higher Diploma in Cloud and Data Centre Administration where she holds a **3.91 / 4.0 CGPA**, project supervisor, and conference co-speaker).
   - **Cloud-Native Systems Engineering & PyCon HK 2026 Research**: Detail our joint work and her presentation at **PyCon Hong Kong 2026** (*「從港域時空到 Kubernetes：將香港遊戲世界化身雲原生學習平台」* / transforming the Hong Kong Zero 3D game environment into an interactive Kubernetes cloud-native learning platform), highlighting her systems programming and container orchestration depth.
   - **Applied AI Innovation (AWS Summit HK, HKOSCon, VTC x Microsoft)**: Detail her work on **Embodied AI Agents controlling physical robots** presented at **AWS Summit Hong Kong**, her **ProvePresent (真出席)** Azure AI anti-proxy attendance system presented at the **Hong Kong Open Source Conference (HKOSCon)**, and her representation of HKIIT demonstrating the **AI Virtual Tutor** for the **VTC & Microsoft Hong Kong partnership**.
   - **Academic Excellence & Competitive Scholarships**: Highlight her **3.91/4.0 CGPA**, her **13 Honors & Awards** (including **The Cathay Group Scholarship 2025/26**, **Lei Foundation Scholarship**, and other competitions/awards found), and her **16 industry certifications/badges** (including Google Kubernetes Engine cost optimization and architecture badges).
   - **Triple Campus Tech Leadership**: Highlight her simultaneous leadership as the **1st AWS Student Builder Group Leader '26**, **Google Developer Group (GDG) on Campus Leader**, and **Red Hat Student Ambassador** at HKIIT, plus her public outreach for AI/Cloud education.
   - **Conclusion**: Strong, unequivocal endorsement for HKUST CSE.

Provide both:
- **Part A**: The complete formal HKUST Computer Science Admission Recommendation Letter (ready to print/sign on institutional letterhead).
- **Part B**: A rich, specific LinkedIn Recommendation (ready to paste into LinkedIn's Recommend box).
"""
    letter_resp = client.models.generate_content(model=model, contents=letter_prompt)
    letter_text = letter_resp.text or ""
    letter_path = store.base_path / "hkust_cs_recommendation_letter.md"
    letter_path.write_text(letter_text, encoding="utf-8")
    termcolor.cprint(
        f"[Portfolio] Saved HKUST CS Recommendation Letter -> {letter_path}",
        color="green",
    )

    # 2. Generate Portfolio Markdown (portfolio/portfolio.md)
    md_lines = [
        "# Student Technical & Leadership Portfolio: Hiu Tung Cheung (Esther / 張曉彤)",
        "",
        "**Target Program**: Bachelor of Engineering in Computer Science, The Hong Kong University of Science and Technology (HKUST)  ",
        "**Current Institution**: Hong Kong Institute of Information Technology (HKIIT) / IVE (Lee Wai Lee)  ",
        "**Current Program**: Higher Diploma in Cloud and Data Centre Administration (**CGPA: 3.91 / 4.0**)  ",
        f"**LinkedIn Profile**: [{DEFAULT_PROFILE_URL}]({DEFAULT_PROFILE_URL})  ",
        "",
        "---",
        "",
        "## 1. Executive Summary & Traced Findings",
        "",
    ]

    for stage_title, summary_text in stage_summaries.items():
        md_lines.append(f"### {stage_title}")
        md_lines.append(summary_text.strip())
        md_lines.append("")

    if store.data["items"]:
        md_lines.append("---")
        md_lines.append("## 2. Structured Portfolio Records")
        md_lines.append("")
        for item in store.data["items"]:
            md_lines.append(
                f"### [{item['section']}] {item['title']} ({item['date']}) — *{item['organization']}*"
            )
            md_lines.append(f"- **Details**: {item['details']}")
            if item.get("relevance_to_hkust_cs"):
                md_lines.append(
                    f"- **Relevance to HKUST CS**: {item['relevance_to_hkust_cs']}"
                )
            md_lines.append("")

    if store.data["images"]:
        md_lines.append("---")
        md_lines.append("## 3. Extracted Activity & Achievement Photos")
        md_lines.append("")
        for img in store.data["images"]:
            caption = img.get("context_note") or img.get("alt") or img["category"]
            md_lines.append(f"### {img['category']} — {caption}")
            md_lines.append(f"![{caption}]({img['path']})")
            md_lines.append("")

    if store.data["screenshots"]:
        md_lines.append("---")
        md_lines.append("## 4. Verified LinkedIn Evidence Screenshots")
        md_lines.append("")
        for sc in store.data["screenshots"]:
            md_lines.append(f"### {sc['title']} (`{sc['category']}`)")
            md_lines.append(f"{sc['description']}")
            md_lines.append(f"![{sc['title']}]({sc['path']})")
            md_lines.append("")

    md_lines.append("---")
    md_lines.append("## 5. HKUST Computer Science Recommendation Letter")
    md_lines.append("")
    md_lines.append(letter_text)

    portfolio_md_path = store.base_path / "portfolio.md"
    portfolio_md_path.write_text("\n".join(md_lines), encoding="utf-8")
    termcolor.cprint(
        f"[Portfolio] Saved Markdown Portfolio -> {portfolio_md_path}", color="green"
    )

    # 3. Generate Visual HTML Portfolio (portfolio/portfolio.html)
    cards_html = []
    for item in store.data["items"]:
        cards_html.append(
            f"""
            <div class="card">
                <div class="badge">{html.escape(item['section'])}</div>
                <h3>{html.escape(item['title'])}</h3>
                <div class="meta">{html.escape(item['organization'])} &bull; {html.escape(item['date'])}</div>
                <p>{html.escape(item['details'])}</p>
                <div class="relevance"><strong>HKUST CS Relevance:</strong> {html.escape(item.get('relevance_to_hkust_cs', ''))}</div>
            </div>
            """
        )

    images_html = []
    for img in store.data["images"]:
        caption = img.get("context_note") or img.get("alt") or img["category"]
        images_html.append(
            f"""
            <figure class="media-card">
                <img src="{html.escape(img['path'])}" alt="{html.escape(caption)}" loading="lazy" />
                <figcaption>
                    <strong>{html.escape(img['category'])}</strong><br/>
                    {html.escape(caption)}
                </figcaption>
            </figure>
            """
        )

    screenshots_html = []
    for sc in store.data["screenshots"]:
        screenshots_html.append(
            f"""
            <figure class="media-card screenshot-card">
                <img src="{html.escape(sc['path'])}" alt="{html.escape(sc['title'])}" loading="lazy" />
                <figcaption>
                    <strong>{html.escape(sc['title'])}</strong> ({html.escape(sc['category'])})<br/>
                    {html.escape(sc['description'])}
                </figcaption>
            </figure>
            """
        )

    html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Portfolio & HKUST CS Recommendation — Hiu Tung Cheung (Esther)</title>
    <style>
        :root {{
            --primary: #003366;
            --accent: #b8860b;
            --bg: #f8fafc;
            --card-bg: #ffffff;
            --text: #1e293b;
            --muted: #64748b;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: var(--bg);
            color: var(--text);
            margin: 0;
            line-height: 1.6;
        }}
        header {{
            background: linear-gradient(135deg, #002147 0%, #004080 100%);
            color: #fff;
            padding: 3rem 2rem;
            text-align: center;
        }}
        header h1 {{ margin: 0 0 0.5rem 0; font-size: 2.2rem; }}
        header p {{ margin: 0.25rem 0; opacity: 0.9; font-size: 1.05rem; }}
        .container {{ max-width: 1200px; margin: 2rem auto; padding: 0 1.5rem; }}
        h2 {{
            color: var(--primary);
            border-bottom: 2px solid var(--accent);
            padding-bottom: 0.5rem;
            margin-top: 2.5rem;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
            gap: 1.25rem;
        }}
        .card {{
            background: var(--card-bg);
            border-radius: 10px;
            padding: 1.25rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            border-left: 4px solid var(--primary);
        }}
        .badge {{
            display: inline-block;
            background: #e0f2fe;
            color: #0369a1;
            font-size: 0.78rem;
            font-weight: 600;
            padding: 0.2rem 0.6rem;
            border-radius: 999px;
            margin-bottom: 0.5rem;
        }}
        .meta {{ font-size: 0.88rem; color: var(--muted); margin-bottom: 0.75rem; }}
        .relevance {{
            margin-top: 0.75rem;
            padding-top: 0.75rem;
            border-top: 1px dashed #e2e8f0;
            font-size: 0.9rem;
            color: #0f172a;
        }}
        .media-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 1.25rem;
        }}
        .media-card {{
            background: var(--card-bg);
            border-radius: 10px;
            overflow: hidden;
            margin: 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        }}
        .media-card img {{
            width: 100%;
            height: 240px;
            object-fit: cover;
            display: block;
            background: #e2e8f0;
        }}
        .screenshot-card img {{
            object-fit: contain;
            height: 260px;
            background: #0f172a;
        }}
        .media-card figcaption {{
            padding: 0.9rem;
            font-size: 0.9rem;
        }}
        .letter-box {{
            background: #fff;
            padding: 2.5rem;
            border-radius: 10px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.08);
            white-space: pre-wrap;
            font-family: Georgia, "Times New Roman", serif;
            line-height: 1.75;
        }}
    </style>
</head>
<body>
    <header>
        <h1>Hiu Tung Cheung (Esther / 張曉彤)</h1>
        <p>AWS Student Builder Group Leader &bull; GDG on Campus Leader &bull; Red Hat Student Ambassador @ HKIIT</p>
        <p>Higher Diploma in Cloud and Data Centre Administration (CGPA: 3.91 / 4.0) &rarr; HKUST Computer Science Portfolio</p>
    </header>
    <div class="container">
        <h2>1. HKUST Computer Science Recommendation Letter</h2>
        <div class="letter-box">{html.escape(letter_text)}</div>

        <h2>2. Traced Achievements, Talks, Awards & Leadership ({len(store.data['items'])})</h2>
        <div class="grid">
            {''.join(cards_html) or '<p>See stage summaries in portfolio.md.</p>'}
        </div>

        <h2>3. Downloaded Activity & Event Photos ({len(store.data['images'])})</h2>
        <div class="media-grid">
            {''.join(images_html) or '<p>No standalone images extracted.</p>'}
        </div>

        <h2>4. Verified LinkedIn Evidence Screenshots ({len(store.data['screenshots'])})</h2>
        <div class="media-grid">
            {''.join(screenshots_html)}
        </div>
    </div>
</body>
</html>
"""
    portfolio_html_path = store.base_path / "portfolio.html"
    portfolio_html_path.write_text(html_doc, encoding="utf-8")
    termcolor.cprint(
        f"[Portfolio] Saved Visual HTML Portfolio -> {portfolio_html_path}",
        color="green",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Trace LinkedIn activities, save pictures/screenshots, build a visual portfolio, and write an HKUST CS recommendation letter."
    )
    parser.add_argument(
        "--profile-url",
        type=str,
        default=DEFAULT_PROFILE_URL,
        help=f"LinkedIn profile URL (default: {DEFAULT_PROFILE_URL}).",
    )
    parser.add_argument(
        "--portfolio-dir",
        type=str,
        default=DEFAULT_PORTFOLIO_DIR,
        help=f"Output directory for portfolio assets (default: {DEFAULT_PORTFOLIO_DIR}).",
    )
    parser.add_argument(
        "--project",
        type=str,
        default=cu_main.DEFAULT_PROJECT,
        help=f"Google Cloud project ID (default: {cu_main.DEFAULT_PROJECT}).",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=cu_main.DEFAULT_MODEL,
        help=f"Gemini Computer Use model (default: {cu_main.DEFAULT_MODEL}).",
    )
    parser.add_argument(
        "--cdp-url",
        type=str,
        default="auto",
        help="CDP connection string ('auto' uses active Chrome DevToolsActivePort).",
    )
    parser.add_argument(
        "--stage-iterations",
        type=int,
        default=8,
        help="Max Computer Use iterations per exploration stage (default: 8).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    base_url = args.profile_url.rstrip("/") + "/"
    store = PortfolioStore(args.portfolio_dir)
    client = cu_main.create_client(project=args.project)

    screen_width = cu_main.DEFAULT_SCREEN_WIDTH
    screen_height = cu_main.DEFAULT_SCREEN_HEIGHT

    stages = [
        (
            "1_Main_Profile_And_Featured",
            base_url,
            (
                "You are building a comprehensive visual portfolio for Hiu Tung Cheung (Esther) to support her HKUST Computer Science degree application. "
                "On her main LinkedIn profile page:\n"
                "1. Call `save_evidence_screenshot` for her top profile header/About/Featured section.\n"
                "2. Call `extract_and_save_page_images` to download her Featured cards / visible images.\n"
                "3. Scroll down gradually through Education, Publications, and Projects, calling `record_portfolio_item` for key entries and `save_evidence_screenshot` on key sections.\n"
                "4. Finish and summarize what you found."
            ),
        ),
        (
            "2_Recent_Activity_Posts",
            f"{base_url}recent-activity/all/",
            (
                "You are now on Esther's LinkedIn Recent Activity (All Posts) feed.\n"
                "1. Scroll through her activity posts (such as PyCon HK 2026 Kubernetes game platform, AWS Summit HK AI Robot, HKOSCon ProvePresent AI attendance, VTC x Microsoft Virtual Tutor, HKIIT videos, AWS/GDG/Red Hat events).\n"
                "2. Click '...more' on posts so the full text is visible.\n"
                "3. Call `save_evidence_screenshot` on her most impressive technical and leadership posts.\n"
                "4. Call `extract_and_save_page_images` as you scroll so all event/project photos are downloaded into `./portfolio/images/`.\n"
                "5. Call `record_portfolio_item` for each major activity post with full details.\n"
                "6. Summarize all posts traced."
            ),
        ),
        (
            "3_Honors_And_Scholarships",
            f"{base_url}details/honors/",
            (
                "You are now on Esther's Honors & Awards detail page (`details/honors/`).\n"
                "1. Take a screenshot with `save_evidence_screenshot`.\n"
                "2. Scroll down to inspect all 13 Honors & Awards (including Cathay Group Scholarship, Lei Foundation Scholarship, competitions, etc.).\n"
                "3. Call `record_portfolio_item` for the scholarships and awards visible, and `save_evidence_screenshot` as you scroll.\n"
                "4. Summarize all honors and awards with exact titles, issuers, and dates."
            ),
        ),
        (
            "4_Volunteering_And_Leadership",
            f"{base_url}details/volunteering-experiences/",
            (
                "You are now on Esther's Volunteering & Leadership detail page (`details/volunteering-experiences/`).\n"
                "1. Call `save_evidence_screenshot` and scroll through all 12 volunteering/leadership entries (AWS Student Builder Group Leader, GDG on Campus Leader, Red Hat Student Ambassador, etc.).\n"
                "2. Call `record_portfolio_item` for her key leadership roles and community contributions.\n"
                "3. Summarize all volunteering and leadership experiences."
            ),
        ),
        (
            "5_Certifications_And_Publications",
            f"{base_url}details/certifications/",
            (
                "You are now on Esther's Licenses & Certifications detail page (`details/certifications/`).\n"
                "1. Call `save_evidence_screenshot` and `extract_and_save_page_images`.\n"
                "2. Scroll down to view all 16 certifications/badges (Google Cloud, GKE, AWS, Red Hat, etc.) and call `record_portfolio_item` for key technical certifications.\n"
                "3. Summarize all 16 certifications."
            ),
        ),
    ]

    with sync_playwright() as p:
        cdp_url = args.cdp_url
        if cdp_url == "auto":
            port_file = os.path.expandvars(
                r"%LOCALAPPDATA%\Google\Chrome\User Data\DevToolsActivePort"
            )
            lines = open(port_file, encoding="utf-8").read().splitlines()
            cdp_url = f"ws://127.0.0.1:{lines[0].strip()}{lines[1].strip()}"
            print(f"Connected to active Chrome DevTools WebSocket: {cdp_url}")

        browser = p.chromium.connect_over_cdp(cdp_url)
        context = browser.contexts[0]

        matching_page = None
        for pg in context.pages:
            if "linkedin.com" in pg.url:
                matching_page = pg
                break
        page = matching_page if matching_page else context.new_page()

        stage_summaries: Dict[str, str] = {}
        for stage_name, target_url, stage_prompt in stages:
            try:
                summary = run_exploration_stage(
                    client=client,
                    page=page,
                    store=store,
                    stage_name=stage_name,
                    target_url=target_url,
                    stage_prompt=stage_prompt,
                    max_iterations=args.stage_iterations,
                    model=args.model,
                    screen_width=screen_width,
                    screen_height=screen_height,
                )
                stage_summaries[stage_name] = summary
            except auth_exceptions.RefreshError as e:
                termcolor.cprint(
                    f"\n[Authentication Error] Please run `gcloud auth application-default login`: {e}",
                    color="red",
                )
                return
            except Exception as e:
                termcolor.cprint(
                    f"\n[Warning] Error in stage {stage_name}: {e}", color="red"
                )

        # Return tab to main profile page when done
        try:
            page.goto(base_url)
        except Exception:
            pass

    generate_portfolio_and_letter(
        client=client,
        model=args.model,
        store=store,
        stage_summaries=stage_summaries,
    )


if __name__ == "__main__":
    import os
    main()
