#!/usr/bin/env python3
"""
Python script to translate text using Google's translateHtml API
"""

import requests
import json
import re
import time
import os
import random


def translate_html(text, source_text="", source_lang="zh-CN", target_lang="th"):
    """
    Translate HTML text using Google's translateHtml API
    
    Args:
        text: The text to translate
        source_text: Additional source text (optional)
        source_lang: Source language code (default: zh-CN)
        target_lang: Target language code (default: th)
    
    Returns:
        Response from the API
    """
    url = "https://translate-pa.googleapis.com/v1/translateHtml"
    
    headers = {
        'accept': '*/*',
        'accept-language': 'th,en-US;q=0.9,en;q=0.8',
        'content-type': 'application/json+protobuf',
        'origin': 'https://tanongkiat.github.io',
        'priority': 'u=1, i',
        'referer': 'https://tanongkiat.github.io/',
        'sec-ch-ua': '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
        'x-browser-channel': 'stable',
        'x-browser-copyright': 'Copyright 2026 Google LLC. All rights reserved.',
        'x-browser-validation': 'lbZsdhRUx3IBWze7ecNtqg7Djq0=',
        'x-browser-year': '2026',
        'x-client-data': 'CJS2yQEIprbJAQipncoBCKLhygEIkqHLAQiGoM0BCNOxzwE=',
        'x-goog-api-key': 'AIzaSyATBXajvzQLTDHEQbcpq0Ihe0vWDHmO520'
    }
    
    # Construct the data payload
    data = [
        [
            [text, source_text],
            source_lang,
            target_lang
        ],
        "te_lib"
    ]
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return None


def parse_chapters(file_path):
    """
    Parse the text file and split it into chapters
    
    Args:
        file_path: Path to the .txt file
        
    Returns:
        List of tuples (chapter_number, chapter_title, chapter_content)
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the start of chapters
    chapter_start = content.find('------章節內容開始-------')
    if chapter_start == -1:
        # If marker not found, use the whole content
        chapter_start = 0
    else:
        chapter_start += len('------章節內容開始-------')
    
    # Get the content from chapters onwards
    chapters_content = content[chapter_start:]
    
    # Split by chapter pattern: 第X章
    chapter_pattern = r'(第\d+章[^\n]*)'
    parts = re.split(chapter_pattern, chapters_content)
    
    chapters = []
    # parts[0] is content before first chapter (if any)
    # parts[1], parts[2] = chapter1 title, chapter1 content
    # parts[3], parts[4] = chapter2 title, chapter2 content
    # ...
    
    for i in range(1, len(parts), 2):
        if i + 1 < len(parts):
            chapter_title = parts[i].strip()
            chapter_content = parts[i + 1].strip()
            
            # Extract chapter number
            match = re.match(r'第(\d+)章', chapter_title)
            if match:
                chapter_num = int(match.group(1))
                chapters.append((chapter_num, chapter_title, chapter_content))
    
    return chapters


def translate_chapter(chapter_num, chapter_title, chapter_content, source_text="侯夫人與殺豬刀", max_retries=3):
    """
    Translate a single chapter with retry logic
    
    Args:
        chapter_num: Chapter number
        chapter_title: Chapter title
        chapter_content: Chapter content
        source_text: Source text name
        max_retries: Maximum number of retry attempts
        
    Returns:
        Translated chapter or None if failed
    """
    print(f"Translating Chapter {chapter_num}: {chapter_title}...")
    
    # Combine title and content for translation
    full_text = f"{chapter_title}\n\n{chapter_content}"
    
    # Try multiple times with exponential backoff
    for attempt in range(max_retries):
        try:
            # Translate
            result = translate_html(full_text, source_text, "zh-CN", "th")
            
            if result:
                return result
            else:
                print(f"  Attempt {attempt + 1}/{max_retries} failed - no result")
                
        except Exception as e:
            print(f"  Attempt {attempt + 1}/{max_retries} failed: {e}")
        
        # Wait before retry with exponential backoff
        if attempt < max_retries - 1:
            wait_time = (2 ** attempt) + random.uniform(1, 3)
            print(f"  Waiting {wait_time:.1f}s before retry...")
            time.sleep(wait_time)
    
    return None


def main():
    input_file = "侯夫人與殺豬刀.txt"
    output_folder = "translated_chapters"
    output_file = "侯夫人與殺豬刀_translated.json"
    
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created folder: {output_folder}")
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found!")
        return
    
    print(f"Reading from {input_file}...")
    chapters = parse_chapters(input_file)
    
    print(f"Found {len(chapters)} chapters")
    
    # Ask user which chapters to translate
    print("\nOptions:")
    print("1. Translate all chapters")
    print("2. Translate specific chapter")
    print("3. Translate a range of chapters")
    print("4. Merge existing translated files into one JSON")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "4":
        merge_translated_files(output_folder, output_file)
        return
    
    chapters_to_translate = []
    
    if choice == "1":
        chapters_to_translate = chapters
    elif choice == "2":
        chapter_num = int(input("Enter chapter number: "))
        chapters_to_translate = [ch for ch in chapters if ch[0] == chapter_num]
    elif choice == "3":
        start = int(input("Enter start chapter: "))
        end = int(input("Enter end chapter: "))
        chapters_to_translate = [ch for ch in chapters if start <= ch[0] <= end]
    else:
        print("Invalid choice")
        return
    
    if not chapters_to_translate:
        print("No chapters to translate")
        return
    
    print(f"\nTranslating {len(chapters_to_translate)} chapters...")
    print("Note: Using random delays (3-7s) between requests to avoid rate limiting")
    print(f"Each chapter will be saved to: {output_folder}/")
    
    translated_count = 0
    failed_chapters = []
    
    for idx, (chapter_num, chapter_title, chapter_content) in enumerate(chapters_to_translate, 1):
        print(f"\n[{idx}/{len(chapters_to_translate)}] ", end="")
        
        # Check if chapter already translated
        chapter_file = os.path.join(output_folder, f"chapter_{chapter_num:03d}.json")
        if os.path.exists(chapter_file):
            print(f"✓ Chapter {chapter_num} already exists, skipping...")
            translated_count += 1
            continue
        
        result = translate_chapter(chapter_num, chapter_title, chapter_content)
        
        if result:
            chapter_data = {
                "chapter_number": chapter_num,
                "chapter_title": chapter_title,
                "original": chapter_content,
                "translated": result
            }
            
            # Save individual chapter file
            with open(chapter_file, 'w', encoding='utf-8') as f:
                json.dump(chapter_data, f, ensure_ascii=False, indent=2)
            
            translated_count += 1
            print(f"✓ Chapter {chapter_num} translated and saved")
        else:
            failed_chapters.append(chapter_num)
            print(f"✗ Chapter {chapter_num} translation failed after retries")
        
        # Random delay between requests (3-7 seconds)
        if idx < len(chapters_to_translate):
            delay = random.uniform(3, 7)
            print(f"  ⏱️  Waiting {delay:.1f}s before next request...")
            time.sleep(delay)
    
    print(f"\n{'='*60}")
    print(f"✓ Translation complete! {translated_count}/{len(chapters_to_translate)} chapters")
    
    if failed_chapters:
        print(f"\n⚠️  Failed chapters: {failed_chapters}")
        print(f"You can retry these chapters later")
    
    # Ask if user wants to merge now
    print(f"\nMerge all translated chapters into {output_file}?")
    merge_choice = input("Enter 'y' to merge now, or any other key to skip: ").strip().lower()
    
    if merge_choice == 'y':
        merge_translated_files(output_folder, output_file)


def merge_translated_files(folder_path, output_file):
    """
    Merge all individual chapter JSON files into one
    
    Args:
        folder_path: Path to folder containing chapter files
        output_file: Output merged JSON filename
    """
    print(f"\n{'='*60}")
    print(f"Merging translated chapters from {folder_path}...")
    
    if not os.path.exists(folder_path):
        print(f"Error: Folder {folder_path} not found!")
        return
    
    # Get all chapter files
    chapter_files = sorted([f for f in os.listdir(folder_path) if f.startswith('chapter_') and f.endswith('.json')])
    
    if not chapter_files:
        print(f"No chapter files found in {folder_path}")
        return
    
    print(f"Found {len(chapter_files)} chapter files")
    
    all_chapters = []
    
    for chapter_file in chapter_files:
        file_path = os.path.join(folder_path, chapter_file)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                chapter_data = json.load(f)
                all_chapters.append(chapter_data)
        except Exception as e:
            print(f"Error reading {chapter_file}: {e}")
    
    # Sort by chapter number
    all_chapters.sort(key=lambda x: x['chapter_number'])
    
    # Save merged file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_chapters, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Merged {len(all_chapters)} chapters into {output_file}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
