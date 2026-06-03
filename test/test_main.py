from unittest.mock import patch

from langchain.messages import AIMessage
from langgraph.graph.state import CompiledStateGraph


from main import MyModel, stringify


def test_main():
    msg = "Multiply 10.0101 and pi. Use an extremely high precision for pi."

    events = [
        {'llm_call': {'messages':
                      [AIMessage('', tool_calls=[{'name': 'multiply',
                                                  'args': {'a': 10.0101, 'b': 3.141592653589793},
                                                  'id': '6e877381-6375-4da6-b987-c14b2b8db670',
                                                  'type': 'tool_call'}]
                                 )]
                      }
         },
        {'llm_call': {'messages': [AIMessage('31.44765662169919')]}}
    ]

    with patch.object(CompiledStateGraph, 'stream', side_effect=[events]):
        o = MyModel()
        o.logged_llm(msg)


def test_stringify():
    assert stringify('abc') == 'abc'
    assert stringify('abc def') == 'abc_def'
    assert stringify('abc\b1') == 'abc1'
