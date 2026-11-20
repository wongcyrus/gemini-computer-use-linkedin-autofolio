"""Generate Google Cloud styled architecture diagrams for dev.to and GitHub."""

from playwright.sync_api import sync_playwright
from pathlib import Path

COMMON_CSS = """
  * { box-sizing: border-box; }
  body {
    margin: 0; padding: 24px;
    background: #0d1117;
    font-family: -apple-system, BlinkMacSystemFont, 'Google Sans', 'Segoe UI', Roboto, Helvetica, sans-serif;
    display: inline-block;
  }
  .card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 16px;
    padding: 32px 36px;
    box-shadow: 0 12px 32px rgba(0,0,0,0.5);
    color: #e6edf3;
    max-width: 1040px;
    min-width: 980px;
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
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
  }
"""

def generate_sequence_diagram(page):
    html = f"""<!DOCTYPE html><html><head><meta charset='utf-8'><style>{COMMON_CSS}
      .seq-grid {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; margin-bottom: 24px; }}
      .actor-box {{
        background: #21262d; border: 1px solid #30363d; border-radius: 10px;
        padding: 12px 8px; text-align: center;
      }}
      .actor-title {{ font-size: 14px; font-weight: 700; color: #58a6ff; }}
      .actor-role {{ font-size: 11px; color: #8b949e; margin-top: 2px; }}
      
      .steps-list {{ display: flex; flex-direction: column; gap: 12px; }}
      .step-row {{
        display: flex; align-items: center; gap: 16px; background: #0d1117;
        border: 1px solid #30363d; border-radius: 10px; padding: 12px 16px;
      }}
      .step-num {{
        background: #1a73e8; color: white; width: 28px; height: 28px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 13px; flex-shrink: 0;
      }}
      .step-content {{ flex: 1; }}
      .step-title {{ font-size: 14px; font-weight: 600; color: #f0f6fc; }}
      .step-desc {{ font-size: 12px; color: #8b949e; margin-top: 2px; }}
      .step-target {{
        background: #161b22; border: 1px solid #30363d; color: #7ee787;
        font-family: monospace; font-size: 12px; padding: 4px 10px; border-radius: 6px;
      }}
    </style></head><body>
    <div class='card' id='diag'>
      <div class='header'>
        <div class='title-group'>
          <div class='logo-badge'>G</div>
          <div>
            <div class='title'>Gemini Computer Use &bull; Agent Execution Loop Sequence</div>
            <div class='subtitle'>Iterative observation-decision-action cycle over Chrome DevTools Protocol</div>
          </div>
        </div>
        <div class='badge-tag'>Google Cloud Vertex AI</div>
      </div>
      <div class='seq-grid'>
        <div class='actor-box'><div class='actor-title'>Educator / Dev</div><div class='actor-role'>CLI Trigger</div></div>
        <div class='actor-box'><div class='actor-title'>AutoFolio Engine</div><div class='actor-role'>build_portfolio.py</div></div>
        <div class='actor-box'><div class='actor-title'>Active Chrome</div><div class='actor-role'>CDP WebSocket</div></div>
        <div class='actor-box'><div class='actor-title'>Vertex AI</div><div class='actor-role'>gemini-3.8-flash</div></div>
        <div class='actor-box'><div class='actor-title'>Local Artifacts</div><div class='actor-role'>portfolio/ Storage</div></div>
      </div>
      <div class='steps-list'>
        <div class='step-row'>
          <div class='step-num'>1</div>
          <div class='step-content'>
            <div class='step-title'>CDP Session Discovery & Attach</div>
            <div class='step-desc'>Reads DevToolsActivePort from user profile, connects Playwright over WebSocket without re-login.</div>
          </div>
          <div class='step-target'>Chrome &rarr; AutoFolio</div>
        </div>
        <div class='step-row'>
          <div class='step-num'>2</div>
          <div class='step-content'>
            <div class='step-title'>Viewport Capture & Base64 Payload</div>
            <div class='step-desc'>Takes active 1280&times;800 viewport screenshot, converts to JPEG, bundles with conversation history.</div>
          </div>
          <div class='step-target'>AutoFolio &rarr; Vertex AI</div>
        </div>
        <div class='step-row'>
          <div class='step-num'>3</div>
          <div class='step-content'>
            <div class='step-title'>Spatial Reasoning & Prompt Injection Defense</div>
            <div class='step-desc'>Gemini 3.8 Flash scans layout, inspects UI elements, verifies safety policies, and outputs tool call.</div>
          </div>
          <div class='step-target'>Vertex AI Engine</div>
        </div>
        <div class='step-row'>
          <div class='step-num'>4</div>
          <div class='step-content'>
            <div class='step-title'>Dual Tool Dispatch: Native GUI vs Custom Domain Tools</div>
            <div class='step-desc'>Denormalizes coordinates for click/scroll OR executes DOM scripts to save proof screenshots & media.</div>
          </div>
          <div class='step-target'>Chrome / File I/O</div>
        </div>
        <div class='step-row'>
          <div class='step-num'>5</div>
          <div class='step-content'>
            <div class='step-title'>Synthesis & Deliverable Generation</div>
            <div class='step-desc'>Compiles verified evidence into portfolio.html, hkust_cs_recommendation_letter.md, and manifest.json.</div>
          </div>
          <div class='step-target'>portfolio/ Output</div>
        </div>
      </div>
    </div></body></html>"""
    page.set_content(html)
    page.locator('#diag').screenshot(path='E:/working/gemini-computer-use/assets/diagram_sequence_loop.png')


def generate_coordinate_pipeline(page):
    html = f"""<!DOCTYPE html><html><head><meta charset='utf-8'><style>{COMMON_CSS}
      .pipeline-row {{ display: flex; align-items: stretch; gap: 14px; margin-bottom: 24px; }}
      .pipe-card {{
        background: #0d1117; border: 1px solid #30363d; border-radius: 12px;
        padding: 18px; flex: 1; display: flex; flex-direction: column; justify-content: space-between;
      }}
      .pipe-step {{ font-size: 11px; font-weight: 700; color: #58a6ff; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; }}
      .pipe-title {{ font-size: 15px; font-weight: 700; color: #ffffff; margin-bottom: 6px; }}
      .pipe-desc {{ font-size: 12px; color: #8b949e; line-height: 1.4; }}
      .pipe-val {{
        background: #161b22; border: 1px solid #21262d; border-radius: 8px;
        padding: 8px 10px; margin-top: 12px; font-family: monospace; font-size: 12px; color: #7ee787;
      }}
      .arrow-col {{ display: flex; align-items: center; color: #58a6ff; font-size: 22px; font-weight: bold; }}
      .formula-box {{
        background: #0d1117; border: 1px solid #30363d; border-radius: 12px;
        padding: 20px 24px; display: flex; align-items: center; justify-content: space-around;
      }}
      .formula-item {{
        font-family: 'Fira Code', monospace; font-size: 16px; color: #f0f6fc;
        display: flex; align-items: center; gap: 12px;
      }}
      .f-frac {{ display: inline-flex; flex-direction: column; align-items: center; }}
      .f-top {{ border-bottom: 2px solid #58a6ff; padding: 0 6px 2px 6px; color: #ff7b72; }}
      .f-bot {{ padding-top: 2px; color: #ffa657; font-weight: 600; }}
    </style></head><body>
    <div class='card' id='diag'>
      <div class='header'>
        <div class='title-group'>
          <div class='logo-badge'>G</div>
          <div>
            <div class='title'>Google Cloud &bull; Coordinate Normalization & Denormalization Pipeline</div>
            <div class='subtitle'>Resolution-independent spatial targeting from Gemini 0..1000 grid to browser pixels</div>
          </div>
        </div>
        <div class='badge-tag'>Spatial UI Perception</div>
      </div>
      <div class='pipeline-row'>
        <div class='pipe-card'>
          <div>
            <div class='pipe-step'>Step 1: Viewport Capture</div>
            <div class='pipe-title'>Physical Browser Tab</div>
            <div class='pipe-desc'>Chrome renders at user's native resolution.</div>
          </div>
          <div class='pipe-val'>1280 &times; 800 px</div>
        </div>
        <div class='arrow-col'>&rarr;</div>
        <div class='pipe-card'>
          <div>
            <div class='pipe-step'>Step 2: Vision Encoding</div>
            <div class='pipe-title'>Gemini 3.8 Flash Grid</div>
            <div class='pipe-desc'>Normalized to [0, 1000] scale independently of screen size.</div>
          </div>
          <div class='pipe-val'>norm_x: 450, norm_y: 320</div>
        </div>
        <div class='arrow-col'>&rarr;</div>
        <div class='pipe-card'>
          <div>
            <div class='pipe-step'>Step 3: Scaling Engine</div>
            <div class='pipe-title'>Denormalization Math</div>
            <div class='pipe-desc'>Multiplies normalized coordinate by physical dimensions / 1000.</div>
          </div>
          <div class='pipe-val'>x = 450 * 1280 / 1000</div>
        </div>
        <div class='arrow-col'>&rarr;</div>
        <div class='pipe-card'>
          <div>
            <div class='pipe-step'>Step 4: Dispatch Action</div>
            <div class='pipe-title'>Playwright Click</div>
            <div class='pipe-desc'>Executes mouse click at calibrated target location.</div>
          </div>
          <div class='pipe-val'>click(576 px, 256 px)</div>
        </div>
      </div>
      <div class='formula-box'>
        <div class='formula-item'>
          <span style='color:#79c0ff; font-weight:700;'>pixel_x</span> = 
          <div class='f-frac'><span class='f-top'>normalized_x &times; viewport_width</span><span class='f-bot'>1000</span></div>
        </div>
        <div style='color:#484f58; font-size:24px;'>|</div>
        <div class='formula-item'>
          <span style='color:#79c0ff; font-weight:700;'>pixel_y</span> = 
          <div class='f-frac'><span class='f-top'>normalized_y &times; viewport_height</span><span class='f-bot'>1000</span></div>
        </div>
      </div>
    </div></body></html>"""
    page.set_content(html)
    page.locator('#diag').screenshot(path='E:/working/gemini-computer-use/assets/diagram_coordinate_pipeline.png')


def generate_hybrid_tools(page):
    html = f"""<!DOCTYPE html><html><head><meta charset='utf-8'><style>{COMMON_CSS}
      .split-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }}
      .branch-box {{
        background: #0d1117; border: 1px solid #30363d; border-radius: 12px; padding: 20px;
      }}
      .branch-header {{
        display: flex; align-items: center; justify-content: space-between;
        margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid #21262d;
      }}
      .branch-title {{ font-size: 16px; font-weight: 700; color: #ffffff; }}
      .branch-badge {{ font-size: 11px; padding: 4px 8px; border-radius: 6px; font-weight: 600; }}
      .badge-native {{ background: rgba(88, 166, 255, 0.15); color: #58a6ff; border: 1px solid #1a73e8; }}
      .badge-custom {{ background: rgba(126, 231, 135, 0.15); color: #7ee787; border: 1px solid #2ea043; }}
      
      .tool-list {{ display: flex; flex-direction: column; gap: 10px; }}
      .tool-item {{
        background: #161b22; border: 1px solid #21262d; border-radius: 8px;
        padding: 10px 14px; display: flex; align-items: center; justify-content: space-between;
      }}
      .tool-name {{ font-family: monospace; font-size: 13px; font-weight: 600; color: #f0f6fc; }}
      .tool-desc {{ font-size: 12px; color: #8b949e; }}
      
      .sync-bar {{
        background: #1f293d; border: 1px solid #1a73e8; border-radius: 10px;
        padding: 14px 20px; text-align: center; color: #e6edf3; font-size: 13px; font-weight: 500;
      }}
    </style></head><body>
    <div class='card' id='diag'>
      <div class='header'>
        <div class='title-group'>
          <div class='logo-badge'>G</div>
          <div>
            <div class='title'>Google Cloud &bull; Hybrid Tool Calling Dual-Dispatch Engine</div>
            <div class='subtitle'>Combining native ComputerUse GUI actions with custom FunctionDeclarations in a single turn</div>
          </div>
        </div>
        <div class='badge-tag'>Unified Agent Tooling</div>
      </div>
      <div class='split-grid'>
        <div class='branch-box'>
          <div class='branch-header'>
            <div class='branch-title'>Native ComputerUse Tool</div>
            <div class='branch-badge badge-native'>types.ComputerUse</div>
          </div>
          <div class='tool-list'>
            <div class='tool-item'><span class='tool-name'>click_at(x, y)</span><span class='tool-desc'>Mouse click with denormalized coords</span></div>
            <div class='tool-item'><span class='tool-name'>scroll_page(direction)</span><span class='tool-desc'>Smooth viewport vertical scrolling</span></div>
            <div class='tool-item'><span class='tool-name'>type_text_at(text, x, y)</span><span class='tool-desc'>Focus input field & dispatch keystrokes</span></div>
            <div class='tool-item'><span class='tool-name'>navigate(url)</span><span class='tool-desc'>Direct sub-page navigation</span></div>
            <div class='tool-item'><span class='tool-name'>wait_5_seconds()</span><span class='tool-desc'>Wait for dynamic feed DOM render</span></div>
          </div>
        </div>
        <div class='branch-box'>
          <div class='branch-header'>
            <div class='branch-title'>Custom AutoFolio Tools</div>
            <div class='branch-badge badge-custom'>types.FunctionDeclaration</div>
          </div>
          <div class='tool-list'>
            <div class='tool-item'><span class='tool-name'>save_evidence_screenshot</span><span class='tool-desc'>Crop & watermark verified proof PNG</span></div>
            <div class='tool-item'><span class='tool-name'>extract_and_save_page_images</span><span class='tool-desc'>DOM evaluate & download post media</span></div>
            <div class='tool-item'><span class='tool-name'>record_portfolio_item</span><span class='tool-desc'>Append structured item to manifest.json</span></div>
            <div class='tool-item'><span class='tool-name'>yield_to_user</span><span class='tool-desc'>HITL review / safety confirmation</span></div>
          </div>
        </div>
      </div>
      <div class='sync-bar'>
        &bull; Synchronized Browser State &bull; Playwright returns observation &bull; Next base64 screenshot feeds back into Vertex AI
      </div>
    </div></body></html>"""
    page.set_content(html)
    page.locator('#diag').screenshot(path='E:/working/gemini-computer-use/assets/diagram_hybrid_tools.png')


def generate_linkedin_stages(page):
    html = f"""<!DOCTYPE html><html><head><meta charset='utf-8'><style>{COMMON_CSS}
      .stages-row {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; margin-bottom: 20px; }}
      .stage-card {{
        background: #0d1117; border: 1px solid #30363d; border-radius: 12px;
        padding: 16px 12px; display: flex; flex-direction: column; justify-content: space-between;
      }}
      .st-badge {{
        background: #1a73e8; color: white; width: 24px; height: 24px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700; margin-bottom: 8px;
      }}
      .st-title {{ font-size: 13px; font-weight: 700; color: #ffffff; margin-bottom: 6px; }}
      .st-path {{ font-family: monospace; font-size: 10px; color: #58a6ff; margin-bottom: 8px; }}
      .st-bullets {{ font-size: 11px; color: #8b949e; line-height: 1.4; }}
      
      .synth-box {{
        background: #161b22; border: 1px solid #238636; border-radius: 12px;
        padding: 16px 24px; display: flex; align-items: center; justify-content: space-between;
      }}
      .synth-title {{ font-size: 15px; font-weight: 700; color: #7ee787; }}
      .synth-desc {{ font-size: 12px; color: #8b949e; margin-top: 2px; }}
      .synth-tags {{ display: flex; gap: 8px; }}
      .synth-tag {{
        background: rgba(46, 160, 67, 0.15); border: 1px solid #238636;
        color: #7ee787; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 600;
      }}
    </style></head><body>
    <div class='card' id='diag'>
      <div class='header'>
        <div class='title-group'>
          <div class='logo-badge'>G</div>
          <div>
            <div class='title'>Google Cloud &bull; 5-Stage LinkedIn Deep Exploration Pipeline</div>
            <div class='subtitle'>Autonomous visual traversal from profile headers to sub-page achievements</div>
          </div>
        </div>
        <div class='badge-tag'>Autonomous Agent Traversal</div>
      </div>
      <div class='stages-row'>
        <div class='stage-card'>
          <div>
            <div class='st-badge'>1</div>
            <div class='st-title'>Profile & Featured</div>
            <div class='st-path'>/in/candidate/</div>
            <div class='st-bullets'>&bull; Headline & About<br>&bull; Featured projects<br>&bull; Education & CGPA</div>
          </div>
        </div>
        <div class='stage-card'>
          <div>
            <div class='st-badge'>2</div>
            <div class='st-title'>Recent Activity</div>
            <div class='st-path'>/recent-activity/all/</div>
            <div class='st-bullets'>&bull; Click &quot;...see more&quot;<br>&bull; Conference talks<br>&bull; Download event photos</div>
          </div>
        </div>
        <div class='stage-card'>
          <div>
            <div class='st-badge'>3</div>
            <div class='st-title'>Honors & Awards</div>
            <div class='st-path'>/details/honors/</div>
            <div class='st-bullets'>&bull; Scholarships<br>&bull; Competition titles<br>&bull; Proof screenshots</div>
          </div>
        </div>
        <div class='stage-card'>
          <div>
            <div class='st-badge'>4</div>
            <div class='st-title'>Volunteering</div>
            <div class='st-path'>/details/volunteering/</div>
            <div class='st-bullets'>&bull; GDG on Campus Lead<br>&bull; Red Hat Ambassador<br>&bull; AWS Cloud Leader</div>
          </div>
        </div>
        <div class='stage-card'>
          <div>
            <div class='st-badge'>5</div>
            <div class='st-title'>Certifications</div>
            <div class='st-path'>/details/certifications/</div>
            <div class='st-bullets'>&bull; AWS & GCP Badges<br>&bull; Red Hat credentials<br>&bull; Issue dates & IDs</div>
          </div>
        </div>
      </div>
      <div class='synth-box'>
        <div>
          <div class='synth-title'>Synthesis & Artifacts Generation Engine</div>
          <div class='synth-desc'>Grounded LLM synthesis compiling all verified screenshots, images, and manifest records.</div>
        </div>
        <div class='synth-tags'>
          <div class='synth-tag'>portfolio.html</div>
          <div class='synth-tag'>recommendation_letter.md</div>
          <div class='synth-tag'>manifest.json</div>
        </div>
      </div>
    </div></body></html>"""
    page.set_content(html)
    page.locator('#diag').screenshot(path='E:/working/gemini-computer-use/assets/diagram_linkedin_stages.png')


def generate_class_batch(page):
    html = f"""<!DOCTYPE html><html><head><meta charset='utf-8'><style>{COMMON_CSS}
      .batch-flow {{ display: flex; align-items: stretch; gap: 14px; margin-bottom: 20px; }}
      .batch-col {{
        background: #0d1117; border: 1px solid #30363d; border-radius: 12px;
        padding: 18px; flex: 1; display: flex; flex-direction: column; justify-content: space-between;
      }}
      .b-step {{ font-size: 11px; font-weight: 700; color: #58a6ff; text-transform: uppercase; margin-bottom: 6px; }}
      .b-title {{ font-size: 15px; font-weight: 700; color: #ffffff; margin-bottom: 8px; }}
      .b-desc {{ font-size: 12px; color: #8b949e; line-height: 1.4; }}
      .b-box {{
        background: #161b22; border: 1px solid #21262d; border-radius: 8px;
        padding: 8px 10px; margin-top: 10px; font-family: monospace; font-size: 11px; color: #7ee787;
      }}
      .b-arrow {{ display: flex; align-items: center; color: #58a6ff; font-size: 22px; font-weight: bold; }}
    </style></head><body>
    <div class='card' id='diag'>
      <div class='header'>
        <div class='title-group'>
          <div class='logo-badge'>G</div>
          <div>
            <div class='title'>Google Cloud &bull; Batch Class Processing Architecture</div>
            <div class='subtitle'>Automated cohort processing from students.txt to unified Class Dashboard</div>
          </div>
        </div>
        <div class='badge-tag'>Educator Batch Runner</div>
      </div>
      <div class='batch-flow'>
        <div class='batch-col'>
          <div>
            <div class='b-step'>Input File</div>
            <div class='b-title'>students.txt</div>
            <div class='b-desc'>Plain-text roster of student names & LinkedIn profile URLs.</div>
          </div>
          <div class='b-box'>Name | URL per line</div>
        </div>
        <div class='b-arrow'>&rarr;</div>
        <div class='batch-col'>
          <div>
            <div class='b-step'>Batch Loop</div>
            <div class='b-title'>Cohort Controller</div>
            <div class='b-desc'>Iterates through candidates, isolating state & browser contexts.</div>
          </div>
          <div class='b-box'>build_portfolio.py --profiles-file</div>
        </div>
        <div class='b-arrow'>&rarr;</div>
        <div class='batch-col'>
          <div>
            <div class='b-step'>Student Subfolders</div>
            <div class='b-title'>Isolated Artifacts</div>
            <div class='b-desc'>Generates dedicated portfolio, letter, and screenshots per candidate.</div>
          </div>
          <div class='b-box'>class_portfolios/&lt;handle&gt;/</div>
        </div>
        <div class='b-arrow'>&rarr;</div>
        <div class='batch-col'>
          <div>
            <div class='b-step'>Class Portal</div>
            <div class='b-title'>Class Dashboard</div>
            <div class='b-desc'>Consolidates all students into a master index with quick links & badges.</div>
          </div>
          <div class='b-box'>class_portfolios/index.html</div>
        </div>
      </div>
    </div></body></html>"""
    page.set_content(html)
    page.locator('#diag').screenshot(path='E:/working/gemini-computer-use/assets/diagram_class_batch.png')


if __name__ == '__main__':
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(device_scale_factor=2)
        print("Rendering sequence diagram...")
        generate_sequence_diagram(page)
        print("Rendering coordinate pipeline...")
        generate_coordinate_pipeline(page)
        print("Rendering hybrid tools...")
        generate_hybrid_tools(page)
        print("Rendering linkedin stages...")
        generate_linkedin_stages(page)
        print("Rendering class batch...")
        generate_class_batch(page)
        browser.close()
    print("All Google Cloud styled diagrams generated successfully!")
