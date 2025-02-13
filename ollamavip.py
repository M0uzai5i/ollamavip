import aiohttp
import asyncio
import json
from aiohttp import ClientTimeout
import sys

async def read_urls(filename):
    """读取url.txt文件中的URL列表"""
    try:
        with open(filename, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
            return urls
    except FileNotFoundError:
        print(f"错误：文件 {filename} 不存在")
        return []
    except Exception as e:
        print(f"读取文件时发生错误：{str(e)}")
        return []

async def check_ollama_models(session, url):
    """异步检查指定URL的Ollama服务模型列表"""
    try:
        timeout = ClientTimeout(total=10)
        async with session.get(f"{url}/api/tags", timeout=timeout) as response:
            response.raise_for_status()
            data = await response.json()
            models = [model['name'] for model in data.get('models', [])]
            print(f"URL: {url}")
            if models:
                print("可用模型:")
                for model in models:
                    print(f"  - {model}")
            else:
                print("警告：未找到任何模型")
            return models
    except asyncio.TimeoutError:
        error_message = f"请求错误：连接超时"
    except aiohttp.ClientError as e:
        error_message = f"请求错误：{str(e)}"
    except json.JSONDecodeError:
        error_message = "错误：响应不是有效的JSON格式"
    except KeyError:
        error_message = "错误：响应格式不符合预期"
    
    print(f"URL: {url}")
    print(f"错误信息：{error_message}")
    return error_message

async def save_results(results, output_file):
    """将结果保存到文本文件"""
    with open(output_file, 'w') as f:
        for url, models in results.items():
            f.write(f"URL: {url}\n")
            
            if isinstance(models, list):
                if models:
                    f.write("可用模型:\n")
                    for model in models:
                        f.write(f"  - {model}\n")
                else:
                    f.write("警告：未找到任何模型\n")
            else:
                f.write(f"错误信息：{models}\n")
            
            f.write("\n")  # 添加空行分隔不同URL的结果
            print(f"URL: {url}")
            
            if isinstance(models, list):
                if models:
                    print("可用模型:")
                    for model in models:
                        print(f"  - {model}")
                else:
                    print("警告：未找到任何模型")
            else:
                print(f"错误信息：{models}")

async def main():
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("用法: python test.py <url_file>")
        return
    
    # 从命令行参数获取输入文件名
    input_file = sys.argv[1]
    output_file = "result.txt"
    
    # 读取URL列表
    urls = await read_urls(input_file)
    if not urls:
        print("没有找到有效的URL，请检查输入文件")
        return
    
    results = {}
    print("开始检查模型...")
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            print(f"正在检查 {url}...")
            task = asyncio.create_task(check_ollama_models(session, url))
            tasks.append((url, task))
        
        for url, task in tasks:
            models = await task
            results[url] = models
    
    # 保存结果
    await save_results(results, output_file)
    print(f"检查完成，结果已保存到 {output_file}")

if __name__ == "__main__":
    asyncio.run(main())
