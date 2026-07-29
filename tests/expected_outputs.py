"""Canonical sample inputs and expected conversion outputs.

The EXPECTED_* constants are the exact return values of the pure
conversion functions; the CLI prints them, appending one extra newline.
"""

SAMPLE_DATA = {
    "name": "John Doe",
    "age": 30,
    "hobbies": ["reading", "coding"],
    "address": {"street": "123 Main St", "city": "Example City"},
}

SAMPLE_YAML = """
name: John Doe
age: 30
hobbies:
  - reading
  - coding
address:
  street: 123 Main St
  city: Example City
"""

EXPECTED_JSON_INDENT2 = """\
{
  "name": "John Doe",
  "age": 30,
  "hobbies": [
    "reading",
    "coding"
  ],
  "address": {
    "street": "123 Main St",
    "city": "Example City"
  }
}"""

EXPECTED_JSON_INDENT4 = """\
{
    "name": "John Doe",
    "age": 30,
    "hobbies": [
        "reading",
        "coding"
    ],
    "address": {
        "street": "123 Main St",
        "city": "Example City"
    }
}"""

EXPECTED_JSON_COMPACT = (
    '{"name": "John Doe", "age": 30, "hobbies": ["reading", "coding"], '
    '"address": {"street": "123 Main St", "city": "Example City"}}'
)

EXPECTED_YAML_INDENT2 = """\
name: John Doe
age: 30
hobbies:
  - reading
  - coding
address:
  street: 123 Main St
  city: Example City
"""

EXPECTED_YAML_COMPACT = """\
name: John Doe
age: 30
hobbies:
- reading
- coding
address:
  street: 123 Main St
  city: Example City
"""
