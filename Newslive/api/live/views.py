import time
from django.core.paginator import Paginator, PageNotAnInteger, InvalidPage, EmptyPage
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.cache import cache
from Newslive.api.live.serializer import ser_data
from Newslive.lib.requests_data.index_request import read_redis, tag_obj
# from Newslive.utils.logging import logger
from Newslive.utils.response import APIResponse
from django.views import View


# 每页显示条数
page_num = 15
# 当前时间戳
time_now = time.time()


class Page_data(APIView):

    def get(self, request):
        # logger.debug('%s - %s' % (1, '错误请求方式'))
        return APIResponse(1, '错误请求方式')

    def post(self, request):
        try:
            tag_id = request.data['tag_id']
            page = request.data.get('page', 1)
            page_theme_id = request.data.get('page_theme_id', None)
            if tag_id:
                theme_data = read_redis(tag_id, page_theme_id, 'all')
                if theme_data['list'] == []:
                    return APIResponse(0, '暂无更新数据')
                else:
                    # if str(tag_id) == '0':
                    # 分页
                    paginator = Paginator(theme_data['list'], page_num)
                    try:
                        theme_data_page = paginator.page(page)
                    except PageNotAnInteger:
                        # 如果请求的页数不是整数, 返回第一页。
                        theme_data_page = paginator.page(1)
                    except InvalidPage:
                        # 如果请求的页数不在合法的页数范围内，返回结果的最后一页。
                        theme_data_page = paginator.page(paginator.num_pages)
                    # print(theme_data_page, list(theme_data_page))
                    theme_data = {'list': list(theme_data_page)}

                    # 返回参数
                    data = {'time_now': time_now, 'theme_data': theme_data}
                    return APIResponse(0, "ok", data)
            else:
                return APIResponse(1, '请求参数有误')
        except Exception as e:
            print(e)
            return APIResponse(1, '请求参数有误')

class Page_update(APIView):
    def post(self, request):
        try:
            tag_id = request.data['tag_id']
            page_theme_id = request.data.get('page_theme_id', None)
            if tag_id:
                theme_data = read_redis(tag_id, page_theme_id, 'update')
                if theme_data['list'] == []:
                    return APIResponse(0, '暂无更新数据')
                else:
                    # 返回参数
                    data = {'time_now': time_now, 'theme_data': theme_data}
                    return APIResponse(0, "ok", data)
            else:
                return APIResponse(1, '请求参数有误')
        except Exception as e:
            print(e)
            return APIResponse(1, '请求参数有误')


class Page_detail(APIView):
    def post(self, request):
        try:
            tag_id = request.data['tag_id']
            theme_id = request.data['theme_id']
            if tag_id and theme_id:
                theme_data = read_redis(tag_id, theme_id, 'detail')
                if theme_data['list'] == []:
                    return APIResponse(0, '数据丢失')
                else:
                    for theme in theme_data['list']:
                        if theme['theme_id'] == theme_id:
                            data = {'time_now': time_now, 'theme_data': theme}
                            return APIResponse(0, 'ok', data)
                    return APIResponse(0, '数据丢失')
            else:
                return APIResponse(1, '请求参数有误')
        except Exception as e:
            print(e)
            return APIResponse(1, '请求参数有误')


class List(View):
    def get(self, request):
        tag_id = 0
        if request.GET:
            tag_id = request.GET['tag_id']  
            if not tag_id:
                tag_id = 0
        title = tag_obj[str(tag_id)]
        context = { 
            "title": title, 
            'tag_obj': tag_obj
        }
        return render(request, 'list.html',context)

    def post(self, request):
        return HttpResponse("from post方法")



class Info(View):
    def get(self, request):
        # print("--------开始")
        # print(time.time())
        tag_id = request.GET['tag_id']
        theme_id = request.GET['theme_id']
        data={}

        if tag_id and theme_id: 
            theme_data = read_redis(tag_id, theme_id, 'detail')
            if theme_data['list'] == []:
                return APIResponse(0, '数据丢失')
            else:
                for theme in theme_data['list']:
                    if theme['theme_id'] == theme_id:
                        data = {'time_now': time_now, 'theme_data': theme}
                        break 
               
        else:
            return render(request, 'info.html',{})
        context = {
            "data":data
        }
        # print(data)
        # print(time.time())
        # print("--------结束")
        return render(request, 'info.html',context)

    def post(self, request):
        return HttpResponse("from post方法")


# 404错误
def page_not_found(request):
    return render(request, '404.html')

# 500错误
def page_error(request):
    return render(request, '500.html')