#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import zipfile
import hashlib
import datetime
import subprocess
import re
from pathlib import Path

# 配置信息
PLUGIN_NAME = "bob-plugin-gemini-translate"
RELEASE_DIR = "release"
VERSION = None  # 将从info.json中读取

def calculate_sha256(file_path):
    """计算文件的SHA256哈希值"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def get_version_from_info():
    """从info.json获取版本号"""
    with open("info.json", "r", encoding="utf-8") as f:
        info = json.load(f)
    return info.get("version", "0.1.0")

def increment_version(version_str):
    """增加版本号，注意小版本号到9之后要升级一个前面的版本号"""
    # 分解版本号
    parts = list(map(int, version_str.split('.')))
    
    # 增加最后一个部分
    parts[-1] += 1
    
    # 如果最后一部分是10，则将其重置为0，并增加前一部分
    for i in range(len(parts) - 1, 0, -1):
        if parts[i] > 9:
            parts[i] = 0
            parts[i-1] += 1
    
    # 组合版本号
    return '.'.join(map(str, parts))

def update_version_in_info_json(new_version):
    """更新info.json中的版本号"""
    with open("info.json", "r", encoding="utf-8") as f:
        info = json.load(f)
    
    info["version"] = new_version
    
    with open("info.json", "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=4)
    
    print(f"✅ 已更新info.json中的版本号为：{new_version}")

def update_appcast(version, plugin_path, release_notes=None):
    """更新appcast.json文件"""
    appcast_path = "appcast.json"
    
    # 计算插件包的SHA256
    sha256 = calculate_sha256(plugin_path)
    
    # 读取或创建appcast.json
    if os.path.exists(appcast_path):
        with open(appcast_path, "r", encoding="utf-8") as f:
            appcast = json.load(f)
    else:
        # 从info.json获取identifier
        with open("info.json", "r", encoding="utf-8") as f:
            info = json.load(f)
        appcast = {
            "identifier": info.get("identifier", "com.example.bob-plugin"),
            "versions": []
        }
    
    # 检查版本是否已存在
    for v in appcast.get("versions", []):
        if v.get("version") == version:
            v["sha256"] = sha256
            v["url"] = f"https://github.com/coulsontl/bob-plugin-gemini-translate/releases/download/v{version}/{PLUGIN_NAME}.bobplugin"
            v["minBobVersion"] = "1.8.0"
            break
    else:
        # 添加新版本
        if release_notes is None:
            release_notes = f"发布{version}版本"
        appcast.get("versions", []).insert(0, {
            "version": version,
            "desc": release_notes,
            "sha256": sha256,
            "url": f"https://github.com/coulsontl/bob-plugin-gemini-translate/releases/download/v{version}/{PLUGIN_NAME}.bobplugin",
            "minBobVersion": "1.8.0"
        })
    
    # 保存更新后的appcast.json
    with open(appcast_path, "w", encoding="utf-8") as f:
        json.dump(appcast, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已更新appcast.json，SHA256: {sha256}")
    return sha256

def build_plugin(version):
    """打包Bob插件"""
    # 创建release目录
    if not os.path.exists(RELEASE_DIR):
        os.makedirs(RELEASE_DIR)
    
    # 插件文件路径
    plugin_path = os.path.join(RELEASE_DIR, f"{PLUGIN_NAME}.bobplugin")
    
    # 创建插件压缩包
    with zipfile.ZipFile(plugin_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 添加必要文件
        for filename in ["info.json", "main.js", "README.md"]:
            if os.path.exists(filename):
                zipf.write(filename)
        
        # 添加其他资源文件
        for filename in [f for f in os.listdir('.') if f.endswith(('.png', '.jpg', '.gif', '.svg'))]:
            zipf.write(filename)
    
    print(f"✅ 插件打包完成: {plugin_path}")
    return plugin_path

def get_github_release_notes(version):
    """从环境变量或输入获取发布说明"""
    # 从环境变量获取（供GitHub Actions使用）
    if 'RELEASE_NOTES' in os.environ:
        return os.environ['RELEASE_NOTES']
    
    # 自动增加版本号时才请求用户输入，否则使用默认说明
    if "--auto-increment" in sys.argv:
        return input(f"请输入v{version}版本的更新说明: ") or f"发布{version}版本"
    else:
        return f"发布{version}版本"

def auto_release(auto_increment=False, release_notes=None):
    """自动发布新版本"""
    global VERSION
    
    # 获取当前版本
    old_version = get_version_from_info()
    
    # 如果需要自动增加版本号
    if auto_increment:
        VERSION = increment_version(old_version)
        update_version_in_info_json(VERSION)
    else:
        VERSION = old_version
    
    # 打包插件
    plugin_path = build_plugin(VERSION)
    
    # 使用提供的发布说明或获取新的
    if release_notes is None:
        release_notes = get_github_release_notes(VERSION)
    
    # 更新appcast.json (修改函数调用，增加发布说明参数)
    sha256 = update_appcast(VERSION, plugin_path, release_notes)
    
    print("\n构建信息:")
    print(f"版本号: v{VERSION}")
    print(f"文件名: {PLUGIN_NAME}.bobplugin")
    print(f"SHA256: {sha256}")
    print(f"输出目录: {os.path.abspath(RELEASE_DIR)}")
    
    return {
        "version": VERSION,
        "plugin_path": plugin_path,
        "sha256": sha256
    }

def main():
    # 解析命令行参数
    auto_increment = "--auto-increment" in sys.argv
    
    # 自动发布
    result = auto_release(auto_increment)
    
    # 可选：打开输出目录
    if "--no-open" not in sys.argv:
        if sys.platform == 'darwin':  # macOS
            subprocess.run(['open', RELEASE_DIR])
        elif sys.platform == 'win32':  # Windows
            os.startfile(RELEASE_DIR)
        elif sys.platform.startswith('linux'):  # Linux
            subprocess.run(['xdg-open', RELEASE_DIR])

if __name__ == "__main__":
    main() 
