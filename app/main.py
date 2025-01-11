import sys
import os
import zlib

def main():
    command = sys.argv[1]
    if command == "init":
        os.mkdir(".git")
        os.mkdir(".git/objects")
        os.mkdir(".git/refs")
        with open(".git/HEAD", "w") as f:
            f.write("ref: refs/heads/main\n")
        print("Initialized git directory")
    elif command == "cat-file":
        if len(sys.argv) != 4 or sys.argv[2] != "-p":
            raise RuntimeError("Usage: git cat-file -p <object_hash>")
    
        object_hash = sys.argv[3]
        git_object_path = f"./.git/objects/{object_hash[:2]}/{object_hash[2:]}"

        with open(git_object_path, "rb") as f:
            compressed_data = f.read()
        decompressed_data = zlib.decompress(compressed_data)

        # Split header and content
        null_index = decompressed_data.index(b'\x00')
        content = decompressed_data[null_index + 1:]
        
        # Print just the content
        print(content.decode(), end="")
    else:
        raise RuntimeError(f"Unknown command #{command}")


if __name__ == "__main__":
    main()
