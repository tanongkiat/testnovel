#!/bin/bash
# Script to convert text file to HTML with chapter navigation

INPUT_FILE="$1"
OUTPUT_FILE="${INPUT_FILE%.txt}_chapters.html"

# Start HTML
cat > "$OUTPUT_FILE" << 'HTML_START'
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>侯夫人與殺豬刀</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: "PingFang SC", "Microsoft YaHei", SimSun, sans-serif;
            line-height: 1.8;
            background-color: #f5f5f5;
            color: #333;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            position: sticky;
            top: 0;
            z-index: 1000;
        }
        .header h1 {
            font-size: 1.8em;
            margin-bottom: 10px;
        }
        .controls {
            background-color: white;
            padding: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            flex-wrap: wrap;
            gap: 10px;
        }
        .chapter-select {
            flex: 1;
            min-width: 200px;
            padding: 10px;
            font-size: 1em;
            border: 2px solid #667eea;
            border-radius: 5px;
            background-color: white;
        }
        .nav-buttons {
            display: flex;
            gap: 10px;
        }
        .btn {
            padding: 10px 20px;
            font-size: 1em;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.3s;
            font-weight: bold;
        }
        .btn:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        .btn-prev {
            background-color: #3498db;
            color: white;
        }
        .btn-next {
            background-color: #e74c3c;
            color: white;
        }
        .content {
            max-width: 900px;
            margin: 30px auto;
            padding: 40px;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            min-height: 500px;
        }
        .chapter-title {
            font-size: 1.8em;
            font-weight: bold;
            color: #e74c3c;
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 15px;
            border-bottom: 3px solid #667eea;
        }
        .chapter-content p {
            text-indent: 2em;
            margin: 1em 0;
            text-align: justify;
        }
        .chapter-info {
            text-align: center;
            color: #7f8c8d;
            font-size: 0.9em;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #ecf0f1;
        }
        .hidden {
            display: none;
        }
        @media (max-width: 768px) {
            .content {
                padding: 20px;
                margin: 15px;
            }
            .header h1 {
                font-size: 1.3em;
            }
            .controls {
                flex-direction: column;
            }
            .chapter-select {
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>侯夫人與殺豬刀</h1>
        <p>作者: 团子来袭</p>
    </div>
    
    <div class="controls">
        <select class="chapter-select" id="chapterSelect" onchange="goToChapter(this.value)">
            <option value="">选择章节 / Select Chapter</option>
        </select>
        <div class="nav-buttons">
            <button class="btn btn-prev" onclick="prevChapter()" id="prevBtn">← 上一章</button>
            <button class="btn btn-next" onclick="nextChapter()" id="nextBtn">下一章 →</button>
        </div>
    </div>

    <div class="content" id="contentArea">
        <div class="chapter-title">请选择章节开始阅读</div>
        <div class="chapter-content">
            <p style="text-align: center; color: #7f8c8d;">使用上方的章节选择器或导航按钮来阅读小说</p>
            <p style="text-align: center; color: #7f8c8d;">Use the chapter selector above or navigation buttons to read</p>
            <p style="text-align: center; color: #7f8c8d; margin-top: 20px;">💡 提示：在 Chrome 浏览器中右键点击页面，选择"翻译为泰语"即可阅读泰语版本</p>
        </div>
    </div>

    <script>
        const chapters = [
HTML_START

# Parse the file and extract chapters
awk '
BEGIN {
    chapter_num = 0
    in_chapter = 0
    content = ""
}
/^第[0-9]+章/ {
    if (in_chapter && content != "") {
        # Close previous chapter
        gsub(/"/, "\\\"", content)
        gsub(/\n/, "\\n", content)
        print "            content: \"" content "\""
        print "        },"
    }
    # Start new chapter
    chapter_num++
    chapter_title = $0
    gsub(/"/, "\\\"", chapter_title)
    print "        {"
    print "            num: " chapter_num ","
    print "            title: \"" chapter_title "\","
    content = ""
    in_chapter = 1
    next
}
{
    if (in_chapter && $0 != "") {
        if (content != "") content = content "\\n"
        line = $0
        gsub(/"/, "\\\"", line)
        content = content line
    }
}
END {
    if (in_chapter && content != "") {
        gsub(/"/, "\\\"", content)
        print "            content: \"" content "\""
        print "        }"
    }
}
' "$INPUT_FILE" >> "$OUTPUT_FILE"

# Complete HTML
cat >> "$OUTPUT_FILE" << 'HTML_END'
        ];

        let currentChapter = 0;

        function initChapters() {
            const select = document.getElementById('chapterSelect');
            chapters.forEach((chapter, index) => {
                const option = document.createElement('option');
                option.value = index;
                option.textContent = `${chapter.title}`;
                select.appendChild(option);
            });
            
            if (chapters.length > 0) {
                displayChapter(0);
            }
        }

        function displayChapter(index) {
            if (index < 0 || index >= chapters.length) return;
            
            currentChapter = index;
            const chapter = chapters[index];
            
            const contentArea = document.getElementById('contentArea');
            const paragraphs = chapter.content.split('\\n')
                .filter(p => p.trim() !== '')
                .map(p => `<p>${p}</p>`)
                .join('');
            
            contentArea.innerHTML = `
                <div class="chapter-title">${chapter.title}</div>
                <div class="chapter-content">
                    ${paragraphs}
                </div>
                <div class="chapter-info">
                    章节 ${index + 1} / ${chapters.length}
                </div>
            `;
            
            // Update select
            document.getElementById('chapterSelect').value = index;
            
            // Update buttons
            document.getElementById('prevBtn').disabled = index === 0;
            document.getElementById('nextBtn').disabled = index === chapters.length - 1;
            
            // Scroll to top
            window.scrollTo(0, 0);
            
            // Save progress
            localStorage.setItem('lastChapter', index);
        }

        function goToChapter(index) {
            if (index !== '') {
                displayChapter(parseInt(index));
            }
        }

        function nextChapter() {
            if (currentChapter < chapters.length - 1) {
                displayChapter(currentChapter + 1);
            }
        }

        function prevChapter() {
            if (currentChapter > 0) {
                displayChapter(currentChapter - 1);
            }
        }

        // Keyboard navigation
        document.addEventListener('keydown', function(e) {
            if (e.key === 'ArrowLeft') {
                prevChapter();
            } else if (e.key === 'ArrowRight') {
                nextChapter();
            }
        });

        // Initialize on load
        window.onload = function() {
            initChapters();
            
            // Resume last chapter
            const lastChapter = localStorage.getItem('lastChapter');
            if (lastChapter !== null) {
                displayChapter(parseInt(lastChapter));
            }
        };
    </script>
</body>
</html>
HTML_END

echo "Chapter-based HTML file created: $OUTPUT_FILE"
echo "Open it in Chrome and translate to Thai!"
