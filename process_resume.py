#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简历处理工具 - 一键完成 PDF 解析和模板生成

使用方式：
    单个文件：python process_resume.py Resumes/xxx.pdf
    批量处理：python process_resume.py Resumes/
    指定输出：python process_resume.py Resumes/xxx.pdf -o Output/
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List, Tuple

# 导入解析和生成模块
from resume_parser import extract_text_from_resume, parse_resume_with_llm
from resume_template_generator import ResumeTemplateGenerator
import json

# 支持的文件格式
SUPPORTED_FORMATS = ['.pdf', '.docx']


def process_single_resume(file_path: str, output_dir: str = None, template_path: str = None) -> Tuple[bool, str]:
    """
    处理单个简历文件
    
    Args:
        file_path: 简历文件路径（支持 .pdf, .docx）
        output_dir: 输出目录（可选，默认与源文件同目录）
        template_path: 模板文件路径（可选）
        
    Returns:
        (是否成功, 消息)
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        return False, f"文件不存在: {file_path}"
    
    suffix = file_path.suffix.lower()
    if suffix not in SUPPORTED_FORMATS:
        return False, f"不支持的文件格式: {suffix}，支持的格式: {', '.join(SUPPORTED_FORMATS)}"
    
    # 确定输出目录
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    else:
        output_dir = file_path.parent
    
    # 输出文件路径
    base_name = file_path.stem
    json_path = output_dir / f"{base_name}_parsed.json"
    excel_path = output_dir / f"{base_name}_filled.xlsx"
    
    # 默认模板路径
    if not template_path:
        template_path = Path(__file__).parent / "Templates" / "template.xlsx"
    
    if not Path(template_path).exists():
        return False, f"模板文件不存在: {template_path}"
    
    try:
        # ========== 步骤1: 提取文本 ==========
        print(f"\n  [1/3] 提取文本 ({suffix})...")
        resume_text = extract_text_from_resume(str(file_path))
        print(f"        提取完成，共 {len(resume_text)} 字符")
        
        # ========== 步骤2: 调用 LLM 解析 ==========
        print(f"  [2/3] 调用 DeepSeek 解析简历...")
        parsed_data = parse_resume_with_llm(resume_text)
        
        # 检查解析结果
        if "error" in parsed_data:
            return False, f"解析失败: {parsed_data['error']}"
        
        # 保存 JSON
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(parsed_data, f, ensure_ascii=False, indent=2)
        print(f"        解析完成，已保存: {json_path}")
        
        # ========== 步骤3: 生成 Excel 模板 ==========
        print(f"  [3/3] 生成 Excel 模板...")
        generator = ResumeTemplateGenerator(str(template_path))
        generator.generate(parsed_data, str(excel_path))
        
        return True, f"处理完成！\n        JSON: {json_path}\n        Excel: {excel_path}"
        
    except Exception as e:
        return False, f"处理出错: {str(e)}"


def process_directory(dir_path: str, output_dir: str = None, template_path: str = None) -> None:
    """
    批量处理目录下的所有简历文件（PDF 和 Word）
    
    Args:
        dir_path: 目录路径
        output_dir: 输出目录（可选）
        template_path: 模板文件路径（可选）
    """
    dir_path = Path(dir_path)
    
    if not dir_path.is_dir():
        print(f"❌ 不是有效目录: {dir_path}")
        return
    
    # 查找所有支持的文件
    resume_files = []
    for fmt in SUPPORTED_FORMATS:
        resume_files.extend(dir_path.glob(f"*{fmt}"))
    
    if not resume_files:
        print(f"⚠️  目录中没有简历文件: {dir_path}")
        print(f"   支持的格式: {', '.join(SUPPORTED_FORMATS)}")
        return
    
    print(f"\n找到 {len(resume_files)} 个简历文件")
    print("=" * 60)
    
    success_count = 0
    fail_count = 0
    results = []
    
    for i, resume_file in enumerate(resume_files, 1):
        print(f"\n[{i}/{len(resume_files)}] 处理: {resume_file.name}")
        print("-" * 40)
        
        success, message = process_single_resume(
            str(resume_file), 
            output_dir, 
            template_path
        )
        
        if success:
            success_count += 1
            print(f"  ✅ {message}")
        else:
            fail_count += 1
            print(f"  ❌ {message}")
        
        results.append((resume_file.name, success, message))
    
    # 打印汇总
    print("\n" + "=" * 60)
    print("批量处理完成！")
    print("=" * 60)
    print(f"  成功: {success_count}")
    print(f"  失败: {fail_count}")
    print(f"  总计: {len(resume_files)}")
    
    if fail_count > 0:
        print("\n失败列表:")
        for name, success, message in results:
            if not success:
                print(f"  - {name}: {message}")


def main():
    parser = argparse.ArgumentParser(
        description="简历处理工具 - 支持 PDF 和 Word (.docx) 格式",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  处理单个 PDF 文件:
    python process_resume.py Resumes/张三.pdf
    
  处理单个 Word 文件:
    python process_resume.py Resumes/李四.docx
    
  批量处理目录:
    python process_resume.py Resumes/
    
  指定输出目录:
    python process_resume.py Resumes/张三.pdf -o Output/
    
  指定模板文件:
    python process_resume.py Resumes/张三.pdf -t Templates/custom.xlsx

支持的文件格式: .pdf, .docx
"""
    )
    
    parser.add_argument(
        "input",
        help="简历文件路径（.pdf/.docx）或包含简历的目录路径"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="输出目录（默认与输入文件同目录）",
        default=None
    )
    
    parser.add_argument(
        "-t", "--template",
        help="Excel 模板文件路径",
        default=None
    )
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    
    # 如果是相对路径，转换为绝对路径
    if not input_path.is_absolute():
        input_path = Path(__file__).parent / input_path
    
    print("=" * 60)
    print("简历处理工具")
    print("=" * 60)
    print(f"输入: {input_path}")
    if args.output:
        print(f"输出目录: {args.output}")
    if args.template:
        print(f"模板: {args.template}")
    
    if input_path.is_dir():
        # 批量处理目录
        process_directory(str(input_path), args.output, args.template)
    elif input_path.is_file():
        # 处理单个文件
        success, message = process_single_resume(
            str(input_path), 
            args.output, 
            args.template
        )
        if success:
            print(f"\n✅ {message}")
        else:
            print(f"\n❌ {message}")
            sys.exit(1)
    else:
        print(f"\n❌ 路径不存在: {input_path}")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
