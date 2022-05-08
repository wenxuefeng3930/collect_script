# -*- coding: utf-8 -*-
# +-------------------------------------------------------------------
# | Date: 2022/3/30
# +-------------------------------------------------------------------
# | Author: Pluto <i@aoaostar.com>
# +-------------------------------------------------------------------

import asyncio
import json
import os

import aiohttp

if __name__ != '__main__':
    os._exit()


def load_json(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return []


def http_get(url, params=None):
    if params is None:
        params = {}
    return aiohttp.request("GET", url, params=params, proxy=PROXY, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/96.0.4664.110 Safari/537.36",
    }, timeout=aiohttp.ClientTimeout(total=TIMEOUT))


def save(output, filename, contents, extension='.json'):
    output = output.rstrip('/\\')
    path = f"{output}/{filename}{extension}"
    if not os.path.exists(output):
        os.makedirs(output)

    with open(path, "w", encoding="utf-8") as f:
        f.write(contents)
        f.flush()


def save_file(output, filename, contents, extension='.jpg'):
    output = output.rstrip('/\\')
    path = f"{output}/{filename}{extension}"
    if not os.path.exists(output):
        os.makedirs(output)
    with open(path, "wb") as f:
        f.write(contents)
        f.flush()


async def semap(sem, func, data, callback=None):
    async with sem:
        res = await func(data)
        if callback:
            callback(data)
        return res


async def download(data):
    filename = data["id"]
    extension = data["url"][data["url"].rindex('.'):]
    filepath = "./images/" + filename + extension
    if os.path.exists(filepath) and os.path.getsize(filepath) > 10240:
        print("已下载跳过", data["url"])
        return
    for i in range(3):
        try:
            async with http_get(data["url"]) as r:
                if r.status != 200:
                    if os.path.exists(filepath):
                        os.unlink(filepath)
                    continue
                save_file(f"./images", filename, await r.read(), extension)
                print("下载成功", data["url"])
                break
        except Exception as e:
            print(f"[{data['url']}]下载异常：{e}")
            continue


async def main():
    semaphore = asyncio.Semaphore(5)
    tasks = []
    url_list = load_json('data.json')
    print("开始下载", len(url_list))
    for k in url_list:
        tasks.append(asyncio.create_task(semap(semaphore, download, {
            "id": k,
            "url": url_list[k],
        }, None)))

    await asyncio.wait(tasks)
    print("下载完毕", len(url_list))


# 并行数
MAX_WORKERS = 3

# http代理
PROXY = ''
# 超时时间
TIMEOUT = 120
loop = asyncio.get_event_loop()

loop.run_until_complete(main())
loop.close()
