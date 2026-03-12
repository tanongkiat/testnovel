#!/usr/bin/env python3
"""
Replace text in all translated chapters using a dictionary of replacements
"""

import json
import os


def replace_in_translated(data, replacements_dict):
    """
    Replace text in the translated field using a dictionary, handling nested list structure
    
    Args:
        data: The data structure to process
        replacements_dict: Dictionary of {old_text: new_text} pairs
    """
    if isinstance(data, list):
        # Handle nested list structure [[translated_text, source_text]]
        if len(data) > 0 and isinstance(data[0], list) and len(data[0]) > 0:
            for old_text, new_text in replacements_dict.items():
                data[0][0] = data[0][0].replace(old_text, new_text)
        elif len(data) > 0 and isinstance(data[0], str):
            for old_text, new_text in replacements_dict.items():
                data[0] = data[0].replace(old_text, new_text)
    elif isinstance(data, str):
        for old_text, new_text in replacements_dict.items():
            data = data.replace(old_text, new_text)
    
    return data


def replace_text_in_chapters(book_name, replacements_dict, books_dir="books"):
    """
    Replace text in all translated chapter files using a dictionary
    
    Args:
        book_name: Name of the book folder (e.g., "侯夫人與殺豬刀")
        replacements_dict: Dictionary of {old_text: new_text} pairs
        books_dir: Base directory containing book folders (default: "books")
    """
    folder = os.path.join(books_dir, book_name, "translated_chapters")
    
    print(f"Applying replacements to: {book_name}")
    print(f"Folder: {folder}/")
    print(f"Number of replacements: {len(replacements_dict)}\n")
    
    for old, new in replacements_dict.items():
        print(f"  '{old}' → '{new}'")
    print()
    
    if not os.path.exists(folder):
        print(f"Error: Folder '{folder}' not found!")
        return False
    
    files = [f for f in os.listdir(folder) if f.startswith('chapter_') and f.endswith('.json')]
    files.sort()
    
    if not files:
        print(f"Error: No chapter files found in {folder}/")
        return False
    
    print(f"Found {len(files)} chapter files\n")
    
    total_replacements = 0
    updated_chapters = 0
    
    for filename in files:
        filepath = os.path.join(folder, filename)
        
        try:
            # Read the file
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Count occurrences before replacement
            original_str = json.dumps(data['translated'], ensure_ascii=False)
            count_before = sum(original_str.count(old_text) for old_text in replacements_dict.keys())
            
            if count_before > 0:
                # Replace in the translated field
                data['translated'] = replace_in_translated(data['translated'], replacements_dict)
                
                # Verify replacement
                new_str = json.dumps(data['translated'], ensure_ascii=False)
                count_after = sum(new_str.count(old_text) for old_text in replacements_dict.keys())
                replacements = count_before - count_after
                
                # Save the file
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                total_replacements += replacements
                updated_chapters += 1
                chapter_num = data.get('chapter_number', '?')
                print(f"  ✓ Chapter {chapter_num}: {replacements} replacement(s)")
        
        except Exception as e:
            print(f"  ✗ Error processing {filename}: {e}")
    
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Total replacements: {total_replacements}")
    print(f"Chapters updated: {updated_chapters}/{len(files)}")
    print(f"\n✓ Done!")
    
    return True


if __name__ == "__main__":
    # Define your replacements dictionary
    replacements = {
        "มาร์ควิส": "ท่านโหว",
        "ข้าราชบริพาร": "ข้ารับใช้",
        "มาดาม": "ฮูหยิน"
        
        # Add more replacements as needed:
        # "old_text_1": "new_text_1",
        # "old_text_2": "new_text_2",
    }
    
    # Specify the book name (folder name in books/)
    book_name = "殘王爆寵囂張醫妃"
    
    # Run the replacement
    replace_text_in_chapters(
        book_name=book_name,
        replacements_dict=replacements,
        books_dir="books"
    )
