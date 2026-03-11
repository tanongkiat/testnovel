#!/usr/bin/env python3
"""
Convert translated JSON to formatted HTML with Thai text
"""

import json
import re
from pathlib import Path


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
        HTML formatted text with paragraphs
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


def create_html(chapters_data, output_file="translated_output.html"):
    """
    Create an HTML file from translated chapters
    
    Args:
        chapters_data: List of chapter dictionaries
        output_file: Output HTML filename
    """
    
    html_content = """<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>侯夫人與殺豬刀 - Thai Translation</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700&display=swap');
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Sarabun', 'Noto Sans Thai', sans-serif;
            line-height: 1.9;
            color: #2c3e50;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 20px;
            padding-top: 80px;
        }
        
        .nav-bar {
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
        }
        
        .nav-bar select {
            flex: 1;
            max-width: 400px;
            padding: 10px 15px;
            font-size: 1em;
            font-family: 'Sarabun', sans-serif;
            border: 2px solid #667eea;
            border-radius: 6px;
            background: white;
            cursor: pointer;
            outline: none;
        }
        
        .nav-bar select:focus {
            border-color: #764ba2;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .nav-btn {
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
        }
        
        .nav-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        
        .nav-btn:active {
            transform: translateY(0);
        }
        
        .nav-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }
        
        .toc-toggle {
            padding: 10px 20px;
            background: #34495e;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-family: 'Sarabun', sans-serif;
            font-size: 1em;
            font-weight: 600;
        }
        
        .toc-sidebar {
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
        }
        
        .toc-sidebar.open {
            left: 0;
        }
        
        .toc-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.5);
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.3s, visibility 0.3s;
            z-index: 998;
        }
        
        .toc-overlay.open {
            opacity: 1;
            visibility: visible;
        }
        
        .toc-title {
            font-size: 1.3em;
            font-weight: 700;
            color: #667eea;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }
        
        .toc-item {
            padding: 10px 15px;
            margin-bottom: 5px;
            cursor: pointer;
            border-radius: 6px;
            transition: background 0.2s;
            color: #2c3e50;
            text-decoration: none;
            display: block;
        }
        
        .toc-item:hover {
            background: #f5f7fa;
        }
        
        .toc-item.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-weight: 600;
        }
        
        .back-to-top {
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 50px;
            height: 50px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 50%;
            font-size: 1.5em;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.3s, visibility 0.3s, transform 0.2s;
            z-index: 997;
        }
        
        .back-to-top.visible {
            opacity: 1;
            visibility: visible;
        }
        
        .back-to-top:hover {
            transform: translateY(-3px);
        }
        
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            border-radius: 10px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 50px;
            padding-bottom: 30px;
            border-bottom: 3px solid #e74c3c;
        }
        
        .title {
            font-size: 2.5em;
            color: #e74c3c;
            margin-bottom: 10px;
            font-weight: 700;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }
        
        .subtitle {
            font-size: 1.2em;
            color: #7f8c8d;
            font-weight: 300;
        }
        
        .chapter {
            margin-bottom: 60px;
            page-break-inside: avoid;
            clear: both;
        }
        
        .chapter-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 20px;
            border-radius: 6px;
            margin-bottom: 30px;
            box-shadow: 0 3px 10px rgba(102, 126, 234, 0.25);
            page-break-after: avoid;
        }
        
        .chapter-number {
            font-size: 0.85em;
            opacity: 0.9;
            margin-bottom: 3px;
            letter-spacing: 0.5px;
        }
        
        .chapter-title {
            font-size: 1.4em;
            font-weight: 600;
            margin: 0;
        }
        
        .chapter-content {
            font-size: 1.15em;
            color: #34495e;
            text-align: justify;
        }
        
        .chapter-content p {
            margin-bottom: 1.8em;
            line-height: 2;
            text-indent: 2em;
        }
        
        .chapter-content p:first-of-type {
            text-indent: 0;
            margin-top: 0;
            padding-top: 0;
        }
        
        .chapter-content p:first-of-type::first-line {
            font-weight: 500;
        }
        
        .original-title {
            font-size: 0.9em;
            color: #95a5a6;
            font-style: italic;
            margin-top: 5px;
        }
        
        .footer {
            text-align: center;
            margin-top: 60px;
            padding-top: 30px;
            border-top: 2px solid #ecf0f1;
            color: #7f8c8d;
            font-size: 0.9em;
        }
        
        @media print {
            body {
                background: white;
                padding: 0;
            }
            
            .container {
                box-shadow: none;
                padding: 20px;
            }
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 20px;
            }
            
            .title {
                font-size: 1.8em;
            }
            
            .chapter-title {
                font-size: 1.4em;
            }
            
            .chapter-content {
                font-size: 1.05em;
            }
        }
    </style>
</head>
<body>
    <!-- Navigation Bar -->
    <div class="nav-bar">
        <button class="toc-toggle" onclick="toggleTOC()">📚 สารบัญ</button>
        <button class="nav-btn" id="prevBtn" onclick="previousChapter()">← ก่อนหน้า</button>
        <select id="chapterSelect" onchange="jumpToChapter()">
            <option value="">เลือกบท...</option>
        </select>
        <button class="nav-btn" id="nextBtn" onclick="nextChapter()">ถัดไป →</button>
    </div>
    
    <!-- Table of Contents Overlay -->
    <div class="toc-overlay" id="tocOverlay" onclick="toggleTOC()"></div>
    
    <!-- Table of Contents Sidebar -->
    <div class="toc-sidebar" id="tocSidebar">
        <div class="toc-title">สารบัญ</div>
        <div id="tocList"></div>
    </div>
    
    <!-- Back to Top Button -->
    <button class="back-to-top" id="backToTop" onclick="scrollToTop()">↑</button>
    
    <div class="container">
        <div class="header">
            <h1 class="title">侯夫人與殺豬刀</h1>
            <p class="subtitle">แปลเป็นภาษาไทย | Thai Translation</p>
        </div>
"""
    
    # Build chapter select options and TOC
    toc_items = []
    for chapter_data in chapters_data:
        chapter_num = chapter_data.get('chapter_number', 'Unknown')
        toc_items.append(f'<option value="chapter-{chapter_num}">บทที่ {chapter_num}</option>')
    
    # Add each chapter
    for chapter_data in chapters_data:
        chapter_num = chapter_data.get('chapter_number', 'Unknown')
        chapter_title_original = chapter_data.get('chapter_title', '')
        translated_raw = chapter_data.get('translated', '')
        
        # Extract Thai text from the API response structure
        thai_text = extract_translated_text(translated_raw)
        
        # Format into paragraphs
        paragraphs = format_thai_paragraphs(thai_text)
        
        # Build chapter HTML
        html_content += f"""
        <div class="chapter" id="chapter-{chapter_num}">
            <div class="chapter-header">
                <div class="chapter-number">บทที่ {chapter_num}</div>
                <h2 class="chapter-title">บท {chapter_num}</h2>
                <div class="original-title">{chapter_title_original}</div>
            </div>
            <div class="chapter-content">
"""
        
        # Add paragraphs
        for para in paragraphs:
            if para.strip():
                html_content += f"                <p>{para}</p>\n"
        
        html_content += """            </div>
        </div>
"""
    
    # Close HTML
    html_content += """
        <div class="footer">
            <p>แปลด้วย Google Translate API</p>
            <p>Created with ❤️ on """ + "March 11, 2026" + """</p>
        </div>
    </div>
    
    <script>
        // Configuration
        const chapters = """ + str([f"chapter-{ch['chapter_number']}" for ch in chapters_data]) + """;
        let currentChapterIndex = 0;
        
        // Initialize on page load
        document.addEventListener('DOMContentLoaded', function() {
            populateChapterSelect();
            populateTOC();
            updateNavigationButtons();
            setupScrollSpy();
            updateBackToTopButton();
        });
        
        // Populate chapter selector
        function populateChapterSelect() {
            const select = document.getElementById('chapterSelect');
            """ + "\n".join([f"select.innerHTML += '<option value=\"chapter-{ch['chapter_number']}\">บทที่ {ch['chapter_number']}</option>';" for ch in chapters_data]) + """
        }
        
        // Populate TOC
        function populateTOC() {
            const tocList = document.getElementById('tocList');
            """ + "\n".join([f"tocList.innerHTML += '<a href=\"#chapter-{ch['chapter_number']}\" class=\"toc-item\" data-chapter=\"chapter-{ch['chapter_number']}\" onclick=\"closeTOC()\">บทที่ {ch['chapter_number']}</a>';" for ch in chapters_data]) + """
        }
        
        // Toggle TOC sidebar
        function toggleTOC() {
            const sidebar = document.getElementById('tocSidebar');
            const overlay = document.getElementById('tocOverlay');
            sidebar.classList.toggle('open');
            overlay.classList.toggle('open');
        }
        
        // Close TOC
        function closeTOC() {
            const sidebar = document.getElementById('tocSidebar');
            const overlay = document.getElementById('tocOverlay');
            sidebar.classList.remove('open');
            overlay.classList.remove('open');
        }
        
        // Jump to selected chapter
        function jumpToChapter() {
            const select = document.getElementById('chapterSelect');
            const chapterId = select.value;
            if (chapterId) {
                const element = document.getElementById(chapterId);
                if (element) {
                    element.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    updateCurrentChapter(chapterId);
                }
            }
        }
        
        // Navigate to previous chapter
        function previousChapter() {
            if (currentChapterIndex > 0) {
                currentChapterIndex--;
                const chapterId = chapters[currentChapterIndex];
                scrollToChapter(chapterId);
            }
        }
        
        // Navigate to next chapter
        function nextChapter() {
            if (currentChapterIndex < chapters.length - 1) {
                currentChapterIndex++;
                const chapterId = chapters[currentChapterIndex];
                scrollToChapter(chapterId);
            }
        }
        
        // Scroll to chapter
        function scrollToChapter(chapterId) {
            const element = document.getElementById(chapterId);
            if (element) {
                element.scrollIntoView({ behavior: 'smooth', block: 'start' });
                updateCurrentChapter(chapterId);
            }
        }
        
        // Update current chapter and UI
        function updateCurrentChapter(chapterId) {
            currentChapterIndex = chapters.indexOf(chapterId);
            document.getElementById('chapterSelect').value = chapterId;
            updateNavigationButtons();
            updateActiveTOCItem(chapterId);
        }
        
        // Update navigation button states
        function updateNavigationButtons() {
            document.getElementById('prevBtn').disabled = currentChapterIndex === 0;
            document.getElementById('nextBtn').disabled = currentChapterIndex === chapters.length - 1;
        }
        
        // Update active TOC item
        function updateActiveTOCItem(chapterId) {
            document.querySelectorAll('.toc-item').forEach(item => {
                item.classList.remove('active');
                if (item.getAttribute('data-chapter') === chapterId) {
                    item.classList.add('active');
                }
            });
        }
        
        // Scroll spy - detect which chapter is in view
        function setupScrollSpy() {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting && entry.intersectionRatio > 0.5) {
                        const chapterId = entry.target.id;
                        if (chapterId && chapters.includes(chapterId)) {
                            updateCurrentChapter(chapterId);
                        }
                    }
                });
            }, { threshold: [0.5] });
            
            chapters.forEach(chapterId => {
                const element = document.getElementById(chapterId);
                if (element) observer.observe(element);
            });
        }
        
        // Back to top button visibility
        window.addEventListener('scroll', updateBackToTopButton);
        
        function updateBackToTopButton() {
            const btn = document.getElementById('backToTop');
            if (window.pageYOffset > 300) {
                btn.classList.add('visible');
            } else {
                btn.classList.remove('visible');
            }
        }
        
        // Scroll to top
        function scrollToTop() {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    </script>
</body>
</html>
"""
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✓ HTML file created: {output_file}")
    print(f"✓ Total chapters: {len(chapters_data)}")


def main():
    input_file = "侯夫人與殺豬刀_translated.json"
    output_file = "侯夫人與殺豬刀_thai.html"
    
    if not Path(input_file).exists():
        print(f"Error: {input_file} not found!")
        return
    
    # Read JSON
    print(f"Reading {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        chapters_data = json.load(f)
    
    print(f"Found {len(chapters_data)} translated chapters")
    
    # Create HTML
    create_html(chapters_data, output_file)
    
    print(f"\n✓ Done! Open {output_file} in your browser to view the translation.")


if __name__ == "__main__":
    main()
