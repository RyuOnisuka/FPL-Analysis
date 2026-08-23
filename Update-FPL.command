#!/bin/bash
# 🚀 1-Click FPL Auto Updater
# ดับเบิลคลิกไฟล์นี้เพื่อดึงข้อมูลสดและอัปเดตขึ้น GitHub ทันที

cd "$(dirname "$0")"
echo "=========================================="
echo "⚽ กำลังดึงข้อมูลคะแนนสดและสถิติล่าสุดจาก FPL..."
echo "=========================================="

python3 update_data.py 4554263

if [ $? -eq 0 ]; then
    echo ""
    echo "📤 กำลังส่งข้อมูลขึ้น GitHub Pages..."
    git add fpl_data.json fpl_data.js
    git commit -m "chore(data): auto-update FPL scores and live points"
    git push origin main
    echo ""
    echo "=========================================="
    echo "✅ สำเร็จเรียบร้อย! หน้าเว็บอัปเดตสดใหม่แล้ว"
    echo "👉 เข้าชมได้ที่: https://ryuonisuka.github.io/FPL-Analysis/"
    echo "=========================================="
else
    echo "❌ เกิดข้อผิดพลาดในการดึงข้อมูล"
fi

read -p "กด Enter เพื่อปิดหน้าต่างนี้..."
