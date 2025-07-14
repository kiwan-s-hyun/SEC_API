from sec_api import QueryApi, ExtractorApi
import re

class Extractor:
    def __init__(self, api_key: str):
        self.query_api = QueryApi(api_key=api_key)
        self.extractor_api = ExtractorApi(api_key=api_key)

    def get_url(self, cik: int, formType: str, **kwargs) -> str:
        query = f"cik:{cik} AND formType:\"{formType}\""
        for key, value in kwargs.items():
            if type(value) is str:
                entry = f"{key}:\"{value}\""
            else:
                entry = f"{key}:{value}"
            query += f" AND {entry}"
        request_query = {
            "query": query,
            "from": "0",
            "size": "1",
            "sort": [{"filedAt": {"order": "desc"}}]
        }
        response = self.query_api.get_filings(request_query)
        if response['filings']:
            url = response['filings'][0]['linkToFilingDetails']
        else:
            url = None

        return url

    def get_section(self, url: str, section: str, *section_filters, 
                    output_fmt: str='html') -> list:
        content = self.extractor_api.get_section(url, section, output_fmt)
        page_break_pattern = r'(?i)(<p[^>]*>\s*\d{1,4}\s*</?p>?.*?<hr\b[^>]*>)'
        parts = re.split(page_break_pattern, content)
        all_pages = {parts[i]: parts[i-1] for i in range(1, len(parts), 2)}
        return all_pages

    def extract_tables(self, page: str):
        pattern = r'##TABLE_START(.*?)##TABLE_END'
        tables = re.findall(pattern, page, flags=re.DOTALL)

        return [table.strip() for table in tables if table.strip()]