# mimedb

MIME-type ↔ extension lookup with category classification, type/subtype
parsing, and a runtime-extensible registry.

- ~190 baked-in MIME types covering text, code, archives, documents,
  images, audio, video, fonts, 3D, scientific data, and more.
- Robust parser for `type/subtype[+suffix][; key=value]` strings.
- Category classifier with a closed set of top-level types and a
  `is_text` predicate that knows about `application/json`,
  `application/atom+xml`, and similar text-like binary types.
- Runtime `register` / `unregister` so libraries can extend the
  database without forking it.
- Strictly typed (`mypy --strict` clean), 100% line and branch coverage.

## Install

```bash
python -m pip install -e .
```

## Quick start

```python
import mimedb

mimedb.extension_for("image/png")            # 'png'
mimedb.extensions_for("image/jpeg")          # ['jpg', 'jpeg', 'jpe']
mimedb.mime_for_extension(".PDF")            # 'application/pdf'
mimedb.mime_for_filename("notes.tar.gz")     # 'application/gzip'
mimedb.category("video/mp4")                 # 'video'
mimedb.is_text("application/vnd.api+json")   # True

parsed = mimedb.parse("text/html; charset=utf-8")
parsed.essence       # 'text/html'
parsed.parameters    # {'charset': 'utf-8'}
mimedb.format_mime(parsed)
# 'text/html; charset=utf-8'
```

## API

| Function                              | What it does                                           |
| ------------------------------------- | ------------------------------------------------------ |
| `parse(mime_type) -> ParsedMimeType`  | Split a MIME string into type/subtype/suffix/params.   |
| `format_mime(parsed) -> str`          | Round-trip a `ParsedMimeType` back to canonical text.  |
| `extension_for(mime_type)`            | Primary extension for a MIME type, or `None`.          |
| `extensions_for(mime_type)`           | Every known extension, in registration order.          |
| `mime_for_extension(ext)`             | MIME type for an extension (with or without leading `.`). |
| `mime_for_filename(name)`             | MIME type from the file's last extension component.    |
| `category(mime_type)`                 | One of `text`, `image`, `audio`, `video`, `application`, `font`, `model`, `multipart`, `message`, `chemical`, `example`, or `unknown`. |
| `is_text` / `is_image` / `is_audio` / `is_video` | Boolean classifiers.                        |
| `iter_types()`                        | Iterator over every registered MIME type.              |
| `lookup(mime_type)`                   | Strict variant — raises `UnknownMimeTypeError` on miss.|
| `register(mime_type, extensions)`     | Add a custom MIME ↔ extension mapping at runtime.      |
| `unregister(mime_type)`               | Remove a previously-registered MIME type.              |

### Errors

All errors are subclasses of `MimeDbError`, which itself extends
`ValueError`:

- `InvalidMimeTypeError` — malformed MIME type string.
- `UnknownMimeTypeError` — `lookup()` couldn't find the type.
- `InvalidExtensionError` — bad `extension` / `filename` argument.

### `ParsedMimeType`

Frozen dataclass with `type_`, `subtype`, `suffix`, `parameters`, and
two computed properties:

- `essence` — `"type/subtype"`.
- `base` — `"type/subtype[+suffix]"` (no parameters).

## Running tests

```bash
pip install pytest pytest-cov mypy
pytest --cov=mimedb --cov-branch
mypy --strict src/mimedb
```

## License

MIT — see [LICENSE](./LICENSE).
