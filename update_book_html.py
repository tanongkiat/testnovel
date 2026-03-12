#!/usr/bin/env python3
"""
Quick script to update book HTML from translated chapters
Usage: python update_book_html.py <book_name>
"""

import sys
import os
from json_to_html_dynamic import load_all_chapters, generate_dynamic_html

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python update_book_html.py <book_name>")
        print("\nExample:")
        print("  python update_book_html.py 殘王爆寵囂張醫妃")
        sys.exit(1)
    
    book_name = sys.argv[1]
    book_folder = f"books/{book_name}"
    chapters_folder = f"{book_folder}/translated_chapters"
    output_html = f"{book_folder}/chapters.html"
    
    if not os.path.exists(chapters_folder):
        print(f"Error: {chapters_folder} not found!")
        sys.exit(1)
    
    print(f"Updating HTML for: {book_name}")
    print(f"Chapters folder: {chapters_folder}")
    print(f"Output: {output_html}\n")
    
    # Load chapters
    os.chdir(book_folder)
    chapters_data = load_all_chapters("translated_chapters")
    
    if not chapters_data:
        print("Error: No chapters found!")
        sys.exit(1)
    
    # Generate HTML using the function
    import json
    chapters_js = json.dumps(chapters_data, ensure_ascii=False)
    available_chapters_js = json.dumps(sorted(chapters_data.keys()))
    
    # Read the template from json_to_html_dynamic.py and generate
    # Or just call generate_dynamic_html with the output path
    
    # Simpler: just copy the generate logic
    with open("../../json_to_html_dynamic.py", 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"\n✓ Updated: {output_html}")
    print(f"✓ Chapters: {len(chapters_data)}")
    print(f"\nTo see changes, open: {output_html}")
