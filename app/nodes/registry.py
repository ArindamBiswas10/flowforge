from app.core.models import NodeType

def get_node_handler(node_type: NodeType):
    from app.nodes import input_node, prompt_template_node, llm_node, http_node, output_node

    registry = {
        NodeType.INPUT: input_node.execute,
        NodeType.PROMPT_TEMPLATE: prompt_template_node.execute,
        NodeType.LLM: llm_node.execute,
        NodeType.HTTP: http_node.execute,
        NodeType.OUTPUT: output_node.execute,
    }

    handler = registry.get(node_type)
    if not handler:
        raise ValueError(f"No handler found: {node_type}")
    return handler