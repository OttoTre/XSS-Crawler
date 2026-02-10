from html import escape as html_escape
from urllib.parse import quote

from src.web.web_utils import evade, _content_variants
from src.web import web_utils


class DummyLocator:
    def __init__(self, count=0, page=None):
        self._count = count
        self.first = self
        self._page = page

    def count(self):
        return self._count

    def nth(self, _index):
        return self

    def is_visible(self):
        return True

    def is_enabled(self):
        return True

    def fill(self, _value, timeout=None):
        return None

    def press(self, _key):
        if self._page and "PAYLOAD" in (self._page._content_text or ""):
            self._page._trigger_dialog(DummyDialog())
        return None

    def click(self, timeout=None):
        return None


class DummyPage:
    def __init__(self, locator_count=0, content_text=""):
        self.url = "https://example.com"
        self._content_text = content_text
        self.visited = []
        self._on_handlers = {}
        self._once_handlers = {}

        self._locator = DummyLocator(locator_count, page=self)

    def goto(self, url, wait_until=None, timeout=None):
        self.url = url
        self.visited.append(url)
        if "PAYLOAD" in (self._content_text or "") or "PAYLOAD" in url:
            self._trigger_dialog(DummyDialog())

    def wait_for_timeout(self, _ms):
        return None

    def on(self, _event, _handler):
        self._on_handlers.setdefault(_event, []).append(_handler)
        return None

    def once(self, _event, _handler):
        self._once_handlers.setdefault(_event, []).append(_handler)
        return None

    def remove_listener(self, _event, _handler):
        if _event in self._on_handlers and _handler in self._on_handlers[_event]:
            self._on_handlers[_event].remove(_handler)
        if _event in self._once_handlers and _handler in self._once_handlers[_event]:
            self._once_handlers[_event].remove(_handler)
        return None

    def _trigger_dialog(self, dialog):
        for h in list(self._on_handlers.get("dialog", [])):
            try:
                h(dialog)
            except Exception:
                pass
        for h in list(self._once_handlers.get("dialog", [])):
            try:
                h(dialog)
            except Exception:
                pass
        self._once_handlers["dialog"] = []

    def locator(self, _selector):
        return self._locator

    def content(self):
        return self._content_text


class DummyDialog:
    def __init__(self):
        self._accepted = False

    def accept(self):
        self._accepted = True


def test_evade_basic_variants(monkeypatch):
    monkeypatch.delenv("OOB_DOMAIN", raising=False)
    payload = "<svg/onload=alert(1)>"
    variants = evade(payload)

    assert payload in variants
    assert html_escape(payload) in variants
    assert len(variants) == len(set(variants))


def test_content_variants_basic():
    payload = "<test>"
    variants = _content_variants(payload)

    assert variants[0] == payload
    assert html_escape(payload) in variants
    assert quote(payload) in variants
    assert payload.replace("<", "&lt;") in variants
    assert len(variants) == 4


def test_form_vulnerability_detects_reflection(monkeypatch):
    monkeypatch.setattr(web_utils, "evade", lambda _p: ["PAYLOAD"])
    page = DummyPage(locator_count=1, content_text="PAYLOAD")
    form = {
        "url": "https://example.com/form",
        "action": "https://example.com/form",
        "method": "get",
        "inputs": [("q", "text")],
    }

    assert web_utils.test_form_vulnerability(page, form, ["x"]) == 1


def test_url_parameters_detects_reflection(monkeypatch):
    monkeypatch.setattr(web_utils, "evade", lambda _p: ["PAYLOAD"])
    page = DummyPage(content_text="PAYLOAD")
    count = web_utils.test_url_parameters(page, "https://example.com/path?param=1", ["x"])

    assert count == 1
    assert any("param=PAYLOAD" in url for url in page.visited)


def test_fragment_parameters_detects_reflection(monkeypatch):
    monkeypatch.setattr(web_utils, "evade", lambda _p: ["PAYLOAD"])
    page = DummyPage(content_text="PAYLOAD")
    count = web_utils.test_fragment_parameters(page, "https://example.com/path", ["x"])

    assert count == 1
    assert any("#PAYLOAD" in url for url in page.visited)


def test_loose_inputs_detects_reflection(monkeypatch):
    monkeypatch.setattr(web_utils, "evade", lambda _p: ["PAYLOAD"])
    page = DummyPage(locator_count=1, content_text="PAYLOAD")

    assert web_utils.test_loose_inputs(page, "https://example.com", ["x"]) == 1


def test_no_false_positives(monkeypatch):
    monkeypatch.setattr(web_utils, "evade", lambda _p: ["PAYLOAD"])

    page = DummyPage(locator_count=1, content_text="SAFE_CONTENT")
    page._trigger_dialog = lambda dialog: None

    form = {
        "url": "https://example.com/form",
        "action": "https://example.com/form",
        "method": "get",
        "inputs": [("q", "text")],
    }

    assert web_utils.test_form_vulnerability(page, form, ["x"]) == 0
    assert web_utils.test_url_parameters(page, "https://example.com/path?param=1", ["x"]) == 0
    assert web_utils.test_fragment_parameters(page, "https://example.com/path", ["x"]) == 0
    assert web_utils.test_loose_inputs(page, "https://example.com", ["x"]) == 0
