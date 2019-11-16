import unittest
from parameterized import parameterized

from prison_parser import grammar, PrisonVisitor
from parsimonious.nodes import NodeVisitor
from parsimonious.exceptions import IncompleteParseError


class MockVisitor(NodeVisitor):
    def __init__(self):
        self.parse_path = []

    def generic_visit(self, node, visited_children):
        if node.expr.name == "":
            return visited_children or []
        return [node.expr.name] + (visited_children or [])


class TestParser(unittest.TestCase):
    @parameterized.expand(
        [
            # Empty string and newline
            ["", {}],
            ["\n", {}],
            # Attribute with white-space
            ["key value", {"key": "value"}],
            ["  key value", {"key": "value"}],
            ["key value  ", {"key": "value"}],
            ["  key value  ", {"key": "value"}],
            ["  key  value  ", {"key": "value"}],
            # Quoted attribute with white-space
            ['"key" value', {"key": "value"}],
            ['  "key" value', {"key": "value"}],
            ['"key" value  ', {"key": "value"}],
            ['  "key" value  ', {"key": "value"}],
            ['  "key"  value  ', {"key": "value"}],
            ['" key" value', {" key": "value"}],
            ['"key " value', {"key ": "value"}],
            ['"key with space" value', {"key with space": "value"}],
            [' "key with space" value ', {"key with space": "value"}],
            # Multiple attributes with white-space
            ["key1 value1\nkey2 value2", {"key1": "value1", "key2": "value2"}],
            [
                "  key1 value1\n  key2 value2",
                {"key1": "value1", "key2": "value2"},
            ],
            [
                "  key1 value1\nkey2 value2  ",
                {"key1": "value1", "key2": "value2"},
            ],
            [
                "key1 value1  \n  key2 value2",
                {"key1": "value1", "key2": "value2"},
            ],
            [
                "key1  value1\nkey2  value2",
                {"key1": "value1", "key2": "value2"},
            ],
            # Multiple quoted attributes with white-space
            [
                '"key1" value1\n"key2" value2',
                {"key1": "value1", "key2": "value2"},
            ],
            [
                '"key with space" value1\nkey2 value2',
                {"key with space": "value1", "key2": "value2"},
            ],
            # Simple sections
            ["BEGIN section alfa beta END", {"section": {"alfa": "beta"}}],
            [
                "  BEGIN   section   alfa   beta   END  ",
                {"section": {"alfa": "beta"}},
            ],
            [
                'BEGIN section "key with spaces" beta END',
                {"section": {"key with spaces": "beta"}},
            ],
            [
                'BEGIN "section with spaces" alfa beta END',
                {"section with spaces": {"alfa": "beta"}},
            ],
            [
                'BEGIN "section with spaces" "key with spaces" beta END',
                {"section with spaces": {"key with spaces": "beta"}},
            ],
            # Nested sections
            [
                "BEGIN outer-section BEGIN inner-section alfa beta END END",
                {"outer-section": {"inner-section": {"alfa": "beta"}}},
            ],
            # TODO: More tests, multiple layers nested
        ]
    )
    def test_grammer(self, text, expected_data):
        # Test that the string parses
        parsed_tree = grammar.parse(text)
        # Test that the correct data is being produced
        visitor = PrisonVisitor()
        prison_visit = visitor.visit(parsed_tree)
        self.assertEqual(prison_visit, expected_data)

    @parameterized.expand(
        [
            # Invalid characters
            ["@", IncompleteParseError],
            ["=", IncompleteParseError],
            # Quoted value is illegal
            ['key "value"', IncompleteParseError],
            # This should be an error
            ["key\nvalue", Exception],
        ]
    )
    def test_invalid_grammar(self, text, exception):
        with self.assertRaises(exception):
            # Test that the string parses
            parsed_tree = grammar.parse(text)
            # Test that the correct data is being produced
            visitor = PrisonVisitor()
            prison_visit = visitor.visit(parsed_tree)

    @parameterized.expand(
        [
            ["", ["expr"]],
            ["\n", ["expr", [["ws"], [["emptyline", ["ws"]]], ["ws"]]]],
        ]
    )
    def test_grammar_visit_order(self, text, expected_visit):
        # Test that the string parses
        parsed_tree = grammar.parse(text)
        # Test that the tree is being visisted correctly
        visitor = MockVisitor()
        mock_visit = visitor.visit(parsed_tree)
        self.assertEqual(mock_visit, expected_visit)
