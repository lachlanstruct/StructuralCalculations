# @ Convert all .csv files in a specified folder to UTF-8 encoding
import os
import chardet

# Define the target directory
target_dir = r'D:\Engineering\Python\repo\StructuralCalculations\SteelLibrary\Members\Main'

# Get list of .csv files in the folder
csv_files = [f for f in os.listdir(target_dir) if f.lower().endswith('.csv')]

if not csv_files:
    print("⚠️ No CSV files found in the folder.")
else:
    for filename in csv_files:
        file_path = os.path.join(target_dir, filename)

        # Detect original encoding
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            source_encoding = result['encoding']

        try:
            # Read using detected encoding
            with open(file_path, 'r', encoding=source_encoding) as f:
                content = f.read()

            # Overwrite with UTF-8 encoding
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"✅ Converted: {filename} (from {source_encoding})")
        except Exception as e:
            print(f"❌ Failed to convert {filename}: {e}")
