import asyncio
import os
import aiohttp
import datetime


token = os.environ.get('GITHUB_TOKEN')
ROOT = 'https://api.github.com'


# should use cache and ETag
async def get_json(client, url):
    while True:
        resp = await client.get(url)
        data = await resp.json()
        limit = resp.headers['X-RateLimit-Limit']
        used = resp.headers['X-RateLimit-Used']
        remaining = resp.headers['X-RateLimit-Remaining']
        print(f'Read {url} (API calls {used}/{limit})')

        if resp.status == 403:
            if 'retry-after' in resp.headers:
                delay = int(resp.headers['retry-after'])
                print(f'Throttling for {url} -- {delay} seconds')
                await asyncio.sleep(delay)
            elif 'X-RateLimit-Reset' in resp.headers:
                reset = datetime.datetime.fromtimestamp(float(resp.headers['X-RateLimit-Reset']))
                now = datetime.datetime.now()
                delta = reset - now
                seconds = delta.seconds
                print(f'Throttling for {url} -- {seconds}')
                await asyncio.sleep(seconds)
        else:
            return data


queue = asyncio.Queue()
results = asyncio.Queue()
done = False
consumers_done = 0


async def producer(tree):
    global done
    for item in tree:
        await queue.put((item['url'], item['path']))
    done = True


async def consumer(client):
    global consumers_done

    while not done:
        try:
            item = queue.get_nowait()
        except asyncio.QueueEmpty:
            await asyncio.sleep(.1)
        else:
            url, path = item
            data = await get_json(client, url)
            if 'tree' in data:
                for item in data['tree']:
                    await queue.put((item['url'], item['path']))
            elif 'content' in data:
                data['path'] = path
                await results.put(data)
    consumers_done += 1


async def get_files(token, owner, repo, branch='main'):
    url = f'{ROOT}/repos/{owner}/{repo}/git/trees/{branch}?recursive=1'

    async with aiohttp.ClientSession(headers={'Authorization': f'token {token}'}) as client:
        data = await get_json(client, url)
        for item in data['tree']:
            await queue.put((item['url'], item['path']))

        consumer_tasks = [asyncio.create_task(consumer(client)) for i in range(10)]
        num = 1

        while True:
            item = await results.get()
            doc = {
                '_id': item['node_id'],
                'path': item['path'],
                '_attachment': item['content'],
                '_timestamp': item['sha']   # will this work?
            }
            yield doc
            num += 1
            if consumers_done == 10:
                break

    await asyncio.gather(consumer_task, producer_task)


if __name__ == '__main__':
    if token is None:
        raise Exception('set the GITHUB_TOKEN variable')
    asyncio.run(get_files(token, 'elastic', 'elasticsearch'))
