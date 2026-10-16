from dataclasses import dataclass, field
from pathlib import Path
import shutil


@dataclass
class VFSNode:

    name: str
    is_dir: bool
    content: bytes = b""
    children: dict[str, "VFSNode"] = field(default_factory=dict)


class VFS:

    def __init__(self, root_path: str):
        self.source_path = Path(root_path).resolve()

        if not self.source_path.exists():
            raise FileNotFoundError(
                f"VFS directory '{root_path}' not found"
            )

        if not self.source_path.is_dir():
            raise ValueError(
                f"VFS path '{root_path}' is not a directory"
            )

        self.root = self._load_directory(self.source_path)
        self.current_path: list[str] = []

    def _load_directory(self, path: Path) -> VFSNode:
        node = VFSNode(name=path.name, is_dir=True)

        try:
            entries = sorted(path.iterdir(), key=lambda item: item.name)

            for entry in entries:
                if entry.is_symlink():
                    raise ValueError(
                        f"Symbolic links are not supported: '{entry}'"
                    )

                if entry.is_dir():
                    child = self._load_directory(entry)
                elif entry.is_file():
                    child = VFSNode(
                        name=entry.name,
                        is_dir=False,
                        content=entry.read_bytes(),
                    )
                else:
                    raise ValueError(
                        f"Unsupported filesystem entry: '{entry}'"
                    )

                node.children[entry.name] = child

        except OSError as error:
            raise OSError(
                f"Cannot load VFS directory '{path}': {error}"
            ) from error

        return node

    def resolve(self, path: str = ".") -> VFSNode:
        normalized = path.replace("\\", "/")
        parts = [] if normalized.startswith("/") else list(
            self.current_path
        )

        for part in normalized.split("/"):
            if part in ("", "."):
                continue
            if part == "..":
                if parts:
                    parts.pop()
                continue
            parts.append(part)

        node = self.root

        for part in parts:
            if not node.is_dir:
                raise NotADirectoryError(part)
            if part not in node.children:
                raise FileNotFoundError(f"Path '{path}' not found")
            node = node.children[part]

        return node

    def list_dir(self, path: str = ".") -> list[str]:
        """Return sorted names of directory entries."""
        node = self.resolve(path)

        if not node.is_dir:
            return [node.name]

        return sorted(node.children)

    def change_dir(self, path: str = "/") -> None:
        node = self.resolve(path)

        if not node.is_dir:
            raise NotADirectoryError(f"'{path}' is not a directory")

        normalized = path.replace("\\", "/")
        parts = [] if normalized.startswith("/") else list(
            self.current_path
        )

        for part in normalized.split("/"):
            if part in ("", "."):
                continue
            if part == "..":
                if parts:
                    parts.pop()
            else:
                parts.append(part)

        self.current_path = parts

    def pwd(self) -> str:
        return "/" + "/".join(self.current_path)

    def save(self, destination: str) -> None:
        raw_path = Path(destination).expanduser()

        if raw_path.is_symlink():
            raise ValueError("Save destination cannot be a symlink")

        target = raw_path.resolve()

        if (
            target == self.source_path
            or target in self.source_path.parents
            or self.source_path in target.parents
        ):
            raise ValueError(
                "Save destination must not overlap the source VFS"
            )

        if target.exists() and not target.is_dir():
            raise ValueError(
                f"Save destination '{destination}' is not a directory"
            )

        if target.exists():
            for child in target.iterdir():
                if child.is_dir() and not child.is_symlink():
                    shutil.rmtree(child)
                else:
                    child.unlink()
        else:
            target.mkdir(parents=True)

        self._write_children(self.root, target)

    def _write_children(self, node: VFSNode, path: Path) -> None:
        for child in node.children.values():
            child_path = path / child.name

            if child.is_dir:
                child_path.mkdir()
                self._write_children(child, child_path)
            else:
                child_path.write_bytes(child.content)
