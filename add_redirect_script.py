#!/usr/bin/env python3
"""
GitHub Pages に mechatora.com へのリダイレクトスクリプトを一括追加
"""
import os
import re
from pathlib import Path

# リダイレクトスクリプト
REDIRECT_SCRIPT = """
    <!-- GitHub Pages to mechatora.com redirect -->
    <script>
    if (window.location.hostname === 'mechatora.github.io') {
        window.location.replace('https://mechatora.com' + window.location.pathname + window.location.search + window.location.hash);
    }
    </script>"""

def add_redirect_to_html(file_path):
    """HTMLファイルにリダイレクトスクリプトを追加"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 既にリダイレクトが追加されているかチェック
    if 'mechatora.github.io' in content:
        print(f"✓ Already has redirect: {file_path}")
        return False
    
    # headタグ内の適切な場所を探す
    # canonical タグの後、またはstyleタグの前に挿入
    patterns = [
        (r'(<link rel="canonical"[^>]*>\s*)', r'\1' + REDIRECT_SCRIPT + '\n    '),
        (r'(<link rel="icon"[^>]*>\s*)', r'\1' + REDIRECT_SCRIPT + '\n    '),
        (r'(\s*<style>)', REDIRECT_SCRIPT + r'\1'),
        (r'(\s*</head>)', REDIRECT_SCRIPT + r'\1')
    ]
    
    modified = False
    for pattern, replacement in patterns:
        if re.search(pattern, content, re.IGNORECASE):
            content = re.sub(pattern, replacement, content, count=1, flags=re.IGNORECASE)
            modified = True
            break
    
    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Added redirect to: {file_path}")
        return True
    else:
        print(f"⚠️  Could not find suitable location in: {file_path}")
        return False

def main():
    """メイン処理"""
    base_dir = Path("/home/sumi/mechatora-pages")
    
    # 処理対象のHTMLファイル（Google認証ファイルは除外）
    html_files = []
    for file_path in base_dir.glob("*.html"):
        if not file_path.name.startswith('google'):
            html_files.append(file_path)
    
    print(f"🔄 Processing {len(html_files)} HTML files...")
    
    success_count = 0
    for file_path in html_files:
        if add_redirect_to_html(file_path):
            success_count += 1
    
    print(f"\n🎉 Successfully added redirects to {success_count}/{len(html_files)} files")

if __name__ == "__main__":
    main()