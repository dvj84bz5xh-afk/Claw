import zipfile, os, sys

epub_path = r"c:\Users\10127\WorkBuddy\Claw\课程资料\scam_cybercrime_compounds.epub"
dst = r"c:\Users\10127\WorkBuddy\Claw\课程资料\epub_extract"
os.makedirs(dst, exist_ok=True)

if not os.path.exists(epub_path):
    print(f"File not found: {epub_path}")
    # Try to find the actual file
    d = r"c:\Users\10127\WorkBuddy\Claw\课程资料"
    for f in os.listdir(d):
        if f.lower().endswith(('.epub',)):
            print(f"Found EPUB: {f}")
    sys.exit(1)

print(f"Reading: {epub_path}")
with zipfile.ZipFile(epub_path, 'r') as z:
    names = z.namelist()
    print(f"Total files in EPUB: {len(names)}")
    print("\n=== First 60 files ===")
    for i, n in enumerate(names[:60]):
        print(f"  [{i}] {n}")
    print("\nExtracting all files...")
    z.extractall(dst)
    print(f"Extracted to: {dst}")
