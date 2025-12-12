from textnode import TextNode, TextType


def split_nodes_delimiter(old_nodes, delimiter, text_type):
    """
    Split TextType.TEXT nodes in `old_nodes` by `delimiter` and convert
    the delimited segments into nodes of `text_type`.

    - Non-Text nodes are copied through unchanged.
    - If a node has an odd number of delimiters, raises ValueError.
    - Empty text segments are skipped (no zero-length TextNode for text).
    """
    if delimiter == "":
        raise ValueError("delimiter must not be empty")

    new_nodes = []
    for node in old_nodes:
        if not isinstance(node, TextNode):
            new_nodes.append(node)
            continue

        # Only attempt to split plain/text nodes
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        text = node.text
        count = text.count(delimiter)
        if count == 0:
            new_nodes.append(node)
            continue
        if count % 2 != 0:
            raise ValueError(f"Unmatched delimiter '{delimiter}' in text: {text!r}")

        parts = text.split(delimiter)
        # parts alternates: text, matched, text, matched, ...
        for idx, part in enumerate(parts):
            if idx % 2 == 0:
                # plain text segment
                if part != "":
                    new_nodes.append(TextNode(part, TextType.TEXT))
            else:
                # delimited segment -> new node with the requested type
                new_nodes.append(TextNode(part, text_type))

    return new_nodes
