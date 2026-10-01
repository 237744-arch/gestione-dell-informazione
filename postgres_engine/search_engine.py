class SearchEngine:
    def __init__(self, cfg, conn, limit=10):
        self.conn  = conn
        self.limit = limit

    def tfidf_search(self, raw_query):
        return self._search(raw_query, method='ts_rank')

    def bm25_search(self, raw_query):
        return self._search(raw_query, method='ts_rank_cd')

    def _search(self, raw_query, method):
        sql = f"""
          SELECT title, {method}(documento, plainto_tsquery('italian', %s)) AS rank
          FROM docs
          WHERE documento @@ plainto_tsquery('italian', %s)
          ORDER BY rank DESC
          LIMIT {self.limit};
        """
        cur = self.conn.cursor()
        cur.execute(sql, (raw_query, raw_query))
        results = cur.fetchall()
        cur.close()
        return results

    def search_by_field(self, raw_query, field, method='ts_rank'):
        if field not in ('title', 'content'):
            raise ValueError("field deve essere 'title' o 'content'")
        sql = f"""
          SELECT title, {method}(to_tsvector('italian', {field}), plainto_tsquery('italian', %s)) AS rank
          FROM docs
          WHERE to_tsvector('italian', {field}) @@ plainto_tsquery('italian', %s)
          ORDER BY rank DESC
          LIMIT {self.limit};
        """
        cur = self.conn.cursor()
        cur.execute(sql, (raw_query, raw_query))
        results = cur.fetchall()
        cur.close()
        return results