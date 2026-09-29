from types import SimpleNamespace

import pytest

from ai_core.gemini_generator import GeminiLegalGenerator


def make_generator(responses):
    generator = GeminiLegalGenerator.__new__(GeminiLegalGenerator)
    generator.settings = SimpleNamespace(
        gemini_api_key="test-key",
        gemini_model="test-model",
    )

    class FakeModels:
        def __init__(self):
            self.calls = 0

        def generate_content(self, **kwargs):
            response = responses[self.calls]
            self.calls += 1
            if isinstance(response, Exception):
                raise response
            return response

    generator._client = SimpleNamespace(models=FakeModels())
    return generator


def test_generate_retries_temporary_service_unavailable(monkeypatch):
    sleeps = []
    monkeypatch.setattr(
        "ai_core.gemini_generator.time.sleep",
        sleeps.append,
    )
    generator = make_generator(
        [
            RuntimeError("503 UNAVAILABLE: model overloaded"),
            RuntimeError("503 UNAVAILABLE: model overloaded"),
            SimpleNamespace(text="Draft document"),
        ]
    )

    result = generator._generate_gemini(
        document_type="Agreement",
        parties="A and B",
        terms="Payment",
        dates="Today",
    )

    assert result == "Draft document"
    assert generator._client.models.calls == 3
    assert sleeps == [1, 2]


def test_generate_stops_after_retry_limit(monkeypatch):
    sleeps = []
    monkeypatch.setattr(
        "ai_core.gemini_generator.time.sleep",
        sleeps.append,
    )
    generator = make_generator(
        [RuntimeError("503 UNAVAILABLE: model overloaded")] * 3
    )

    with pytest.raises(RuntimeError, match="Gemini API request failed"):
        generator._generate_gemini(
            document_type="Agreement",
            parties="A and B",
            terms="Payment",
            dates="Today",
        )

    assert generator._client.models.calls == 3
    assert sleeps == [1, 2]


def test_generate_uses_fallback_model(monkeypatch):
    sleeps = []
    monkeypatch.setattr(
        "ai_core.gemini_generator.time.sleep",
        sleeps.append,
    )
    generator = GeminiLegalGenerator.__new__(GeminiLegalGenerator)
    generator.settings = SimpleNamespace(
        gemini_api_key="test-key",
        gemini_model="primary-model",
        fallback_model_list=["fallback-model-1", "fallback-model-2"],
    )

    class FakeModels:
        def __init__(self):
            self.models_called = []

        def generate_content(self, **kwargs):
            self.models_called.append(kwargs.get("model"))
            if kwargs.get("model") == "primary-model":
                raise RuntimeError("503 UNAVAILABLE: primary overloaded")
            return SimpleNamespace(text="Draft from fallback")

    generator._client = SimpleNamespace(models=FakeModels())

    result = generator._generate_gemini(
        document_type="Agreement",
        parties="A and B",
        terms="Payment",
        dates="Today",
    )

    assert result == "Draft from fallback"
    assert "primary-model" in generator._client.models.models_called
    assert "fallback-model-1" in generator._client.models.models_called