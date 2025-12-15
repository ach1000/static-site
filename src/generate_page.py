import os
from node_splitter import markdown_to_html_node
from extract_title import extract_title


def generate_page(from_path, template_path, dest_path, basepath="/"):
    """Generate an HTML page from markdown and template.
    
    Args:
        from_path: Path to the source markdown file.
        template_path: Path to the HTML template file.
        dest_path: Path where the generated HTML should be written.
        basepath: Base path for the site (default "/").
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
    
    # Replace relative paths with basepath
    final_html = final_html.replace('href="/', f'href="{basepath}')
    final_html = final_html.replace('src="/', f'src="{basepath}')
    
    # Create destination directory if it doesn't exist
    dest_dir = os.path.dirname(dest_path)
    if dest_dir and not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    
    # Write the final HTML to the destination
    with open(dest_path, 'w') as f:
        f.write(final_html)


def generate_pages_recursive(dir_path_content, template_path, dest_dir_path, basepath="/"):
    """Recursively generate HTML pages from all markdown files in content directory.
    
    Crawls the content directory structure and generates corresponding HTML files
    in the destination directory, maintaining the same directory structure.
    
    Args:
        dir_path_content: Root path to the content directory (containing markdown files).
        template_path: Path to the HTML template file.
        dest_dir_path: Root path where generated HTML files should be written.
        basepath: Base path for the site (default "/").
    """
    # Iterate through all entries in the content directory
    for entry in os.listdir(dir_path_content):
        entry_path = os.path.join(dir_path_content, entry)
        
        if os.path.isfile(entry_path):
            # If it's a markdown file, generate an HTML page for it
            if entry.endswith('.md'):
                # Create the corresponding output path
                html_filename = entry.replace('.md', '.html')
                dest_path = os.path.join(dest_dir_path, html_filename)
                
                # Generate the HTML page
                generate_page(entry_path, template_path, dest_path, basepath)
        
        elif os.path.isdir(entry_path):
            # If it's a directory, recursively process it
            dest_subdir = os.path.join(dest_dir_path, entry)
            
            # Create the destination subdirectory if it doesn't exist
            if not os.path.exists(dest_subdir):
                os.makedirs(dest_subdir)
            
            # Recursively generate pages in the subdirectory
            generate_pages_recursive(entry_path, template_path, dest_subdir, basepath)
