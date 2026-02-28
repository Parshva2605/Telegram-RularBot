"""
Supabase wrapper for non-JWT API keys
Works with sb_publishable_ and sb_secret_ key formats
"""
import requests
from typing import Optional, Dict, List, Any

class SupabaseTable:
    def __init__(self, base_url: str, table_name: str, headers: Dict[str, str]):
        self.base_url = base_url
        self.table_name = table_name
        self.headers = headers
        self.url = f"{base_url}/rest/v1/{table_name}"
    
    def select(self, columns: str = "*", count: Optional[str] = None):
        """Select rows from table - returns SelectQuery for chaining"""
        return SelectQuery(self.url, self.headers, columns, count)
    
    def insert(self, data: Dict[str, Any]):
        """Insert row into table - returns InsertQuery for chaining"""
        return InsertQuery(self.url, data, self.headers)
    
    def update(self, data: Dict[str, Any]):
        """Update rows - returns UpdateQuery for chaining"""
        return UpdateQuery(self.url, data, self.headers)
    
    def delete(self):
        """Delete rows - returns DeleteQuery for chaining"""
        return DeleteQuery(self.url, self.headers)
    
    def eq(self, column: str, value: Any):
        """Filter by equality"""
        return SelectQuery(self.url, self.headers).eq(column, value)


class SelectQuery:
    def __init__(self, url: str, headers: Dict[str, str], columns: str = "*", count: Optional[str] = None):
        self.url = url
        self.headers = headers
        self.filters = []
        self.columns = columns
        self._limit = None
        self._order = None
        self._count = count
    
    def select(self, columns: str = "*"):
        self.columns = columns
        return self
    
    def eq(self, column: str, value: Any):
        self.filters.append(f"{column}=eq.{value}")
        return self
    
    def limit(self, count: int):
        self._limit = count
        return self
    
    def order(self, column: str, desc: bool = False):
        self._order = f"{column}.{'desc' if desc else 'asc'}"
        return self
    
    def execute(self):
        params = {"select": self.columns}
        if self._limit:
            params["limit"] = self._limit
        if self._order:
            params["order"] = self._order
        
        headers = self.headers.copy()
        if self._count == 'exact':
            headers["Prefer"] = "count=exact"
        
        url = self.url
        if self.filters:
            url += "?" + "&".join(self.filters)
        
        response = requests.get(url, headers=headers, params=params)
        
        class Result:
            def __init__(self, data, count=None):
                self.data = data
                self.count = count if count is not None else len(data)
        
        if response.status_code in [200, 206]:
            data = response.json()
            count_header = response.headers.get('Content-Range', '')
            if count_header and '/' in count_header:
                count_str = count_header.split('/')[-1]
                try:
                    count = int(count_str) if count_str != '*' else len(data)
                except ValueError:
                    count = len(data)
            else:
                count = len(data)
            return Result(data, count)
        else:
            raise Exception(f"Query failed: {response.status_code} - {response.text}")


class UpdateQuery:
    def __init__(self, url: str, data: Dict[str, Any], headers: Dict[str, str]):
        self.url = url
        self.data = data
        self.headers = headers
        self.filters = []
    
    def eq(self, column: str, value: Any):
        self.filters.append(f"{column}=eq.{value}")
        return self
    
    def execute(self):
        url = self.url
        if self.filters:
            url += "?" + "&".join(self.filters)
        
        response = requests.patch(
            url,
            json=self.data,
            headers={**self.headers, "Prefer": "return=representation"}
        )
        
        class Result:
            def __init__(self, data):
                self.data = data
        
        if response.status_code == 200:
            return Result(response.json())
        else:
            raise Exception(f"Update failed: {response.status_code} - {response.text}")


class InsertQuery:
    def __init__(self, url: str, data: Dict[str, Any], headers: Dict[str, str]):
        self.url = url
        self.data = data
        self.headers = headers
    
    def execute(self):
        response = requests.post(
            self.url,
            json=self.data,
            headers={**self.headers, "Prefer": "return=representation"}
        )
        
        class Result:
            def __init__(self, data):
                self.data = data
        
        if response.status_code in [200, 201]:
            return Result(response.json())
        else:
            raise Exception(f"Insert failed: {response.status_code} - {response.text}")


class DeleteQuery:
    def __init__(self, url: str, headers: Dict[str, str]):
        self.url = url
        self.headers = headers
        self.filters = []
    
    def eq(self, column: str, value: Any):
        self.filters.append(f"{column}=eq.{value}")
        return self
    
    def execute(self):
        url = self.url
        if self.filters:
            url += "?" + "&".join(self.filters)
        
        response = requests.delete(
            url,
            headers={**self.headers, "Prefer": "return=representation"}
        )
        
        class Result:
            def __init__(self, data):
                self.data = data
        
        if response.status_code in [200, 204]:
            return Result(response.json() if response.text else [])
        else:
            raise Exception(f"Delete failed: {response.status_code} - {response.text}")


class SupabaseClient:
    def __init__(self, url: str, key: str):
        self.url = url
        self.headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
    
    def table(self, table_name: str):
        """Get table interface"""
        return SupabaseTable(self.url, table_name, self.headers)


def create_client(url: str, key: str):
    """Create Supabase client that works with any key format"""
    return SupabaseClient(url, key)
