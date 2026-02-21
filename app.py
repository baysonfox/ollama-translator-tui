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
            self.notify("基础 TUI 已就绪，翻译逻辑将在下一步接入。")


def main() -> None:
    app = TranslatorApp()
    app.run()


if __name__ == "__main__":
    main()
