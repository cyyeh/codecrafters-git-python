import hashlib
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
    elif command == "hash-object":
        if len(sys.argv) != 4 or sys.argv[2] != "-w":
            raise RuntimeError("Usage: git hash-object -w <file_path>")
        
        file_path = sys.argv[3]
        with open(file_path, "rb") as f:
            file_data = f.read()

        header = f"blob {len(file_data)}\x00"
        content = header.encode() + file_data
        object_hash = hashlib.sha1(content).hexdigest()

        os.makedirs(f"./.git/objects/{object_hash[:2]}", exist_ok=True)
        with open(f"./.git/objects/{object_hash[:2]}/{object_hash[2:]}", "wb") as f:
            f.write(zlib.compress(content))
        
        print(object_hash)
    else:
        raise RuntimeError(f"Unknown command #{command}")


if __name__ == "__main__":
    main()
