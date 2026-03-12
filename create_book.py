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
from pathlib import Path


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
    Generate HTML reader from translated chapters
    """
    # Import the formatting function from json_to_html_dynamic
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    
    try:
        from json_to_html_dynamic import (
            extract_translated_text,
            format_thai_paragraphs,
            load_all_chapters
        )
    except ImportError:
        print("Error: json_to_html_dynamic.py not found")
        return False
    
    print(f"\nGenerating HTML reader...")
    print(f"Reading chapters from: {chapters_folder}/")
    
    # Load and format all chapters
    chapters_data = {}
    chapter_files = sorted([f for f in os.listdir(chapters_folder) 
                           if f.startswith('chapter_') and f.endswith('.json')])
    
    for filename in chapter_files:
        filepath = os.path.join(chapters_folder, filename)
        ch_num = int(filename.replace('chapter_', '').replace('.json', ''))
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            
            # Extract and format
            translated_text = extract_translated_text(raw_data['translated'])
            paragraphs = format_thai_paragraphs(translated_text)
            formatted_html = '\n'.join([f'<p>{para}</p>' for para in paragraphs])
            
            chapters_data[ch_num] = {
                'chapter_number': raw_data.get('chapter_number', ch_num),
                'chapter_title': raw_data.get('chapter_title', f'บทที่ {ch_num}'),
                'content': formatted_html
            }
        except Exception as e:
            print(f"  Error loading chapter {ch_num}: {e}")
    
    if not chapters_data:
        print("Error: No chapters found")
        return False
    
    print(f"  Loaded {len(chapters_data)} chapters")
    
    # Generate HTML
    chapters_js = json.dumps(chapters_data, ensure_ascii=False)
    available_chapters_js = json.dumps(sorted(chapters_data.keys()))
    
    html_content = f"""<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{book_title} - Thai Translation</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700&display=swap');
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Sarabun', 'Noto Sans Thai', sans-serif;
            font-size: 18px;
            line-height: 1.9;
            color: #2c3e50;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 20px;
            padding-top: 80px;
        }}
        
        .nav-bar {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background: rgba(255, 255, 255, 0.98);
            backdrop-filter: blur(10px);
            padding: 15px 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            z-index: 1000;
            display: flex;
            align-items: center;
            gap: 15px;
            flex-wrap: wrap;
        }}
        
        .nav-bar select {{
            flex: 1;
            min-width: 200px;
            max-width: 400px;
            padding: 10px 15px;
            font-size: 1em;
            font-family: 'Sarabun', sans-serif;
            border: 2px solid #667eea;
            border-radius: 6px;
            background: white;
            cursor: pointer;
            outline: none;
        }}
        
        .nav-btn {{
            padding: 10px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-family: 'Sarabun', sans-serif;
            font-size: 1em;
            font-weight: 600;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .nav-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }}
        
        .nav-btn:disabled {{
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }}
        
        .logout-btn {{
            padding: 10px 20px;
            background: #e74c3c;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-family: 'Sarabun', sans-serif;
            font-size: 1em;
            font-weight: 600;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .logout-btn:hover {{
            background: #c0392b;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(231, 76, 60, 0.4);
        }}
        
        .logout-btn:active {{
            transform: translateY(0);
        }}
        
        .toc-toggle {{
            padding: 10px 20px;
            background: #34495e;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-family: 'Sarabun', sans-serif;
            font-size: 1em;
            font-weight: 600;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
        }}
        
        .chapter {{
            background: white;
            padding: 40px;
            margin: 30px 0;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        
        .chapter-title {{
            font-size: 1.4em;
            font-weight: 700;
            color: #667eea;
            margin-bottom: 25px;
            padding: 12px 20px;
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        
        .chapter-content p {{
            margin-bottom: 1.2em;
            text-align: justify;
            text-indent: 2em;
            font-size: 1.05em;
            line-height: 2;
        }}
        
        .loading {{
            text-align: center;
            padding: 40px;
            font-size: 1.2em;
            color: #667eea;
        }}
        
        .toc-sidebar {{
            position: fixed;
            left: -350px;
            top: 0;
            bottom: 0;
            width: 350px;
            background: white;
            box-shadow: 2px 0 10px rgba(0,0,0,0.1);
            overflow-y: auto;
            transition: left 0.3s ease;
            z-index: 999;
            padding: 80px 20px 20px 20px;
        }}
        
        .toc-sidebar.open {{
            left: 0;
        }}
        
        .toc-overlay {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.5);
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.3s ease;
            z-index: 998;
        }}
        
        .toc-overlay.open {{
            opacity: 1;
            pointer-events: all;
        }}
        
        .toc-item {{
            display: block;
            padding: 12px 15px;
            color: #2c3e50;
            text-decoration: none;
            border-radius: 6px;
            margin-bottom: 5px;
            transition: all 0.2s;
        }}
        
        .toc-item:hover {{
            background: #f0f0f0;
            transform: translateX(5px);
        }}
        
        .toc-item.active {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-weight: 600;
        }}
        
        .back-to-top {{
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 50px;
            height: 50px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 50%;
            cursor: pointer;
            font-size: 1.5em;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.3s, transform 0.2s;
            z-index: 500;
        }}
        
        .back-to-top.show {{
            opacity: 1;
            pointer-events: all;
        }}
        
        .back-to-top:hover {{
            transform: translateY(-3px);
            box-shadow: 0 6px 16px rgba(102, 126, 234, 0.5);
        }}
        
        .chapter-info {{
            text-align: center;
            color: #7f8c8d;
            margin-top: 20px;
            font-size: 0.9em;
        }}
        
        @media (max-width: 768px) {{
            body {{
                padding: 10px;
                padding-top: 70px;
            }}
            
            .container {{
                max-width: 100%;
                padding: 0;
            }}
            
            .chapter {{
                padding: 20px 15px;
                margin: 15px 0;
                border-radius: 8px;
            }}
            
            .nav-bar {{
                padding: 8px;
                gap: 8px;
            }}
            
            .toc-sidebar {{
                width: 280px;
                left: -280px;
            }}
        }}
        
        @media (max-width: 480px) {{
            body {{
                padding: 5px;
                padding-top: 65px;
            }}
            
            .container {{
                max-width: 100%;
            }}
            
            .chapter {{
                padding: 15px 10px;
                margin: 10px 0;
                border-radius: 6px;
            }}
        }}
    </style>
</head>
<body>
    <div class="nav-bar">
        <button class="toc-toggle" onclick="toggleTOC()">☰ สารบัญ</button>
        <a href="../index.html" class="nav-btn" style="text-decoration: none; display: inline-flex; align-items: center;">🏠 ห้องสมุด</a>
        <select id="chapterSelect" onchange="loadChapter(parseInt(this.value))">
            <option value="">-- เลือกบท --</option>
        </select>
        <button class="nav-btn" id="prevBtn" onclick="previousChapter()">← ก่อนหน้า</button>
        <button class="nav-btn" id="nextBtn" onclick="nextChapter()">ถัดไป →</button>
        <button class="logout-btn" onclick="handleLogout()">🚪 ออกจากระบบ</button>
    </div>

    <div class="toc-sidebar" id="tocSidebar">
        <h3 style="margin-bottom: 20px; color: #667eea;">สารบัญ</h3>
        <div id="tocList"></div>
    </div>

    <div class="toc-overlay" id="tocOverlay" onclick="closeTOC()"></div>

    <div class="container">
        <div id="chapterContent">
            <div class="loading">กำลังโหลด...</div>
        </div>
    </div>

    <button class="back-to-top" id="backToTop" onclick="scrollToTop()">↑</button>

    <script>
        const chaptersData = {chapters_js};
        const availableChapters = {available_chapters_js};
        let currentChapter = 1;

        function loadChapter(chapterNum) {{
            if (!availableChapters.includes(chapterNum)) {{
                document.getElementById('chapterContent').innerHTML = 
                    `<div class="error">ไม่พบบทที่ ${{chapterNum}}</div>`;
                return;
            }}
            
            document.getElementById('chapterContent').innerHTML = 
                `<div class="loading">กำลังโหลดบทที่ ${{chapterNum}}...</div>`;
            
            currentChapter = chapterNum;
            localStorage.setItem('lastReadChapter_{book_title}', chapterNum);
            
            setTimeout(() => {{
                const data = chaptersData[chapterNum];
                if (data) {{
                    displayChapter(data);
                }} else {{
                    document.getElementById('chapterContent').innerHTML = 
                        `<div class="error">ไม่พบข้อมูลบทที่ ${{chapterNum}}</div>`;
                }}
            }}, 100);
        }}

        function displayChapter(data) {{
            const html = `
                <div class="chapter">
                    <div class="chapter-title">${{data.chapter_title}}</div>
                    <div class="chapter-content">
                        ${{data.content}}
                    </div>
                    <div class="chapter-info">
                        บทที่ ${{data.chapter_number}} / ${{availableChapters.length}}
                    </div>
                </div>
            `;
            
            document.getElementById('chapterContent').innerHTML = html;
            window.scrollTo({{ top: 0, behavior: 'smooth' }});
            updateNavigation();
        }}

        function previousChapter() {{
            const currentIndex = availableChapters.indexOf(currentChapter);
            if (currentIndex > 0) {{
                loadChapter(availableChapters[currentIndex - 1]);
            }}
        }}

        function nextChapter() {{
            const currentIndex = availableChapters.indexOf(currentChapter);
            if (currentIndex < availableChapters.length - 1) {{
                loadChapter(availableChapters[currentIndex + 1]);
            }}
        }}

        function updateNavigation() {{
            const currentIndex = availableChapters.indexOf(currentChapter);
            document.getElementById('prevBtn').disabled = currentIndex <= 0;
            document.getElementById('nextBtn').disabled = currentIndex >= availableChapters.length - 1;
            document.getElementById('chapterSelect').value = currentChapter;
            updateActiveTOCItem(currentChapter);
        }}

        function toggleTOC() {{
            document.getElementById('tocSidebar').classList.toggle('open');
            document.getElementById('tocOverlay').classList.toggle('open');
        }}

        function closeTOC() {{
            document.getElementById('tocSidebar').classList.remove('open');
            document.getElementById('tocOverlay').classList.remove('open');
        }}

        function updateActiveTOCItem(chapterNum) {{
            document.querySelectorAll('.toc-item').forEach(item => {{
                item.classList.remove('active');
                if (parseInt(item.dataset.chapter) === chapterNum) {{
                    item.classList.add('active');
                }}
            }});
        }}

        function scrollToTop() {{
            window.scrollTo({{ top: 0, behavior: 'smooth' }});
        }}

        window.addEventListener('scroll', function() {{
            const backToTop = document.getElementById('backToTop');
            if (window.pageYOffset > 300) {{
                backToTop.classList.add('show');
            }} else {{
                backToTop.classList.remove('show');
            }}
        }});
        
        function handleLogout() {{
            if (confirm('คุณต้องการออกจากระบบหรือไม่?')) {{
                localStorage.removeItem('libraryLoggedIn');
                localStorage.removeItem('libraryUsername');
                sessionStorage.removeItem('libraryLoggedIn');
                sessionStorage.removeItem('libraryUsername');
                window.location.href = '../login.html';
            }}
        }}

        document.addEventListener('DOMContentLoaded', function() {{
            const select = document.getElementById('chapterSelect');
            availableChapters.forEach(ch => {{
                const option = document.createElement('option');
                option.value = ch;
                option.textContent = `บทที่ ${{ch}}`;
                select.appendChild(option);
            }});
            
            const tocList = document.getElementById('tocList');
            availableChapters.forEach(ch => {{
                const item = document.createElement('a');
                item.href = '#';
                item.className = 'toc-item';
                item.dataset.chapter = ch;
                item.textContent = `บทที่ ${{ch}}`;
                item.onclick = (e) => {{
                    e.preventDefault();
                    loadChapter(ch);
                    closeTOC();
                }};
                tocList.appendChild(item);
            }});
            
            let chapterToLoad = availableChapters[0];
            const lastRead = localStorage.getItem('lastReadChapter_{book_title}');
            if (lastRead) {{
                const lastReadNum = parseInt(lastRead);
                if (availableChapters.includes(lastReadNum)) {{
                    chapterToLoad = lastReadNum;
                }}
            }}
            
            if (availableChapters.length > 0) {{
                loadChapter(chapterToLoad);
            }}
        }});
    </script>
</body>
</html>"""
    
    # Write HTML file
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    file_size_mb = len(html_content) / 1024 / 1024
    print(f"  ✓ HTML created: {output_html}")
    print(f"  ✓ File size: {file_size_mb:.2f} MB")
    print(f"  ✓ Chapters: {len(chapters_data)}")
    
    return True


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
    import sys
    
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
    else:
        txt_file = input("Enter txt file path: ").strip()
    
    if not os.path.exists(txt_file):
        print(f"Error: File '{txt_file}' not found!")
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
