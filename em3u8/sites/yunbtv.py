from em3u8.sites import Site



class YunBTV(Site):
    '''
    云播 yunbtv.net

    change:
        _m3u8_filter: find resource
        _title_filter: filter title 
    '''

    def __init__(self, url, timeout=10):
        super().__init__(url, timeout)
        self._m3u8_filter = [
            r'(http[^"]+m3u8)'
        ]
        self._title_filter = r'(^[^_]+_[^_]+)_'
