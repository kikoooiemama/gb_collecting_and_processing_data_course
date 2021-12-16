import scrapy
from scrapy.http import HtmlResponse
import re
import json
from copy import deepcopy
from instaparser.items import InstaparserItem


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['http://instagram.com/']
    inst_login_link = '	https://www.instagram.com/accounts/login/ajax/'
    COUNT_ELS_ON_PAGE = 12
    inst_login = 'Onliskill_udm'
    inst_pwd = '#PWD_INSTAGRAM_BROWSER:10:1638551736:AedQAFI0vAAYTOunJJUOmrJPoJO3A6MjtJf+QOH/3ovuYhh9eIlQNGUh2MDiWMtQL80BL3LJqk7DfHobv+o7STw2Qg6qLwcDSuHFLa+tiYoPvNwdkG6zno3Y6Pr/Et12HLssUesjh66gbKA/Regr'

    # https://i.instagram.com/api/v1/friendships/1738740612/followers/?count=12&max_id=168&search_surface=follow_list_page
    inst_api_link = 'https://i.instagram.com/api/v1/friendships/'

    def __init__(self, users):
        self.users = users

    def parse(self, response):
        # извлекаем токен сессии
        csrf = self.fetch_csrf_token(response.text)
        # начинаем новую сессию и далее с помощью response.follow() работаем в этой же сессии!
        yield scrapy.FormRequest(self.inst_login_link,
                                 method='POST',
                                 callback=self.login,
                                 formdata={'username': self.inst_login,
                                           'enc_password': self.inst_pwd},  # это смотрим в браузере
                                 headers={'X-CSRFToken': csrf})

    def login(self, response: HtmlResponse):
        j_data = response.json()
        if j_data.get('authenticated'):
            for user in self.users:
                yield response.follow(
                    f'/{user}',  # относительная ссылка
                    callback=self.parse_all,
                    cb_kwargs={'username': user}  # доп параметры в след метод. помечаем с каким юзером работаем
                )

    def parse_all(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        content = response.xpath('//meta[@property="og:description"]/@content').get().split()
        n_followers = int(content[0])
        n_following = int(content[2])
        follow_info = {'followers': n_followers, 'followings': n_following}
        # followers
        url_posts = f'{self.inst_api_link}{user_id}/followers/?count={self.COUNT_ELS_ON_PAGE}&search_surface=follow_list_page'
        follow_type = 'follower'
        yield response.follow(
            url_posts,
            callback=self.parse_user,
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'follow_info': deepcopy(follow_info),
                       'follow_type': deepcopy(follow_type)
                       }
        )
        d_followers = n_followers // self.COUNT_ELS_ON_PAGE
        for i in range(1, d_followers + 1):
            url_post = f'{self.inst_api_link}{user_id}/followers/?count={self.COUNT_ELS_ON_PAGE}&max_id={i * self.COUNT_ELS_ON_PAGE}&search_surface=follow_list_page'
            yield response.follow(
                url_post,
                callback=self.parse_user,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'follow_info': deepcopy(follow_info),
                           'follow_type': deepcopy(follow_type)
                           }
            )
        # followings
        url_posts_f = f'{self.inst_api_link}{user_id}/followers/?count={self.COUNT_ELS_ON_PAGE}'
        follow_type = 'following'
        yield response.follow(
            url_posts_f,
            callback=self.parse_user,
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'follow_info': deepcopy(follow_info),
                       'follow_type': deepcopy(follow_type)
                       }
        )
        d_followins = n_following // self.COUNT_ELS_ON_PAGE
        for i in range(1, d_followins + 1):
            url_post = f'{self.inst_api_link}{user_id}/following/?count={self.COUNT_ELS_ON_PAGE}&max_id={i * self.COUNT_ELS_ON_PAGE}'
            yield response.follow(
                url_post,
                callback=self.parse_user,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'follow_info': deepcopy(follow_info),
                           'follow_type': deepcopy(follow_type)
                           }
            )

    def parse_user(self, response: HtmlResponse, username, user_id, follow_info, follow_type):
        j_data = response.json()
        followers_data = j_data.get('users')
        for follower in followers_data:
            item = InstaparserItem(
                user_id=user_id,
                user_name=username,
                user_followers_n=follow_info['followers'],
                user_followings_n=follow_info['followings'],
                f_account_full_name=follower['full_name'],
                f_account_name=follower['username'],
                f_account_id=follower['pk'],
                f_account_profile_pic_url=follower['profile_pic_url'],
                f_account_type=follow_type
            )
            yield item

    def fetch_csrf_token(self, text):
        ''' Get csrf-token for auth '''
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')
