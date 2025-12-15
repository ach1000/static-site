import os
from node_splitter import markdown_to_html_node
from extract_title import extract_title


def generate_page(from_path, template_path, dest_path):
    """Generate an HTML page from markdown and template.
    
    Args:
        from_path: Path to the source markdown file.
        template_path: Path to the HTML template file.
        dest_path: Path where the generated HTML should be written.
    """
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    
    # Read the markdown file
    with open(from_path, 'r') as f:
        markdown_content = f.read()
    
    # Read the template file
    with open(template_path, 'r') as f:
        template_content = f.read()
    
    # Convert markdown to HTML
    html_node = markdown_to_html_node(markdown_content)
    html_content = html_node.to_html()
    
    # Extract title from markdown
    title = extract_title(markdown_content)
    
    # Replace placeholders in template
    final_html = template_content.replace("{{ Title }}", title)
    final_html = final_html.replace("{{ Content }}", html_content)
    
    # Create destination directory if it doesn't exist
    dest_dir = os.path.dirname(dest_path)
    if dest_dir and not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    
    # Write the final HTML to the destination
    with open(dest_path, 'w') as f:
        f.write(final_html)
