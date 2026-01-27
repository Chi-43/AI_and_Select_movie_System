import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from .models import Rating, Movie, User

class CollaborativeFiltering:
    """协同过滤推荐系统"""
    
    def __init__(self):
        self.user_movie_matrix = None
        self.user_ids = None
        self.movie_ids = None
        self.user_similarity = None
        self.movie_similarity = None
        
    def build_user_movie_matrix(self):
        """构建用户-电影评分矩阵"""
        ratings = Rating.objects.all().select_related('user', 'movie')
        
        if not ratings:
            return False
            
        # 获取所有用户和电影
        users = User.objects.all()
        movies = Movie.objects.all()
        
        if not users or not movies:
            return False
            
        self.user_ids = [user.id for user in users]
        self.movie_ids = [movie.id for movie in movies]
        
        # 创建用户-电影矩阵
        self.user_movie_matrix = np.zeros((len(self.user_ids), len(self.movie_ids)))
        
        # 创建映射字典
        user_index = {user_id: idx for idx, user_id in enumerate(self.user_ids)}
        movie_index = {movie_id: idx for idx, movie_id in enumerate(self.movie_ids)}
        
        # 填充矩阵
        for rating in ratings:
            user_idx = user_index.get(rating.user.id)
            movie_idx = movie_index.get(rating.movie.id)
            if user_idx is not None and movie_idx is not None:
                self.user_movie_matrix[user_idx, movie_idx] = rating.rating
                
        return True
    
    def calculate_user_similarity(self):
        """计算用户相似度"""
        if self.user_movie_matrix is None:
            if not self.build_user_movie_matrix():
                return False
                
        # 使用余弦相似度计算用户相似度
        self.user_similarity = cosine_similarity(self.user_movie_matrix)
        return True
    
    def calculate_movie_similarity(self):
        """计算电影相似度"""
        if self.user_movie_matrix is None:
            if not self.build_user_movie_matrix():
                return False
                
        # 使用余弦相似度计算电影相似度（转置矩阵）
        self.movie_similarity = cosine_similarity(self.user_movie_matrix.T)
        return True
    
    def user_based_recommendations(self, user_id, top_n=10):
        """基于用户的协同过滤推荐"""
        if self.user_similarity is None:
            if not self.calculate_user_similarity():
                return []
                
        # 找到用户索引
        if user_id not in self.user_ids:
            return []
            
        user_idx = self.user_ids.index(user_id)
        
        # 获取相似用户
        user_similarities = self.user_similarity[user_idx]
        
        # 获取用户未评分的电影
        user_ratings = self.user_movie_matrix[user_idx]
        unrated_movies = np.where(user_ratings == 0)[0]
        
        if len(unrated_movies) == 0:
            return []
            
        # 预测评分
        predicted_ratings = []
        for movie_idx in unrated_movies:
            # 找到评过该电影的用户
            rated_users = np.where(self.user_movie_matrix[:, movie_idx] > 0)[0]
            if len(rated_users) == 0:
                continue
                
            # 计算加权平均评分
            similarities = user_similarities[rated_users]
            ratings = self.user_movie_matrix[rated_users, movie_idx]
            
            # 避免除零
            if np.sum(np.abs(similarities)) > 0:
                predicted_rating = np.sum(similarities * ratings) / np.sum(np.abs(similarities))
                predicted_ratings.append((self.movie_ids[movie_idx], predicted_rating))
        
        # 按预测评分排序
        predicted_ratings.sort(key=lambda x: x[1], reverse=True)
        
        return [movie_id for movie_id, _ in predicted_ratings[:top_n]]
    
    def item_based_recommendations(self, user_id, top_n=10):
        """基于物品的协同过滤推荐"""
        if self.movie_similarity is None:
            if not self.calculate_movie_similarity():
                return []
                
        # 找到用户索引
        if user_id not in self.user_ids:
            return []
            
        user_idx = self.user_ids.index(user_id)
        
        # 获取用户已评分的电影
        user_ratings = self.user_movie_matrix[user_idx]
        rated_movies = np.where(user_ratings > 0)[0]
        
        if len(rated_movies) == 0:
            return []
            
        # 获取用户未评分的电影
        unrated_movies = np.where(user_ratings == 0)[0]
        
        if len(unrated_movies) == 0:
            return []
            
        # 预测评分
        predicted_ratings = []
        for movie_idx in unrated_movies:
            # 找到与目标电影相似的已评分电影
            movie_similarities = self.movie_similarity[movie_idx]
            
            # 只考虑用户评过分的电影
            relevant_similarities = movie_similarities[rated_movies]
            relevant_ratings = user_ratings[rated_movies]
            
            # 计算加权平均评分
            if np.sum(np.abs(relevant_similarities)) > 0:
                predicted_rating = np.sum(relevant_similarities * relevant_ratings) / np.sum(np.abs(relevant_similarities))
                predicted_ratings.append((self.movie_ids[movie_idx], predicted_rating))
        
        # 按预测评分排序
        predicted_ratings.sort(key=lambda x: x[1], reverse=True)
        
        return [movie_id for movie_id, _ in predicted_ratings[:top_n]]
    
    def get_top_movies(self, top_n=10):
        """获取评分最高的电影"""
        ratings = Rating.objects.all()
        if not ratings:
            return []
            
        # 计算每部电影的平均评分
        movie_ratings = {}
        for rating in ratings:
            movie_id = rating.movie.id
            if movie_id not in movie_ratings:
                movie_ratings[movie_id] = []
            movie_ratings[movie_id].append(rating.rating)
        
        # 计算平均分
        avg_ratings = []
        for movie_id, ratings_list in movie_ratings.items():
            avg_rating = np.mean(ratings_list)
            avg_ratings.append((movie_id, avg_rating, len(ratings_list)))
        
        # 按评分排序（考虑评分数量和评分）
        avg_ratings.sort(key=lambda x: (x[1], x[2]), reverse=True)
        
        return [movie_id for movie_id, _, _ in avg_ratings[:top_n]]