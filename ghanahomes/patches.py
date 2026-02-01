"""
Compatibility monkeypatch for Django Context.copy on Python 3.14.
This is a local-dev temporary workaround — prefer using a supported Python
(interpreter 3.11) for production or long-term work.

What it does:
- Replaces django.template.context.Context.__copy__ with a safe implementation
  that constructs a new Context from the flattened data.

Note: Keep this file small and fail-safe.
"""

try:
    from django.template import context as _context_module
except Exception:
    _context_module = None

if _context_module is not None:
    try:
        # Save original if needed
        if not hasattr(_context_module.Context, '_original_copy'):
            _context_module.Context._original_copy = _context_module.Context.__copy__

        def _compat_copy(self):
            # Construct a fresh Context using the flattened data. This avoids
            # relying on internal attributes that changed in Python 3.14.
            try:
                data = self.flatten()
            except Exception:
                # Fallback: try to build from dicts
                data = {}
                for d in getattr(self, 'dicts', []):
                    try:
                        data.update(dict(d))
                    except Exception:
                        pass
            return _context_module.Context(data)

        _context_module.Context.__copy__ = _compat_copy
    except Exception:
        # Silently ignore — this patch is only a convenience for local dev.
        pass
