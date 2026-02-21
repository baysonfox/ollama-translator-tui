import json
import urllib.error
import urllib.request

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Label, Select, TextArea


LANGUAGE_OPTIONS: list[tuple[str, str]] = [
    ("Auto", "auto"),
    ("Chinese", "zh"),
    ("English", "en"),
    ("Japanese", "ja"),
    ("Korean", "ko"),
]


class TranslatorApp(App[None]):
    CSS_PATH = "styles.tcss"
    TITLE = "Translator"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="root"):
            with Horizontal(id="panes"):
                with Vertical(classes="pane"):
                    yield Label("Original", classes="pane_title")
                    yield TextArea("", id="original_input")
                with Vertical(classes="pane"):
                    yield Label("Translated", classes="pane_title")
                    translated = TextArea("", id="translated_output")
                    translated.read_only = True
                    yield translated
            with Horizontal(id="controls"):
                yield Select(
                    LANGUAGE_OPTIONS,
                    value="auto",
                    id="source_language",
                    prompt="Source Language",
                )
                yield Button("Translate", id="translate_button", variant="primary")
                yield Select(
                    LANGUAGE_OPTIONS,
                    value="zh",
                    id="target_language",
                    prompt="Target Language",
                )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "translate_button":
            self._translate_text()

    def _translate_text(self) -> None:
        original = self.query_one("#original_input", TextArea)
        translated = self.query_one("#translated_output", TextArea)
        source = self.query_one("#source_language", Select[str]).value
        target = self.query_one("#target_language", Select[str]).value
        source_code = source if isinstance(source, str) else "auto"
        target_code = target if isinstance(target, str) else "zh"
        original_text = original.text.strip()

        if not original_text:
            self.notify("请输入要翻译的内容。", severity="warning")
            return

        try:
            result = self._call_ollama_translate(
                text=original_text,
                source_lang=source_code,
                target_lang=target_code,
            )
            translated.text = result
            self.notify("翻译完成。")
        except RuntimeError as error:
            self.notify(str(error), severity="error")

    def _call_ollama_translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
    ) -> str:
        source_prompt = (
            "auto-detect" if source_lang == "auto" else f"language code '{source_lang}'"
        )
        prompt = (
            "You are a translation engine. Translate the text exactly. "
            "Return only the translated text.\n"
            f"Source: {source_prompt}\n"
            f"Target language code: '{target_lang}'\n\n"
            f"Text:\n{text}"
        )
        payload = {
            "model": "translategemma:4b",
            "prompt": prompt,
            "stream": False,
        }
        request = urllib.request.Request(
            url="http://127.0.0.1:11434/api/generate",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                body = response.read().decode("utf-8")
        except urllib.error.URLError as error:
            raise RuntimeError(
                "无法连接 Ollama，请确认 `ollama serve` 正在运行。"
            ) from error
        except TimeoutError as error:
            raise RuntimeError("请求 Ollama 超时，请重试。") from error

        try:
            decoded = json.loads(body)
        except json.JSONDecodeError as error:
            raise RuntimeError("Ollama 返回内容无法解析。") from error

        translated = decoded.get("response", "").strip()
        if not translated:
            raise RuntimeError("Ollama 未返回翻译结果。")
        return translated


def main() -> None:
    app = TranslatorApp()
    app.run()


if __name__ == "__main__":
    main()
