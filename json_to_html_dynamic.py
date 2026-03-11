#!/usr/bin/env python3
"""
Generate HTML with dynamic chapter loading (data embedded in HTML)
"""

import json
import os
import re


def extract_translated_text(translated_data):
    """
    Extract Thai translated text from the API response structure
    
    Args:
        translated_data: The translated field from JSON
        
    Returns:
        Cleaned Thai text
    """
    if isinstance(translated_data, list):
        # Handle nested list structure from API response
        # Structure is typically: [[translated_text, source_text]]
        if len(translated_data) > 0:
            if isinstance(translated_data[0], list) and len(translated_data[0]) > 0:
                return translated_data[0][0]
            elif isinstance(translated_data[0], str):
                return translated_data[0]
    elif isinstance(translated_data, str):
        return translated_data
    
    return str(translated_data)


def format_thai_paragraphs(text):
    """
    Format Thai text into proper paragraphs with sentence breaks
    Keep related sentences together for better readability
    
    Args:
        text: Thai text string
        
    Returns:
        List of paragraph strings
    """
    # Clean up the text
    text = text.strip()
    
    # First, handle chapter markers that appear in content
    # Split when "บทที่ XX" appears (e.g., "บทที่ 76 หลังจาก...")
    # Using a pattern that captures text before and after the marker
    chapter_parts = []
    current_pos = 0
    
    for match in re.finditer(r'บทที่\s*\d+', text):
        start = match.start()
        # If there's text before this match, add it
        if start > current_pos:
            chapter_parts.append(text[current_pos:start].strip())
        # Start new part from this chapter marker
        current_pos = start
    
    # Add remaining text
    if current_pos < len(text):
        chapter_parts.append(text[current_pos:].strip())
    
    # If no chapter markers found, use the whole text
    if not chapter_parts:
        chapter_parts = [text]
    
    all_paragraphs = []
    
    for part in chapter_parts:
        if not part:
            continue
        
        # Check if this part starts with chapter marker
        chapter_match = re.match(r'^(บทที่\s*\d+)\s+(.+)$', part, re.DOTALL)
        if chapter_match:
            # Separate the chapter marker from the content
            chapter_marker = chapter_match.group(1)
            content = chapter_match.group(2)
            
            # Add chapter marker as its own paragraph
            all_paragraphs.append(f"<strong>{chapter_marker}</strong>")
            part = content
        
        # Split by clear paragraph markers (multiple newlines)
        sub_parts = re.split(r'\n\n+', part)
        
        for sub_part in sub_parts:
            sub_part = sub_part.strip()
            if not sub_part:
                continue
            
            # Check if this part has dialogue
            has_dialogue = '"' in sub_part or '"' in sub_part or '"' in sub_part or '«' in sub_part
            
            # Split by sentence endings
            sentences = re.split(r'(?<=[.!?])\s+', sub_part)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if not sentences:
                continue
            
            # Strategy: Group 2-4 related sentences together
            min_sentences = 1 if has_dialogue else 2
            max_sentences = 2 if has_dialogue else 4
            min_length = 200
            max_length = 600
            
            current_paragraph = []
            current_length = 0
            sentence_count = 0
            
            for i, sentence in enumerate(sentences):
                sentence_length = len(sentence)
                sentence_count += 1
                current_paragraph.append(sentence)
                current_length += sentence_length
                
                is_last_sentence = (i == len(sentences) - 1)
                next_is_dialogue = False
                
                if not is_last_sentence and i + 1 < len(sentences):
                    next_sentence = sentences[i + 1]
                    next_is_dialogue = (next_sentence.startswith('"') or 
                                      next_sentence.startswith('"') or 
                                      next_sentence.startswith('«'))
                
                should_break = False
                
                if sentence_count >= min_sentences:
                    if sentence_count >= max_sentences:
                        should_break = True
                    elif current_length >= max_length:
                        should_break = True
                    elif next_is_dialogue:
                        should_break = True
                    elif (sentence.endswith('"') or sentence.endswith('"') or sentence.endswith('»')) and current_length >= min_length:
                        should_break = True
                
                if should_break and not is_last_sentence:
                    all_paragraphs.append(' '.join(current_paragraph))
                    current_paragraph = []
                    current_length = 0
                    sentence_count = 0
            
            if current_paragraph:
                all_paragraphs.append(' '.join(current_paragraph))
    
    # Fallback: split paragraphs that are still too long
    final_paragraphs = []
    for para in all_paragraphs:
        if len(para) > 800 and not para.startswith('<strong>'):
            words = para.split()
            temp_para = []
            temp_len = 0
            
            for word in words:
                word_len = len(word)
                if temp_len + word_len > 600 and temp_para:
                    final_paragraphs.append(' '.join(temp_para))
                    temp_para = [word]
                    temp_len = word_len
                else:
                    temp_para.append(word)
                    temp_len += word_len + 1
            
            if temp_para:
                final_paragraphs.append(' '.join(temp_para))
        else:
            final_paragraphs.append(para)
    
    return final_paragraphs if final_paragraphs else all_paragraphs


def load_all_chapters(folder="translated_chapters"):
    """Load all chapter data and pre-format content"""
    if not os.path.exists(folder):
        return {}
    
    chapters_data = {}
    for filename in sorted(os.listdir(folder)):
        if filename.startswith('chapter_') and filename.endswith('.json'):
            # Extract chapter number from filename
            ch_num = int(filename.replace('chapter_', '').replace('.json', ''))
            filepath = os.path.join(folder, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    raw_data = json.load(f)
                
                # Extract and format the translated text
                translated_text = extract_translated_text(raw_data['translated'])
                paragraphs = format_thai_paragraphs(translated_text)
                
                # Create formatted HTML content
                formatted_html = '\n'.join([f'<p>{para}</p>' for para in paragraphs])
                
                # Store formatted data
                chapters_data[ch_num] = {
                    'chapter_number': raw_data.get('chapter_number', ch_num),
                    'chapter_title': raw_data.get('chapter_title', f'บทที่ {ch_num}'),
                    'content': formatted_html
                }
                
                print(f"  Loaded and formatted chapter {ch_num}")
            except Exception as e:
                print(f"  Error loading chapter {ch_num}: {e}")
    
    return chapters_data


def generate_dynamic_html(output_file="侯夫人與殺豬刀_thai.html"):
    """
    Generate HTML file with embedded chapter data for dynamic loading
    """
    print("Generating dynamic loading HTML...")
    print("Loading all chapters into memory...")
    
    # Load all chapters
    chapters_data = load_all_chapters()
    
    if not chapters_data:
        print("Error: No translated chapters found in translated_chapters/")
        return False
    
    print(f"\nFound {len(chapters_data)} translated chapters")
    print("Embedding chapter data into HTML...")
    
    # Convert chapters data to JavaScript object
    # We'll store it as a compressed JSON string
    chapters_js = json.dumps(chapters_data, ensure_ascii=False)
    available_chapters = sorted(chapters_data.keys())
    available_chapters_js = json.dumps(available_chapters)
    
    html_content = f"""<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>侯夫人與殺豬刀 - Thai Translation</title>
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
        
        .nav-bar select:focus {{
            border-color: #764ba2;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
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
        
        .nav-btn:active {{
            transform: translateY(0);
        }}
        
        .nav-btn:disabled {{
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
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
        
        .loading {{
            text-align: center;
            padding: 40px;
            font-size: 1.2em;
            color: #667eea;
        }}
        
        .error {{
            text-align: center;
            padding: 40px;
            font-size: 1.1em;
            color: #e74c3c;
            background: #ffe6e6;
            border-radius: 8px;
            margin: 20px;
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
            
            .chapter-title {{
                font-size: 1.2em;
                padding: 10px 15px;
                margin-bottom: 20px;
            }}
            
            .chapter-content p {{
                text-indent: 1.5em;
            }}
            
            .nav-bar {{
                padding: 8px;
                gap: 8px;
            }}
            
            .nav-bar select {{
                min-width: 120px;
                padding: 8px 10px;
                font-size: 0.95em;
            }}
            
            .nav-btn {{
                padding: 8px 15px;
                font-size: 0.95em;
            }}
            
            .toc-toggle {{
                padding: 8px 15px;
                font-size: 0.95em;
            }}
            
            .toc-sidebar {{
                width: 280px;
                left: -280px;
            }}
            
            .back-to-top {{
                width: 45px;
                height: 45px;
                bottom: 20px;
                right: 20px;
                font-size: 1.3em;
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
            
            .chapter-title {{
                font-size: 1.1em;
                padding: 8px 12px;
                margin-bottom: 15px;
            }}
            
            .nav-bar {{
                padding: 6px;
                gap: 6px;
            }}
            
            .nav-bar select {{
                min-width: 100px;
                padding: 6px 8px;
                font-size: 0.9em;
            }}
            
            .nav-btn {{
                padding: 6px 12px;
                font-size: 0.9em;
            }}
            
            .toc-toggle {{
                padding: 6px 12px;
                font-size: 0.9em;
            }}
            
            .toc-sidebar {{
                width: 260px;
                left: -260px;
            }}
        }}
    </style>
</head>
<body>
    <div class="nav-bar">
        <button class="toc-toggle" onclick="toggleTOC()">☰ สารบัญ</button>
        <select id="chapterSelect" onchange="loadChapter(parseInt(this.value))">
            <option value="">-- เลือกบท --</option>
        </select>
        <button class="nav-btn" id="prevBtn" onclick="previousChapter()">← ก่อนหน้า</button>
        <button class="nav-btn" id="nextBtn" onclick="nextChapter()">ถัดไป →</button>
    </div>

    <div class="toc-sidebar" id="tocSidebar">
        <h3 style="margin-bottom: 20px; color: #667eea;">สารบัญ</h3>
        <div id="tocList"></div>
    </div>

    <div class="toc-overlay" id="tocOverlay" onclick="closeTOC()"></div>

    <div class="container">
        <div id="chapterContent">
            <div class="loading">กำลังโหลดบทที่ 1...</div>
        </div>
    </div>

    <button class="back-to-top" id="backToTop" onclick="scrollToTop()">↑</button>

    <script>
        // Embedded chapter data (pre-formatted)
        const chaptersData = {chapters_js};
        const availableChapters = {available_chapters_js};
        let currentChapter = 1;

        // Load chapter from embedded data
        function loadChapter(chapterNum) {{
            if (!availableChapters.includes(chapterNum)) {{
                document.getElementById('chapterContent').innerHTML = 
                    `<div class="error">ไม่พบบทที่ ${{chapterNum}}</div>`;
                return;
            }}
            
            // Show loading briefly for UX
            document.getElementById('chapterContent').innerHTML = 
                `<div class="loading">กำลังโหลดบทที่ ${{chapterNum}}...</div>`;
            
            currentChapter = chapterNum;
            
            // Use setTimeout to allow loading message to show
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

        // Display chapter content (already formatted)
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

        // Navigation functions
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

        // TOC functions
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

        // Back to top
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

        // Initialize on load
        document.addEventListener('DOMContentLoaded', function() {{
            // Populate chapter selector
            const select = document.getElementById('chapterSelect');
            availableChapters.forEach(ch => {{
                const option = document.createElement('option');
                option.value = ch;
                option.textContent = `บทที่ ${{ch}}`;
                select.appendChild(option);
            }});
            
            // Populate TOC
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
            
            // Load first chapter
            if (availableChapters.length > 0) {{
                loadChapter(availableChapters[0]);
            }}
        }});
    </script>
</body>
</html>"""
    
    # Write HTML files
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # Also create chapters.html copy
    with open('chapters.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    file_size_mb = len(html_content) / 1024 / 1024
    print(f"\n✓ Dynamic HTML created: {output_file}")
    print(f"✓ Copy created: chapters.html")
    print(f"✓ Total chapters embedded: {len(chapters_data)}")
    print(f"✓ File size: {file_size_mb:.2f} MB")
    print(f"\nChapters load dynamically from embedded data")
    print(f"✓ Done! Open {output_file} or chapters.html in your browser")
    
    return True


if __name__ == "__main__":
    generate_dynamic_html()
