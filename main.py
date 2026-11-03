"""Gemini Computer Use Agent implementation using Google Gen AI SDK and Playwright."""

import argparse
import os
import sys
import time
from typing import Any, Dict, List, Tuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from google import genai
from google.auth import exceptions as auth_exceptions
from google.genai import types
from google.genai.types import Content, FunctionResponse, Part
from playwright.sync_api import sync_playwright
import termcolor

DEFAULT_SCREEN_WIDTH = 1440
DEFAULT_SCREEN_HEIGHT = 900
DEFAULT_PROJECT = "cyrus-testing-2023"
DEFAULT_MODEL = "gemini-3.8-flash"
DEFAULT_START_URL = "https://www.google.com"
DEFAULT_PROMPT = (
    "Search for flights from San Francisco to Honolulu departing June 30 "
    "and returning July 6."
)


def denormalize_x(x: int, screen_width: int) -> int:
    """Convert normalized x coordinate (0-1000) to actual pixel coordinate."""
    return int(x / 1000 * screen_width)


def denormalize_y(y: int, screen_height: int) -> int:
    """Convert normalized y coordinate (0-1000) to actual pixel coordinate."""
    return int(y / 1000 * screen_height)


def get_safety_confirmation(safety_decision: Dict[str, Any]) -> str:
    """Prompt user for confirmation when safety check is triggered."""
    termcolor.cprint("Safety service requires explicit confirmation!", color="red")
    print(safety_decision.get("explanation", ""))

    decision = ""
    while decision.lower() not in ("y", "n", "ye", "yes", "no"):
        decision = input("Do you wish to proceed? [Y]es/[N]o\n")

    if decision.lower() in ("n", "no"):
        return "TERMINATE"
    return "CONTINUE"


def yield_to_user(reason: str) -> Dict[str, str]:
    """Yields control back to the user for assistance or verification when an automated action is unsafe or ambiguous.

    Args:
        reason: The reason why the agent is yielding control to the human.
    """
    termcolor.cprint(f"\n[Agent yielded to user]: {reason}", color="yellow")
    user_input = input("Press Enter after completing the manual step (or type feedback for the agent): ")
    return {"status": "yielded", "reason": reason, "user_feedback": user_input}


def execute_function_calls(
    response, page, screen_width: int, screen_height: int
) -> List[Tuple[str, Dict[str, Any]]]:
    """Extract and execute modern and legacy function calls from Gemini response."""
    candidate = response.candidates[0]
    function_calls = []
    thoughts = []

    for part in candidate.content.parts:
        if hasattr(part, "function_call") and part.function_call:
            function_calls.append(part.function_call)
        elif hasattr(part, "text") and part.text:
            thoughts.append(part.text)

    if thoughts:
        print(f"Model Reasoning: {' '.join(thoughts)}")

    results: List[Tuple[str, Dict[str, Any]]] = []
    for function_call in function_calls:
        fname = function_call.name
        args = dict(function_call.args) if function_call.args else {}
        action_result: Dict[str, Any] = {}

        print(f" -> Executing: {fname} (Intent: {args.get('intent', 'N/A')})")

        # Check for safety decision before executing
        if "safety_decision" in args:
            decision = get_safety_confirmation(args["safety_decision"])
            if decision == "TERMINATE":
                print("Terminating agent loop")
                break
            action_result["safety_acknowledgement"] = "true"

        try:
            if fname in ("open_web_browser", "open_app", "take_screenshot"):
                pass

            elif fname == "yield_to_user":
                action_result.update(yield_to_user(args.get("reason", "Manual assistance requested.")))

            elif fname in (
                "click",
                "click_at",
                "double_click",
                "triple_click",
                "middle_click",
                "right_click",
                "mouse_down",
                "mouse_up",
                "move",
                "hover_at",
            ):
                actual_x = denormalize_x(args["x"], screen_width)
                actual_y = denormalize_y(args["y"], screen_height)

                if fname in ("click", "click_at"):
                    page.mouse.click(actual_x, actual_y)
                elif fname == "double_click":
                    page.mouse.dblclick(actual_x, actual_y)
                elif fname == "triple_click":
                    page.mouse.click(actual_x, actual_y, click_count=3)
                elif fname == "middle_click":
                    page.mouse.click(actual_x, actual_y, button="middle")
                elif fname == "right_click":
                    page.mouse.click(actual_x, actual_y, button="right")
                elif fname == "mouse_down":
                    page.mouse.move(actual_x, actual_y)
                    page.mouse.down()
                elif fname == "mouse_up":
                    page.mouse.move(actual_x, actual_y)
                    page.mouse.up()
                elif fname in ("move", "hover_at"):
                    page.mouse.move(actual_x, actual_y)

            elif fname in ("type", "type_text_at"):
                actual_x = denormalize_x(args["x"], screen_width) if "x" in args else None
                actual_y = denormalize_y(args["y"], screen_height) if "y" in args else None
                text = args["text"]
                press_enter = args.get("press_enter", False)
                clear_before_typing = args.get("clear_before_typing", True)

                if actual_x is not None and actual_y is not None:
                    page.mouse.click(actual_x, actual_y)
                    time.sleep(0.1)

                if clear_before_typing:
                    page.keyboard.press("ControlOrMeta+A")
                    page.keyboard.press("Backspace")

                page.keyboard.type(text)
                if press_enter:
                    page.keyboard.press("Enter")

            elif fname in ("scroll", "scroll_at", "scroll_document"):
                if "x" in args and "y" in args:
                    page.mouse.move(
                        denormalize_x(args["x"], screen_width),
                        denormalize_y(args["y"], screen_height),
                    )
                direction = args.get("direction", "down")
                magnitude = args.get("magnitude_in_pixels", args.get("magnitude", 300))
                dx, dy = 0, 0
                if direction == "down":
                    dy = magnitude
                elif direction == "up":
                    dy = -magnitude
                elif direction == "right":
                    dx = magnitude
                elif direction == "left":
                    dx = -magnitude
                page.mouse.wheel(dx, dy)

            elif fname == "drag_and_drop":
                start_x = denormalize_x(args.get("start_x", args.get("x", 0)), screen_width)
                start_y = denormalize_y(args.get("start_y", args.get("y", 0)), screen_height)
                end_x = denormalize_x(
                    args.get("end_x", args.get("destination_x", 0)), screen_width
                )
                end_y = denormalize_y(
                    args.get("end_y", args.get("destination_y", 0)), screen_height
                )
                page.mouse.move(start_x, start_y)
                page.mouse.down()
                page.mouse.move(end_x, end_y)
                page.mouse.up()

            elif fname == "press_key":
                page.keyboard.press(args["key"])
            elif fname == "key_down":
                page.keyboard.down(args["key"])
            elif fname == "key_up":
                page.keyboard.up(args["key"])
            elif fname == "hotkey":
                page.keyboard.press("+".join(args.get("keys", [])))
            elif fname == "key_combination":
                page.keyboard.press(args["keys"])
            elif fname == "navigate":
                page.goto(args["url"])
            elif fname == "search":
                page.goto("https://www.google.com")
            elif fname == "go_back":
                page.go_back()
            elif fname == "go_forward":
                page.go_forward()
            elif fname in ("wait", "wait_5_seconds"):
                time.sleep(5 if fname == "wait_5_seconds" else args.get("seconds", 1))
            else:
                action_result["warning"] = f"unhandled_function: {fname}"

            page.wait_for_load_state(timeout=5000)
            time.sleep(1)

        except Exception as e:
            print(f"Error executing {fname}: {e}")
            action_result["error"] = str(e)

        results.append((fname, action_result))

    return results


def get_function_responses(
    page, results: List[Tuple[str, Dict[str, Any]]]
) -> Content:
    """Capture screenshot and URL and package them as FunctionResponses."""
    screenshot = page.screenshot(type="png")
    current_url = page.url
    function_response_parts = []

    for name, action_result in results:
        function_response_parts.append(
            Part(
                function_response=FunctionResponse(
                    name=name,
                    response={
                        "url": current_url,
                        **action_result,
                    },
                    parts=[
                        types.FunctionResponsePart(
                            inline_data=types.FunctionResponseBlob(
                                mime_type="image/png",
                                data=screenshot,
                            )
                        )
                    ],
                )
            )
        )

    return Content(
        role="user",
        parts=function_response_parts,
    )


def has_function_calls(response) -> bool:
    """Check if model response contains any function calls."""
    if not response.candidates:
        return False
    candidate = response.candidates[0]
    if not candidate.content or not candidate.content.parts:
        return False
    return any(
        hasattr(part, "function_call") and part.function_call
        for part in candidate.content.parts
    )


def create_client(
    project: str | None = None,
    location: str = "global",
    api_key: str | None = None,
) -> genai.Client:
    """Initialize the Google GenAI client for Enterprise/Vertex AI or API key."""
    if api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"):
        return genai.Client(api_key=api_key)

    resolved_project = project or os.environ.get("GOOGLE_CLOUD_PROJECT", DEFAULT_PROJECT)
    resolved_location = location or os.environ.get("GOOGLE_CLOUD_LOCATION", "global")

    if resolved_project:
        # Check if enterprise parameter is supported in installed google-genai version
        try:
            return genai.Client(
                enterprise=True,
                project=resolved_project,
                location=resolved_location,
            )
        except TypeError:
            return genai.Client(
                vertexai=True,
                project=resolved_project,
                location=resolved_location,
            )

    return genai.Client()


def build_generate_content_config(
    client: genai.Client,
    environment: types.Environment = types.Environment.ENVIRONMENT_BROWSER,
    enable_prompt_injection_detection: bool = True,
    excluded_functions: List[str] | None = None,
    disabled_safety_policies: List[types.SafetyPolicy] | None = None,
    enable_yield_to_user: bool = False,
    include_thoughts: bool = False,
) -> types.GenerateContentConfig:
    """Build GenerateContentConfig with ComputerUse tool and optional settings."""
    computer_use_kwargs: Dict[str, Any] = {
        "environment": environment,
    }
    if enable_prompt_injection_detection:
        computer_use_kwargs["enable_prompt_injection_detection"] = True
    if excluded_functions:
        computer_use_kwargs["excluded_predefined_functions"] = excluded_functions
    if disabled_safety_policies:
        computer_use_kwargs["disabled_safety_policies"] = disabled_safety_policies

    tools = [
        types.Tool(
            computer_use=types.ComputerUse(**computer_use_kwargs)
        )
    ]

    if enable_yield_to_user:
        tools.append(
            types.Tool(
                function_declarations=[
                    types.FunctionDeclaration.from_callable(
                        client=client, callable=yield_to_user
                    )
                ]
            )
        )

    config_kwargs: Dict[str, Any] = {"tools": tools}
    if include_thoughts:
        config_kwargs["thinking_config"] = types.ThinkingConfig(include_thoughts=True)

    return types.GenerateContentConfig(**config_kwargs)


def run_agent(
    prompt: str = DEFAULT_PROMPT,
    model: str = DEFAULT_MODEL,
    start_url: str = DEFAULT_START_URL,
    max_iterations: int = 10,
    headless: bool = False,
    screen_width: int = DEFAULT_SCREEN_WIDTH,
    screen_height: int = DEFAULT_SCREEN_HEIGHT,
    project: str | None = None,
    location: str = "global",
    api_key: str | None = None,
    enable_prompt_injection_detection: bool = True,
    excluded_functions: List[str] | None = None,
    enable_yield_to_user: bool = False,
    include_thoughts: bool = False,
    user_data_dir: str | None = None,
    channel: str | None = None,
    cdp_url: str | None = None,
    pause_before_start: bool = False,
    output_file: str | None = None,
) -> None:
    """Run the end-to-end computer use agent loop with Playwright."""
    client = create_client(project=project, location=location, api_key=api_key)
    generate_content_config = build_generate_content_config(
        client=client,
        environment=types.Environment.ENVIRONMENT_BROWSER,
        enable_prompt_injection_detection=enable_prompt_injection_detection,
        excluded_functions=excluded_functions,
        enable_yield_to_user=enable_yield_to_user,
        include_thoughts=include_thoughts,
    )

    with sync_playwright() as p:
        browser = None
        if cdp_url:
            if cdp_url == "auto":
                port_file = os.path.expandvars(
                    r"%LOCALAPPDATA%\Google\Chrome\User Data\DevToolsActivePort"
                )
                lines = open(port_file, encoding="utf-8").read().splitlines()
                cdp_url = f"ws://127.0.0.1:{lines[0].strip()}{lines[1].strip()}"
                print(f"Connected to active Chrome DevTools WebSocket: {cdp_url}")

            browser = p.chromium.connect_over_cdp(cdp_url)
            context = (
                browser.contexts[0]
                if browser.contexts
                else browser.new_context(
                    viewport={"width": screen_width, "height": screen_height}
                )
            )
            matching_page = None
            if start_url:
                for pg in context.pages:
                    if start_url.rstrip("/") in pg.url or "hiu-tung-cheung-esther" in pg.url:
                        matching_page = pg
                        break
            if matching_page:
                page = matching_page
                print(f"Reusing existing open tab: {page.url}")
                if start_url and page.url.rstrip("/") != start_url.rstrip("/"):
                    page.goto(start_url)
            else:
                page = context.new_page()
                if start_url:
                    page.goto(start_url)
        elif user_data_dir:
            context = p.chromium.launch_persistent_context(
                user_data_dir=os.path.abspath(user_data_dir),
                headless=headless,
                channel=channel,
                viewport={"width": screen_width, "height": screen_height},
            )
            page = context.pages[0] if context.pages else context.new_page()
        else:
            browser = p.chromium.launch(headless=headless, channel=channel)
            context = browser.new_context(
                viewport={"width": screen_width, "height": screen_height}
            )
            page = context.new_page()

        if not cdp_url:
            page.goto(start_url)

        if pause_before_start:
            termcolor.cprint(
                "\n[Paused before start] Please log in or prepare the browser window, "
                "then press Enter here to start the agent...",
                color="yellow",
            )
            input()

        initial_screenshot = page.screenshot(type="png")
        contents: List[Content] = [
            Content(
                role="user",
                parts=[
                    Part(text=prompt),
                    Part.from_bytes(data=initial_screenshot, mime_type="image/png"),
                ],
            )
        ]

        # Agent loop: iterate until model provides a final text response
        for iteration in range(max_iterations):
            print(f"\n--- Iteration {iteration + 1} ---")

            try:
                response = client.models.generate_content(
                    model=model,
                    contents=contents,
                    config=generate_content_config,
                )
            except auth_exceptions.RefreshError as e:
                termcolor.cprint(
                    "\n[Authentication Error] Google Cloud Application Default Credentials (ADC) "
                    "have expired or are invalid.\n"
                    "Please re-authenticate by running:\n"
                    "  gcloud auth application-default login\n"
                    f"Details: {e}",
                    color="red",
                )
                break

            contents.append(response.candidates[0].content)

            if not has_function_calls(response):
                print(f"FINAL RESPONSE:\n{response.text}")
                if output_file and response.text:
                    open(output_file, "w", encoding="utf-8").write(response.text)
                break

            results = execute_function_calls(
                response, page, screen_width, screen_height
            )
            if not results:
                break

            user_feedback_content = get_function_responses(page, results)
            contents.append(user_feedback_content)
        else:
            print("\nReached max iterations; requesting final summary from model...")
            contents.append(
                Content(
                    role="user",
                    parts=[
                        Part(
                            text="Stop calling any more tools and provide your complete, detailed final response based on everything observed so far."
                        )
                    ],
                )
            )
            final_resp = client.models.generate_content(
                model=model,
                contents=contents,
            )
            print(f"FINAL RESPONSE:\n{final_resp.text}")
            if output_file and final_resp.text:
                open(output_file, "w", encoding="utf-8").write(final_resp.text)

        if cdp_url:
            pass  # Keep the user's Chrome window open when connected via CDP
        elif browser:
            browser.close()
        else:
            context.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the Gemini Computer Use browser agent."
    )
    parser.add_argument(
        "--prompt",
        type=str,
        default=DEFAULT_PROMPT,
        help="Goal or task prompt for the computer use agent.",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=DEFAULT_MODEL,
        help=f"Gemini model name (default: {DEFAULT_MODEL}).",
    )
    parser.add_argument(
        "--url",
        type=str,
        default=DEFAULT_START_URL,
        help=f"Initial URL to open (default: {DEFAULT_START_URL}).",
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=10,
        help="Maximum number of agent loop iterations (default: 10).",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run Playwright browser in headless mode.",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=DEFAULT_SCREEN_WIDTH,
        help=f"Browser viewport width (default: {DEFAULT_SCREEN_WIDTH}).",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=DEFAULT_SCREEN_HEIGHT,
        help=f"Browser viewport height (default: {DEFAULT_SCREEN_HEIGHT}).",
    )
    parser.add_argument(
        "--project",
        type=str,
        default=DEFAULT_PROJECT,
        help=f"Google Cloud project ID (default: {DEFAULT_PROJECT}).",
    )
    parser.add_argument(
        "--location",
        type=str,
        default="global",
        help="Google Cloud location (default: global).",
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="Gemini API key (or set GEMINI_API_KEY).",
    )
    parser.add_argument(
        "--no-prompt-injection-detection",
        action="store_true",
        help="Disable prompt injection detection on screenshots.",
    )
    parser.add_argument(
        "--exclude-function",
        action="append",
        dest="excluded_functions",
        default=None,
        help="Predefined computer use function to exclude (can be specified multiple times).",
    )
    parser.add_argument(
        "--enable-yield-to-user",
        action="store_true",
        help="Register custom yield_to_user function for human-in-the-loop handoff.",
    )
    parser.add_argument(
        "--include-thoughts",
        action="store_true",
        help="Enable thinking_config with include_thoughts=True.",
    )
    parser.add_argument(
        "--user-data-dir",
        type=str,
        default=None,
        help="Path to persistent browser profile directory (saves cookies/logins across runs, e.g. './browser_profile').",
    )
    parser.add_argument(
        "--channel",
        type=str,
        default=None,
        help="Browser channel to launch, e.g. 'chrome' or 'msedge'.",
    )
    parser.add_argument(
        "--cdp-url",
        type=str,
        default=None,
        help="Connect to an existing Chrome instance over CDP (e.g. 'http://localhost:9222').",
    )
    parser.add_argument(
        "--pause-before-start",
        action="store_true",
        help="Wait for user to press Enter (e.g., after logging in manually) before capturing the initial screenshot.",
    )
    parser.add_argument(
        "--output-file",
        type=str,
        default=None,
        help="Optional path to save the model's final text response (UTF-8).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_agent(
        prompt=args.prompt,
        model=args.model,
        start_url=args.url,
        max_iterations=args.max_iterations,
        headless=args.headless,
        screen_width=args.width,
        screen_height=args.height,
        project=args.project,
        location=args.location,
        api_key=args.api_key,
        enable_prompt_injection_detection=not args.no_prompt_injection_detection,
        excluded_functions=args.excluded_functions,
        enable_yield_to_user=args.enable_yield_to_user,
        include_thoughts=args.include_thoughts,
        user_data_dir=args.user_data_dir,
        channel=args.channel,
        cdp_url=args.cdp_url,
        pause_before_start=args.pause_before_start,
        output_file=args.output_file,
    )


if __name__ == "__main__":
    main()
