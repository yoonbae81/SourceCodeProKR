# Source Code Pro KR

[Source Code Pro](https://github.com/adobe-fonts/source-code-pro)에 [D2Coding](https://github.com/naver/d2codingfont)의 한글 영역 (U+3131-U+318E, U+AC00-U+D7A3)을 덧씌운 폰트입니다.

**Forked from [Jhyub/JetBrainsMonoHangul](https://github.com/Jhyub/JetBrainsMonoHangul)**

## Features

- Adobe Source Code Pro 기반의 코딩 폰트
- D2Coding 한글 glyphs 통합
- 한글 좌우 여백 조정 가능
- 다양한 폰트 웨이트 지원 (Regular, Medium, Bold 등)
- Apple FontBook 호환 name table 구조

## Requirements

- macOS with Homebrew
- Python 3.12+
- FontForge (installed via Homebrew)

## Installation

```bash
# Clone repository
git clone https://github.com/yuneal/SourceCodeProKR
cd SourceCodeProKR

# Run setup script (installs FontForge, creates venv, installs Python deps)
./scripts/setup-env.sh
```

## Usage

### Build Fonts

```bash
# Build fonts (downloads fonts and builds)
./scripts/build.sh all

# Or if fonts are already downloaded, just build
./scripts/build.sh build
```

### Install Fonts (Linux)

```bash
# 폰트 디렉토리 생성 (이미 있으면 무시됨)
mkdir -p ~/.local/share/fonts/SourceCodeProKR
# ttf 파일들을 해당 디렉토리로 복사
cp out/*.ttf ~/.local/share/fonts/SourceCodeProKR/
# 폰트 캐시 갱신
fc-cache -fv
```

### Clean Build Artifacts

```bash
./scripts/clean.sh
```

## Configuration

Create a `.env` file from the example to customize font variants and spacing:

```bash
cp .env.example .env
```

Edit the `.env` file:

```env
# Hangul glyph bearing adjustment (spacing)
# The value is divided by 2 for left and right bearings.
HANGUL_BEARING_ADJUSTMENT=-60

# Font variants to include in build (comma-separated)
FONT_VARIANTS=Regular,Bold
```

### Bearing Adjustment Values

| Value | Effect                                |
| ----- | ------------------------------------- |
| -80   | Remove 40px from each side (narrower) |
| -60   | Remove 30px from each side            |
| -40   | Remove 20px from each side            |
| 0     | No change to spacing                  |
| 100   | Add 50px to each side                 |
| 200   | Add 100px to each side (original)     |

## Project Structure

```
SourceCodeProKR/
├── src/                    # Source code
│   ├── main.py            # Build script entry point
│   ├── config.py          # Configuration
│   └── hangulify.py       # Font building logic
├── scripts/                # Setup and build scripts
│   ├── setup-env.sh       # Environment setup
│   ├── build.sh           # Build execution
│   └── clean.sh           # Clean artifacts
├── tests/                  # Test suite
├── assets/                 # Downloaded fonts (gitignored)
├── out/                    # Built fonts (gitignored)
└── .venv/                  # Virtual environment (gitignored)
```

## License

OFL-1.1 (SIL Open Font License 1.1)

Source Code Pro is licensed under the SIL Open Font License.
D2Coding is licensed under the SIL Open Font License.

---

## Acknowledgments

- [Source Code Pro](https://github.com/adobe-fonts/source-code-pro) by Adobe
- [D2Coding](https://github.com/naver/d2codingfont) by Naver
