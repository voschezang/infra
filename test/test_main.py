from unittest.mock import patch
from langchain.messages import AIMessage

from main import MyModel, stringify


def test_model_run():
    msg = "Multiply 10.0101 and pi. Use an extremely high precision for pi."

    events = [
        AIMessage('', tool_calls=[{'name': 'multiply',
                                           'args': {'a': 10.0101, 'b': 3.141592653589793},
                                           'id': '6e877381-6375-4da6-b987-c14b2b8db670',
                                           'type': 'tool_call'}]),
        AIMessage('31.44765662169919')
    ]

    o = MyModel()

    # patch model.invoke() for efficiency
    with patch.object(o, 'invoke', side_effect=events):
        results = list(o.run(msg))

        assert results[0]['messages'][0].tool_calls == events[0].tool_calls
        assert results[0]['llm_calls'] == 1
        assert results[1]['messages'][0].content == '31.44765662169919'
        assert 'llm_calls' not in results[1]
        assert results[2]['messages'][0].content == '31.44765662169919'
        assert results[0]['llm_calls'] == 1

        assert len(results) == 3


def test_stringify():
    assert stringify('abc') == 'abc'
    assert stringify('abc def') == 'abc_def'
    assert stringify('abc\b1') == 'abc1'


def message(msg):
    return {'llm_call': {'messages': [msg]}}
