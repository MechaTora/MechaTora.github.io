import os
import glob

# AdSense code to insert
adsense_code = """
    <!-- Google AdSense -->
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-1184134440246706"
         crossorigin="anonymous"></script>
"""

# Directory to search
root_dir = r"C:\Users\USER\OneDrive\デスクトップ\mechatora-pages"

# Find all HTML files recursively
html_files = glob.glob(os.path.join(root_dir, "**/*.html"), recursive=True)

count = 0
for file_path in html_files:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check if AdSense code is already present
        if "ca-pub-1184134440246706" in content:
            print(f"Skipping (already exists): {file_path}")
            continue
            
        # Insert before </head>
        if "</head>" in content:
            new_content = content.replace("</head>", f"{adsense_code}</head>")
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"Added to: {file_path}")
            count += 1
        else:
            print(f"Skipping (no </head> tag): {file_path}")
            
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

print(f"AdSense code added to {count} files.")
