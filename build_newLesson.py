#!/usr/bin/env python
# -*- coding:utf-8 -*-

import ast
import os
import re
import shutil
import subprocess
import sys


SCRIPT_NAME = "newLesson.py"


def find_default_version(script_path):
    with open(script_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=script_path)

    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if len(node.targets) != 1:
            continue

        target = node.targets[0]
        value = node.value
        if not (
            isinstance(target, ast.Attribute)
            and isinstance(target.value, ast.Name)
            and target.value.id == "self"
            and target.attr == "version"
            and isinstance(value, ast.Call)
            and isinstance(value.func, ast.Attribute)
            and value.func.attr == "get"
            and len(value.args) >= 2
        ):
            continue

        key_arg = value.args[0]
        default_arg = value.args[1]
        if not isinstance(key_arg, ast.Constant) or key_arg.value != "version":
            continue

        default_value = ast.literal_eval(default_arg)
        return str(default_value)

    raise RuntimeError("未能从源码中解析 self.version 的默认值")


def sanitize_version(version):
    sanitized = re.sub(r'[<>:"/\\|?*]+', "-", version.strip())
    sanitized = sanitized.strip(". ")
    if not sanitized:
        raise RuntimeError("解析到的版本号不能为空")
    return sanitized


def iter_python_candidates():
    seen = set()
    candidates = []

    if sys.executable:
        candidates.append(sys.executable)

    python_on_path = shutil.which("python")
    if python_on_path:
        candidates.append(python_on_path)

    try:
        result = subprocess.run(
            ["py", "-0p"],
            check=True,
            capture_output=True,
            text=True,
        )
        for line in result.stdout.splitlines():
            match = re.search(r"([A-Za-z]:\\.+python\.exe)", line, re.IGNORECASE)
            if match:
                candidates.append(match.group(1))
    except Exception:
        pass

    for candidate in candidates:
        normalized = os.path.normcase(os.path.abspath(candidate))
        if normalized in seen:
            continue
        seen.add(normalized)
        if os.path.exists(candidate) and candidate.lower().endswith(".exe"):
            yield candidate


def get_python_launcher():
    candidates = list(iter_python_candidates())
    preferred = [c for c in candidates if "libreoffice" not in c.lower()]

    for launcher in preferred + candidates:
        if os.path.basename(launcher).lower() == "python.exe":
            return launcher

    raise RuntimeError("未找到可用于执行 PyInstaller 的 Python 解释器")


def has_module(python_launcher, module_name):
    env = build_env()
    result = subprocess.run(
        [python_launcher, "-c", f"import {module_name}"],
        capture_output=True,
        text=True,
        env=env,
    )
    return result.returncode == 0


def ensure_module(python_launcher, module_name, package_name):
    if has_module(python_launcher, module_name):
        return

    print(f"正在安装依赖: {package_name}")
    subprocess.run(
        [
            python_launcher,
            "-m",
            "pip",
            "install",
            "--upgrade",
            "--target",
            dependency_dir(),
            package_name,
        ],
        check=True,
        env=build_env(),
    )


def dependency_dir():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dep_dir = os.path.join(base_dir, "build", "pydeps")
    os.makedirs(dep_dir, exist_ok=True)
    return dep_dir


def build_env():
    env = os.environ.copy()
    dep_dir = dependency_dir()
    python_path = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = dep_dir if not python_path else dep_dir + os.pathsep + python_path
    return env


def build():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(base_dir, SCRIPT_NAME)
    python_launcher = get_python_launcher()
    version = sanitize_version(find_default_version(script_path))
    exe_name = f"newLesson-version{version}"
    exe_path = os.path.join(base_dir, f"{exe_name}.exe")
    work_path = os.path.join(base_dir, "build", "pyinstaller", exe_name)
    spec_path = os.path.join(base_dir, "build", "spec")
    icon_path = os.path.join(base_dir, "lesson.ico")

    os.makedirs(work_path, exist_ok=True)
    os.makedirs(spec_path, exist_ok=True)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    ensure_module(python_launcher, "PyInstaller", "pyinstaller")
    ensure_module(python_launcher, "selenium", "selenium")
    ensure_module(python_launcher, "cv2", "opencv-python")

    command = [
        python_launcher,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--hidden-import",
        "selenium.webdriver.common.action_chains",
        "--distpath",
        base_dir,
        "--workpath",
        work_path,
        "--specpath",
        spec_path,
        "--name",
        exe_name,
    ]

    if os.path.exists(icon_path):
        command.extend(["--icon", icon_path])

    command.append(script_path)

    print(f"使用解释器: {python_launcher}")
    print(f"检测到默认版本: {version}")
    print(f"输出文件名: {exe_name}.exe")
    subprocess.run(command, check=True, cwd=base_dir, env=build_env())
    print(f"打包完成: {exe_path}")


if __name__ == "__main__":
    build()
