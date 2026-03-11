#!/usr/bin/env python3
"""
Translate a specific chapter by breaking it into smaller chunks
Use this for chapters that fail due to being too long or rate limiting
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
    """Parse the text file and split it into chapters"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    chapter_start = content.find('------章節內容開始-------')
    if chapter_start == -1:
        chapter_start = 0
    else:
        chapter_start += len('------章節內容開始-------')
    
    chapters_content = content[chapter_start:]
    chapter_pattern = r'(第\d+章[^\n]*)'
    parts = re.split(chapter_pattern, chapters_content)
    
    chapters = []
    for i in range(1, len(parts), 2):
        if i + 1 < len(parts):
            chapter_title = parts[i].strip()
            chapter_content = parts[i + 1].strip()
            
            match = re.match(r'第(\d+)章', chapter_title)
            if match:
                chapter_num = int(match.group(1))
                chapters.append((chapter_num, chapter_title, chapter_content))
    
    return chapters


def split_into_chunks(text, max_chars=2500):
    """
    Split text into smaller chunks at sentence boundaries
    
    Args:
        text: Text to split
        max_chars: Maximum characters per chunk (increased for speed)
        
    Returns:
        List of text chunks
    """
    # Split by paragraph markers first
    paragraphs = re.split(r'\n　　', text)
    
    chunks = []
    current_chunk = []
    current_length = 0
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        
        para_length = len(para)
        
        # If adding this paragraph would exceed max, save current chunk
        if current_chunk and current_length + para_length > max_chars:
            chunks.append('\n　　'.join(current_chunk))
            current_chunk = [para]
            current_length = para_length
        else:
            current_chunk.append(para)
            current_length += para_length
    
    # Add remaining paragraphs
    if current_chunk:
        chunks.append('\n　　'.join(current_chunk))
    
    return chunks


def translate_chunk(chunk, source_text, chunk_num, total_chunks, max_retries=3):
    """
    Translate a single chunk with retry logic
    
    Args:
        chunk: Text chunk to translate
        source_text: Source text name
        chunk_num: Current chunk number
        total_chunks: Total number of chunks
        max_retries: Maximum retry attempts
        
    Returns:
        Translated chunk or None if failed
    """
    print(f"  Translating chunk {chunk_num}/{total_chunks} ({len(chunk)} chars)...")
    
    for attempt in range(max_retries):
        try:
            result = translate_html(chunk, source_text, "zh-CN", "th")
            
            if result:
                print(f"    ✓ Chunk {chunk_num} translated")
                return result
            else:
                print(f"    Attempt {attempt + 1}/{max_retries} failed - no result")
                
        except Exception as e:
            print(f"    Attempt {attempt + 1}/{max_retries} failed: {e}")
        
        if attempt < max_retries - 1:
            wait_time = 1 + random.uniform(0.5, 1.5)  # Much shorter retry wait
            print(f"    Waiting {wait_time:.1f}s before retry...")
            time.sleep(wait_time)
    
    return None


def combine_translated_chunks(chunks):
    """
    Combine translated chunks into a single result
    
    Args:
        chunks: List of translated chunk results
        
    Returns:
        Combined translation in the expected format
    """
    # Extract the translated text from each chunk
    combined_text = []
    
    for chunk in chunks:
        if isinstance(chunk, list) and len(chunk) > 0:
            if isinstance(chunk[0], list) and len(chunk[0]) > 0:
                combined_text.append(chunk[0][0])
            elif isinstance(chunk[0], str):
                combined_text.append(chunk[0])
    
    # Join all translated texts
    full_translation = ' '.join(combined_text)
    
    # Return in the same format as the API
    return [[full_translation, "侯夫人與殺豬刀"]]


def get_missing_chapters(output_folder="translated_chapters"):
    """
    Check which chapters are missing from the translated_chapters folder
    Automatically detects the maximum chapter number from existing files
    
    Args:
        output_folder: Folder containing translated chapters
        
    Returns:
        List of missing chapter numbers
    """
    if not os.path.exists(output_folder):
        print("Warning: No translated_chapters folder found!")
        return []
    
    # Get all existing chapter files
    existing_files = os.listdir(output_folder)
    existing_chapters = set()
    
    for filename in existing_files:
        if filename.startswith('chapter_') and filename.endswith('.json'):
            try:
                # Extract chapter number from filename like "chapter_023.json"
                chapter_num = int(filename.replace('chapter_', '').replace('.json', ''))
                existing_chapters.add(chapter_num)
            except ValueError:
                continue
    
    if not existing_chapters:
        print("Warning: No translated chapters found!")
        return []
    
    # Find the maximum chapter number (this is our limit)
    max_chapter = max(existing_chapters)
    print(f"Maximum chapter found: {max_chapter}")
    
    # Find missing chapters from 1 to max_chapter
    all_chapters = set(range(1, max_chapter + 1))
    missing_chapters = sorted(all_chapters - existing_chapters)
    
    return missing_chapters


def translate_chapter_chunked(chapter_num, input_file="侯夫人與殺豬刀.txt", output_folder="translated_chapters"):
    """
    Translate a specific chapter by breaking it into chunks
    
    Args:
        chapter_num: Chapter number to translate
        input_file: Path to input text file
        output_folder: Folder to save translated chapter
    """
    print(f"{'='*60}")
    print(f"Translating Chapter {chapter_num} using chunked method")
    print(f"{'='*60}\n")
    
    # Create output folder if needed
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Parse chapters
    print(f"Reading from {input_file}...")
    chapters = parse_chapters(input_file)
    
    # Find the requested chapter
    target_chapter = None
    for ch_num, ch_title, ch_content in chapters:
        if ch_num == chapter_num:
            target_chapter = (ch_num, ch_title, ch_content)
            break
    
    if not target_chapter:
        print(f"Error: Chapter {chapter_num} not found!")
        return False
    
    chapter_num, chapter_title, chapter_content = target_chapter
    print(f"Found: {chapter_title}")
    print(f"Content length: {len(chapter_content)} characters\n")
    
    # Split into chunks
    print("Splitting into chunks...")
    chunks = split_into_chunks(chapter_content, max_chars=1500)
    print(f"Created {len(chunks)} chunks\n")
    
    # Translate each chunk
    translated_chunks = []
    failed_chunks = []
    
    for i, chunk in enumerate(chunks, 1):
        result = translate_chunk(chunk, "侯夫人與殺豬刀", i, len(chunks))
        
        if result:
            translated_chunks.append(result)
        else:
            failed_chunks.append(i)
            print(f"    ✗ Chunk {i} failed after retries")
        
        # Wait between chunks (reduced to 2-4 seconds for speed)
        if i < len(chunks):
            delay = random.uniform(2, 4)
            print(f"  ⏱️  Waiting {delay:.1f}s before next chunk...\n")
            time.sleep(delay)
    
    # Check if all chunks translated successfully
    if failed_chunks:
        print(f"\n⚠️  Failed chunks: {failed_chunks}")
        print(f"Only {len(translated_chunks)}/{len(chunks)} chunks translated")
        return False
    
    # Combine chunks
    print(f"\n{'='*60}")
    print("Combining translated chunks...")
    combined_result = combine_translated_chunks(translated_chunks)
    
    # Save result
    chapter_data = {
        "chapter_number": chapter_num,
        "chapter_title": chapter_title,
        "original": chapter_content,
        "translated": combined_result
    }
    
    output_file = os.path.join(output_folder, f"chapter_{chapter_num:03d}.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(chapter_data, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Chapter {chapter_num} saved to {output_file}")
    print(f"{'='*60}")
    
    return True


def main():
    print("="*60)
    print("Chunked Chapter Translator")
    print("="*60)
    print("\nOptions:")
    print("1. Translate specific chapter")
    print("2. Auto-translate all missing chapters")
    
    choice = input("\nEnter your choice (1-2): ").strip()
    
    if choice == "1":
        # Manual mode - translate specific chapter
        chapter_num = input("Enter chapter number to translate: ").strip()
        
        try:
            chapter_num = int(chapter_num)
        except ValueError:
            print("Error: Invalid chapter number")
            return
        
        success = translate_chapter_chunked(chapter_num)
        
        if success:
            print("\n✓ Chapter translated successfully!")
        else:
            print("\n✗ Chapter translation failed")
            
    elif choice == "2":
        # Auto mode - find and translate missing chapters
        print("\nScanning for missing chapters...")
        missing_chapters = get_missing_chapters()
        
        if not missing_chapters:
            print("✓ All chapters are already translated!")
            return
        
        print(f"\nFound {len(missing_chapters)} missing chapters:")
        print(f"{missing_chapters}\n")
        
        confirm = input(f"Translate all {len(missing_chapters)} missing chapters? (y/n): ").strip().lower()
        
        if confirm != 'y':
            print("Cancelled.")
            return
        
        # Translate each missing chapter
        success_count = 0
        failed_chapters = []
        
        for idx, chapter_num in enumerate(missing_chapters, 1):
            print(f"\n{'='*60}")
            print(f"Progress: {idx}/{len(missing_chapters)}")
            print(f"{'='*60}")
            
            success = translate_chapter_chunked(chapter_num)
            
            if success:
                success_count += 1
            else:
                failed_chapters.append(chapter_num)
            
            # Wait between chapters
            if idx < len(missing_chapters):
                wait_time = random.uniform(3, 6)
                print(f"\n⏱️  Waiting {wait_time:.1f}s before next chapter...")
                time.sleep(wait_time)
        
        # Summary
        print(f"\n{'='*60}")
        print("SUMMARY")
        print(f"{'='*60}")
        print(f"✓ Successfully translated: {success_count}/{len(missing_chapters)}")
        
        if failed_chapters:
            print(f"✗ Failed chapters: {failed_chapters}")
            print("\nYou can retry failed chapters using option 1")
        else:
            print("\n🎉 All missing chapters translated successfully!")
            print("You can now merge all chapters using option 4 in translate_api.py")
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()
