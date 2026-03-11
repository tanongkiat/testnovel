#!/usr/bin/env python3
"""
Merge all individual translated chapter files into a single JSON file
"""

import json
import os


def merge_translated_chapters(input_folder="translated_chapters", output_file="侯夫人與殺豬刀_translated.json"):
    """
    Merge all individual chapter JSON files into one
    
    Args:
        input_folder: Path to folder containing chapter files
        output_file: Output merged JSON filename
    """
    print(f"{'='*60}")
    print("Translated Chapters Merger")
    print(f"{'='*60}\n")
    
    if not os.path.exists(input_folder):
        print(f"Error: Folder '{input_folder}' not found!")
        return False
    
    # Get all chapter files
    print(f"Reading from: {input_folder}/")
    chapter_files = [f for f in os.listdir(input_folder) 
                     if f.startswith('chapter_') and f.endswith('.json')]
    
    if not chapter_files:
        print(f"Error: No chapter files found in {input_folder}/")
        return False
    
    print(f"Found {len(chapter_files)} chapter files\n")
    
    all_chapters = []
    failed_files = []
    
    for chapter_file in chapter_files:
        file_path = os.path.join(input_folder, chapter_file)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                chapter_data = json.load(f)
                all_chapters.append(chapter_data)
                chapter_num = chapter_data.get('chapter_number', '?')
                print(f"  ✓ Loaded chapter {chapter_num}")
        except Exception as e:
            failed_files.append(chapter_file)
            print(f"  ✗ Error reading {chapter_file}: {e}")
    
    if not all_chapters:
        print("\nError: No chapters could be loaded!")
        return False
    
    # Sort by chapter number
    print(f"\nSorting chapters...")
    all_chapters.sort(key=lambda x: x.get('chapter_number', 0))
    
    # Display chapter range
    first_chapter = all_chapters[0].get('chapter_number')
    last_chapter = all_chapters[-1].get('chapter_number')
    print(f"Chapter range: {first_chapter} - {last_chapter}")
    
    # Check for gaps
    chapter_numbers = [ch.get('chapter_number') for ch in all_chapters]
    expected_range = set(range(first_chapter, last_chapter + 1))
    actual_set = set(chapter_numbers)
    missing = sorted(expected_range - actual_set)
    
    if missing:
        print(f"\n⚠️  Warning: Missing chapters in sequence: {missing}")
    else:
        print(f"✓ No gaps in chapter sequence")
    
    # Save merged file
    print(f"\nSaving merged file: {output_file}")
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_chapters, f, ensure_ascii=False, indent=2)
        print(f"✓ Successfully saved {len(all_chapters)} chapters")
    except Exception as e:
        print(f"✗ Error saving file: {e}")
        return False
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Total chapters merged: {len(all_chapters)}")
    print(f"Output file: {output_file}")
    print(f"File size: {os.path.getsize(output_file) / 1024 / 1024:.2f} MB")
    
    if failed_files:
        print(f"\nFailed to load {len(failed_files)} files:")
        for f in failed_files:
            print(f"  - {f}")
    
    if missing:
        print(f"\nNote: {len(missing)} chapters missing from sequence")
        print("Use translate_chapter_chunked.py to translate missing chapters")
    
    print(f"\n✓ Done! You can now use json_to_html.py to generate HTML")
    print(f"{'='*60}")
    
    return True


def main():
    print("\nThis script merges all individual chapter files into one JSON\n")
    
    # Allow custom paths
    use_default = input("Use default paths? (y/n): ").strip().lower()
    
    if use_default == 'y':
        input_folder = "translated_chapters"
        output_file = "侯夫人與殺豬刀_translated.json"
    else:
        input_folder = input("Enter input folder (default: translated_chapters): ").strip() or "translated_chapters"
        output_file = input("Enter output filename (default: 侯夫人與殺豬刀_translated.json): ").strip() or "侯夫人與殺豬刀_translated.json"
    
    print()
    success = merge_translated_chapters(input_folder, output_file)
    
    if not success:
        print("\n✗ Merge failed!")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
