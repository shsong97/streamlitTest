from pathlib import Path
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm


def apply_nanumgothic_font(font_path=None):
    if font_path is None:
        font_path = Path(__file__).resolve().parents[1] / "static" / "NanumGothic.ttf"
    else:
        font_path = Path(font_path)

    if font_path.exists():
        fm.fontManager.addfont(str(font_path))
        font_name = fm.FontProperties(fname=str(font_path)).get_name()
        matplotlib.rc("font", family=[font_name])
    else:
        matplotlib.rc("font", family=["NanumGothic", "AppleGothic", "DejaVu Sans"])

    plt.rcParams["axes.unicode_minus"] = False