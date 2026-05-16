"""MavizOS operating-system layer — kernel, shell, VFS, and services."""

from mavizos.os.kernel.kernel import Kernel, get_kernel

__all__ = ["Kernel", "get_kernel"]
