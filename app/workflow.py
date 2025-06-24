from graph.graph import Graph

compiled_graph = Graph  
print("Graph:", compiled_graph)

try:
    img_data = compiled_graph.get_graph().draw_mermaid_png()
    with open("workflow.png", "wb") as f:
        f.write(img_data)
    print("Graph saved as workflow.png")
except Exception as e:
    print(f"Error: {e}")