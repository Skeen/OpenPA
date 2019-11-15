from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor

grammar = Grammar(
    r"""
    expr        = (ws (block / attribute / emptyline) ws)*

    block       = "BEGIN" ws name ws expr ws "END"
    attribute   = name ws attribute_value

    name        = ~"(?!BEGIN|END)" (bare_name / quoted_name)
    bare_name   = attribute_value
    quoted_name = quoted

    attribute_value = ~r"[a-zA-Z0-9\.\-\[\]_]+"
    emptyline   = ws+
    
    quoted      = ~'"[^\"]+"'
    ws          = ~"\s*"
    """
)

class PrisonVisitor(NodeVisitor):
    def visit_expr(self, node, visited_children):
        output = {}
        for child in visited_children:
            # ws, block/attribute/emptyline ws
            _, content, ws = child
            output.update(content[0])
        return output

    def visit_block(self, node, visited_children):
        # BEGIN, ws, name, ws, exprs, ws, end, ws
        _, _, name, _, exprs, _, _ = visited_children
        return {
            name: exprs
        }

    def visit_emptyline(self, node, visited_children):
        return {}

    def visit_name(self, node, visited_children):
        # not_begin_end, name/quote
        _, name = visited_children
        return name[0]

    def visit_bare_name(self, node, visited_children):
        return node.text

    def visit_quoted(self, node, visited_children):
        return node.text.strip('"')

    def visit_attribute(self, node, visited_children):
        key, _, value = visited_children
        return {key: value}

    def visit_attribute_value(self, node, visited_children):
        return node.text

    def visit_ws(self, node, visited_children):
        return {}

    def generic_visit(self, node, visited_children):
        return visited_children


if __name__ == '__main__':
    from pprint import pprint
    with open("example.prison", "r") as prison_file:
        text = "".join(prison_file.readlines())
        parsed_tree = grammar.parse(text)
        visitor = PrisonVisitor()
        prison_visit = visitor.visit(parsed_tree)
        pprint(prison_visit)
