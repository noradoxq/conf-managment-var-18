from dataclasses import dataclass, field
from pathlib import Path
import copy
import posixpath
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
        self._validate_source(root_path)
        self.root = self._load_directory(self.source_path)
        self.current_path: list[str] = []

    def _validate_source(self, root_path: str) -> None:
        if not self.source_path.exists():
            raise FileNotFoundError(f"VFS directory '{root_path}' not found")
        if not self.source_path.is_dir():
            raise ValueError(f"VFS path '{root_path}' is not a directory")

    def _load_directory(self, path: Path) -> VFSNode:
        node = VFSNode(name=path.name, is_dir=True)
        try:
            for entry in sorted(path.iterdir(), key=lambda item: item.name):
                node.children[entry.name] = self._load_entry(entry)
        except OSError as error:
            raise OSError(
                f"Cannot load VFS directory '{path}': {error}"
            ) from error
        return node

    def _load_entry(self, entry: Path) -> VFSNode:
        if entry.is_symlink():
            raise ValueError(f"Symbolic links are not supported: '{entry}'")
        if entry.is_dir():
            return self._load_directory(entry)
        if entry.is_file():
            return VFSNode(
                name=entry.name,
                is_dir=False,
                content=entry.read_bytes(),
            )
        raise ValueError(f"Unsupported filesystem entry: '{entry}'")

    def _normalize_parts(self, path: str) -> list[str]:
        normalized = path.replace("\\", "/")
        parts = [] if normalized.startswith("/") else list(self.current_path)
        for part in normalized.split("/"):
            self._apply_path_part(parts, part)
        return parts

    @staticmethod
    def _apply_path_part(parts: list[str], part: str) -> None:
        if part in ("", "."):
            return
        if part == "..":
            if parts:
                parts.pop()
            return
        parts.append(part)

    def resolve(self, path: str = ".") -> VFSNode:
        node = self.root
        for part in self._normalize_parts(path):
            node = self._resolve_child(node, part, path)
        return node

    @staticmethod
    def _resolve_child(
        node: VFSNode, part: str, original_path: str
    ) -> VFSNode:
        if not node.is_dir:
            raise NotADirectoryError(part)
        if part not in node.children:
            raise FileNotFoundError(f"Path '{original_path}' not found")
        return node.children[part]

    def copy_file(self, source_path: str, destination_path: str) -> None:
        source = self._get_copy_source(source_path)
        destination, parent_path, new_name = self._resolve_copy_destination(
            source, destination_path
        )
        parent = self.resolve(parent_path or ".")
        self._validate_copy_parent(parent, parent_path)
        self._ensure_name_available(parent, new_name, destination)
        self._insert_copy(parent, source, new_name)

    def _get_copy_source(self, source_path: str) -> VFSNode:
        source = self.resolve(source_path)
        if source.is_dir:
            raise IsADirectoryError(
                f"'{source_path}' is a directory; only files can be copied"
            )
        return source

    def _resolve_copy_destination(
        self, source: VFSNode, destination_path: str
    ) -> tuple[str, str, str]:
        if not destination_path:
            raise ValueError("Destination path cannot be empty")

        destination = destination_path.rstrip("/") or "/"
        try:
            destination_node = self.resolve(destination_path)
        except (FileNotFoundError, KeyError):
            destination_node = None

        if destination_node is not None:
            if not destination_node.is_dir:
                raise FileExistsError(f"'{destination_path}' already exists")
            destination = posixpath.join(destination_path, source.name)

        parent_path, _, new_name = destination.rpartition("/")
        new_name = new_name or destination
        if new_name in ("", ".", ".."):
            raise ValueError("Invalid destination filename")
        return destination, parent_path, new_name

    @staticmethod
    def _validate_copy_parent(parent: VFSNode, parent_path: str) -> None:
        if not parent.is_dir:
            raise NotADirectoryError(parent_path or ".")

    @staticmethod
    def _ensure_name_available(
        parent: VFSNode, new_name: str, destination: str
    ) -> None:
        if new_name in parent.children:
            raise FileExistsError(f"'{destination}' already exists")

    @staticmethod
    def _insert_copy(parent: VFSNode, source: VFSNode, new_name: str) -> None:
        new_node = copy.deepcopy(source)
        new_node.name = new_name
        parent.children[new_name] = new_node

    def list_dir(self, path: str = ".") -> list[str]:
        node = self.resolve(path)
        if not node.is_dir:
            return [node.name]
        return sorted(node.children)

    def change_dir(self, path: str = "/") -> None:
        node = self.resolve(path)
        if not node.is_dir:
            raise NotADirectoryError(f"'{path}' is not a directory")
        self.current_path = self._normalize_parts(path)

    def pwd(self) -> str:
        return "/" + "/".join(self.current_path)

    def save(self, destination: str) -> None:
        target = self._prepare_destination(destination)
        self._clear_destination(target)
        self._write_children(self.root, target)

    def _prepare_destination(self, destination: str) -> Path:
        raw_path = Path(destination).expanduser()
        if raw_path.is_symlink():
            raise ValueError("Save destination cannot be a symlink")
        target = raw_path.resolve()
        self._validate_destination(target, destination)
        target.mkdir(parents=True, exist_ok=True)
        return target

    def _validate_destination(self, target: Path, destination: str) -> None:
        if self._paths_overlap_source(target):
            raise ValueError("Save destination must not overlap the source VFS")
        if target.exists() and not target.is_dir():
            raise ValueError(
                f"Save destination '{destination}' is not a directory"
            )

    def _paths_overlap_source(self, target: Path) -> bool:
        return (
            target == self.source_path
            or target in self.source_path.parents
            or self.source_path in target.parents
        )

    def _clear_destination(self, target: Path) -> None:
        for child in target.iterdir():
            self._remove_physical_entry(child)

    @staticmethod
    def _remove_physical_entry(child: Path) -> None:
        if child.is_dir() and not child.is_symlink():
            shutil.rmtree(child)
        else:
            child.unlink()

    def _write_children(self, node: VFSNode, path: Path) -> None:
        for child in node.children.values():
            child_path = path / child.name
            self._write_node(child, child_path)

    def _write_node(self, node: VFSNode, path: Path) -> None:
        if node.is_dir:
            path.mkdir()
            self._write_children(node, path)
            return
        path.write_bytes(node.content)

    def read_file(self, path: str) -> bytes:
        node = self.resolve(path)
        if node.is_dir:
            raise IsADirectoryError(f"'{path}' is a directory, not a file")
        return node.content

    def remove(self, path: str, recursive: bool = False) -> None:
        node = self._get_removable_node(path, recursive)
        parent = self._get_parent_for_removal(path)
        self._delete_child(parent, node, path)

    def _get_removable_node(self, path: str, recursive: bool) -> VFSNode:
        if path in ("", "/", "."):
            raise ValueError("Cannot remove the VFS root")
        node = self.resolve(path)
        if node is self.root:
            raise ValueError("Cannot remove the VFS root")
        if node.is_dir and not recursive:
            raise IsADirectoryError(
                f"'{path}' is a directory; use rm -r to remove it"
            )
        return node

    def _get_parent_for_removal(self, path: str) -> VFSNode:
        parts = self._normalize_parts(path)
        parent_parts = parts[:-1]
        parent_path = "/" + "/".join(parent_parts)
        return self.resolve(parent_path)

    @staticmethod
    def _delete_child(parent: VFSNode, node: VFSNode, path: str) -> None:
        if not parent.is_dir:
            raise NotADirectoryError(path)
        if node.name not in parent.children:
            raise FileNotFoundError(f"'{path}' not found")
        del parent.children[node.name]
