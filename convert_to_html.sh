#!/bin/bash
# Script to convert text file to HTML for Chrome translation

INPUT_FILE="$1"
OUTPUT_FILE="${INPUT_FILE%.txt}.html"

cat > "$OUTPUT_FILE" << 'EOF'
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>侯夫人與殺豬刀</title>
    <style>
        body {
            font-family: "PingFang SC", "Microsoft YaHei", SimSun, sans-serif;
            line-height: 1.8;
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }
        .content {
            background-color: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        h1 {
            text-align: center;
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        p {
            text-indent: 2em;
            margin: 1em 0;
        }
        .chapter {
            font-size: 1.3em;
            font-weight: bold;
            color: #e74c3c;
            margin-top: 2em;
            text-indent: 0;
        }
    </style>
</head>
<body>
    <div class="content">
        <h1>侯夫人與殺豬刀</h1>
        <div id="text-content">
EOF

# Process the text file and add it to HTML
while IFS= read -r line; do
    if [[ "$line" =~ ^第[0-9]+章 ]]; then
        echo "            <p class=\"chapter\">$line</p>" >> "$OUTPUT_FILE"
    elif [[ -n "$line" ]]; then
        echo "            <p>$line</p>" >> "$OUTPUT_FILE"
    fi
done < "$INPUT_FILE"

cat >> "$OUTPUT_FILE" << 'EOF'
        </div>
    </div>
</body>
</html>
EOF

echo "HTML file created: $OUTPUT_FILE"
echo "Open it in Chrome and use right-click -> Translate to Thai"
