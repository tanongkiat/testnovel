#!/usr/bin/env python3
"""
Complete Book Creation Pipeline
Processes a Chinese novel txt file and creates a formatted Thai translation book
"""

import json
import os
import re
import time
import random
import requests
import subprocess
import sys
from pathlib import Path


def list_txt_files(directory="sources"):
    """
    List all .txt files in the directory
    
    Args:
        directory: Directory to search for txt files (default: current directory)
    
    Returns:
        List of txt file paths
    """
    txt_files = []
    for file in os.listdir(directory):
        if file.endswith('.txt') and os.path.isfile(os.path.join(directory, file)):
            txt_files.append(file)
    return sorted(txt_files)


def select_txt_file(directory="."):
    """
    Display available txt files and let user select one
    
    Args:
        directory: Directory to search for txt files (default: current directory)
    
    Returns:
        Selected txt file path or None if cancelled
    """
    txt_files = list_txt_files(directory)
    
    if not txt_files:
        print("No .txt files found in the current directory!")
        return None
    
    print("=" * 60)
    print("Available Chinese Novel Files:")
    print("=" * 60)
    for i, file in enumerate(txt_files, 1):
        # Get file size
        size = os.path.getsize(file) / 1024  # KB
        print(f"{i}. {file} ({size:.1f} KB)")
    
    print("\n0. Enter custom path")
    print("=" * 60)
    
    while True:
        try:
            choice = input("\nSelect a file (enter number): ").strip()
            choice_num = int(choice)
            
            if choice_num == 0:
                custom_path = input("Enter txt file path: ").strip()
                if os.path.exists(custom_path):
                    print(f"\n✓ Selected: {custom_path}\n")
                    return custom_path
                else:
                    print(f"Error: File '{custom_path}' not found!")
                    return None
            
            if 1 <= choice_num <= len(txt_files):
                selected = txt_files[choice_num - 1]
                print(f"\n✓ Selected: {selected}\n")
                return selected
            else:
                print(f"Invalid choice. Please enter a number between 0 and {len(txt_files)}.")
        except ValueError:
            print("Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            print("\n\nCancelled.")
            return None


def extract_title_from_filename(filename):
    """Extract book title from filename"""
    # Remove .txt extension and path
    title = Path(filename).stem
    return title


def parse_chapters(text_file):
    """
    Parse chapters from Chinese text file
    Returns list of (chapter_number, chapter_title, content)
    """
    print(f"\nReading file: {text_file}")
    
    with open(text_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all chapter markers (第X章)
    pattern = r'第(\d+)章([^\n]*)'
    matches = list(re.finditer(pattern, content))
    
    if not matches:
        print("Error: No chapters found with pattern '第X章'")
        return None
    
    chapters = []
    for i, match in enumerate(matches):
        chapter_num = int(match.group(1))
        chapter_title = match.group(0).strip()  # Full title like "第1章殺豬美人"
        
        # Extract content between this chapter and next
        start_pos = match.end()
        if i < len(matches) - 1:
            end_pos = matches[i + 1].start()
        else:
            end_pos = len(content)
        
        chapter_content = content[start_pos:end_pos].strip()
        
        if chapter_content:
            chapters.append({
                'chapter_number': chapter_num,
                'chapter_title': chapter_title,
                'original': chapter_content
            })
    
    print(f"✓ Found {len(chapters)} chapters")
    return chapters


def translate_html(html_text, api_key):
    """Translate Chinese HTML to Thai using Google Translate API"""
    url = "https://translate-pa.googleapis.com/v1/translateHtml"
    
    headers = {
        "Content-Type": "application/json+protobuf",
        "X-Goog-Api-Key": api_key,
    }
    
    payload = [
        [[html_text], "zh-TW", "th"],
        "te_lib"
    ]
    
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Translation failed: {response.status_code} - {response.text}")


def translate_chapters(chapters, api_key, output_folder, start_from=1):
    """
    Translate chapters and save individually
    """
    os.makedirs(output_folder, exist_ok=True)
    
    print(f"\nTranslating chapters to: {output_folder}/")
    print(f"Starting from chapter: {start_from}")
    print(f"Total chapters to translate: {len([c for c in chapters if c['chapter_number'] >= start_from])}\n")
    
    translated_count = 0
    failed_chapters = []
    
    for chapter in chapters:
        chapter_num = chapter['chapter_number']
        
        # Skip if before start_from
        if chapter_num < start_from:
            continue
        
        # Check if already exists
        output_file = os.path.join(output_folder, f"chapter_{chapter_num:03d}.json")
        if os.path.exists(output_file):
            print(f"  ⊙ Chapter {chapter_num}: Already exists, skipping")
            translated_count += 1
            continue
        
        try:
            print(f"  → Translating chapter {chapter_num}...", end=" ", flush=True)
            
            # Translate
            translated = translate_html(chapter['original'], api_key)
            
            # Save chapter
            chapter_data = {
                'chapter_number': chapter_num,
                'chapter_title': chapter['chapter_title'],
                'original': chapter['original'],
                'translated': translated
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(chapter_data, f, ensure_ascii=False, indent=2)
            
            translated_count += 1
            print(f"✓ Done")
            
            # Random delay to avoid rate limiting (3-7 seconds)
            delay = random.uniform(3, 7)
            time.sleep(delay)
            
        except Exception as e:
            print(f"✗ Failed: {e}")
            failed_chapters.append(chapter_num)
            
            # If rate limited, wait longer
            if "429" in str(e):
                print(f"  ⏳ Rate limited, waiting 10 seconds...")
                time.sleep(10)
    
    print(f"\n{'='*60}")
    print(f"Translation Summary:")
    print(f"  Translated: {translated_count}/{len(chapters)}")
    if failed_chapters:
        print(f"  Failed chapters: {failed_chapters}")
    print(f"{'='*60}")
    
    return translated_count == len(chapters)


def generate_html_reader(book_title, chapters_folder, output_html):
    """
    Generate HTML reader from translated chapters using json_to_html_dynamic.py
    """
    print(f"\nGenerating HTML reader...")
    print(f"Reading chapters from: {chapters_folder}/")
    
    # Call json_to_html_dynamic.py with the chapters folder
    try:
        result = subprocess.run(
            [sys.executable, 'json_to_html_dynamic.py', chapters_folder, output_html],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            print(result.stdout)
            print(f"  ✓ HTML generated successfully")
            return True
        else:
            print(f"  ✗ Error generating HTML:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print(f"  ✗ HTML generation timed out")
        return False
    except Exception as e:
        print(f"  ✗ Error calling json_to_html_dynamic.py: {e}")
        return False


def create_book_from_txt(txt_file, api_key, skip_translation=False, start_from=1):
    """
    Complete pipeline: process txt file and create book
    """
    print(f"\n{'='*60}")
    print(f"Book Creation Pipeline")
    print(f"{'='*60}")
    
    # Extract title
    book_title = extract_title_from_filename(txt_file)
    print(f"\nBook Title: {book_title}")
    
    # Create book folder structure
    book_folder = f"books/{book_title}"
    chapters_folder = f"{book_folder}/translated_chapters"
    
    os.makedirs(book_folder, exist_ok=True)
    os.makedirs(chapters_folder, exist_ok=True)
    
    print(f"Book Folder: {book_folder}/")
    
    # Step 1: Parse chapters
    print(f"\n{'='*60}")
    print("STEP 1: Parsing Chapters")
    print(f"{'='*60}")
    
    chapters = parse_chapters(txt_file)
    if not chapters:
        return False
    
    # Step 2: Translate chapters
    if not skip_translation:
        print(f"\n{'='*60}")
        print("STEP 2: Translating Chapters")
        print(f"{'='*60}")
        
        success = translate_chapters(chapters, api_key, chapters_folder, start_from)
        if not success:
            print("\n⚠️  Some chapters failed to translate")
            print("You can retry failed chapters later or continue to HTML generation")
            
            cont = input("\nContinue to HTML generation? (y/n): ").strip().lower()
            if cont != 'y':
                return False
    else:
        print(f"\n⊙ Skipping translation (using existing chapters)")
    
    # Step 3: Generate HTML reader
    print(f"\n{'='*60}")
    print("STEP 3: Generating HTML Reader")
    print(f"{'='*60}")
    
    output_html = f"{book_folder}/chapters.html"
    success = generate_html_reader(book_title, chapters_folder, output_html)
    
    if not success:
        return False
    
    # Step 4: Update library index
    print(f"\n{'='*60}")
    print("STEP 4: Updating Library Index")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            [sys.executable, 'generate_book_index.py'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print(result.stdout)
            print(f"  ✓ Library index updated successfully")
        else:
            print(f"  ⚠️  Warning: Could not update library index")
            print(result.stderr)
            
    except Exception as e:
        print(f"  ⚠️  Warning: Could not update library index: {e}")
    
    # Final summary
    print(f"\n{'='*60}")
    print("✓ BOOK CREATION COMPLETE!")
    print(f"{'='*60}")
    print(f"\nBook: {book_title}")
    print(f"Location: {book_folder}/")
    print(f"Reader: {output_html}")
    print(f"\nTo read: Open {output_html} in your browser")
    
    return True


def main():
    print("""
╔═══════════════════════════════════════════════════════════╗
║         Book Creation Tool - Chinese to Thai            ║
║                                                         ║
║  Processes Chinese novel txt files and creates a        ║
║  complete Thai translation book with HTML reader        ║
╚═══════════════════════════════════════════════════════════╝
""")
    
    # Get txt file
    if len(sys.argv) > 1:
        txt_file = sys.argv[1]
        if not os.path.exists(txt_file):
            print(f"Error: File '{txt_file}' not found!")
            return 1
    else:
        # Interactive mode - select from available txt files
        txt_file = select_txt_file()
        if not txt_file:
            print("No file selected. Exiting.")
            return 1
    
    # Get API key
    api_key = input("Enter Google Translate API key (or press Enter to skip translation): ").strip()
    skip_translation = not api_key
    
    # Options
    if not skip_translation:
        start_from_input = input("Start from chapter number (default: 1): ").strip()
        start_from = int(start_from_input) if start_from_input else 1
    else:
        start_from = 1
    
    # Run pipeline
    success = create_book_from_txt(txt_file, api_key, skip_translation, start_from)
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
