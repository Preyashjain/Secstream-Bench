from pathlib import Path

import secstream


def test_secstream_imports_from_src():
    package_path = Path(secstream.__file__).resolve()
    assert "src" in package_path.parts