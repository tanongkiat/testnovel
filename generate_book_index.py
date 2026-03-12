#!/usr/bin/env python3
"""
Generate Book Index HTML
Scans the books directory and creates an index.html with available books
"""

import json
import os
from pathlib import Path


def get_book_metadata(book_folder):
    """Extract metadata from a book folder"""
    metadata = {
        'folder_name': book_folder.name,
        'chinese_title': book_folder.name,
        'thai_title': None,
        'chapter_count': 0,
        'has_chapters_html': False,
        'has_title_image': False
    }
    
    # Check if chapters.html exists
    chapters_html = book_folder / 'chapters.html'
    metadata['has_chapters_html'] = chapters_html.exists()
    
    # Check if title.jpg exists
    title_image = book_folder / 'title.jpg'
    metadata['has_title_image'] = title_image.exists()
    
    # Count chapters in translated_chapters folder
    translated_chapters_dir = book_folder / 'translated_chapters'
    if translated_chapters_dir.exists():
        chapter_files = list(translated_chapters_dir.glob('chapter_*.json'))
        metadata['chapter_count'] = len(chapter_files)
        
        # Try to get Thai title from first chapter
        if chapter_files:
            try:
                first_chapter = sorted(chapter_files)[0]
                with open(first_chapter, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'translated' in data and len(data['translated']) > 0:
                        # Thai title is usually the last element in the translated array
                        if len(data['translated'][0]) > 1:
                            metadata['thai_title'] = data['translated'][0][-1]
            except Exception as e:
                print(f"Warning: Could not extract Thai title from {first_chapter}: {e}")
    
    return metadata


def generate_index_html(books_dir, output_file):
    """Generate index.html for all books in the directory"""
    
    books_dir = Path(books_dir)
    
    # Scan for book folders (directories that contain chapters.html or translated_chapters)
    book_folders = []
    for item in books_dir.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            # Check if it's a valid book folder
            if (item / 'chapters.html').exists() or (item / 'translated_chapters').exists():
                book_folders.append(item)
    
    # Get metadata for all books
    books_metadata = []
    for book_folder in sorted(book_folders):
        metadata = get_book_metadata(book_folder)
        books_metadata.append(metadata)
        print(f"Found book: {metadata['chinese_title']} ({metadata['chapter_count']} chapters)")
    
    # Generate HTML
    html_content = generate_html_template(books_metadata)
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n✓ Generated index at: {output_file}")
    print(f"  Total books: {len(books_metadata)}")


def generate_html_template(books_metadata):
    """Generate the HTML template with book cards"""
    
    # Generate book cards HTML
    book_cards = []
    for book in books_metadata:
        thai_title = book['thai_title'] or 'ไม่มีชื่อภาษาไทย'
        chapter_text = f"{book['chapter_count']} ตอน" if book['chapter_count'] > 0 else "ไม่มีตอน"
        
        # Determine cover image HTML
        if book['has_title_image']:
            cover_html = f'''<img src="{book['folder_name']}/title.jpg" alt="{book['chinese_title']}" class="book-cover-image" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                <div class="book-cover-placeholder" style="display:none;">
                    <span class="book-icon">📖</span>
                </div>'''
        else:
            cover_html = '''<div class="book-cover-placeholder">
                    <span class="book-icon">📖</span>
                </div>'''
        
        card_html = f'''
        <div class="book-card">
            <a href="{book['folder_name']}/chapters.html" class="book-link">
                <div class="book-cover">
                    {cover_html}
                </div>
                <div class="book-info">
                    <h2 class="book-title-chinese">{book['chinese_title']}</h2>
                    <h3 class="book-title-thai">{thai_title}</h3>
                    <p class="book-chapters">{chapter_text}</p>
                </div>
            </a>
            <a href="{book['folder_name']}/chapters.html" class="read-button">อ่านเลย</a>
        </div>'''
        book_cards.append(card_html)
    
    books_html = '\n'.join(book_cards)
    
    # Full HTML template
    html = f'''<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ห้องสมุดนิยายแปล - Thai Novel Library</title>
    <script>
        // Check if user is logged in
        const isLoggedIn = localStorage.getItem('libraryLoggedIn') === 'true' || 
                          sessionStorage.getItem('libraryLoggedIn') === 'true';
        if (!isLoggedIn) {{
            window.location.href = 'login.html';
        }}
    </script>
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
            line-height: 1.6;
            color: #2c3e50;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
            padding: 20px;
            padding-top: 80px;
        }}
        
        .header-bar {{
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
        
        .header-bar h2 {{
            font-size: 1.3em;
            color: #667eea;
            margin: 0;
            font-weight: 700;
        }}
        
        .library-title {{
            text-decoration: none;
            color: #667eea;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .library-title:hover {{
            color: #764ba2;
            transform: translateY(-1px);
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .header {{
            text-align: center;
            padding: 40px 20px;
            margin-bottom: 40px;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 1.2em;
            color: #546e7a;
            font-weight: 400;
        }}
        
        .books-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 25px;
            padding: 20px 0;
        }}
        
        .book-card {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            max-width: 250px;
            margin: 0 auto;
        }}
        
        .book-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 30px rgba(102, 126, 234, 0.3);
        }}
        
        .book-link {{
            text-decoration: none;
            color: inherit;
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 100%;
            cursor: pointer;
        }}
        
        .book-link:hover .book-title-chinese {{
            color: #667eea;
        }}
        
        .book-link:hover .book-cover-image {{
            transform: scale(1.02);
        }}
        
        .book-cover {{
            width: 100%;
            max-width: 180px;
            margin: 0 auto 15px;
        }}
        
        .book-cover-image {{
            width: 100%;
            aspect-ratio: 2/3;
            object-fit: cover;
            border-radius: 8px;
            border: 2px solid #667eea;
            transition: transform 0.2s;
        }}
        
        .book-cover-placeholder {{
            width: 100%;
            aspect-ratio: 2/3;
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 2px solid #667eea;
        }}
        
        .book-icon {{
            font-size: 3em;
        }}
        
        .book-info {{
            width: 100%;
        }}
        
        .book-title-chinese {{
            font-size: 1.1em;
            font-weight: 700;
            color: #2c3e50;
            margin-bottom: 8px;
            word-wrap: break-word;
            line-height: 1.3;
            transition: color 0.2s;
        }}
        
        .book-title-thai {{
            font-size: 0.95em;
            font-weight: 600;
            color: #667eea;
            margin-bottom: 8px;
            word-wrap: break-word;
            line-height: 1.3;
        }}
        
        .book-chapters {{
            font-size: 0.85em;
            color: #7f8c8d;
            margin-bottom: 15px;
        }}
        
        .read-button {{
            display: inline-block;
            padding: 10px 25px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 600;
            font-size: 0.9em;
            transition: all 0.2s;
            margin-top: 10px;
        }}
        
        .read-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }}
        
        .read-button:active {{
            transform: translateY(0);
        }}
        
        .footer {{
            text-align: center;
            padding: 40px 20px;
            color: #7f8c8d;
            font-size: 0.9em;
        }}
        
        .user-info {{
            padding: 8px 15px;
            background: rgba(102, 126, 234, 0.1);
            color: #2c3e50;
            border-radius: 6px;
            font-size: 0.9em;
            font-weight: 600;
            margin-left: auto;
        }}
        
        .logout-button {{
            padding: 10px 20px;
            background: #e74c3c;
            color: white;
            border: none;
            border-radius: 6px;
            font-weight: 600;
            font-family: 'Sarabun', sans-serif;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 0.9em;
        }}
        
        .logout-button:hover {{
            background: #c0392b;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(231, 76, 60, 0.4);
        }}
        
        @media (max-width: 768px) {{
            body {{
                padding-top: 70px;
            }}
            
            .header-bar {{
                padding: 10px 15px;
            }}
            
            .header-bar h2 {{
                font-size: 1.1em;
            }}
            
            .user-info {{
                padding: 6px 10px;
                font-size: 0.8em;
            }}
            
            .logout-button {{
                padding: 6px 12px;
                font-size: 0.8em;
            }}
            
            .header h1 {{
                font-size: 2em;
            }}
            
            .header p {{
                font-size: 1em;
            }}
            
            .books-grid {{
                grid-template-columns: 1fr;
                gap: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="header-bar">
        <a href="index.html" class="library-title">
            <h2>📚 ห้องสมุดนิยายแปล</h2>
        </a>
        <div class="user-info" id="userInfo"></div>
        <button class="logout-button" onclick="handleLogout()">🚪 ออกจากระบบ</button>
    </div>
    
    <div class="container">
        <div class="header">
            <h1>📚 ห้องสมุดนิยายแปล</h1>
            <p>Thai Novel Translation Library</p>
        </div>
        
        <div class="books-grid">{books_html}
        </div>
        
        <div class="footer">
    
    <script>
        // Display username
        const username = localStorage.getItem('libraryUsername') || 
                        sessionStorage.getItem('libraryUsername') || 
                        'ผู้ใช้';
        document.getElementById('userInfo').textContent = '👤 ' + username;
        
        // Handle logout
        function handleLogout() {{
            if (confirm('คุณต้องการออกจากระบบหรือไม่?')) {{
                localStorage.removeItem('libraryLoggedIn');
                localStorage.removeItem('libraryUsername');
                sessionStorage.removeItem('libraryLoggedIn');
                sessionStorage.removeItem('libraryUsername');
                window.location.href = 'login.html';
            }}
        }}
    </script>
            <p>© 2026 Thai Novel Translation Library | สร้างด้วย ❤️</p>
        </div>
    </div>
</body>
</html>'''
    
    return html


def main():
    """Main function"""
    import sys
    
    # Get the script directory
    script_dir = Path(__file__).parent
    books_dir = script_dir / 'books'
    output_file = books_dir / 'index.html'
    
    if not books_dir.exists():
        print(f"Error: Books directory not found at {books_dir}")
        sys.exit(1)
    
    print("Generating book index...")
    print(f"Scanning: {books_dir}")
    print()
    
    generate_index_html(books_dir, output_file)


if __name__ == '__main__':
    main()
