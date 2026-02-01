# Apply local patches early (keeps them in one place). This import is
# safe: if patches.py fails it will not stop Django from loading.
try:
	from . import patches  # noqa: F401
except Exception:
	# Don't let the patch import break production startup; it's only for dev
	pass

