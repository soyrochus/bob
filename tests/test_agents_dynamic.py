from bob.settings import Settings
from bob import agents

class DummyProvider:
    def __init__(self, data):
        self.data = data
    def load(self, path):
        return self.data

def test_dynamic_agent_loading(monkeypatch):
    data = {
        "agents": {
            "foo": {"agent_type": "tutor", "home_selector": "Foo"},
            "default": {"agent_type": "default", "home_selector": "Raw"},
        }
    }
    s = Settings(provider=DummyProvider(data), path="dummy")
    monkeypatch.setattr(agents, "settings", s)
    agents.load_agents()
    foo = agents.get_agent("foo")
    assert isinstance(foo, agents.TutorAgent)
    choices = agents.get_selector_choices()
    assert ("foo", "Foo") in choices
