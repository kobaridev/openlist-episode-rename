import os
import html
from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn

from core import InteractiveEpisodeRenamer

app = FastAPI(title="Episode Renamer Web UI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局存储renamer实例，简单实现，多用户请使用session
renamer_instance: Optional[InteractiveEpisodeRenamer] = None

class LoginRequest(BaseModel):
    url: str
    username: str
    password: str

class PathRequest(BaseModel):
    path: str

class RenameItem(BaseModel):
    path: str
    new_name: str

class RenameRequest(BaseModel):
    dir_path: str
    renames: List[RenameItem]

@app.post("/api/login")
def login(req: LoginRequest):
    global renamer_instance
    renamer_instance = InteractiveEpisodeRenamer(req.url, req.username, req.password)
    success = renamer_instance.login()
    if success:
        return {"status": "success", "message": "登录成功"}
    else:
        raise HTTPException(status_code=401, detail="登录失败，请检查配置。")

@app.get("/api/config")
def get_config():
    # 尝试加载本地配置
    temp_renamer = InteractiveEpisodeRenamer("", "", "")
    config = temp_renamer.load_config()
    return {"url": config.get('base_url', 'http://127.0.0.1:5244')}

@app.post("/api/list")
def list_directory(req: PathRequest):
    if not renamer_instance:
        raise HTTPException(status_code=401, detail="请先登录")
    
    contents = renamer_instance.get_directory_contents(req.path)
    if contents is None:
        raise HTTPException(status_code=400, detail="获取目录失败")
    
    dirs = [item for item in contents if item.get('is_dir')]
    files = [item for item in contents if not item.get('is_dir')]
    
    return {
        "current_path": req.path,
        "directories": dirs,
        "files": files
    }

@app.post("/api/extract_info")
def extract_info(req: dict = Body(...)):
    if not renamer_instance:
        raise HTTPException(status_code=401, detail="请先登录")
    
    filenames = req.get("filenames", [])
    result = {}
    for fname in filenames:
        info = renamer_instance.extract_episode_info(fname)
        result[fname] = info
    return result

@app.post("/api/tmdb_search")
def tmdb_search(req: dict = Body(...)):
    keyword = req.get("keyword")
    if not keyword:
        raise HTTPException(status_code=400, detail="请输入搜索关键词")
        
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
    }
    try:
        import requests
        from bs4 import BeautifulSoup
        
        # 请求 TMDB 网页搜索
        res = requests.get(f"https://www.themoviedb.org/search/tv?query={keyword}&language=zh-CN", headers=headers, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        
        results = []
        seen = set()
        
        for a in soup.find_all('a', attrs={'data-media-type': 'tv'}):
            href = a.get('href', '')
            if '/tv/' in href:
                tv_id = href.split('/tv/')[-1].split('?')[0].split('-')[0].strip('/')
                if not tv_id or not tv_id.isdigit() or tv_id in seen:
                    continue
                    
                title = None
                date = ''
                
                wrapper = a.find_parent('div', class_='wrapper')
                if wrapper:
                    title_elem = wrapper.find('h2')
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                    
                    wrapper_text = wrapper.get_text(separator='|', strip=True)
                    for p in wrapper_text.split('|'):
                        if '年' in p and '月' in p:
                            date = p
                            break
                            
                if not title:
                     if a.get('title'):
                         title = a.get('title')
                     else:
                         title_img = a.find('img')
                         if title_img and title_img.get('alt'):
                             title = title_img.get('alt')
                
                if title:
                    seen.add(tv_id)
                    results.append({"id": tv_id, "title": title, "date": date})
                    
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索TMDB失败: {str(e)}")

@app.post("/api/tmdb_fetch")
def tmdb_fetch(req: dict = Body(...)):
    url = req.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")
    
    # 确保追加中文语言参数
    if '?' not in url:
        url += '?language=zh-CN'
    elif 'language' not in url:
        url += '&language=zh-CN'
        
    # TMDB 请求伪装成正常浏览器
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
    }
    try:
        import requests
        from bs4 import BeautifulSoup
        
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        
        episodes = {}
        # 尝试选取包含所有集数信息的元素
        for a in soup.select('h3 > a'):
            href = a.get('href', '')
            if '/episode/' in href:
                # 获取 URL 最后的数字部分 `/tv/85937/season/1/episode/1`
                ep_num = href.split('/episode/')[-1].split('?')[0].strip('/')
                if ep_num.isdigit():
                    episodes[str(int(ep_num))] = a.get_text(strip=True)
                    
        # 额外兼容策略: class包含 info 的包裹层
        if not episodes:
            for wrapper in soup.select('.info'):
                a = wrapper.select_one('a[href*="/episode/"]')
                if a:
                    href = a.get('href', '')
                    ep_num = href.split('/episode/')[-1].split('?')[0].strip('/')
                    if ep_num.isdigit():
                        episodes[str(int(ep_num))] = a.get_text(strip=True)
                        
        return {"episodes": episodes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"抓取TMDB失败: {str(e)}")

@app.post("/api/generate_name")
def generate_name(req: dict = Body(...)):
    """
    接收 episode_info 和 naming_pattern，返回标准名称
    """
    if not renamer_instance:
        raise HTTPException(status_code=401, detail="请先登录")
    
    episode_info = req.get("episode_info", {})
    naming_pattern = req.get("naming_pattern", "{title}.S{season}E{episode:02d}")
    
    # 支持 {episode_title}
    new_name = renamer_instance.generate_standard_name(episode_info, naming_pattern)
    
    return {"new_name": new_name}

@app.post("/api/rename")
def batch_rename(req: RenameRequest):
    if not renamer_instance:
        raise HTTPException(status_code=401, detail="请先登录")
    
    rename_mapping = {}
    for item in req.renames:
        src_name = html.unescape(item.path)
        new_name = html.unescape(item.new_name)
        rename_mapping[src_name] = new_name
    success = renamer_instance.batch_rename(req.dir_path, rename_mapping)
    if success:
        return {"status": "success", "message": "批量重命名完成"}
    else:
        raise HTTPException(status_code=500, detail="批量重命名失败或部分失败")

class RenameSingleRequest(BaseModel):
    path: str
    new_name: str

@app.post("/api/rename_single")
def rename_single(req: RenameSingleRequest):
    if not renamer_instance:
        raise HTTPException(status_code=401, detail="请先登录")
    
    path = html.unescape(req.path)
    new_name = html.unescape(req.new_name)
    success = renamer_instance.rename_single_item(path, new_name)
    if success:
        return {"status": "success", "message": "重命名成功"}
    else:
        raise HTTPException(status_code=500, detail="重命名失败")

# 挂载前端页面
@app.get("/")
def index():
    return FileResponse("frontend/index.html")

if __name__ == "__main__":
    print("启动服务器: http://127.0.0.1:8000")
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
