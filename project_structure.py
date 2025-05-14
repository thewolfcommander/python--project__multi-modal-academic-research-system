# project_structure.py
import os

def create_project_structure():
    """Create the project directory structure"""
    directories = [
        "multi_modal_rag",
        "multi_modal_rag/data_collectors",
        "multi_modal_rag/data_processors",
        "multi_modal_rag/indexing",
        "multi_modal_rag/retrieval",
        "multi_modal_rag/orchestration",
        "multi_modal_rag/ui",
        "multi_modal_rag/utils",
        "data/papers",
        "data/videos",
        "data/podcasts",
        "data/processed",
        "configs",
        "logs"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        
    # Create __init__.py files
    for directory in directories:
        if directory.startswith("multi_modal_rag"):
            init_file = os.path.join(directory, "__init__.py")
            open(init_file, 'a').close()
    
    print("Project structure created successfully!")

if __name__ == "__main__":
    create_project_structure()