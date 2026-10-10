#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""对比两个参数表 HTML(Mission Planner 参数导出格式)。

按参数名(NAME)匹配,逐个比较 VALUE,生成对比 HTML;
值不同或仅单侧存在的参数,VALUE 单元格用青色底、红色字标出。

用法:
    python compare_params.py <a.html> <b.html> [-o out.html] [-d]

    -o  指定输出文件(默认 <a文件名>_vs_<b文件名>.html)
    -d  只输出有差异的参数
"""

import argparse
import html
import re
import sys
from pathlib import Path

TR_RE = re.compile(r"<tr[^>]*>(.*?)</tr>", re.IGNORECASE | re.DOTALL)
TD_RE = re.compile(r"<td[^>]*>(.*?)</td>", re.IGNORECASE | re.DOTALL)

DIFF_STYLE = ' style="background-color: cyan; color: red;"'


def read_text(path):
    for enc in ("utf-8-sig", "utf-8", "gbk"):
        try:
            return Path(path).read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
    return Path(path).read_text(encoding="utf-8", errors="replace")


def parse_params(path):
    """解析参数表,返回 {NAME: (seq, value, meaning)},保持文件中的行序。"""
    params = {}
    for row in TR_RE.findall(read_text(path)):
        cells = [html.unescape(c).strip() for c in TD_RE.findall(row)]
        if len(cells) < 3 or not cells[1]:
            continue  # 表头行(<th>)或残缺行
        meaning = cells[3] if len(cells) > 3 else ""
        params[cells[1]] = (cells[0], cells[2], meaning)
    return params


def values_equal(a, b):
    a, b = a.strip(), b.strip()
    if a == b:
        return True
    try:  # 数值相等即视为相同(如 1100.0 与 1100)
        return float(a) == float(b)
    except ValueError:
        return False


def td(text, diff=False):
    attrs = DIFF_STYLE if diff else ' bgcolor="#FDFDFD"'
    body = html.escape(text) if text else "&#32;"
    return f"<td{attrs}>{body}</td>"


def sort_key(seq):
    try:
        return (0, int(seq))
    except ValueError:
        return (1, seq)


def build_html(name_a, name_b, pa, pb, diffs_only):
    same_rows, diff_rows = [], []
    n_value_diff = n_only_a = n_only_b = 0

    for name, (seq, val, meaning) in pa.items():
        b = pb.get(name)
        if b is None:
            n_only_a += 1
            diff_rows.append((sort_key(seq),
                              f"<tr>{td(seq)}{td(name)}{td(val, True)}"
                              f"{td('—(仅A)', True)}{td(meaning)}</tr>"))
        elif values_equal(val, b[1]):
            same_rows.append((sort_key(seq),
                              f"<tr>{td(seq)}{td(name)}{td(val)}"
                              f"{td(b[1])}{td(meaning)}</tr>"))
        else:
            n_value_diff += 1
            diff_rows.append((sort_key(seq),
                              f"<tr>{td(seq)}{td(name)}{td(val, True)}"
                              f"{td(b[1], True)}{td(meaning)}</tr>"))

    for name, (seq, val, meaning) in pb.items():
        if name not in pa:
            n_only_b += 1
            diff_rows.append((sort_key(seq),
                              f"<tr>{td(seq)}{td(name)}{td('—(仅B)', True)}"
                              f"{td(val, True)}{td(meaning)}</tr>"))

    rows = same_rows + diff_rows if not diffs_only else diff_rows
    rows.sort(key=lambda r: r[0])
    body = "\n".join(r[1] for r in rows)

    summary = (
        f"<p><b>文件A:</b> {html.escape(name_a)}（{len(pa)} 个参数）<br>\n"
        f"<b>文件B:</b> {html.escape(name_b)}（{len(pb)} 个参数）<br>\n"
        f"<b>结果:</b> 相同 {len(same_rows)}"
        f"，值不同 {n_value_diff}，仅A {n_only_a}，仅B {n_only_b}\n"
        f"&nbsp;&nbsp;<span style=\"background-color: cyan; color: red;\">"
        f"青底红字 = 值不同/缺失</span></p>\n"
    )

    table = (
        "<table border=\"1\" cellpadding=\"4\" cellspacing=\"0\">\n"
        "<tr align=\"left\">"
        "<th bgcolor=\"#F6F6F6\">seq</th>"
        "<th bgcolor=\"#F6F6F6\">NAME</th>"
        "<th bgcolor=\"#F6F6F6\">VALUE(A)</th>"
        "<th bgcolor=\"#F6F6F6\">VALUE(B)</th>"
        "<th bgcolor=\"#F6F6F6\">MEANING</th>"
        "</tr>\n"
        f"{body}\n"
        "</table>\n"
    )
    return (
        "<!DOCTYPE html>\n<html lang=\"zh\">\n<head>\n"
        "<meta charset=\"utf-8\">\n"
        f"<title>参数对比: {html.escape(name_a)} vs {html.escape(name_b)}</title>\n"
        "</head>\n<body>\n"
        f"{summary}{table}</body>\n</html>\n"
    )


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="对比两个参数表 HTML,高亮值不同的参数")
    ap.add_argument("file_a", help="文件A(基准)")
    ap.add_argument("file_b", help="文件B")
    ap.add_argument("-o", "--output", help="输出文件(默认 <a>_vs_<b>.html)")
    ap.add_argument("-d", "--diffs-only", action="store_true",
                    help="只输出有差异的参数")
    args = ap.parse_args()

    pa, pb = parse_params(args.file_a), parse_params(args.file_b)
    if not pa or not pb:
        sys.exit("错误: 至少一个文件中未解析到参数行,请确认文件格式")

    out_path = args.output or f"{Path(args.file_a).stem}_vs_{Path(args.file_b).stem}.html"
    Path(out_path).write_text(
        build_html(Path(args.file_a).name, Path(args.file_b).name, pa, pb, args.diffs_only),
        encoding="utf-8")

    n_diff = sum(1 for n in pa if n not in pb or not values_equal(pa[n][1], pb.get(n, ("", "", ""))[1])) \
        + sum(1 for n in pb if n not in pa)
    print(f"A: {args.file_a} ({len(pa)} 个参数)")
    print(f"B: {args.file_b} ({len(pb)} 个参数)")
    if n_diff == 0:
        print("结果: 两文件参数值完全一致")
    else:
        print(f"结果: 差异 {n_diff} 处")
    print(f"已写入: {out_path}")


if __name__ == "__main__":
    main()
