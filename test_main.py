"""Unit tests for the Gemini Computer Use agent implementation."""

from unittest.mock import MagicMock, patch
from google.genai import types

import main


def test_denormalize_coordinates():
    assert main.denormalize_x(500, 1440) == 720
    assert main.denormalize_y(500, 900) == 450
    assert main.denormalize_x(0, 1440) == 0
    assert main.denormalize_y(1000, 900) == 900


def test_build_generate_content_config():
    mock_client = MagicMock()
    config = main.build_generate_content_config(
        client=mock_client,
        environment=types.Environment.ENVIRONMENT_BROWSER,
        enable_prompt_injection_detection=True,
        excluded_functions=["drag_and_drop"],
        disabled_safety_policies=[
            types.SafetyPolicy.FINANCIAL_TRANSACTIONS,
            types.SafetyPolicy.COMMUNICATION_TOOL,
        ],
        enable_yield_to_user=True,
        include_thoughts=True,
    )
    assert len(config.tools) == 2
    cu = config.tools[0].computer_use
    assert cu.environment == types.Environment.ENVIRONMENT_BROWSER
    assert cu.enable_prompt_injection_detection is True
    assert cu.excluded_predefined_functions == ["drag_and_drop"]
    assert cu.disabled_safety_policies == [
        types.SafetyPolicy.FINANCIAL_TRANSACTIONS,
        types.SafetyPolicy.COMMUNICATION_TOOL,
    ]
    assert config.thinking_config.include_thoughts is True


def test_execute_function_calls_click_and_type():
    page = MagicMock()

    part1 = types.Part(text="I will click and type.")
    part2 = types.Part(
        function_call=types.FunctionCall(
            name="click",
            args={"x": 500, "y": 500, "intent": "Click search box"},
        )
    )
    part3 = types.Part(
        function_call=types.FunctionCall(
            name="type",
            args={
                "x": 500,
                "y": 500,
                "text": "flights to Honolulu",
                "press_enter": True,
                "intent": "Enter search query",
            },
        )
    )
    response = MagicMock()
    response.candidates = [
        MagicMock(content=types.Content(role="model", parts=[part1, part2, part3]))
    ]

    with patch("main.time.sleep"):
        results = main.execute_function_calls(response, page, 1440, 900)

    assert len(results) == 2
    assert results[0] == ("click", {})
    assert results[1] == ("type", {})
    page.mouse.click.assert_any_call(720, 450)
    page.keyboard.type.assert_called_once_with("flights to Honolulu")
    page.keyboard.press.assert_any_call("Enter")


def test_safety_confirmation_acknowledged():
    page = MagicMock()
    part = types.Part(
        function_call=types.FunctionCall(
            name="click",
            args={
                "x": 100,
                "y": 200,
                "intent": "Click checkbox",
                "safety_decision": {
                    "explanation": "CAPTCHA encountered",
                    "decision": "require_confirmation",
                },
            },
        )
    )
    response = MagicMock()
    response.candidates = [
        MagicMock(content=types.Content(role="model", parts=[part]))
    ]

    with patch("builtins.input", return_value="y"), patch("main.time.sleep"):
        results = main.execute_function_calls(response, page, 1000, 1000)

    assert len(results) == 1
    assert results[0] == ("click", {"safety_acknowledgement": "true"})
    page.mouse.click.assert_called_once_with(100, 200)


def test_get_function_responses():
    page = MagicMock()
    page.screenshot.return_value = b"fake_png_bytes"
    page.url = "https://www.google.com/search?q=flights"

    content = main.get_function_responses(
        page, [("click", {"safety_acknowledgement": "true"})]
    )
    assert content.role == "user"
    assert len(content.parts) == 1
    fr = content.parts[0].function_response
    assert fr.name == "click"
    assert fr.response == {
        "url": "https://www.google.com/search?q=flights",
        "safety_acknowledgement": "true",
    }
    assert fr.parts[0].inline_data.mime_type == "image/png"
    assert fr.parts[0].inline_data.data == b"fake_png_bytes"


def test_load_profiles_from_file(tmp_path=None):
    import tempfile
    from pathlib import Path
    import build_portfolio

    content = """
    # Class list comment
    Hiu Tung Cheung (Esther) | https://www.linkedin.com/in/hiu-tung-cheung-esther-085656387/
    https://www.linkedin.com/in/another-student-12345/?trk=public_profile
    Arthur Chin, linkedin.com/in/arthur-chin-example
    """
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write(content)
        temp_name = f.name

    try:
        entries = build_portfolio.load_profiles_from_file(temp_name)
        assert len(entries) == 3
        assert entries[0]["handle"] == "hiu-tung-cheung-esther-085656387"
        assert entries[0]["name_hint"] == "Hiu Tung Cheung (Esther)"
        assert entries[1]["url"] == "https://www.linkedin.com/in/another-student-12345/"
        assert entries[2]["url"] == "https://www.linkedin.com/in/arthur-chin-example/"
    finally:
        Path(temp_name).unlink(missing_ok=True)


if __name__ == "__main__":
    test_denormalize_coordinates()
    test_build_generate_content_config()
    test_execute_function_calls_click_and_type()
    test_safety_confirmation_acknowledged()
    test_get_function_responses()
    test_load_profiles_from_file()
    print("All tests passed successfully!")
