"""Render exact Mermaid diagrams with Google Cloud styling using Mermaid.js and Playwright."""

from playwright.sync_api import sync_playwright
import os

DIAGRAMS = [
    {
        "id": "google_diagram1_system_architecture",
        "title": "Google Cloud \u2022 End-to-End System Architecture",
        "subtitle": "Playwright CDP Attach + Vertex AI Gemini 3.8 Flash Hybrid Agentic Loop",
        "badge": "Architecture Overview",
        "code": """flowchart TD
    subgraph BrowserEnvironment["🖥️ Local Client Environment"]
        A["Active Google Chrome Browser<br/>(Authenticated Session, Cookies, 2FA Active)"]
        DT["DevToolsActivePort<br/>(%LOCALAPPDATA%/.../DevToolsActivePort)"]
        PW["Playwright CDP Bridge<br/>(connect_over_cdp ws://127.0.0.1:port/...)"]
        A -->|"Writes Port and GUID"| DT
        DT -->|"WebSocket URL Discovery"| PW
        PW -->|"Attaches to Active Tab"| A
    end

    subgraph GoogleCloud["☁️ Google Cloud Vertex AI"]
        ADC["Google Cloud IAM / ADC<br/>(gcloud auth application-default login)"]
        SDK["Google Gen AI SDK (google-genai)<br/>(Client vertexai=True, location='global')"]
        MODEL["Gemini 3.8 Flash (Computer Use Model)<br/>(Spatial Reasoning, Prompt Injection Detection)"]
        ADC --> SDK --> MODEL
    end

    subgraph AgentLoop["🔄 Hybrid Agent Execution Loop"]
        SCREEN["1. Viewport Base64 Screenshot"]
        DECISION{"2. Gemini Multi-Modal Decision"}
        NATIVE["3a. Native ComputerUse Actions<br/>(click_at, scroll_page, type_text, wait)"]
        CUSTOM["3b. Custom Domain Tools<br/>(save_evidence_screenshot, extract_and_save_page_images)"]
        
        PW -->|"Capture"| SCREEN --> MODEL --> DECISION
        DECISION --> NATIVE -->|"Mouse and Keyboard Commands"| PW
        DECISION --> CUSTOM -->|"DOM Injection and File I/O"| ARTIFACTS
    end

    subgraph ARTIFACTS["📁 Generated Showcase Artifacts"]
        ART1["Interactive HTML Portfolio<br/>(portfolio.html and portfolio.md)"]
        ART2["Evidence-Backed Rec Letter<br/>(hkust_cs_recommendation_letter.md)"]
        ART3["4-Page Admissions Dossier<br/>(supporting_doc.pdf and docx)"]
        ART4["Consolidated Class Dashboard<br/>(class_portfolios/index.html)"]
    end"""
    },
    {
        "id": "google_diagram2_execution_sequence",
        "title": "Google Cloud \u2022 Agent Execution Loop Sequence",
        "subtitle": "Step-by-step observation, spatial reasoning, tool dispatch, and artifact synthesis",
        "badge": "Execution Sequence",
        "code": """sequenceDiagram
    autonumber
    actor User as Educator / Developer
    participant Script as build_portfolio.py
    participant Chrome as Active Chrome Tab
    participant VertexAI as Google Cloud Vertex AI (Gemini 3.8 Flash)
    participant Disk as Local File System (portfolio/)

    User->>Script: Run with --profile-url or --profiles-file
    Script->>Chrome: Discover DevToolsActivePort & Attach via CDP
    Chrome-->>Script: CDP WebSocket Connection Established
    
    loop 5-Stage Autonomous Traversal
        Script->>Chrome: Capture Current Viewport (Base64 JPEG)
        Chrome-->>Script: Viewport Image (1280x800)
        Script->>VertexAI: generate_content(Image + History + Tools)
        Note over VertexAI: Spatial UI Understanding & Prompt Injection Defense
        VertexAI-->>Script: Tool Call Decision (click_at / custom function)
        
        alt Native Computer Use Tool Call
            Script->>Script: Denormalize Coordinates (0..1000 -> 1280x800 px)
            Script->>Chrome: page.mouse.click(pixel_x, pixel_y) / page.mouse.wheel()
            Chrome-->>Script: DOM Updates & Navigation
        else Custom Function: save_evidence_screenshot
            Script->>Chrome: Capture Full-Res Element / Crop Screenshot
            Script->>Disk: Save to portfolio/screenshots/*.png
            Script-->>VertexAI: FunctionResponse(status="saved", file_path=...)
        else Custom Function: extract_and_save_page_images
            Script->>Chrome: Evaluate DOM script to find high-res post images
            Script->>Disk: Download to portfolio/images/*.jpg
            Script-->>VertexAI: FunctionResponse(extracted_count=N)
        end
    end

    Script->>VertexAI: Request Final Synthesis (Markdown & Letter)
    VertexAI-->>Script: Formatted Portfolio, Rec Letter & 4-Page Dossier
    Script->>Disk: Write portfolio.html, recommendation_letter.md, manifest.json
    Script-->>User: Open portfolio.html in Browser"""
    },
    {
        "id": "google_diagram3_coordinate_pipeline",
        "title": "Google Cloud \u2022 Coordinate Normalization & Denormalization Pipeline",
        "subtitle": "Resolution-independent spatial targeting from Gemini 0..1000 grid to browser viewport pixels",
        "badge": "Spatial Vision Pipeline",
        "code": """flowchart LR
    A["Raw Viewport Screenshot<br/>(e.g., 1280 x 800 px)"] -->|"Sent to Gemini"| B["Gemini 3.8 Flash Vision Encoder<br/>(Normalized Grid: [0, 1000] x [0, 1000])"]
    B -->|"Predicts Action Target"| C["Normalized Coordinate Output<br/>(e.g., x: 450, y: 320)"]
    C -->|"Denormalization Formula"| D["Denormalizer Engine<br/>x = 450 * 1280 / 1000 = 576 px<br/>y = 320 * 800 / 1000 = 256 px"]
    D -->|"Executes Playwright Action"| E["Chrome Mouse / Click Dispatch<br/>page.mouse.click(576, 256)"]"""
    },
    {
        "id": "google_diagram4_hybrid_tools",
        "title": "Google Cloud \u2022 Hybrid Tool Calling Dual-Dispatch Engine",
        "subtitle": "Parallel dispatch between native types.ComputerUse and domain types.FunctionDeclaration",
        "badge": "Dual Tooling Engine",
        "code": """flowchart TD
    MODEL["Gemini 3.8 Flash on Vertex AI"] -->|"Generates Model Turn"| CANDIDATE{"Inspect Candidate FunctionCall"}
    
    subgraph NativeComputerUse["🌐 Native ComputerUse Tool (types.ComputerUse)"]
        CANDIDATE -->|"click_at(x, y)"| CU_CLICK["Translate coordinates and page.mouse.click"]
        CANDIDATE -->|"scroll_page(direction)"| CU_SCROLL["page.mouse.wheel(0, dy)"]
        CANDIDATE -->|"type_text_at(text, x, y)"| CU_TYPE["page.mouse.click and page.keyboard.type"]
        CANDIDATE -->|"navigate(url)"| CU_NAV["page.goto(url)"]
        CANDIDATE -->|"wait_5_seconds()"| CU_WAIT["page.wait_for_timeout(5000)"]
    end

    subgraph CustomDomainTools["🛠️ Custom AutoFolio Tools (FunctionDeclaration)"]
        CANDIDATE -->|"save_evidence_screenshot"| CT_SHOT["Capture high-res proof, watermark, and catalog"]
        CANDIDATE -->|"extract_and_save_page_images"| CT_IMG["DOM evaluate image elements, download media files"]
        CANDIDATE -->|"record_portfolio_item"| CT_ITEM["Append structured JSON record to manifest.json"]
        CANDIDATE -->|"yield_to_user"| CT_HITL["Pause for Human-in-the-Loop review"]
    end

    CU_CLICK --> SYNC["Synchronize Browser State and Next Viewport"]
    CU_SCROLL --> SYNC
    CU_TYPE --> SYNC
    CU_NAV --> SYNC
    CU_WAIT --> SYNC
    CT_SHOT --> SYNC
    CT_IMG --> SYNC
    CT_ITEM --> SYNC
    CT_HITL --> SYNC
    
    SYNC -->|"FunctionResponse + New Screenshot"| MODEL"""
    },
    {
        "id": "google_diagram5_linkedin_stages",
        "title": "Google Cloud \u2022 5-Stage LinkedIn Deep Exploration Pipeline",
        "subtitle": "Disciplined multi-stage traversal from main profile header to sub-page achievements",
        "badge": "Autonomous Traversal",
        "code": """flowchart TD
    START["Start: Profile URL Loaded"] --> S1["Stage 1: Main Profile and Featured<br/>- Headline, About, Education, Skills<br/>- Featured Projects and GitHub Links<br/>- Capture Profile Header Screenshot"]
    
    S1 --> S2["Stage 2: Recent Activity Posts (/recent-activity/all/)<br/>- Visually scan timeline posts<br/>- Click '...see more' on truncated posts<br/>- Identify conference talks, hackathons, open source<br/>- Extract and download embedded event photos"]
    
    S2 --> S3["Stage 3: Honors and Scholarships (/details/honors/)<br/>- Navigate to dedicated honors sub-page<br/>- Record award titles, issuing bodies, dates<br/>- Capture high-res proof screenshots"]
    
    S3 --> S4["Stage 4: Volunteering and Leadership (/details/volunteering-experiences/)<br/>- Navigate to volunteering sub-page<br/>- Catalog student ambassador and community roles<br/>- Quantify leadership impact (e.g., students mentored)"]
    
    S4 --> S5["Stage 5: Certifications and Badges (/details/certifications/)<br/>- Verify cloud and industry certifications (AWS, GCP, Red Hat)<br/>- Record verification IDs and issue dates"]
    
    S5 --> SYNTH["Synthesis and Artifacts Generation<br/>- Compile manifest.json<br/>- Generate portfolio.html and portfolio.md<br/>- Generate hkust_cs_recommendation_letter.md<br/>- Format 4-page admissions supporting document (PDF/DOCX)"]
    
    SYNTH --> DONE["Finish: Autonomous Run Complete"]"""
    },
    {
        "id": "google_diagram6_class_batch",
        "title": "Google Cloud \u2022 Batch Class Processing Architecture",
        "subtitle": "Iterative cohort runner generating isolated candidate dossiers and central Class Dashboard",
        "badge": "Batch Cohort Runner",
        "code": """flowchart TD
    INPUT["students.txt<br/>Name - https://www.linkedin.com/in/..."] --> BATCH["AutoFolio Batch Controller<br/>(build_portfolio.py --profiles-file)"]
    
    subgraph CohortLoop["Cohort Iteration Loop"]
        BATCH --> P1["Student 1: Esther Cheung"]
        BATCH --> P2["Student 2: Alex Wong"]
        BATCH --> P3["Student 3: Chloe Chan"]
    end

    subgraph PerStudentArtifacts["Per-Student Dedicated Repositories"]
        P1 --> D1["class_portfolios/esther-cheung/<br/>- portfolio.html and .md<br/>- hkust_cs_recommendation_letter.md<br/>- screenshots/ and images/<br/>- manifest.json"]
        P2 --> D2["class_portfolios/alex-wong/<br/>- portfolio.html and .md<br/>- recommendation_letter.md<br/>- screenshots/ and images/"]
        P3 --> D3["class_portfolios/chloe-chan/<br/>- portfolio.html and .md<br/>- recommendation_letter.md<br/>- screenshots/ and images/"]
    end

    D1 --> DASH["Master Class Dashboard Generator<br/>(class_portfolios/index.html and index.md)"]
    D2 --> DASH
    D3 --> DASH
    DASH --> VIEW["Educator Review & One-Click PDF Export"]"""
    }
]

HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
  <meta charset='utf-8'>
  <script src='https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js'></script>
  <style>
    * { box-sizing: border-box; }
    body {
      margin: 0;
      padding: 24px;
      background: #0d1117;
      font-family: -apple-system, BlinkMacSystemFont, 'Google Sans', 'Segoe UI', Roboto, sans-serif;
      display: inline-block;
    }
    .card {
      background: #161b22;
      border: 1px solid #30363d;
      border-radius: 16px;
      padding: 28px 32px;
      box-shadow: 0 12px 32px rgba(0,0,0,0.5);
      color: #e6edf3;
      max-width: 1200px;
    }
    .header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 24px;
      padding-bottom: 16px;
      border-bottom: 1px solid #21262d;
    }
    .title-group { display: flex; align-items: center; gap: 12px; }
    .logo-badge {
      background: #1a73e8; color: white; width: 36px; height: 36px; border-radius: 8px;
      display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 18px;
    }
    .title { font-size: 20px; font-weight: 700; color: #ffffff; letter-spacing: -0.2px; }
    .subtitle { font-size: 13px; color: #8b949e; margin-top: 2px; }
    .badge-tag {
      background: rgba(26, 115, 232, 0.15);
      border: 1px solid #1a73e8;
      color: #58a6ff;
      padding: 4px 14px;
      border-radius: 20px;
      font-size: 12px;
      font-weight: 600;
    }
    .mermaid-container {
      background: #0d1117;
      border: 1px solid #21262d;
      border-radius: 12px;
      padding: 24px;
      display: flex;
      justify-content: center;
    }
    .mermaid svg {
      max-width: 100% !important;
      height: auto !important;
      font-family: -apple-system, BlinkMacSystemFont, 'Google Sans', 'Segoe UI', Roboto, sans-serif !important;
    }
    /* Google Cloud themed Mermaid node styles */
    .node rect, .node circle, .node polygon {
      fill: #1f293d !important;
      stroke: #3b82f6 !important;
      stroke-width: 1.5px !important;
    }
    .cluster rect {
      fill: #161b22 !important;
      stroke: #30363d !important;
      stroke-width: 1.5px !important;
      rx: 8px !important;
    }
    .edgePath .path {
      stroke: #58a6ff !important;
      stroke-width: 1.8px !important;
    }
    .edgeLabel {
      background-color: #0d1117 !important;
      color: #8ab4f8 !important;
      font-size: 11px !important;
    }
    .actor {
      fill: #1f293d !important;
      stroke: #1a73e8 !important;
    }
    text.actor > tspan {
      fill: #e6edf3 !important;
      font-weight: 600 !important;
    }
    .messageText {
      fill: #8ab4f8 !important;
      font-size: 12px !important;
    }
  </style>
</head>
<body>
  <div class='card' id='diag-card'>
    <div class='header'>
      <div class='title-group'>
        <div class='logo-badge'>G</div>
        <div>
          <div class='title'>__TITLE__</div>
          <div class='subtitle'>__SUBTITLE__</div>
        </div>
      </div>
      <div class='badge-tag'>__BADGE__</div>
    </div>
    <div class='mermaid-container'>
      <pre class='mermaid'>
__MERMAID_CODE__
      </pre>
    </div>
  </div>
  <script>
    mermaid.initialize({
      startOnLoad: true,
      theme: 'dark',
      themeVariables: {
        darkMode: true,
        background: '#0d1117',
        primaryColor: '#1f293d',
        primaryTextColor: '#f0f6fc',
        primaryBorderColor: '#38bdf8',
        lineColor: '#58a6ff',
        secondaryColor: '#238636',
        tertiaryColor: '#21262d',
        mainBkg: '#1f293d',
        nodeBorder: '#38bdf8',
        clusterBkg: '#161b22',
        clusterBorder: '#30363d',
        titleColor: '#ffffff',
        edgeLabelBackground: '#0d1117',
        nodeTextColor: '#f0f6fc',
        actorBkg: '#1f293d',
        actorBorder: '#1a73e8',
        actorTextColor: '#ffffff',
        actorLineColor: '#58a6ff',
        signalColor: '#58a6ff',
        signalTextColor: '#e6edf3',
        labelBoxBkgColor: '#161b22',
        labelBoxBorderColor: '#30363d',
        labelTextColor: '#f0f6fc',
        loopTextColor: '#e6edf3',
        noteBkgColor: '#1f293d',
        noteBorderColor: '#1a73e8',
        noteTextColor: '#f0f6fc'
      }
    });
  </script>
</body>
</html>"""

def main():
    os.makedirs("E:/working/gemini-computer-use/assets", exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(device_scale_factor=2)
        
        for d in DIAGRAMS:
            print(f"Rendering {d['id']} from exact Mermaid definition...")
            html = HTML_TEMPLATE.replace("__TITLE__", d["title"]) \
                                .replace("__SUBTITLE__", d["subtitle"]) \
                                .replace("__BADGE__", d["badge"]) \
                                .replace("__MERMAID_CODE__", d["code"])
            
            page.set_content(html, wait_until="networkidle")
            page.wait_for_selector(".mermaid svg")
            out_path = f"E:/working/gemini-computer-use/assets/{d['id']}.png"
            page.locator("#diag-card").screenshot(path=out_path)
            print(f"Saved {out_path}")
            
        browser.close()
    print("All Mermaid diagrams successfully rendered with Google Cloud styling!")

if __name__ == "__main__":
    main()
