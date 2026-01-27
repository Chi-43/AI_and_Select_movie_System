import os
import django
import random

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movie_recommender.settings')
django.setup()

from recommendation.models import Movie, User, Rating

def create_sample_data():
    """创建示例数据"""
    
    # 清空现有数据
    Movie.objects.all().delete()
    User.objects.all().delete()
    Rating.objects.all().delete()
    
    # 创建电影
    movies_data = [
        {"title": "肖申克的救赎", "genre": "剧情", "year": 1994, "description": "银行家安迪被冤枉谋杀妻子和她的情人，被判无期徒刑，在肖申克监狱中他利用自己的金融知识帮助狱警逃税，最终成功越狱。"},
        {"title": "教父", "genre": "犯罪", "year": 1972, "description": "维托·柯里昂是黑手党柯里昂家族的首领，带领家族从事非法的勾当，但同时他也是许多弱小平民的保护神，深得人们爱戴。"},
        {"title": "教父2", "genre": "犯罪", "year": 1974, "description": "影片主要讲述第二代教父迈克尔·柯里昂的奋斗历程，同时回忆了第一代教父维多·柯里昂创业的艰辛。"},
        {"title": "黑暗骑士", "genre": "动作", "year": 2008, "description": "蝙蝠侠、警官吉姆·戈登和检察官哈维·丹特联手打击哥谭市的有组织犯罪，但小丑的出现让哥谭市陷入混乱。"},
        {"title": "十二怒汉", "genre": "剧情", "year": 1957, "description": "一个在贫民窟长大的男孩被指控谋杀生父，案件的旁观者和凶器均呈堂铁证如山，而担任此案陪审团的12个人要于案件结案前在陪审团休息室里讨论案情，而讨论结果必须要一致通过才能正式结案。"},
        {"title": "辛德勒的名单", "genre": "传记", "year": 1993, "description": "德国商人奥斯卡·辛德勒在二战期间雇用了1100多名犹太人在他的工厂工作，帮助他们逃过被屠杀的劫数。"},
        {"title": "指环王：王者归来", "genre": "奇幻", "year": 2003, "description": "甘道夫和阿拉贡在罗翰国军队与精灵兵的帮助下，取得圣盔谷的胜利，和树胡们一起打败了白袍巫师萨鲁曼的皮平和梅利，也赶来与阿拉贡他们会合。"},
        {"title": "低俗小说", "genre": "犯罪", "year": 1994, "description": "影片由6个彼此独立而又紧密相连的故事所构成，6个故事都各自讲述了一个不同的事件，但他们却都有着共同的戏剧属性将它们紧密相连。"},
        {"title": "搏击俱乐部", "genre": "剧情", "year": 1999, "description": "该片讲述了生活苦闷的泰勒为了找寻刺激与好友杰克组成'搏击俱乐部'，在那里他们可以把一切不快的情绪宣泄，借着自由搏击获得片刻快感的故事。"},
        {"title": "阿甘正传", "genre": "剧情", "year": 1994, "description": "先天智障的小镇男孩福瑞斯特·甘自强不息，最终'傻人有傻福'地得到上天眷顾，在多个领域创造奇迹的励志故事。"},
        {"title": "盗梦空间", "genre": "科幻", "year": 2010, "description": "讲述由莱昂纳多·迪卡普里奥扮演的造梦师，带领约瑟夫·高登-莱维特、艾伦·佩吉扮演的特工团队，进入他人梦境，从他人的潜意识中盗取机密，并重塑他人梦境的故事。"},
        {"title": "星际穿越", "genre": "科幻", "year": 2014, "description": "在不久的将来，随着地球自然环境的恶化，人类面临着无法生存的威胁。这时科学家们在太阳系中的土星附近发现了一个虫洞，通过它可以打破人类的能力限制，到更遥远外太空寻找延续生命希望的机会。"},
        {"title": "泰坦尼克号", "genre": "爱情", "year": 1997, "description": "1912年泰坦尼克号邮轮在其处女启航时触礁冰山而沉没的事件为背景，讲述了处于不同阶层的两个人穷画家杰克和贵族女露丝抛弃世俗的偏见坠入爱河，最终杰克把生命的机会让给了露丝的感人故事。"},
        {"title": "黑客帝国", "genre": "科幻", "year": 1999, "description": "一名年轻的网络黑客尼奥发现看似正常的现实世界实际上是由一个名为'矩阵'的计算机人工智能系统控制的，尼奥在一名神秘女郎崔妮蒂的引导下见到了黑客组织的首领墨菲斯，三人走上了抗争矩阵征途的故事。"},
        {"title": "飞屋环游记", "genre": "动画", "year": 2009, "description": "讲述了一个老人曾经与老伴约定去一座坐落在遥远南美洲的瀑布旅行，却因为生活奔波一直未能成行，直到政府要强拆自己的老屋时才决定带着屋子一起飞向瀑布，路上与结识的小胖子罗素一起冒险的经历。"},
    ]
    
    movies = []
    for data in movies_data:
        movie = Movie.objects.create(**data)
        movies.append(movie)
        print(f"创建电影: {movie.title}")
    
    # 创建用户
    users_data = [
        {"username": "张三"},
        {"username": "李四"},
        {"username": "王五"},
        {"username": "赵六"},
        {"username": "钱七"},
        {"username": "孙八"},
        {"username": "周九"},
        {"username": "吴十"},
    ]
    
    users = []
    for data in users_data:
        user = User.objects.create(**data)
        users.append(user)
        print(f"创建用户: {user.username}")
    
    # 创建评分
    print("创建评分...")
    for user in users:
        # 每个用户随机评价5-10部电影
        num_ratings = random.randint(5, 10)
        rated_movies = random.sample(movies, num_ratings)
        
        for movie in rated_movies:
            # 随机生成1-5分的评分
            rating_value = random.randint(1, 5)
            Rating.objects.create(user=user, movie=movie, rating=rating_value)
            print(f"  {user.username} 给 {movie.title} 评分: {rating_value}")
    
    print("示例数据创建完成！")
    print(f"共创建 {len(movies)} 部电影")
    print(f"共创建 {len(users)} 个用户")
    print(f"共创建 {Rating.objects.count()} 个评分")

if __name__ == "__main__":
    create_sample_data()