#!/usr/bin/env python3
"""
Replace text in all translated chapters using a dictionary of replacements
"""

import json
import os
import sys


# Define replacement dictionaries for each novel type
NOVEL_TYPE_REPLACEMENTS = {
    "historical": {
        "มาร์ควิส": "ท่านโหว",
        "ข้าราชบริพาร": "ข้ารับใช้",
        "มาดาม": "ฮูหยิน",
        "ประตูเมริเดียน": "ประตูอู่เหมิน",
        "บัญชีเสือ": "บัญชีลับ",
        "หว่านเชื้อ": "สืบทายาท",
        "แค่เลือดนิดหน่อย": "แค่เลือดออกนิดเดียว",
        "กลับไปคนเดิม": "กลับไปเป็นเหมือนเดิม",
        "การเชี่ยวชาญในศิลปะนี้": "ความชำนาญในศาสตร์ขนาดนี้",
    },
    "fantasy": {
        "มาร์ควิส": "ท่านโหว",
        "ข้าราชบริพาร": "ข้ารับใช้",
        "มาดาม": "ฮูหยิน",
        "พลังวิเศษ": "พลังเวทมนตร์",
        "อาณาจักร": "อาณาจักร",
    },
    "romance": {
        "มาร์ควิส": "ท่านโหว",
        "ข้าราชบริพาร": "ข้ารับใช้",
        "มาดาม": "ฮูหยิน",
        "คุณชาย": "ท่านชาย",
        "คุณหญิง": "ท่านหญิง",
    },
    "modern": {
        "บริษัท": "บริษัท",
        "ซีอีโอ": "ซีอีโอ",
        "ประธาน": "ประธาน",
    },
    "xianxia": {
        "การเพาะปลูก": "การบ่มเพาะวิชา",
        "ดินแดนอมตะ": "ดินแดนเซียน",
        "พลังเวท": "พลังชี",
        "ระดับ": "ขั้น",
    },
    "wuxia": {
        "มาร์ควิส": "ท่านโหว",
        "ข้าราชบริพาร": "ข้ารับใช้",
        "ศิลปะการต่อสู้": "กังฟู",
        "พลังภายใน": "กำลังภายใน",
        "นักรบ": "นักดาบ",
    },
    "custom": {
        # Empty - user can add their own
    }
}


def select_novel_type():
    """
    Display available novel types and let user select one
    
    Returns:
        Selected novel type key or None if cancelled
    """
    types = list(NOVEL_TYPE_REPLACEMENTS.keys())
    
    print("=" * 60)
    print("Select Novel Type:")
    print("=" * 60)
    print("1. Historical (หมู่บ้านโบราณ - ราชสำนัก)")
    print("2. Fantasy (แฟนตาซี)")
    print("3. Romance (โรแมนซ์)")
    print("4. Modern (ร่วมสมัย)")
    print("5. Xianxia (เซียนเซี่ย - ภูตผีปีศาจ)")
    print("6. Wuxia (อู๋เซี่ย - ยุทธ์)")
    print("7. Custom (กำหนดเอง)")
    print("\n0. Cancel")
    print("=" * 60)
    
    type_map = {
        1: "historical",
        2: "fantasy",
        3: "romance",
        4: "modern",
        5: "xianxia",
        6: "wuxia",
        7: "custom"
    }
    
    while True:
        try:
            choice = input("\nSelect novel type (enter number): ").strip()
            choice_num = int(choice)
            
            if choice_num == 0:
                print("Cancelled.")
                return None
            
            if choice_num in type_map:
                selected = type_map[choice_num]
                replacements = NOVEL_TYPE_REPLACEMENTS[selected]
                print(f"\n✓ Selected: {selected}")
                print(f"  Replacements defined: {len(replacements)}\n")
                return selected
            else:
                print(f"Invalid choice. Please enter a number between 0 and 7.")
        except ValueError:
            print("Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            print("\n\nCancelled.")
            return None


def list_books(books_dir="books"):
    """
    List all available books in the books directory
    
    Args:
        books_dir: Base directory containing book folders (default: "books")
    
    Returns:
        List of book folder names
    """
    if not os.path.exists(books_dir):
        print(f"Error: Books directory '{books_dir}' not found!")
        return []
    
    books = []
    for item in os.listdir(books_dir):
        item_path = os.path.join(books_dir, item)
        if os.path.isdir(item_path):
            # Check if it has a translated_chapters folder
            chapters_path = os.path.join(item_path, "translated_chapters")
            if os.path.exists(chapters_path):
                books.append(item)
    
    return sorted(books)


def select_book(books_dir="books"):
    """
    Display available books and let user select one
    
    Args:
        books_dir: Base directory containing book folders (default: "books")
    
    Returns:
        Selected book name or None if cancelled
    """
    books = list_books(books_dir)
    
    if not books:
        print("No books with translated chapters found!")
        return None
    
    print("=" * 60)
    print("Available Books:")
    print("=" * 60)
    for i, book in enumerate(books, 1):
        # Count chapters
        chapters_path = os.path.join(books_dir, book, "translated_chapters")
        chapter_files = [f for f in os.listdir(chapters_path) 
                        if f.startswith('chapter_') and f.endswith('.json')]
        print(f"{i}. {book} ({len(chapter_files)} chapters)")
    
    print("\n0. Cancel")
    print("=" * 60)
    
    while True:
        try:
            choice = input("\nSelect a book (enter number): ").strip()
            choice_num = int(choice)
            
            if choice_num == 0:
                print("Cancelled.")
                return None
            
            if 1 <= choice_num <= len(books):
                selected = books[choice_num - 1]
                print(f"\n✓ Selected: {selected}\n")
                return selected
            else:
                print(f"Invalid choice. Please enter a number between 0 and {len(books)}.")
        except ValueError:
            print("Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            print("\n\nCancelled.")
            return None


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
    print("""
╔═══════════════════════════════════════════════════════════╗
║         Text Replacement Tool for Translations          ║
║                                                         ║
║  Replace terms in translated chapters based on         ║
║  novel type (Historical, Fantasy, Romance, etc.)        ║
╚═══════════════════════════════════════════════════════════╝
""")
    
    # Step 1: Select novel type
    novel_type = select_novel_type()
    
    if not novel_type:
        print("No novel type selected. Exiting.")
        sys.exit(0)
    
    # Get replacements for selected type
    replacements = NOVEL_TYPE_REPLACEMENTS[novel_type]
    
    # If custom type, allow user to add custom replacements
    if novel_type == "custom":
        print("\nNo predefined replacements for custom type.")
        print("You can add your custom replacements by editing the NOVEL_TYPE_REPLACEMENTS['custom'] dictionary in the script.")
        add_custom = input("\nDo you want to add custom replacements now? (y/n): ").strip().lower()
        
        if add_custom == 'y':
            print("\nEnter replacements (format: old_text => new_text)")
            print("Type 'done' when finished")
            
            while True:
                entry = input("Replacement: ").strip()
                if entry.lower() == 'done':
                    break
                
                if '=>' in entry:
                    old_text, new_text = entry.split('=>', 1)
                    old_text = old_text.strip()
                    new_text = new_text.strip()
                    
                    if old_text and new_text:
                        replacements[old_text] = new_text
                        print(f"  ✓ Added: '{old_text}' → '{new_text}'")
                    else:
                        print("  ✗ Invalid format. Please use: old_text => new_text")
                else:
                    print("  ✗ Invalid format. Please use: old_text => new_text")
        
        if not replacements:
            print("\nNo replacements defined. Exiting.")
            sys.exit(0)
    
    print(f"\nUsing {len(replacements)} replacement(s) for '{novel_type}' type\n")
    
    # Step 2: Select book from directory
    book_name = select_book(books_dir="books")
    
    if book_name:
        # Run the replacement
        replace_text_in_chapters(
            book_name=book_name,
            replacements_dict=replacements,
            books_dir="books"
        )
    else:
        print("No book selected. Exiting.")
        sys.exit(0)
