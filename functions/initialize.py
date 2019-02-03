def url_list_generator() -> list:
    """アクセス先のURL集をリストで返却する
    """
    url_list = []
    URL_FIRST_PART = 'https://www.mercari.com/jp/search/?page='
    URL_SECOND_PART = '&keyword=%E3%82%82%E3%81%97%E9%AB%98%E6%A0%A1%E9%87%8E%E7%90%83%E3%81%AE%E5%A5%B3%E5%AD%90%E3%83%9E%E3%83%8D%E3%83%BC%E3%82%B8%E3%83%A3%E3%83%BC%E3%81%8C%E3%83%89%E3%83%A9%E3%83%83%E3%82%AB%E3%83%BC%E3%81%AE%E3%80%8E%E3%83%9E%E3%83%8D%E3%82%B8%E3%83%A1%E3%83%B3%E3%83%88%E3%80%8F%E3%82%92%E8%AA%AD%E3%82%93%E3%81%A0%E3%82%89'

    for page_num in range(1, 51):
        url_list.append(URL_FIRST_PART + str(page_num) + URL_SECOND_PART)

    return url_list