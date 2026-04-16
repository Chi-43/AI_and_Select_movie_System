import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from .models import Rating, Movie, User


class CollaborativeFiltering:
    """协同过滤推荐系统（升级版）"""

    def __init__(self):
        self.user_movie_matrix = None
        self.user_ids = None
        self.movie_ids = None
        self.user_similarity = None
        self.movie_similarity = None

    def build_user_movie_matrix(self):
        """构建用户-电影评分矩阵"""
        ratings = Rating.objects.all().select_related("user", "movie")
        if not ratings.exists():
            return False

        users = User.objects.all()
        movies = Movie.objects.all()

        if not users.exists() or not movies.exists():
            return False

        self.user_ids = [user.id for user in users]
        self.movie_ids = [movie.id for movie in movies]

        self.user_movie_matrix = np.zeros((len(self.user_ids), len(self.movie_ids)))

        user_index = {user_id: idx for idx, user_id in enumerate(self.user_ids)}
        movie_index = {movie_id: idx for idx, movie_id in enumerate(self.movie_ids)}

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

        self.user_similarity = cosine_similarity(self.user_movie_matrix)
        return True

    def calculate_movie_similarity(self):
        """计算电影相似度"""
        if self.user_movie_matrix is None:
            if not self.build_user_movie_matrix():
                return False

        self.movie_similarity = cosine_similarity(self.user_movie_matrix.T)
        return True

    def get_user_rated_movies(self, user_id):
        """获取用户已评分电影"""
        ratings = (
            Rating.objects.filter(user_id=user_id)
            .select_related("movie")
            .order_by("-rating")
        )
        return [
            {
                "movie_id": r.movie.id,
                "title": r.movie.title,
                "rating": r.rating,
                "genre": r.movie.genre,
            }
            for r in ratings
        ]

    def get_top_similar_users(self, user_id, top_n=5):
        """获取最相似的用户"""
        if self.user_similarity is None:
            if not self.calculate_user_similarity():
                return []

        if user_id not in self.user_ids:
            return []

        user_idx = self.user_ids.index(user_id)
        similarities = self.user_similarity[user_idx]

        similar_users = []
        for idx, sim in enumerate(similarities):
            other_user_id = self.user_ids[idx]
            if other_user_id != user_id:
                similar_users.append((other_user_id, float(sim)))

        similar_users.sort(key=lambda x: x[1], reverse=True)
        return similar_users[:top_n]

    def user_based_recommendations_with_scores(self, user_id, top_n=10):
        """基于用户的协同过滤，返回推荐分数"""
        if self.user_similarity is None:
            if not self.calculate_user_similarity():
                return []

        if user_id not in self.user_ids:
            return []

        user_idx = self.user_ids.index(user_id)
        user_similarities = self.user_similarity[user_idx]

        user_ratings = self.user_movie_matrix[user_idx]
        unrated_movies = np.where(user_ratings == 0)[0]

        if len(unrated_movies) == 0:
            return []

        predicted_ratings = []

        for movie_idx in unrated_movies:
            rated_users = np.where(self.user_movie_matrix[:, movie_idx] > 0)[0]
            if len(rated_users) == 0:
                continue

            similarities = user_similarities[rated_users]
            ratings = self.user_movie_matrix[rated_users, movie_idx]

            denom = np.sum(np.abs(similarities))
            if denom > 0:
                predicted_rating = np.sum(similarities * ratings) / denom
                predicted_ratings.append(
                    {
                        "movie_id": self.movie_ids[movie_idx],
                        "score": float(predicted_rating),
                        "algorithm": "user_based",
                    }
                )

        predicted_ratings.sort(key=lambda x: x["score"], reverse=True)
        return predicted_ratings[:top_n]

    def item_based_recommendations_with_scores(self, user_id, top_n=10):
        """基于物品的协同过滤，返回推荐分数"""
        if self.movie_similarity is None:
            if not self.calculate_movie_similarity():
                return []

        if user_id not in self.user_ids:
            return []

        user_idx = self.user_ids.index(user_id)
        user_ratings = self.user_movie_matrix[user_idx]

        rated_movies = np.where(user_ratings > 0)[0]
        unrated_movies = np.where(user_ratings == 0)[0]

        if len(rated_movies) == 0 or len(unrated_movies) == 0:
            return []

        predicted_ratings = []

        for movie_idx in unrated_movies:
            movie_similarities = self.movie_similarity[movie_idx]

            relevant_similarities = movie_similarities[rated_movies]
            relevant_ratings = user_ratings[rated_movies]

            denom = np.sum(np.abs(relevant_similarities))
            if denom > 0:
                predicted_rating = np.sum(relevant_similarities * relevant_ratings) / denom
                predicted_ratings.append(
                    {
                        "movie_id": self.movie_ids[movie_idx],
                        "score": float(predicted_rating),
                        "algorithm": "item_based",
                    }
                )

        predicted_ratings.sort(key=lambda x: x["score"], reverse=True)
        return predicted_ratings[:top_n]

    def get_top_movies_with_scores(self, top_n=10):
        """热门电影推荐，返回平均分和评分人数"""
        ratings = Rating.objects.all().select_related("movie")
        if not ratings.exists():
            return []

        movie_ratings = {}
        for rating in ratings:
            movie_id = rating.movie.id
            if movie_id not in movie_ratings:
                movie_ratings[movie_id] = {
                    "scores": [],
                    "title": rating.movie.title,
                }
            movie_ratings[movie_id]["scores"].append(rating.rating)

        results = []
        for movie_id, data in movie_ratings.items():
            avg_rating = np.mean(data["scores"])
            rating_count = len(data["scores"])
            results.append(
                {
                    "movie_id": movie_id,
                    "score": float(avg_rating),
                    "rating_count": rating_count,
                    "algorithm": "top",
                }
            )

        results.sort(key=lambda x: (x["score"], x["rating_count"]), reverse=True)
        return results[:top_n]

    def build_reason_context(self, user_id, movie_id, algorithm="user_based"):
        """
        构造推荐理由所需上下文
        后面给 AI 推荐理由生成直接用
        """
        try:
            movie = Movie.objects.get(id=movie_id)
        except Movie.DoesNotExist:
            return None

        user_rated_movies = self.get_user_rated_movies(user_id)[:5]
        similar_users = self.get_top_similar_users(user_id, top_n=3)

        context = {
            "user_id": user_id,
            "movie_id": movie.id,
            "movie_title": movie.title,
            "movie_genre": movie.genre,
            "movie_year": movie.year,
            "movie_country": getattr(movie, "country", ""),
            "movie_rating": getattr(movie, "rating", None),
            "algorithm": algorithm,
            "user_high_rating_movies": [
                item for item in user_rated_movies if item["rating"] >= 4
            ],
            "similar_users": similar_users,
        }

        return context

    def user_based_recommendations(self, user_id, top_n=10):
        """兼容旧接口：只返回 movie_id"""
        recs = self.user_based_recommendations_with_scores(user_id, top_n)
        return [item["movie_id"] for item in recs]

    def item_based_recommendations(self, user_id, top_n=10):
        """兼容旧接口：只返回 movie_id"""
        recs = self.item_based_recommendations_with_scores(user_id, top_n)
        return [item["movie_id"] for item in recs]

    def get_top_movies(self, top_n=10):
        """兼容旧接口：只返回 movie_id"""
        recs = self.get_top_movies_with_scores(top_n)
        return [item["movie_id"] for item in recs]