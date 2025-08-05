#!/bin/bash

echo "🎮 启动1944空战传奇游戏..."
echo "正在打开游戏..."

# 检查是否有可用的浏览器
if command -v google-chrome &> /dev/null; then
    google-chrome index.html
elif command -v firefox &> /dev/null; then
    firefox index.html
elif command -v chromium-browser &> /dev/null; then
    chromium-browser index.html
elif command -v xdg-open &> /dev/null; then
    xdg-open index.html
else
    echo "❌ 未找到可用的浏览器"
    echo "请手动打开 index.html 文件"
    exit 1
fi

echo "✅ 游戏已启动！"
echo "🎯 游戏控制："
echo "   ↑↓←→ 移动飞机"
echo "   空格键 发射子弹"
echo "   ESC 暂停游戏"
echo ""
echo "祝您游戏愉快！🎮✈️"