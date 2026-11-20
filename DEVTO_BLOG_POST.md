---
title: Building an Autonomous LinkedIn Portfolio & Recommendation Agent with Gemini Computer Use on Google Cloud
published: false
description: Learn how to harness Gemini 3.8 Flash Computer Use on Vertex AI with Playwright CDP attach to build an autonomous agent that navigates authenticated web sessions and generates evidence-backed portfolios.
tags: googlecloud, gemini, ai, python
canonical_url: https://github.com/wongcyrus/gemini-computer-use-linkedin-autofolio
cover_image: https://raw.githubusercontent.com/wongcyrus/gemini-computer-use-linkedin-autofolio/main/assets/devto_cover.png
---

*Author: **Cyrus Wong** — AWS Hero / Educator / Tech Innovator. Published under the **Google Developer Expert (GDE) / Google Cloud** community blog series.*  
*Case Study Contributor & Credits: **Hiu Tung Cheung (Esther / 張曉彤)** — **GDG on Campus Lead at HKIIT** (Higher Diploma in Cloud and Data Centre Administration).*

---

![Building an Autonomous LinkedIn Portfolio & Recommendation Agent with Gemini Computer Use on Google Cloud](https://raw.githubusercontent.com/wongcyrus/gemini-computer-use-linkedin-autofolio/main/assets/devto_cover.png)

## The Promise and the Pitfall of "Computer Use"

When Google announced **Gemini Computer Use** capabilities on Vertex AI, the developer community immediately saw the potential: AI agents that don't just read JSON APIs or parse headless HTML, but actually **see** the screen, understand spatial UI layouts, click buttons, scroll feeds, and interact with complex web applications just like a human engineer.

However, if you've tried deploying automated browser agents into production, you've probably run into the **"Cold-Start Authentication Wall"**:

1. **2FA & Captchas**: Modern enterprise portals (LinkedIn, Google Cloud Console, Jira, Salesforce) vigorously block automated login attempts from blank headless browser instances.
2. **Credential Leaks**: Hardcoding your enterprise passwords or session cookies into scripts or environment variables is a major security risk.
3. **Session Loss**: Even with storage state dumps, token rotation breaks automated runs mid-flight.

To solve this, I built **[Gemini Computer Use LinkedIn AutoFolio](https://github.com/wongcyrus/gemini-computer-use-linkedin-autofolio)** — an open-source autonomous agent powered by **Google Cloud Vertex AI** (`gemini-3.8-flash`), the **Google Gen AI SDK (`google-genai`)**, and **Playwright CDP Attach**.

Instead of trying to bypass login forms or scraping messy HTML, AutoFolio attaches directly to your **already logged-in Google Chrome browser** via the Chrome DevTools Protocol (`DevToolsActivePort`). It then visually traverses LinkedIn profiles, navigates deep sub-pages (Honors, Volunteering, Certifications, Activity Posts), clicks *"…more"*, captures high-resolution visual evidence, and generates:

- **An Interactive Visual Web Portfolio (`portfolio.html` & `portfolio.md`)** with embedded event photos and verified screenshot proof.
- **An Evidence-Backed University / Job Recommendation Letter (`hkust_cs_recommendation_letter.md`)** grounded in concrete architectural contributions and verified awards.
- **A 4-Page Executive Supporting Document (PDF / DOCX / HTML)** formatted with high-density visual proof for competitive admissions or job applications.
- **Batch Class Processing (`students.txt`)** with an automated central class dashboard for educators and team leads.

In this deep dive, I'll walk through the architecture, Google Cloud configuration, CDP attach technique, and **Hybrid Tool Calling** that make this possible.

---

## High-Level Solution Architecture

Here is the end-to-end architecture of AutoFolio, showing how Vertex AI, Chrome DevTools Protocol, and Playwright work in concert:

![Gemini Computer Use + Chrome CDP Attach Architecture on Google Cloud](https://raw.githubusercontent.com/wongcyrus/gemini-computer-use-linkedin-autofolio/main/assets/architecture_infographic.png)

---

## Agent Execution Loop: Step-by-Step Sequence

To understand how Gemini Computer Use iteratively interacts with the browser, here is the full execution loop sequence:

![Gemini Computer Use Agent Execution Loop Sequence](https://raw.githubusercontent.com/wongcyrus/gemini-computer-use-linkedin-autofolio/main/assets/diagram_sequence_loop.png)

---

## 1. Setting Up Google Cloud Vertex AI & Gemini Computer Use

Google Cloud provides enterprise-grade access to Gemini through the unified **Google Gen AI SDK (`google-genai`)**.

### Authentication via Google Cloud Application Default Credentials (ADC)

Rather than juggling API keys, we leverage standard Google Cloud IAM via ADC:

```powershell
# Authenticate your local development environment
gcloud auth application-default login

# Configure Google Cloud environment variables
$env:GOOGLE_CLOUD_PROJECT = "your-gcp-project-id"
$env:GOOGLE_CLOUD_LOCATION = "global"
$env:GOOGLE_GENAI_USE_ENTERPRISE = "True"
```

### Initializing the Vertex AI Client in Python

With the new `google-genai` SDK, initializing Vertex AI with Computer Use is clean and concise:

```python
import os
from google import genai
from google.genai import types

project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "your-gcp-project-id")
location = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")

client = genai.Client(
    vertexai=True,
    project=project_id,
    location=location,
)
```

### Defining the Computer Use Tool with Enterprise Security

Gemini's Computer Use tool comes with built-in prompt injection defense:

```python
computer_use_tool = types.Tool(
    computer_use=types.ComputerUse(
        environment=types.Environment.ENVIRONMENT_BROWSER,
        enable_prompt_injection_detection=True
    )
)
```

> **Security Tip**: Setting `enable_prompt_injection_detection=True` is critical when your agent navigates public user-generated content on platforms like LinkedIn, protecting your agent from adversarial prompts hidden in profile bios or posts.

---

## 2. The Secret Sauce: Connecting to Active Chrome via `DevToolsActivePort`

If you try to launch a fresh Chromium browser, LinkedIn will hit you with auth walls and CAPTCHAs. 

Instead, we tell Chrome to expose its DevTools port, and our Python agent attaches directly to the **user's active, authenticated browser tab**.

### How `DevToolsActivePort` Auto-Discovery Works

On Windows, macOS, and Linux, whenever Chrome is running with remote debugging enabled, it writes its active port and browser GUID to a file named `DevToolsActivePort` inside the user data directory:

```python
from pathlib import Path
import os

def discover_active_chrome_ws_url() -> str:
    """Auto-detect active Chrome debugger WebSocket URL from DevToolsActivePort."""
    candidate_paths = [
        Path(os.environ.get("LOCALAPPDATA", "")) / "Google" / "Chrome" / "User Data" / "DevToolsActivePort",
        Path.home() / ".config" / "google-chrome" / "DevToolsActivePort",
        Path.home() / "Library" / "Application Support" / "Google" / "Chrome" / "DevToolsActivePort",
    ]
    
    for path in candidate_paths:
        if path.is_file():
            lines = path.read_text(encoding="utf-8").splitlines()
            if len(lines) >= 2:
                port = lines[0].strip()
                guid = lines[1].strip()
                ws_url = f"ws://127.0.0.1:{port}/devtools/browser/{guid}"
                return ws_url
                
    return "http://localhost:9222"
```

### Attaching with Playwright

Connecting Playwright to the active browser takes just a few lines:

```python
from playwright.sync_api import sync_playwright

playwright = sync_playwright().start()
ws_url = discover_active_chrome_ws_url()

# Connect over CDP
browser = playwright.chromium.connect_over_cdp(ws_url)
context = browser.contexts[0]

# Pick up the active LinkedIn tab without opening a blank one
page = context.pages[0] if context.pages else context.new_page()
```

Zero re-login, zero 2FA prompts, zero cookies written to disk. The agent inherits your live session instantly.

---

## 3. Coordinate Normalization & Denormalization Pipeline

One of the most elegant architectural choices in Gemini Computer Use is its resolution-independent coordinate system. Gemini's visual perception engine processes all screenshots on a normalized `[0, 1000]` grid:

![Coordinate Normalization and Denormalization Pipeline](https://raw.githubusercontent.com/wongcyrus/gemini-computer-use-linkedin-autofolio/main/assets/diagram_coordinate_pipeline.png)

This ensures that whether you run on a 1080p desktop, a 4K monitor, or a scaled cloud container, Gemini's visual actions hit the exact target buttons without resolution calibration drift.

---

## 4. Hybrid Tool Calling Architecture: Dual-Dispatch Engine

One of the most powerful features of Gemini on Google Cloud is **Hybrid Tool Calling**: you don't have to choose between visual Computer Use or function calling. You can give the model **both** in the exact same prompt configuration!

![Hybrid Tool Calling Dual-Dispatch Engine](https://raw.githubusercontent.com/wongcyrus/gemini-computer-use-linkedin-autofolio/main/assets/diagram_hybrid_tools.png)

### Passing Both Tools to `generate_content`

```python
# Pass both Computer Use and your custom tool definitions
response = client.models.generate_content(
    model="gemini-3.8-flash",
    contents=conversation_history,
    config=types.GenerateContentConfig(
        tools=[computer_use_tool, custom_folio_tools],
        temperature=0.2,
    ),
)
```

When Gemini responds, our loop inspects the candidate calls:

```python
for candidate in response.candidates:
    for part in candidate.content.parts:
        if part.function_call:
            fn_name = part.function_call.name
            fn_args = part.function_call.args
            
            if fn_name == "click_at":
                # Convert normalized (0-1000) coordinates to browser viewport pixels
                x = int(fn_args["x"] * viewport_width / 1000)
                y = int(fn_args["y"] * viewport_height / 1000)
                page.mouse.click(x, y)
                
            elif fn_name == "save_evidence_screenshot":
                # Execute our custom domain tool
                result = save_evidence_screenshot(page, fn_args["label"], fn_args["category"])
                
            elif fn_name == "extract_and_save_page_images":
                result = extract_page_images(page, fn_args["category"])
```

---

## 5. Multi-Stage Autonomous Workflow: Turning Activity into Grounded Evidence

Rather than letting an agent roam aimlessly, AutoFolio runs a disciplined **5-stage exploration pipeline**:

![5-Stage LinkedIn Deep Exploration Pipeline](https://raw.githubusercontent.com/wongcyrus/gemini-computer-use-linkedin-autofolio/main/assets/diagram_linkedin_stages.png)

1. **Stage 1 (Main Profile & Featured)**: Scans profile headline, About section, featured projects, and top skills.
2. **Stage 2 (Recent Activity & Posts)**: Visits `/recent-activity/all/`, scrolls down, expands *"…see more"*, captures conference speaking announcements, hackathon podium finishes, and extracts embedded event photos.
3. **Stage 3 (Honors & Scholarships)**: Visits `/details/honors/` to catalog official government and university scholarship awards with exact issuing bodies and dates.
4. **Stage 4 (Volunteering & Community Leadership)**: Visits `/details/volunteering-experiences/` to record tech community leadership (e.g. Red Hat Student Ambassador, AWS Cloud Leader, Google Developer Group).
5. **Stage 5 (Certifications & Badges)**: Visits `/details/certifications/` to validate industry credentials.

---

## 6. Batch Class Processing Architecture

For educators, admissions officers, and engineering team leads, AutoFolio provides an automated batch runner that reads student links from a text file (`students.txt`) and synthesizes an entire cohort in one command:

![Batch Class Processing Architecture](https://raw.githubusercontent.com/wongcyrus/gemini-computer-use-linkedin-autofolio/main/assets/diagram_class_batch.png)

---

## 7. Real-World Case Study: AutoFolio in Action

As an educator (Senior Lecturer at HKIIT / IVE Lee Wai Lee, Hong Kong), I write dozens of university recommendation letters every year for students transferring into elite Bachelor of Engineering programs (like **HKUST Computer Science**).

Traditional recommendation letters suffer from a common flaw: they rely on vague adjectives (*"hardworking"*, *"passionate"*) because teachers don't have time to dig through 3 years of extracurricular activities.

We ran AutoFolio on the profile of **Hiu Tung Cheung (Esther / 張曉彤)**, an outstanding student leader serving as the **GDG on Campus Lead at HKIIT** (Hong Kong Institute of Information Technology), who maintains a stellar **3.91 / 4.0 CGPA** in Cloud & Data Centre Administration while applying for **HKUST BEng in Computer Science**.

### Sample Verified Evidence Captured Autonomously by Gemini Computer Use

During its 5-stage traversal, Gemini autonomously inspected her LinkedIn profile, clicked *"…see more"*, captured high-resolution screenshot proofs, and downloaded original event media:

| Profile & Featured Header | PyCon HK 2026 Speaker Announcement |
| :---: | :---: |
| ![Profile Header](https://raw.githubusercontent.com/wongcyrus/gemini-computer-use-linkedin-autofolio/main/portfolio/screenshots/01_profile_header_Esther_Cheung_-_LinkedIn_Profile_Header_About_Featured.png) | ![PyCon HK 2026](https://raw.githubusercontent.com/wongcyrus/gemini-computer-use-linkedin-autofolio/main/portfolio/screenshots/04_conference_talk_PyCon_Hong_Kong_2026_Speaker_Announcement_-_Kubernetes_Game_.png) |

| Honors & Scholarships (`details/honors/`) | Volunteering & Leadership (`details/volunteering-experiences/`) |
| :---: | :---: |
| ![Honors & Scholarships](https://raw.githubusercontent.com/wongcyrus/gemini-computer-use-linkedin-autofolio/main/portfolio/screenshots/05_scholarship_award_Honors_Awards_Page_-_Section_1.png) | ![Volunteering & Leadership](https://raw.githubusercontent.com/wongcyrus/gemini-computer-use-linkedin-autofolio/main/portfolio/screenshots/08_leadership_Volunteering_Leadership_-_Red_Hat_AWS_Leader_GDG_Leader.png) |

---

### What Gemini Discovered and Synthesized Autonomously:

1. **Pioneering Tech Community Leadership**:
   - Traced her concurrent roles as Hong Kong's 1st Red Hat Student Ambassador, 1st AWS Student Builder Group Leader '26, and Google Developer Group (GDG) on Campus Leader.
   - Identified her community volunteer work teaching elderly citizens generative AI applications with CLP Power Hong Kong.

2. **Public Conference Speaking & Tech Evangelism**:
   - Verified her speaking engagement at **PyCon Hong Kong 2026** presenting *「從港域時空到 Kubernetes: 將香港遊戲世界化身雲原生學習平台」 (From Hong Kong Zero to Kubernetes)*.
   - Documented project demos presented to Microsoft Hong Kong and VTC leadership at the MoU Signing Ceremony.

3. **Academic Diligence & Honors**:
   - Verified her **CGPA of 3.91 / 4.0**, Cathay Group Scholarship 2025/26, and Lei Foundation Scholarship.
   - Cataloged 1st Prize and Outstanding Teamwork awards at the Greater Bay Area IT Application System Development Competition.
   - Verified 16 industry credentials spanning AWS, Google Cloud (GKE badges), and Red Hat OpenShift.

---

### Live Deliverables Generated in the Repository

You can view the full live artifacts generated during this run directly in the repository:

- 📄 **[Evidence-Backed HKUST CS Recommendation Letter](https://github.com/wongcyrus/gemini-computer-use-linkedin-autofolio/blob/main/portfolio/hkust_cs_recommendation_letter.md)**: A grounded, professional 1,200-word recommendation letter with structured admissions rubrics.
- 🌐 **[Generated Visual HTML Portfolio](https://github.com/wongcyrus/gemini-computer-use-linkedin-autofolio/blob/main/portfolio/portfolio.html)**: Interactive portfolio with hero badges, category filters, and screenshot proof modals.
- 📝 **[Generated Markdown Portfolio](https://github.com/wongcyrus/gemini-computer-use-linkedin-autofolio/blob/main/portfolio/portfolio.md)**: Clean, portable documentation ready for static site generators.
- 📊 **[Structured Manifest (`manifest.json`)](https://github.com/wongcyrus/gemini-computer-use-linkedin-autofolio/blob/main/portfolio/manifest.json)**: Machine-readable JSON cataloging all traced achievements, issuing bodies, dates, and media paths.
- 🎓 **[Consolidated Class Dashboard](https://github.com/wongcyrus/gemini-computer-use-linkedin-autofolio/blob/main/README.md#a-run-for-an-entire-class-from-a-text-file---profiles-file-studentstxt)**: Multi-student cohort index generated when running with `--profiles-file students.txt`.

---

## 8. How to Run It in Your Own Environment

You can try this today on your machine with Google Cloud Vertex AI:

### Clone & Install

```powershell
git clone https://github.com/wongcyrus/gemini-computer-use-linkedin-autofolio.git
cd gemini-computer-use-linkedin-autofolio

python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install chromium
```

### Authenticate with Google Cloud

```powershell
gcloud auth application-default login
$env:GOOGLE_CLOUD_PROJECT = "your-gcp-project-id"
$env:GOOGLE_CLOUD_LOCATION = "global"
$env:GOOGLE_GENAI_USE_ENTERPRISE = "True"
```

### Start Chrome with Remote Debugging

Either visit `chrome://inspect/#remote-debugging` in Chrome or launch:

```powershell
chrome.exe --remote-debugging-port=9222
```

Navigate to LinkedIn in any tab.

### Run AutoFolio for a Candidate

```powershell
.\.venv\Scripts\python.exe build_portfolio.py `
  --profile-url "https://www.linkedin.com/in/target-profile-handle/" `
  --portfolio-dir portfolio `
  --target-program "Bachelor of Engineering in Computer Science, HKUST" `
  --recommender "Cyrus Wong, Senior Lecturer, HKIIT"
```

Or run for your whole class:

```powershell
.\.venv\Scripts\python.exe build_portfolio.py `
  --profiles-file students.txt `
  --portfolio-dir class_portfolios
```

Once complete, open the visual portfolio:

```powershell
Start-Process .\portfolio\portfolio.html
```

---

## Key Takeaways for Google Cloud Developers

1. **Computer Use is Ready for Production Enterprise Apps**: You don't need dedicated API endpoints for internal dashboards or authenticated sites. Combining Vertex AI's `gemini-3.8-flash` with CDP attach lets agents operate within legitimate, authenticated human sessions.
2. **Hybrid Tooling is the Winning Pattern**: Native GUI actions provide universal web navigation, while custom functions allow your Python code to inject precise DOM scripts, extract media, and persist structured state.
3. **Security First**: Always enable `enable_prompt_injection_detection=True` when dealing with user-generated content from the web to safeguard your agent workflows.
4. **Social Good & Education**: Autonomous agents can remove administrative friction from education and hiring, ensuring that students and candidates are judged on their verified, concrete achievements.

---

## Acknowledgments & Credits

Special credit and gratitude to **Hiu Tung Cheung (Esther / 張曉彤)** — **GDG on Campus Lead at HKIIT** — for co-developing community initiatives, testing early iterations of AutoFolio, and graciously providing her rich profile data, conference talks, and community achievements as our live benchmark case study. Her leadership bridging Google Developer Groups (GDG) with campus learning embodies the collaborative spirit of the Google developer community.

---

## Resources & Open Source Code

- **GitHub Repository**: [wongcyrus/gemini-computer-use-linkedin-autofolio](https://github.com/wongcyrus/gemini-computer-use-linkedin-autofolio)
- **Google Cloud Gemini Computer Use Documentation**: [Cloud Enterprise Agent Platform Docs](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/computer-use)
- **Google Gen AI Python SDK**: [google-genai on PyPI](https://pypi.org/project/google-genai/)

*Have questions or ideas about building browser agents on Google Cloud? Drop a comment below or open an issue on GitHub!*
