"""Generate a 4-Page Supporting Document (PDF, DOCX, and HTML) for HKUST CS Admission.

Features:
- Strictly formatted as a 4-page A4 document.
- 2-column table layout: Left column = Photo / Cropped Visual Evidence, Right column = Supporting Details.
- Ranked by Impact & Relevance to HKUST Computer Science Admission (rather than chronological order):
    Page 1: Rank #1–#3 (Triple Tech Community Leadership, Enterprise MoU Keynote, Academic Excellence & Scholarships)
    Page 2: Rank #4–#6 (Flagship Tech Conference Presentations: PyCon HK, AWS Summit & HKOSCon, Google HK & AWS UG)
    Page 3: Rank #7–#9 (Regional Competition Championships, ESG & Smart City Innovation, 16 Cloud & Linux Credentials)
    Page 4: Rank #10–#12 (Public AI Outreach, Youth College Academic Transformation, Endorsement Summary)
"""

import html
from pathlib import Path
from PIL import Image
from docx import Document
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Inches, Pt, RGBColor
from playwright.sync_api import sync_playwright

PORTFOLIO_DIR = Path("portfolio").resolve()
SCREENSHOTS_DIR = PORTFOLIO_DIR / "screenshots"
IMAGES_DIR = PORTFOLIO_DIR / "images"
CROPPED_DIR = PORTFOLIO_DIR / "supporting_doc_crops"
CROPPED_DIR.mkdir(parents=True, exist_ok=True)


def crop_screenshot(src_name: str, out_name: str, box: tuple[int, int, int, int]) -> Path:
    """Crop the main LinkedIn content card from a 1920x1008 screenshot."""
    src_path = SCREENSHOTS_DIR / src_name
    out_path = CROPPED_DIR / out_name
    with Image.open(src_path) as im:
        w, h = im.size
        # Scale box if resolution differs from 1920x1008
        sx, sy = w / 1920.0, h / 1008.0
        scaled_box = (
            int(box[0] * sx),
            int(box[1] * sy),
            int(box[2] * sx),
            int(box[3] * sy),
        )
        cropped = im.crop(scaled_box)
        cropped.save(out_path, format="PNG")
    return out_path


def prepare_visual_assets() -> dict[str, Path]:
    """Prepare clean, high-visibility photos and cropped evidence cards for all 12 ranked items."""
    assets = {
        # Page 1
        "rank1_leadership": IMAGES_DIR / "img_05_profile_featured.jpg",
        "rank2_microsoft_mou": IMAGES_DIR / "img_02_profile_featured.jpg",
        "rank3_scholarships": crop_screenshot(
            "05_scholarship_award_Honors_Awards_Page_-_Section_1.png",
            "crop_rank3_scholarships.png",
            (370, 125, 1185, 675),
        ),
        # Page 2
        "rank4_pycon": IMAGES_DIR / "img_09_pycon_hk.jpg",
        "rank5_conferences": crop_screenshot(
            "10_leadership_Volunteering_Leadership_-_AWS_Summit_HKOSCon_Google_Cloud_Le.png",
            "crop_rank5_aws_hkoscon.png",
            (370, 115, 1185, 760),
        ),
        "rank6_gdg_awsug": crop_screenshot(
            "08_leadership_Volunteering_Leadership_-_Red_Hat_AWS_Leader_GDG_Leader.png",
            "crop_rank6_gdg_awsug.png",
            (370, 540, 1185, 1000),
        ),
        # Page 3
        "rank7_gba_awards": crop_screenshot(
            "06_scholarship_award_Honors_Awards_Page_-_Section_2.png",
            "crop_rank7_gba_awards.png",
            (370, 140, 1185, 625),
        ),
        "rank8_esg_city_it": crop_screenshot(
            "06_scholarship_award_Honors_Awards_Page_-_Section_2.png",
            "crop_rank8_esg_city_it.png",
            (370, 610, 1185, 920),
        ),
        "rank9_certifications": crop_screenshot(
            "11_certification_Certifications_-_Part_1_Google_Cloud_GKE.png",
            "crop_rank9_certifications.png",
            (370, 125, 1185, 720),
        ),
        # Page 4
        "rank10_ai_media": IMAGES_DIR / "img_04_profile_featured.jpg",
        "rank11_campus_demo": IMAGES_DIR / "img_03_profile_featured.jpg",
        "rank12_redhat_premier": IMAGES_DIR / "img_07_profile_featured.jpg",
    }
    return assets


def get_pages_data(assets: dict[str, Path]) -> list[dict]:
    """Return the 4 structured pages, re-ranked by strategic impact for HKUST CS admission."""
    return [
        {
            "page_num": 1,
            "page_title": "TIER 1: TECH COMMUNITY LEADERSHIP, INDUSTRY REPRESENTATION & ACADEMIC EXCELLENCE",
            "items": [
                {
                    "rank": "RANK #1 — TRIPLE CAMPUS TECH COMMUNITY LEADERSHIP",
                    "title": "1st AWS Student Builder Leader, GDG on Campus Leader & Red Hat Ambassador",
                    "image": assets["rank1_leadership"],
                    "caption": "Esther with HKIIT Cloud Innovation Centre mentor Cyrus Wong & industry leadership",
                    "bullets": [
                        "Simultaneously leads three major developer communities at HKIIT: Inaugural AWS Student Builder Group Leader '26, Google Developer Group (GDG) on Campus Leader, and Hong Kong's first Red Hat Student Ambassador.",
                        "Organizes campus Cloud Study Jams, AI workshops, and peer study groups—empowering fellow students to learn cloud computing, Linux, and container technologies.",
                        "Why it matters for HKUST CS: Demonstrates rare initiative, peer mentorship, and ecosystem-building leadership that will enrich HKUST's student computing community.",
                    ],
                },
                {
                    "rank": "RANK #2 — FLAGSHIP INSTITUTIONAL & ENTERPRISE REPRESENTATION",
                    "title": "Student Keynote Presenter — HKIIT × Microsoft Hong Kong MoU Signing Ceremony",
                    "image": assets["rank2_microsoft_mou"],
                    "caption": "Official MoU Signing Ceremony between HKIIT and Microsoft Hong Kong (21 Aug 2026)",
                    "bullets": [
                        "Selected as the sole student keynote presenter to represent HKIIT before Microsoft Hong Kong executives and VTC senior leadership.",
                        "Delivered live demonstrations of student-built AI solutions (ProvePresent & AI Virtual Tutor), translating technical cloud workflows into clear, impactful presentations.",
                        "Why it matters for HKUST CS: Proves exceptional communication poise, reliability under pressure, and ability to bridge academic projects with industry stakeholders.",
                    ],
                },
                {
                    "rank": "RANK #3 — ACADEMIC EXCELLENCE & PRESTIGIOUS SCHOLARSHIPS",
                    "title": "3.91 / 4.0 CGPA, The Cathay Group Scholarship & Lei Foundation Scholarship",
                    "image": assets["rank3_scholarships"],
                    "caption": "Verified LinkedIn Honors record: Lei Foundation & Cathay Group Scholarships",
                    "bullets": [
                        "Maintains a near-perfect Cumulative GPA of 3.91 / 4.0 in the Higher Diploma in Cloud and Data Centre Administration at HKIIT / IVE (Lee Wai Lee).",
                        "Awarded both The Cathay Group Scholarship 2025/26 (recognizing top VTC talent in aviation and technology) and the Lei Foundation Scholarship for academic & leadership distinction.",
                        "Why it matters for HKUST CS: Confirms her strong academic discipline, consistent work ethic, and readiness for rigorous university-level coursework.",
                    ],
                },
            ],
        },
        {
            "page_num": 2,
            "page_title": "TIER 2: PUBLIC SPEAKING, OPEN-SOURCE CONFERENCES & DEVELOPER ADVOCACY",
            "items": [
                {
                    "rank": "RANK #4 — NATIONAL & REGIONAL CONFERENCE CO-SPEAKER (PYCON HK 2026)",
                    "title": "PyCon Hong Kong 2026: Transforming 'Hong Kong Zero' into a Kubernetes Learning Platform",
                    "image": assets["rank4_pycon"],
                    "caption": "Official PyCon HK 2026 Speaker Poster (Cyrus Wong, Esther Cheung, Arthur Chin)",
                    "bullets": [
                        "Invited co-speaker presenting '從港域時空到 Kubernetes：將香港遊戲世界化身雲原生學習平台' (From Hong Kong Zero to Kubernetes).",
                        "Collaborated with mentors and teammates to validate the gamified student learning experience and demonstrate how in-game quests connect to live Kubernetes tasks.",
                        "Why it matters for HKUST CS: Highlights her passion for making complex cloud-native concepts accessible and engaging for beginner developers.",
                    ],
                },
                {
                    "rank": "RANK #5 — INDUSTRY SUMMIT & OPEN-SOURCE CONFERENCE PRESENTER",
                    "title": "AWS Summit Hong Kong 2026 & Hong Kong Open Source Conference (HKOSCon 2026)",
                    "image": assets["rank5_conferences"],
                    "caption": "Verified presenter records for AWS Summit HK 2026 & HKOSCon 2026",
                    "bullets": [
                        "AWS Summit HK 2026 (Developer Zone): Co-presented and assisted with the live robotics demo for 'What Happens When an AI Agent Takes Control of a Robot? [LIT-001]'.",
                        "HKOSCon 2026 Speaker: Presented 'ProvePresent (真出席) - AI Anti-Proxy Attendance Solution' to the Hong Kong open-source community.",
                        "Why it matters for HKUST CS: Shows extraordinary confidence in stepping onto major public tech stages to share applied AI and cloud team projects.",
                    ],
                },
                {
                    "rank": "RANK #6 — DEVELOPER MEETUP & GOOGLE HK COMMUNITY WORKSHOPS",
                    "title": "GDGHK Build with AI (Google HK Office) & AWS User Group Hong Kong Presenter",
                    "image": assets["rank6_gdg_awsug"],
                    "caption": "Verified speaking roles at AWS User Group HK & GDGHK AI Session",
                    "bullets": [
                        "Google Hong Kong Office ('GDGHK Build with AI'): Spoke on 'On-Device Intelligence & Agentic Web' and assisted at Google Cloud Leaders Connect HK 2026.",
                        "AWS User Group HK Meetup: Shared the '#doom × #k8s' interactive live demonstration with local cloud engineers and practitioners.",
                        "Why it matters for HKUST CS: Reflects sustained, active engagement with Hong Kong's professional practitioner communities beyond the classroom.",
                    ],
                },
            ],
        },
        {
            "page_num": 3,
            "page_title": "TIER 3: TEAMWORK IN REGIONAL COMPETITIONS, SOCIAL IMPACT & CERTIFICATIONS",
            "items": [
                {
                    "rank": "RANK #7 — GREATER BAY AREA (GBA) COMPETITION TEAMWORK & CHAMPIONSHIPS",
                    "title": "10th GBA IT Competition First Prize & Outstanding Teamwork Award (+ 9th & 8th GBA Awards)",
                    "image": assets["rank7_gba_awards"],
                    "caption": "Verified certificates for 10th GBA First Prize, Outstanding Teamwork & 9th GBA Second Prize",
                    "bullets": [
                        "Won First Prize (一等獎) and the Outstanding Teamwork Award (團隊協作卓越獎) at the 10th GBA IT Application System Development Competition ('A-Eye' project).",
                        "Also earned Finals Second Prize at the 9th GBA IT Competition, Silver Award at the 8th GBA STEAM Excellence Award (Tertiary ICT), and Best Application Award at the 8th GBA Finals.",
                        "Why it matters for HKUST CS: Serves as the collaborative glue in project teams—excelling at coordination, user-centric design, testing, and pitching.",
                    ],
                },
                {
                    "rank": "RANK #8 — TECHNOLOGY FOR SOCIAL GOOD & SMART CITY INNOVATION",
                    "title": "CLP Energy Saving Competition Gold Award & 2nd City I&T Grand Challenge Innovation Award",
                    "image": assets["rank8_esg_city_it"],
                    "caption": "Media feature on CLP Gold Award & 2nd City I&T Grand Challenge Innovation Award",
                    "bullets": [
                        "Gold Award (CLP Competition 2024): Recognized in local press ('中電辦比賽鼓勵大專學生以科技改善弱勢社群生活') for applying technology to improve the lives of underprivileged communities.",
                        "Innovation Award (2nd City I&T Grand Challenge): Recognized by the HKSAR Innovation and Technology Commission (ITC) for community-focused smart city innovation.",
                        "Why it matters for HKUST CS: Demonstrates strong empathy and a commitment to applying computing for social good and community well-being.",
                    ],
                },
                {
                    "rank": "RANK #9 — SELF-MOTIVATED MULTI-CLOUD & LINUX LEARNING (16 CREDENTIALS)",
                    "title": "16 Verified Certifications Across Google Cloud (GKE), Red Hat (Linux/Ansible) & AWS",
                    "image": assets["rank9_certifications"],
                    "caption": "Verified Google Kubernetes Engine (GKE) & Cloud Infrastructure credentials",
                    "bullets": [
                        "Proactively completed 16 industry certifications and skill badges to better understand the cloud and open-source technologies she advocates for.",
                        "Includes AWS Certified Cloud Practitioner, Google Cloud GKE Skill Badges, and 4 Red Hat credentials (RH124 System Admin, RH294 Ansible, DO188 Podman/OpenShift, CL110 OpenStack).",
                        "Why it matters for HKUST CS: Proves her self-discipline and eagerness to build solid technical foundations alongside her community work.",
                    ],
                },
            ],
        },
        {
            "page_num": 4,
            "page_title": "TIER 4: PUBLIC AI OUTREACH, ACADEMIC TRANSFORMATION & ENDORSEMENT SUMMARY",
            "items": [
                {
                    "rank": "RANK #10 — PUBLIC AI OUTREACH, MEDIA AMBASSADOR & ELDERLY TECH LITERACY",
                    "title": "Featured Student in '與其怕AI，不如讀AI' Media Series & CLP Elderly AI Workshops",
                    "image": assets["rank10_ai_media"],
                    "caption": "Featured media interview promoting AI & Cloud education at HKIIT",
                    "bullets": [
                        "Featured in public media interviews ('與其怕AI，不如讀AI') and HKIIT Info Days, demystifying AI and cloud computing for secondary students and parents.",
                        "Volunteered as a workshop presenter with CLP Power Hong Kong (Apr 2026) to teach elderly citizens practical, everyday uses of generative AI.",
                        "Why it matters for HKUST CS: Embodies an inclusive, service-oriented mindset—sharing technology knowledge with both youth and senior citizens.",
                    ],
                },
                {
                    "rank": "RANK #11 — CAMPUS AMBASSADOR & UPWARD ACADEMIC TRANSFORMATION",
                    "title": "From Youth College Outstanding Learning Award to 3.91 CGPA Higher Diploma Leader",
                    "image": assets["rank11_campus_demo"],
                    "caption": "Esther demonstrating cloud & AI learning experiences in campus video series",
                    "bullets": [
                        "While earlier secondary public exam results did not reflect her potential, Esther blossomed completely once she found her passion in Information Technology.",
                        "Earned the Youth College Outstanding Learning Award & Extracurricular Award (2023) before achieving a 3.91 / 4.0 CGPA and 13 honors in her Higher Diploma.",
                        "Why it matters for HKUST CS: Her sustained tertiary excellence proves her true academic aptitude and determination to succeed at university.",
                    ],
                },
                {
                    "rank": "RANK #12 — INSTITUTIONAL IMPACT & WHY HKUST COMPUTER SCIENCE",
                    "title": "Driving HKIIT to Red Hat Premier Tier & Seeking Deeper CS Foundations at HKUST",
                    "image": assets["rank12_redhat_premier"],
                    "caption": "Official Red Hat Academy Premier Tier recognition supported by Esther's ambassadorship",
                    "bullets": [
                        "Her active student ambassadorship helped propel HKIIT to the highest 'Premier Tier' in the Red Hat Academy Excellence Program.",
                        "Self-aware & growth-oriented: Having experienced the tech industry through community leadership and live demos, she is eager to strengthen her core coding and theoretical CS depth at HKUST.",
                        "Mentor's Endorsement (Cyrus Wong, Senior Lecturer): 'Esther will bring unmatched energy, teamwork, and community leadership to HKUST CSE.'",
                    ],
                },
            ],
        },
    ]


def build_html_and_pdf(pages_data: list[dict], html_path: Path, pdf_path: Path) -> None:
    """Generate a 4-page print-exact HTML document and render it to a 4-page A4 PDF via Playwright."""
    pages_html = []
    for page in pages_data:
        rows_html = []
        for item in page["items"]:
            img_rel = item["image"].relative_to(PORTFOLIO_DIR).as_posix()
            bullets_html = "".join(
                f"<li>{html.escape(b)}</li>" for b in item["bullets"]
            )
            rows_html.append(
                f"""
                <tr>
                    <td class="photo-cell">
                        <div class="img-wrap">
                            <img src="{html.escape(img_rel)}" alt="{html.escape(item['title'])}" />
                        </div>
                        <div class="caption">{html.escape(item['caption'])}</div>
                    </td>
                    <td class="detail-cell">
                        <div class="rank-badge">{html.escape(item['rank'])}</div>
                        <div class="item-title">{html.escape(item['title'])}</div>
                        <ul class="bullet-list">
                            {bullets_html}
                        </ul>
                    </td>
                </tr>
                """
            )

        pages_html.append(
            f"""
            <div class="page">
                <div class="page-header">
                    <div class="header-left">
                        <strong>OTHER SUPPORTING DOCUMENT — HKUST BEng in Computer Science Application</strong><br/>
                        <span>Candidate: Hiu Tung Cheung (Esther / 張曉彤) &bull; HKIIT / IVE (Lee Wai Lee) &bull; CGPA: 3.91 / 4.0</span>
                    </div>
                    <div class="header-right">
                        Page {page['page_num']} of 4<br/>
                        <span class="sub">Ranked by Impact</span>
                    </div>
                </div>
                <div class="tier-banner">{html.escape(page['page_title'])}</div>
                <table class="evidence-table">
                    <colgroup>
                        <col style="width: 38%;" />
                        <col style="width: 62%;" />
                    </colgroup>
                    <thead>
                        <tr>
                            <th>Visual Evidence / Activity Photo</th>
                            <th>Supporting Details &amp; Relevance to HKUST Computer Science</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(rows_html)}
                    </tbody>
                </table>
                <div class="page-footer">
                    Verified &amp; Compiled by Cyrus Wong (黃俊彥), Senior Lecturer, Department of Information Technology, HKIIT &bull; LinkedIn AutoFolio Evidence Portfolio
                </div>
            </div>
            """
        )

    doc_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>Supporting Document — Hiu Tung Cheung (Esther) — HKUST CS Application</title>
    <style>
        @page {{
            size: A4 portrait;
            margin: 10mm 12mm;
        }}
        * {{
            box-sizing: border-box;
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
        }}
        body {{
            font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, Roboto, "Microsoft JhengHei", sans-serif;
            margin: 0;
            padding: 0;
            background: #e2e8f0;
            color: #1e293b;
            font-size: 9.2pt;
            line-height: 1.38;
        }}
        .page {{
            width: 186mm;
            height: 276mm;
            background: #ffffff;
            margin: 6mm auto;
            padding: 4mm 5mm;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            page-break-after: always;
            break-after: page;
            overflow: hidden;
        }}
        .page:last-child {{
            page-break-after: auto;
            break-after: auto;
        }}
        @media print {{
            body {{ background: #ffffff; }}
            .page {{
                width: 100%;
                height: 276mm;
                margin: 0;
                padding: 0;
                box-shadow: none;
            }}
        }}
        .page-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid #003366;
            padding-bottom: 4px;
            margin-bottom: 5px;
            font-size: 8.5pt;
        }}
        .header-left strong {{
            color: #003366;
            font-size: 9.5pt;
        }}
        .header-left span {{
            color: #475569;
        }}
        .header-right {{
            text-align: right;
            font-weight: 700;
            color: #003366;
            font-size: 9pt;
        }}
        .header-right .sub {{
            font-weight: 400;
            font-size: 7.5pt;
            color: #64748b;
        }}
        .tier-banner {{
            background: #003366;
            color: #ffffff;
            font-weight: 700;
            font-size: 8.5pt;
            padding: 4px 8px;
            border-radius: 4px;
            margin-bottom: 6px;
            letter-spacing: 0.3px;
        }}
        .evidence-table {{
            width: 100%;
            border-collapse: collapse;
            table-layout: fixed;
            flex-grow: 1;
        }}
        .evidence-table th {{
            background: #f1f5f9;
            color: #0f172a;
            font-size: 8.2pt;
            text-align: left;
            padding: 5px 8px;
            border: 1px solid #cbd5e1;
        }}
        .evidence-table td {{
            border: 1px solid #cbd5e1;
            padding: 7px 9px;
            vertical-align: top;
            height: 76mm;
        }}
        .photo-cell {{
            background: #f8fafc;
            text-align: center;
            vertical-align: middle !important;
        }}
        .img-wrap {{
            width: 100%;
            height: 60mm;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 4px;
        }}
        .img-wrap img {{
            max-width: 100%;
            max-height: 58mm;
            object-fit: contain;
            display: block;
        }}
        .caption {{
            font-size: 7.4pt;
            color: #475569;
            margin-top: 4px;
            line-height: 1.25;
            font-style: italic;
        }}
        .detail-cell {{
            background: #ffffff;
        }}
        .rank-badge {{
            display: inline-block;
            background: #e0f2fe;
            color: #0369a1;
            font-weight: 700;
            font-size: 7.5pt;
            padding: 2px 6px;
            border-radius: 3px;
            margin-bottom: 3px;
        }}
        .item-title {{
            font-weight: 700;
            font-size: 9.8pt;
            color: #0f172a;
            margin-bottom: 5px;
            line-height: 1.25;
        }}
        .bullet-list {{
            margin: 0;
            padding-left: 15px;
        }}
        .bullet-list li {{
            margin-bottom: 4.5px;
            font-size: 8.6pt;
            line-height: 1.35;
            color: #1e293b;
        }}
        .page-footer {{
            border-top: 1px solid #cbd5e1;
            padding-top: 4px;
            margin-top: 5px;
            font-size: 7.5pt;
            color: #64748b;
            text-align: center;
        }}
    </style>
</head>
<body>
    {''.join(pages_html)}
</body>
</html>
"""
    html_path.write_text(doc_html, encoding="utf-8")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(html_path.as_uri(), wait_until="networkidle")
        page.pdf(
            path=str(pdf_path),
            format="A4",
            print_background=True,
            margin={"top": "10mm", "bottom": "10mm", "left": "12mm", "right": "12mm"},
        )
        browser.close()


def set_cell_shading(cell, color_hex: str) -> None:
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading)


def build_docx(pages_data: list[dict], docx_path: Path) -> None:
    """Generate an editable 4-page Word (.docx) supporting document with a 2-column table per page."""
    doc = Document()

    # Set A4 page dimensions and compact margins
    for section in doc.sections:
        section.page_width = Inches(8.27)
        section.page_height = Inches(11.69)
        section.top_margin = Inches(0.4)
        section.bottom_margin = Inches(0.4)
        section.left_margin = Inches(0.45)
        section.right_margin = Inches(0.45)

    for idx, page in enumerate(pages_data):
        if idx > 0:
            doc.add_page_break()

        # Header paragraph
        hdr = doc.add_paragraph()
        hdr.paragraph_format.space_before = Pt(0)
        hdr.paragraph_format.space_after = Pt(2)
        r1 = hdr.add_run(
            f"OTHER SUPPORTING DOCUMENT (Page {page['page_num']} of 4) — HKUST BEng in CS Application\n"
        )
        r1.bold = True
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = RGBColor(0x00, 0x33, 0x66)

        r2 = hdr.add_run(
            f"Candidate: Hiu Tung Cheung (Esther / 張曉彤) | HKIIT / IVE (Lee Wai Lee) | CGPA: 3.91 / 4.0 | {page['page_title']}"
        )
        r2.font.size = Pt(8)
        r2.font.color.rgb = RGBColor(0x47, 0x55, 0x69)

        # 2-Column Table
        table = doc.add_table(rows=1, cols=2)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.style = "Table Grid"
        table.autofit = False

        col_widths = [Inches(2.75), Inches(4.62)]
        hdr_cells = table.rows[0].cells
        hdr_cells[0].width = col_widths[0]
        hdr_cells[1].width = col_widths[1]
        set_cell_shading(hdr_cells[0], "003366")
        set_cell_shading(hdr_cells[1], "003366")

        for c_idx, text in enumerate(
            [
                "Visual Evidence / Photo",
                "Supporting Details & Relevance to HKUST CS (Re-Ranked by Impact)",
            ]
        ):
            p = hdr_cells[c_idx].paragraphs[0]
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            run = p.add_run(text)
            run.bold = True
            run.font.size = Pt(8.5)
            run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

        for item in page["items"]:
            row = table.add_row()
            c_left, c_right = row.cells[0], row.cells[1]
            c_left.width = col_widths[0]
            c_right.width = col_widths[1]
            c_left.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            c_right.vertical_alignment = WD_ALIGN_VERTICAL.TOP
            set_cell_shading(c_left, "F8FAFC")

            # Left cell: Photo + caption
            p_img = c_left.paragraphs[0]
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(2)
            p_img.paragraph_format.space_after = Pt(2)

            # Scale image to fit cleanly inside 2.55" x 1.95"
            with Image.open(item["image"]) as im:
                iw, ih = im.size
                aspect = iw / float(ih)
                max_w, max_h = 2.52, 1.85
                if max_w / aspect <= max_h:
                    draw_w = Inches(max_w)
                    draw_h = Inches(max_w / aspect)
                else:
                    draw_h = Inches(max_h)
                    draw_w = Inches(max_h * aspect)

            p_img.add_run().add_picture(str(item["image"]), width=draw_w, height=draw_h)

            p_cap = c_left.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_before = Pt(1)
            p_cap.paragraph_format.space_after = Pt(2)
            r_cap = p_cap.add_run(item["caption"])
            r_cap.italic = True
            r_cap.font.size = Pt(7.2)
            r_cap.font.color.rgb = RGBColor(0x47, 0x55, 0x69)

            # Right cell: Rank badge, Title, Bullets
            p_title = c_right.paragraphs[0]
            p_title.paragraph_format.space_before = Pt(2)
            p_title.paragraph_format.space_after = Pt(3)

            r_rank = p_title.add_run(f"[{item['rank']}]\n")
            r_rank.bold = True
            r_rank.font.size = Pt(7.5)
            r_rank.font.color.rgb = RGBColor(0x03, 0x69, 0xA1)

            r_ttl = p_title.add_run(item["title"])
            r_ttl.bold = True
            r_ttl.font.size = Pt(9.5)
            r_ttl.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

            for b in item["bullets"]:
                p_b = c_right.add_paragraph()
                p_b.paragraph_format.space_before = Pt(1)
                p_b.paragraph_format.space_after = Pt(2)
                p_b.paragraph_format.left_indent = Inches(0.12)
                r_b = p_b.add_run(f"• {b}")
                r_b.font.size = Pt(8.3)
                r_b.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)

    doc.save(str(docx_path))


def main() -> None:
    assets = prepare_visual_assets()
    pages_data = get_pages_data(assets)

    html_path = PORTFOLIO_DIR / "esther_supporting_document_4pages.html"
    pdf_path = PORTFOLIO_DIR / "esther_supporting_document_4pages.pdf"
    docx_path = PORTFOLIO_DIR / "esther_supporting_document_4pages.docx"

    build_html_and_pdf(pages_data, html_path, pdf_path)
    build_docx(pages_data, docx_path)

    print(f"Generated 4-page HTML: {html_path}")
    print(f"Generated 4-page PDF:  {pdf_path}")
    print(f"Generated 4-page DOCX: {docx_path}")


if __name__ == "__main__":
    main()
