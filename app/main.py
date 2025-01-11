import hashlib
import sys
import os
import zlib
from dataclasses import dataclass


@dataclass
class TreeEntry:
    mode: str
    type: str
    hash: str
    name: str


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
    elif command == "ls-tree":
        if len(sys.argv) < 3:
            raise RuntimeError("Usage: git ls-tree <object_hash>")
        elif len(sys.argv) == 4 and sys.argv[2] != "--name-only":
            raise RuntimeError("Usage: git ls-tree --name-only <object_hash>")
        
        object_hash = sys.argv[-1]
        git_object_path = f"./.git/objects/{object_hash[:2]}/{object_hash[2:]}"

        with open(git_object_path, "rb") as f:
            data = zlib.decompress(f.read())

        results :list[TreeEntry] = []
        _, binary_data = data.split(b"\x00", maxsplit=1)
        while binary_data:
            mode_and_name, binary_data = binary_data.split(b"\x00", maxsplit=1)
            mode, name = mode_and_name.split()
            binary_data = binary_data[20:]

            results.append(TreeEntry(
                mode=mode.decode("utf-8"),
                type="tree" if mode.decode("utf-8").startswith("40000") else "blob",
                hash=object_hash,
                name=name.decode("utf-8")
            ))
        
        
        for result in sorted(results, key=lambda x: x.name):
            if "--name-only" in sys.argv:
                print(result.name)
            else:
                print(f"{result.mode} {result.type} {result.hash} {result.name}")
    else:
        raise RuntimeError(f"Unknown command #{command}")


if __name__ == "__main__":
    main()
