# -*- coding: utf-8 -*-
"""renumber_citations.py — 按正文首次出现顺序重排全部引用编号并重建 References。

支持 N* 占位键（来自 new_refs_built.json）。范围 [a-b] 会按新编号重新压缩，
若重排后不再连续则自动展开为逗号列表。
"""
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "outputs" / "paper" / "manuscript.en.md"
NEW = ROOT / "outputs" / "paper" / "new_refs_built.json"
BACKUP = ROOT / "outputs" / "paper" / "manuscript.en.md.bak"

GROUP = re.compile(r"\[([0-9N][0-9N,\u2013-]*)\]")


def load_refs(sec):
    refs = {}
    for m in re.finditer(r"^\[(\d+)\]\s*(.+)$", sec, re.M):
        refs[m.group(1)] = m.group(2).strip()
    return refs


def parse_group(tok_str):
    keys = []
    for part in tok_str.split(","):
        part = part.strip()
        if not part:
            continue
        if re.fullmatch(r"N\d+", part):
            keys.append(part)
        elif re.fullmatch(r"\d+", part):
            keys.append(part)
        elif re.fullmatch(r"\d+[\u2013-]\d+", part):
            a, b = re.split(r"[\u2013-]", part)
            keys.extend(str(i) for i in range(int(a), int(b) + 1))
        else:
            raise ValueError(f"cannot parse citation token: {part!r} in {tok_str!r}")
    return keys


def compress(nums):
    nums = sorted(set(nums))
    out, i = [], 0
    while i < len(nums):
        j = i
        while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1:
            j += 1
        run = nums[i:j + 1]
        if len(run) >= 3:
            out.append(f"{run[0]}-{run[-1]}")
        else:
            out.extend(str(n) for n in run)
        i = j + 1
    return "[" + ",".join(out) + "]"


def main():
    md = MD.read_text(encoding="utf-8")
    head, sep, refsec = md.partition("## References")
    if not sep:
        sys.exit("References section not found")

    old_refs = load_refs(refsec)
    new_refs = {k: v["entry"] for k, v in json.loads(NEW.read_text(encoding="utf-8")).items()}

    assign, entry_by_key = {}, {}
    for k, v in old_refs.items():
        entry_by_key[k] = v
    for k, v in new_refs.items():
        entry_by_key[k] = v

    counter = [0]

    def repl(m):
        keys = parse_group(m.group(1))
        nums = []
        for k in keys:
            if k not in entry_by_key:
                raise ValueError(f"unknown ref key: {k}")
            if k not in assign:
                counter[0] += 1
                assign[k] = counter[0]
            nums.append(assign[k])
        return compress(nums)

    body = GROUP.sub(repl, head)

    # 校验：每个已有引用都被引用到
    uncited = [k for k in entry_by_key if k not in assign]
    new_list = "\n\n".join(f"[{assign[k]}] {entry_by_key[k]}"
                           for k in sorted(assign, key=lambda x: assign[x]))
    shutil.copy2(MD, BACKUP)
    MD.write_text(body + "## References\n\n" + new_list + "\n", encoding="utf-8")

    print(f"refs total: {len(assign)}  (was {len(old_refs)} + new {len(new_refs)})")
    print(f"uncited entries: {uncited if uncited else 'none'}")
    print(f"backup -> {BACKUP}")
    print("\nfirst appearance order:")
    for k in sorted(assign, key=lambda x: assign[x]):
        print(f"  [{assign[k]:2d}] <- {k}")


if __name__ == "__main__":
    main()
