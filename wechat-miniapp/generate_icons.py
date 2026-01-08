# 生成微信小程序TabBar占位图标的脚本
# 使用PIL库创建简单的彩色方块图标

try:
    from PIL import Image, ImageDraw
except ImportError:
    print("正在安装Pillow库...")
    import subprocess
    subprocess.run(['pip', 'install', 'Pillow'], check=True)
    from PIL import Image, ImageDraw

import os

# 图标配置
icons = [
    ('home', '#999999', '#409EFF'),      # 首页
    ('calendar', '#999999', '#409EFF'),  # 排班
    ('clock', '#999999', '#409EFF'),     # 打卡
    ('file', '#999999', '#409EFF'),      # 加班
    ('user', '#999999', '#409EFF'),      # 我的
]

output_dir = r'd:\PythonProject\Working_Hours_System\wechat-miniapp\images'

# 图标符号映射（使用简单形状）
def create_icon(name, color, size=81):
    """创建简单的占位图标"""
    img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # 将hex颜色转为RGB
    if color.startswith('#'):
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        color_rgb = (r, g, b, 255)
    else:
        color_rgb = (100, 100, 100, 255)
    
    margin = 10
    
    if name == 'home':
        # 房子形状
        points = [
            (size//2, margin),           # 顶点
            (size-margin, size//2),      # 右上
            (size-margin, size-margin),  # 右下
            (margin, size-margin),       # 左下
            (margin, size//2),           # 左上
        ]
        draw.polygon(points, fill=color_rgb)
    elif name == 'calendar':
        # 日历形状（矩形+顶部装饰）
        draw.rectangle([margin, margin+10, size-margin, size-margin], fill=color_rgb)
        draw.rectangle([margin+15, margin, margin+25, margin+15], fill=color_rgb)
        draw.rectangle([size-margin-25, margin, size-margin-15, margin+15], fill=color_rgb)
    elif name == 'clock':
        # 圆形时钟
        draw.ellipse([margin, margin, size-margin, size-margin], fill=color_rgb)
    elif name == 'file':
        # 文件形状
        draw.rectangle([margin+5, margin, size-margin-5, size-margin], fill=color_rgb)
        # 折角
        draw.polygon([
            (size-margin-5, margin),
            (size-margin-5, margin+20),
            (size-margin-20, margin)
        ], fill=(255, 255, 255, 200))
    elif name == 'user':
        # 用户图标（圆+半圆）
        # 头部
        draw.ellipse([size//2-12, margin, size//2+12, margin+24], fill=color_rgb)
        # 身体
        draw.ellipse([margin+5, margin+30, size-margin-5, size-margin+20], fill=color_rgb)
    
    return img

# 创建所有图标
for name, normal_color, active_color in icons:
    # 普通状态图标
    normal_icon = create_icon(name, normal_color)
    normal_path = os.path.join(output_dir, f'{name}.png')
    normal_icon.save(normal_path)
    print(f'已创建: {normal_path}')
    
    # 激活状态图标
    active_icon = create_icon(name, active_color)
    active_path = os.path.join(output_dir, f'{name}-active.png')
    active_icon.save(active_path)
    print(f'已创建: {active_path}')

print('\n✅ 所有图标创建完成！')
