import aiohttp


class PasteService:
    _conn = aiohttp.TCPConnector()
    session = aiohttp.ClientSession(connector=_conn, timeout=aiohttp.ClientTimeout(total=10))
    _endpoint = "https://paste.mozilla.org/api/"

    async def create_paste(self, data: str) -> str:
        payload = {"format": "url", "content": data, "expires": "604800", "lexer": "_markdown"}
        try:
            async with self.session.post(self._endpoint, data=payload) as resp:
                if resp.status != 200:
                    return f"Error: {resp.status}, {await resp.text()}"
                return await resp.text()
        except Exception as e:
            return str(e)
