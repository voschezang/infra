from dataclasses import dataclass, field
from typing import List
from unittest.mock import patch
from langchain.messages import AIMessage, ToolMessage

from main import MyModel, init_model,  stringify
from tools import trips, multiply


@dataclass
class Result:
    message: type
    content: str | list | None
    tool_calls: list = field(default_factory=list)


def test_model_run():
    msg = "Multiply 10.0101 and pi. Use an extremely high precision for pi."

    mock_events = [
        AIMessage('', tool_calls=[{'name': 'multiply',
                                           'args': {'a': 10.0101, 'b': 3.141592653589793},
                                           'id': '6e877381-6375-4da6-b987-c14b2b8db670',
                                           'type': 'tool_call'}]),
        AIMessage('31.44765662169919')
    ]

    expected = [
        Result(AIMessage, '', mock_events[0].tool_calls),
        Result(ToolMessage, '31.44765662169919'),
        Result(AIMessage, mock_events[1].content)
    ]

    o = MyModel(tools=[multiply])

    # patch model.invoke() for efficiency
    with patch.object(o, 'invoke', side_effect=mock_events):
        results = list(o.run(msg))

        verify_results(results, expected)


def test_trip_tools():
    mock_events = [
        AIMessage('', tool_calls=[{'name': 'list_trips',
                                           'args': {},
                                           'id': 'abcd-efgh',
                                           'type': 'tool_call'}]),
        AIMessage('', tool_calls=[{'name': 'post_trip',
                                           'args': {'title': 'My trip',
                                                    'description': '...'},
                                           'id': 'abcd-efgh',
                                           'type': 'tool_call'}]),
        AIMessage('', tool_calls=[{'name': 'read_trip',
                                           'args': {},
                                           'id': 'abcd-efgh',
                                           'type': 'tool_call'}]),
        AIMessage('All done')
    ]

    expected = [
        Result(AIMessage, '', mock_events[0].tool_calls),
        Result(ToolMessage, []),
        Result(AIMessage, '', mock_events[1].tool_calls),
        Result(ToolMessage, 'None'),
        Result(AIMessage, '', mock_events[2].tool_calls),
        Result(ToolMessage, ['0',
                             'Trip to Rome',
                             'A magnificient trip to Rome']),
        Result(AIMessage, mock_events[3].content)
    ]

    planner = init_model('dummy')
    with patch.object(planner, 'invoke', side_effect=mock_events):
        results = list(planner.run(''))
        verify_results(results, expected)

    assert trips == []


def test_review_tools():
    mock_events = [
        AIMessage('', tool_calls=[{'name': 'list_reviews',
                                           'args': {},
                                           'id': 'abcd-efgh',
                                           'type': 'tool_call'}]),
        AIMessage('', tool_calls=[{'name': 'post_review',
                                           'args': {'i': 0,
                                                    'review': '...'},
                                           'id': 'abcd-efgh',
                                           'type': 'tool_call'}]),
        AIMessage('', tool_calls=[{'name': 'read_review',
                                           'args': {'i': 0},
                                           'id': 'abcd-efgh',
                                           'type': 'tool_call'}]),
        AIMessage('All done')
    ]

    expected = [
        Result(AIMessage, '', mock_events[0].tool_calls),
        Result(ToolMessage, []),
        Result(AIMessage, '', mock_events[1].tool_calls),
        Result(ToolMessage, 'None'),
        Result(AIMessage, '', mock_events[2].tool_calls),
        Result(ToolMessage, 'A great plan'),
        Result(AIMessage, mock_events[3].content)
    ]

    reviewer = init_model('dummy')
    with patch.object(reviewer, 'invoke', side_effect=mock_events):
        results = list(reviewer.run(''))
        verify_results(results, expected)

    assert trips == []


def test_stringify():
    assert stringify('abc') == 'abc'
    assert stringify('abc def') == 'abc_def'
    assert stringify('abc\b1') == 'abc1'


def verify_results(expected: list, results: List[Result]):
    for item, result in zip(expected, results):
        item = item['messages'][0]
        assert isinstance(item, result.message)
        assert item.content == result.content
        if result.tool_calls:
            assert item.tool_calls == result.tool_calls

    assert len(expected) == len(results)


def message(msg):
    return {'llm_call': {'messages': [msg]}}
