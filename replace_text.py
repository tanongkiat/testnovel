#!/usr/bin/env python3
"""
Replace text in all translated chapters
"""

import json
import os


def replace_in_translated(data, old_text, new_text):
    """
    Replace text in the translated field, handling nested list structure
    """
    if isinstance(data, list):
        # Handle nested list structure [[translated_text, source_text]]
        if len(data) > 0 and isinstance(data[0], list) and len(data[0]) > 0:
            data[0][0] = data[0][0].replace(old_text, new_text)
        elif len(data) > 0 and isinstance(data[0], str):
            data[0] = data[0].replace(old_text, new_text)
    elif isinstance(data, str):
        data = data.replace(old_text, new_text)
    
    return data


def replace_text_in_chapters(folder="translated_chapters", old_text="ท่านมาร์ควิสอู๋อัน", new_text="ท่านอู๋อันโหว"):
    """
    Replace text in all translated chapter files
    """
    print(f"Replacing '{old_text}' with '{new_text}' in all chapters...")
    print(f"Folder: {folder}/\n")
    
    if not os.path.exists(folder):
        print(f"Error: Folder '{folder}' not found!")
        return False
    
    files = [f for f in os.listdir(folder) if f.startswith('chapter_') and f.endswith('.json')]
    files.sort()
    
    if not files:
        print(f"Error: No chapter files found in {folder}/")
        return False
    
    print(f"Found {len(files)} chapter files")
    
    total_replacements = 0
    updated_chapters = 0
    
    for filename in files:
        filepath = os.path.join(folder, filename)
        
        try:
            # Read the file
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convert to string to count occurrences
            original_str = json.dumps(data['translated'], ensure_ascii=False)
            count_before = original_str.count(old_text)
            
            if count_before > 0:
                # Replace in the translated field
                data['translated'] = replace_in_translated(data['translated'], old_text, new_text)
                
                # Verify replacement
                new_str = json.dumps(data['translated'], ensure_ascii=False)
                count_after = new_str.count(old_text)
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
    # Replace "ท่านมาร์ควิส" with "ท่านโหว"
    replace_text_in_chapters(
        folder="translated_chapters",
        old_text="ท่านหญิง",
        new_text="นายหญิง"
    )
