#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import zipfile
import hashlib
import datetime
import subprocess
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

def update_appcast(version, plugin_path):
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
            v["url"] = f"https://github.com/mrjoy/bob-plugin-gemini-translate/releases/download/v{version}/{PLUGIN_NAME}.bobplugin"
            v["minBobVersion"] = "1.8.0"
            break
    else:
        # 添加新版本
        release_notes = input(f"请输入v{version}版本的更新说明: ") or f"发布{version}版本"
        appcast.get("versions", []).insert(0, {
            "version": version,
            "desc": release_notes,
            "sha256": sha256,
            "url": f"https://github.com/mrjoy/bob-plugin-gemini-translate/releases/download/v{version}/{PLUGIN_NAME}.bobplugin",
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

def main():
    # 获取版本号
    global VERSION
    VERSION = get_version_from_info()
    
    # 打包插件
    plugin_path = build_plugin(VERSION)
    
    # 更新appcast.json
    sha256 = update_appcast(VERSION, plugin_path)
    
    print("\n构建信息:")
    print(f"版本号: v{VERSION}")
    print(f"文件名: {PLUGIN_NAME}.bobplugin")
    print(f"SHA256: {sha256}")
    print(f"输出目录: {os.path.abspath(RELEASE_DIR)}")
    
    # 可选：打开输出目录
    if sys.platform == 'darwin':  # macOS
        subprocess.run(['open', RELEASE_DIR])
    elif sys.platform == 'win32':  # Windows
        os.startfile(RELEASE_DIR)
    elif sys.platform.startswith('linux'):  # Linux
        subprocess.run(['xdg-open', RELEASE_DIR])

if __name__ == "__main__":
    main() 
