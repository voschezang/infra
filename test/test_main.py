from dataclasses import dataclass, field
from typing import List
from unittest.mock import patch
from langchain.messages import AIMessage, ToolMessage

from main import MyModel, init_models,  stringify
from tools import trips, multiply


@dataclass
class Result:
    message: type
    content: str | list | dict | None
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


def test_tool_access():
    planner, reviewer = init_models()
    # planner should have read + write access to trips
    assert 'list_trips' in planner.tools_by_name
    assert 'read_trip' in planner.tools_by_name
    assert 'write_trip' in planner.tools_by_name
    # planner should have read access to reviews
    assert 'list_reviews' in planner.tools_by_name
    assert 'read_review' in planner.tools_by_name
    assert len(planner.tools_by_name) == 5

    # reviewer should have read access to trips
    assert 'list_trips' in reviewer.tools_by_name
    assert 'read_trip' in reviewer.tools_by_name
    # reviewer should have read + write access to reviews
    assert 'list_reviews' in reviewer.tools_by_name
    assert 'read_review' in reviewer.tools_by_name
    assert 'write_review' in reviewer.tools_by_name
    assert len(reviewer.tools_by_name) == 5


def test_trip_tools():
    title = 'Trip to Rome'
    review = 'A magnificient trip to Rome'
    trip = {'title': title, 'description': review}
    mock_events = [
        AIMessage('', tool_calls=[{'name': 'list_trips',
                                           'args': {},
                                           'id': 'abcd-efgh',
                                           'type': 'tool_call'}]),
        AIMessage('', tool_calls=[{'name': 'write_trip',
                                           'args': trip,
                                           'id': 'abcd-efgh',
                                           'type': 'tool_call'}]),
        AIMessage('', tool_calls=[{'name': 'read_trip',
                                           'args': {'i': 0},
                                           'id': 'abcd-efgh',
                                           'type': 'tool_call'}]),
        AIMessage('All done')
    ]

    expected = [
        Result(AIMessage, '', mock_events[0].tool_calls),
        Result(ToolMessage, []),
        Result(AIMessage, '', mock_events[1].tool_calls),
        Result(ToolMessage, '0'),
        Result(AIMessage, '', mock_events[2].tool_calls),
        Result(ToolMessage, str(trip)),
        Result(AIMessage, mock_events[3].content)
    ]

    planner, reviewer = init_models()
    with patch.object(planner, 'invoke', side_effect=mock_events):
        results = list(planner.run(''))
        verify_results(results, expected)

    assert trips == []


def test_review_tools():
    review = 'A great plan'
    mock_events = [
        AIMessage('', tool_calls=[{'name': 'list_reviews',
                                           'args': {},
                                           'id': 'abcd-efgh',
                                           'type': 'tool_call'}]),
        AIMessage('', tool_calls=[{'name': 'write_review',
                                           'args': {'i': 0,
                                                    'data': review},
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
        Result(ToolMessage, '0'),
        Result(AIMessage, '', mock_events[2].tool_calls),
        Result(ToolMessage, review),
        Result(AIMessage, mock_events[3].content)
    ]

    planner, reviewer = init_models()
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
