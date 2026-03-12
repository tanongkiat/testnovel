#!/usr/bin/env python3
"""
Fix file encoding issues
Automatically detects and converts to UTF-8
"""

import sys
import chardet
from pathlib import Path


def detect_encoding(file_path):
    """Detect file encoding"""
    with open(file_path, 'rb') as f:
        raw_data = f.read()
    result = chardet.detect(raw_data)
    return result['encoding'], result['confidence']


def fix_encoding(input_file, output_file=None):
    """Fix encoding by converting to UTF-8"""
    input_path = Path(input_file)
    
    if output_file is None:
        output_file = input_path.parent / f"{input_path.stem}_fixed{input_path.suffix}"
    
    # Detect original encoding
    print(f"Detecting encoding of: {input_file}")
    encoding, confidence = detect_encoding(input_file)
    print(f"Detected encoding: {encoding} (confidence: {confidence:.2%})")
    
    # Try common Chinese encodings if detection is uncertain
    encodings_to_try = [encoding, 'gbk', 'gb2312', 'gb18030', 'big5', 'utf-8']
    
    for enc in encodings_to_try:
        if enc is None:
            continue
        try:
            print(f"\nTrying to read with encoding: {enc}")
            with open(input_file, 'r', encoding=enc) as f:
                content = f.read()
            
            # Check if content looks reasonable (has Chinese characters)
            if any('\u4e00' <= c <= '\u9fff' for c in content[:1000]):
                print(f"✓ Successfully read with encoding: {enc}")
                
                # Write as UTF-8
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"✓ Fixed file saved to: {output_file}")
                print(f"✓ Original encoding: {enc} → UTF-8")
                return True
        except (UnicodeDecodeError, Exception) as e:
            print(f"✗ Failed with {enc}: {e}")
            continue
    
    print("\n✗ Could not fix encoding with any known method")
    return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python fix_encoding.py <input_file> [output_file]")
        print("\nExample:")
        print("  python fix_encoding.py 殘王爆寵囂張醫妃.txt")
        print("  python fix_encoding.py input.txt output.txt")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not Path(input_file).exists():
        print(f"Error: File not found: {input_file}")
        sys.exit(1)
    
    success = fix_encoding(input_file, output_file)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
